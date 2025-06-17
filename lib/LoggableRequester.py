import enum
from typing import Mapping

from requests import request, RequestException, Response

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

    def request(self, method: Methods, url: str, headers: Mapping[str, str | bytes | None] | None, data: dict[str, str] = None) -> Response:
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
        self._logger.info(f"Requesting to {url} " if self._msg is None else self._msg, False)
        return (Retryer[Response](self._logger, self._retries, self._delay)
                .apply(self.__request, method, url, self._timeout, headers, payload['data'], payload['params']))


    def __request(self, method: Methods, url, timeout, headers, data , params) -> Response:
        """

        :param method:
        :param url:
        :param headers:
        :param data:
        :return:
        :raise RequestException:
        """
        try:
            resp = request(method.value, url, timeout=timeout, headers=headers, data=data, params=params)
            if not resp: # checks the response status code and raises an exception for HTTP errors (4xx or 5xx)
                raise RequestException(response=resp)
            self._logger.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)
            return resp
        except RequestException as e:
            self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
            self._logger.error(f"Failed to get data from {e.request.url} by {e.request.method} method: {e.response.status_code} - {e.response.reason}")
            raise e
