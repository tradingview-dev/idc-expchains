import enum
from abc import ABC
from typing import TypeVar, Generic, Mapping

from requests import request, RequestException, Response

from lib.ConsoleOutput import ConsoleOutput
from lib.Retryer import Retryer

class LoggedRequest(ABC):

    def __init__(self, logger: ConsoleOutput = None):
        super().__init__()
        # protected non-static variables
        self._logger = ConsoleOutput(type(self).__name__) if logger is None else logger

    class Methods(enum.StrEnum):
        GET = "GET"
        POST = "POST"

    __TIMEOUT = 15 # sec

    def request(self, method: Methods, url: str, headers: Mapping[str, str | bytes | None] | None, data: dict[str, str]) -> Response:
        """

        :param method:
        :param url:
        :param headers:
        :param data:
        :return:
        :raise RequestException:
        :raise JSONDecodeError:
        """
        payload = {
            "data": data if method is LoggedRequest.Methods.POST else None,
            "params": data if method is LoggedRequest.Methods.GET else None
        }
        return Retryer[Response](self._logger).apply(self.__request, method, url, self.__TIMEOUT, headers, payload['data'], payload['params'])


    @staticmethod
    def __request(method: Methods, url, timeout, headers, data , params) -> Response:
        """

        :param method:
        :param url:
        :param headers:
        :param data:
        :return:
        :raise RequestException:
        :raise JSONDecodeError:
        """
        try:
            resp = request(method.value, url, timeout=timeout, headers=headers, data=data, params=params)
            if not resp:
                raise RequestException("Response is empty")
            resp.raise_for_status()  # checks the response status code and raises an exception for HTTP errors (4xx or 5xx)
            return resp
        except RequestException as e:
            # self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
            # self._logger.error(f"Failed to get data from {e.request.url} by {e.request.method} method: {str(e)}")
            raise e
