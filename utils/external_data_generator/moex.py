#!/usr/bin/env python3
# coding=utf-8

import json
import math
import os
from collections import deque

from lib.ConsoleOutput import ConsoleOutput
from lib.LoggableRequester import LoggableRequester
from DataGenerator import DataGenerator


def write_to_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
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
                "names": ["TQCB", "TQOB", "TQIR", "TQOY", "TQRD", "TQOD"]
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
    requester = LoggableRequester(logger)
    for instr_t, instr_subtypes in boards.items():
        for instr_subtype, boards in instr_subtypes.items():
            for board in boards["names"]:
                req_url = board_securities_url_pattern.format(type=instr_t, subtype=instr_subtype, board=board)
                req_data = {"iss.only": "securities"}
                if "lang" in boards:
                    req_data["lang"] = boards["lang"]

                resp = (requester.message(f"[{curr_req_num}/{num_of_names}] Requesting {board} board securities... ")
                        .request(LoggableRequester.Methods.GET, req_url, headers, req_data)).json()

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
    requester = LoggableRequester(logger)
    processed, total, counter = start, start, 1
    while processed <= total:
        requester.message(f"Requesting page {counter}/{'undefined' if start == total else math.ceil(total/page_size)}... ")
        n_resp, page_size, total = request_page(requester, base_url, headers, params, processed, page_size)
        processed += page_size
        counter += 1
        resp['rates']['columns'] = n_resp['rates']['columns']
        resp['rates']['data'] += n_resp['rates']['data']

    return resp


def request_page(requester: LoggableRequester, base_url: str, headers: dict[str, str], params: dict, start: int, page_size: int):
    params['start'] = start
    params['page_size'] = page_size
    response = requester.request(LoggableRequester.Methods.GET, base_url, headers, params).json()

    cursor = {}
    for col, index in zip(response['rates.cursor']['columns'], range(len(response['rates.cursor']['data'][0]))):
        cursor[col] = response['rates.cursor']['data'][0][index]

    return response, int(cursor['PAGESIZE']), int(cursor['TOTAL'])


class MOEXDataGenerator(DataGenerator):

    def generate(self) -> list[str]:

        dictionaries_paths = {
            "boards_securities": "moex_boards_securities.json",
            "index_boards_securities": "moex_index_boards_securities.json",
            "stock_rates": "moex_stock_rates.json"
        }

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en,ru;q=0.7,en-US;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

        boards_securities = request_boards_securities(self._logger, headers)
        self._logger.log("Writing to file... ", write_to_file, dictionaries_paths["boards_securities"], boards_securities)
        if not os.path.getsize(dictionaries_paths["boards_securities"]):
            e = OSError("Requested data are empty")
            self._logger.error(e)
            raise e

        index_boards_securities_url = "https://iss.moex.com/iss/engines/stock/markets/index/securities.json"
        index_boards_securities = (LoggableRequester(self._logger).message("Requesting index boards securities... ")
                                   .request(LoggableRequester.Methods.GET, index_boards_securities_url, headers, {"lang": "ru"}).json())

        self._logger.log("Writing to file... ", write_to_file, dictionaries_paths["index_boards_securities"], index_boards_securities)
        if not os.path.getsize(dictionaries_paths["index_boards_securities"]):
            e = OSError("Requested data are empty")
            self._logger.error(e)
            raise e

        rates_base_url = "https://iss.moex.com/iss/apps/infogrid/stock/rates.json"
        rates_base_url_params = {"_": 1607005374424, "lang": "ru", "iss.meta": "off", "sort_order": "asc", "sort_column": "SECID"}
        morning_rates_url_params = rates_base_url_params | {"morning": 1}
        morning_moex_stock_rates = paginated_request(self._logger, rates_base_url, headers, morning_rates_url_params, 0, 100)
        evening_rates_url_params = rates_base_url_params | {"evening": 1}
        evening_moex_stock_rates = paginated_request(self._logger, rates_base_url, headers, evening_rates_url_params, 0, 100)
        weekend_rates_url_params = rates_base_url_params | {"weekend": 1}
        weekend_moex_stock_rates = paginated_request(self._logger, rates_base_url, headers, weekend_rates_url_params, 0, 100)
        moex_stock_rates = {
            "morning": morning_moex_stock_rates['rates'],
            "evening": evening_moex_stock_rates['rates'],
            "weekend": weekend_moex_stock_rates['rates'],
        }
        self._logger.log("Writing to file... ", write_to_file, dictionaries_paths["stock_rates"], moex_stock_rates)
        if not os.path.getsize(dictionaries_paths["stock_rates"]):
            e = OSError("Requested data are empty")
            self._logger.error(e)
            raise e

        return list(dictionaries_paths.values())


if __name__ == "__main__":
    try:
        MOEXDataGenerator().generate()
        exit(0)
    except (OSError, KeyError, TypeError):
        exit(1)
