import time
from typing import Callable, Generic, TypeVar

from requests import RequestException

from lib.ConsoleOutput import ConsoleOutput

T = TypeVar('T')
class Retryer(Generic[T]):

    def __init__(self, logger: ConsoleOutput = None, retries: int = 3, delay = 0):
        super().__init__()
        self._retries = retries
        self._delay = delay
        self._logger = ConsoleOutput(type(self).__name__) if logger is None else logger

    def apply(self, func: Callable, *args) -> T:
        for i in range(self._retries + 1):
            try:
                return func(*args)
            except Exception:
                if i < self._retries:
                    self._logger.info(f"Applying {i+1}/{self._retries} attempt", False)
                    if self._delay > 0:
                        self._logger.info(f" (delay {self._delay} sec)", False)
                        time.sleep(self._delay)
                    self._logger.info("... ", False)
        raise RequestException("Attempts are left")
