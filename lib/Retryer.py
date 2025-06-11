from typing import Callable, Generic, TypeVar

from lib.ConsoleOutput import ConsoleOutput

T = TypeVar('T')
class Retryer(Generic[T]):
    def __init__(self, logger: ConsoleOutput = None, attempts: int = 3):
        super().__init__()
        self._attempts = attempts
        self._logger = ConsoleOutput(type(self).__name__) if logger is None else logger

    def apply(self, func: Callable, *args) -> T:
        for i in range(self._attempts + 1):
            try:
                return func(*args)
            except Exception:
                if i < self._attempts:
                    self._logger.info(f"Applying {i+1}/{self._attempts} attempt... ", False)
        raise RuntimeError("Attempts are left")
