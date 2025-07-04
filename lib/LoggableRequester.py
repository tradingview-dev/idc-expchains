import enum
import json
from json import JSONDecodeError
from typing import Mapping

from requests import Session, Request, Response, RequestException, ReadTimeout

from lib.ConsoleOutput import ConsoleOutput
from lib.Retryer import Retryer


class LoggableRequester:
    """
    A Simple Loggable Requester
    """

    def __init__(self, logger: ConsoleOutput = None, retries = 3, timeout = 5, delay = 0):
        # protected non-static variables
        self._logger = ConsoleOutput(type(self).__name__) if logger is None else logger
        self._retries = retries
        self._timeout = timeout
        self._delay = delay
        self._msg = None

    class Methods(enum.StrEnum):
        GET = "GET"
        POST = "POST"

    def message(self, msg: str) -> "LoggableRequester":
        self._msg = msg
        return self

    def request(self, method: Methods, url: str, headers: Mapping[str, str | bytes | None] = None, data: dict[str, str] = None) -> Response:
        """

        :param method:
        :param url:
        :param headers:
        :param data:
        :return:
        :raise RequestException:
        """
        payload = {
            "data": data if method is LoggableRequester.Methods.POST else None,
            "params": data if method is LoggableRequester.Methods.GET else None
        }
        self._logger.info(f"[{method.value}] Requesting to {url}... " if self._msg is None else self._msg, False)
        return (Retryer[Response](self._logger, self._retries, self._delay)
                .apply(self.__request, method.value, url, self._timeout, headers, payload['data'], payload['params']))


    def __request(self, method: Methods, url, timeout, headers, data, params) -> Response:
        """

        :param method:
        :param url:
        :param headers:
        :param data:
        :return:
        :raise RequestException:
        """
        request = Request(method, url, headers=headers, data=data, params=params)
        prepared_request = request.prepare()
        try:
            with Session() as session:
                response = session.send(prepared_request, timeout=timeout)
            if not response: # checks the response status code and raises an exception for HTTP errors (4xx or 5xx)
                raise RequestException(request=request, response=response)
            self._logger.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)
            return response
        except ReadTimeout as e:
            self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
            self._logger.error(e)
            raise e
        except RequestException as e:
            self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
            msg = f"{e.response.status_code} - {e.response.reason}"
            try:
                self._logger.error(f"{msg}: {json.loads(e.response.text)['Message']}")
            except (JSONDecodeError, KeyError, TypeError):
                self._logger.error(msg)
            raise e
