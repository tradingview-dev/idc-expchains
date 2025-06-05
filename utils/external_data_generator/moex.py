#!/usr/bin/env python3
# coding=utf-8

import enum
import json
import os
import sys
from collections import deque
from json import JSONDecodeError
from typing import Mapping, Generic, TypeVar, Callable

from requests import request, RequestException

from lib.ConsoleOutput import ConsoleOutput

T1 = TypeVar('T1')
class Retryer(Generic[T1]):
    def __init__(self, logger: ConsoleOutput = None, attempts: int = 3):
        super().__init__()
        self._attempts = attempts
        self._logger = ConsoleOutput(type(self).__name__) if logger is None else logger

    def apply(self, func: Callable, *args) -> T1:
        for i in range(1, self._attempts):
            try:
                return func(*args)
            except Exception:
                if i < self._attempts:
                    self._logger.info(f"Applying {i}/{self._attempts} attempt... ", False)
        raise RuntimeError("Attempts are left")


T2 = TypeVar('T2')
class LoggedRequest(Generic[T2]):

    def __init__(self, logger: ConsoleOutput = None):
        super().__init__()
        # protected non-static variables
        self._logger = ConsoleOutput(type(self).__name__) if logger is None else logger

    class Methods(enum.StrEnum):
        GET = "GET"
        POST = "POST"

    __TIMEOUT = (10, 20) # (connect, read) in sec

    def request(self, method: Methods, url: str, headers: Mapping[str, str | bytes | None] | None, data: dict[str, str]) -> T2:
        """

        :param method:
        :param url:
        :param headers:
        :param data:
        :return:
        :raise RequestException:
        :raise JSONDecodeError:
        """
        def __request():
            payload = {
                "data": data if method is LoggedRequest.Methods.POST else None,
                "params": data if method is LoggedRequest.Methods.GET else None
            }
            try:
                resp = request(method.value, url, timeout=self.__TIMEOUT, headers=headers, data=payload['data'], params=payload['params'])
                resp.raise_for_status()
                if not resp:
                    raise RequestException("Response is empty")
                return resp.json()
            except RequestException as e:
                self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
                self._logger.error(f"Failed to get data from {e.request.url} by {e.request.method} method:")
                raise e
            except JSONDecodeError as e:
                self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
                self._logger.error(f"Failed to decode response: {e.msg}\nStart index of doc where parsing failed {e.pos}, line {e.lineno}, column {e.colno}")
                raise e

        return Retryer[T2](self._logger).apply(__request)


def write_to_file(filename, content):
    with open(filename, 'w') as file:
        json.dump(content, file, ensure_ascii=False)


def request_boards_securities(logger: ConsoleOutput, headers: dict[str, str]):

    def count_names(data: dict):
        queue = deque([data])
        total = 0

        while queue:
            current_dict = queue.popleft()

            for key, value in current_dict.items():
                if key == 'names':
                    total += len(value)
                elif isinstance(value, dict):
                    queue.append(value)

        return total

    boards = {
        "stock": {
            "shares": {
                "names": ["TQBR", "TQIF", "TQPI", "TQTF", "TQTD", "TQTE"]
            },
            "index": {
                "names": ["RTSI", "SNDX", "MMIX"],
                "lang": "en"
            },
            "bonds": {
                "names": ["TQCB", "TQOB", "TQIR"]
            }
        },
        "otc": {
            "shares": {
                "names": ["MTQR"]
            }
        },
        "currency": {
            "selt": {
                "names": ["CETS", "SDBP"]
            }
        },
        "futures": {
            "forts": {
                "names": ["RFUD"]
            }
        }
    }
    board_securities_url_pattern: str = "https://iss.moex.com/iss/engines/{type}/markets/{subtype}/boards/{board}/securities.json"
    boards_securities = {}
    num_of_names = count_names(boards)
    curr_req_num = 1
    for instr_t, instr_subtypes in boards.items():
        for instr_subtype, boards in instr_subtypes.items():
            for board in boards["names"]:
                req_url = board_securities_url_pattern.format(type=instr_t, subtype=instr_subtype, board=board)
                req_data = {"iss.only": "securities"}
                if "lang" in boards:
                    req_data["lang"] = boards["lang"]
                logger.info(f"[{curr_req_num}/{num_of_names}] Requesting {board} board securities... ", False)
                try:
                    resp = LoggedRequest[dict](logger).request(LoggedRequest.Methods.GET, req_url, headers, req_data)
                    logger.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)
                except (RequestException, JSONDecodeError) as e:
                    raise e

                securities = resp['securities']
                boards_securities[board] = {
                    'columns': securities['columns'],
                    'data': securities['data']
                }

                curr_req_num += 1

    return boards_securities


def paginated_request(logger: ConsoleOutput, base_url, headers: dict[str, str], params: dict, start: int, page_size: int):
    resp = {
        "rates": {
            "data": []
        }
    }
    requester = LoggedRequest[dict](logger)
    processed, total, counter = start, start, 1
    while processed <= total:
        logger.info(f"Requesting page {counter}/{'undefined' if start == total else total/page_size}... ", False)
        n_resp, page_size, total = request_page(requester, base_url, headers, params, processed, page_size)
        logger.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)
        processed += page_size
        counter += 1
        resp['rates']['columns'] = n_resp['rates']['columns']
        resp['rates']['data'] += n_resp['rates']['data']

    return resp


def request_page(requester: LoggedRequest, base_url: str, headers: dict[str, str], params: dict, start: int, page_size: int):
    params['start'] = start
    params['page_size'] = page_size
    response = requester.request(LoggedRequest.Methods.GET, base_url, headers, params)

    cursor = {}
    for col, index in zip(response['rates.cursor']['columns'], range(len(response['rates.cursor']['data'][0]))):
        cursor[col] = response['rates.cursor']['data'][0][index]

    return response, int(cursor['PAGESIZE']), int(cursor['TOTAL'])


def update_moex_data(logger: ConsoleOutput) -> int:

    dictionaries_paths = {
        "boards_securities": "moex_boards_securities.json",
        "index_boards_securities": "moex_index_boards_securities.json",
        "stock_rates": f"moex_stock_rates.json"
    }

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en,ru;q=0.7,en-US;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    boards_securities = request_boards_securities(logger, headers)
    logger.log("Writing to file... ", write_to_file, dictionaries_paths["boards_securities"], boards_securities)
    if not os.path.getsize(dictionaries_paths["boards_securities"]):
        logger.error("Requested data are empty")
        return 1

    index_boards_securities_url = "https://iss.moex.com/iss/engines/stock/markets/index/securities.json"
    logger.info(f"Requesting index boards securities... ", False)
    try:
        index_boards_securities = LoggedRequest[dict](logger).request(LoggedRequest.Methods.GET, index_boards_securities_url, headers, {"lang": "ru"})
        logger.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)
    except Exception as e:
        logger.error(e)
        return 1

    logger.log("Writing to file... ", write_to_file, dictionaries_paths["index_boards_securities"], index_boards_securities)
    if not os.path.getsize(dictionaries_paths["index_boards_securities"]):
        logger.error("Requested data are empty")
        return 1

    rates_base_url = "https://iss.moex.com/iss/apps/infogrid/stock/rates.json"
    rates_base_url_params = {"_": 1607005374424, "lang": "ru", "iss.meta": "off", "sort_order": "asc", "sort_column": "SECID"}
    morning_rates_url_params = rates_base_url_params | {"morning": 1}
    morning_moex_stock_rates = paginated_request(logger, rates_base_url, headers, morning_rates_url_params, 0, 100)
    evening_rates_url_params = rates_base_url_params | {"evening": 1}
    evening_moex_stock_rates = paginated_request(logger, rates_base_url, headers, evening_rates_url_params, 0, 100)
    weekend_rates_url_params = rates_base_url_params | {"weekend": 1}
    weekend_moex_stock_rates = paginated_request(logger, rates_base_url, headers, weekend_rates_url_params, 0, 100)
    moex_stock_rates = {
        "morning": morning_moex_stock_rates['rates'],
        "evening": evening_moex_stock_rates['rates'],
        "weekend": weekend_moex_stock_rates['rates'],
    }
    logger.log("Writing to file... ", write_to_file, dictionaries_paths["stock_rates"], moex_stock_rates)
    if not os.path.getsize(dictionaries_paths["stock_rates"]):
        logger.error("Requested data are empty")
        return 1

    return 0


def moex_handler():
    logger = ConsoleOutput(os.path.splitext(os.path.basename(__file__))[0])
    try:
        return update_moex_data(logger)
    except Exception as e:
        logger.error(e)
        return 1


if __name__ == "__main__":
    sys.exit(moex_handler())
