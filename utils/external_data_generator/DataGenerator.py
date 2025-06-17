from abc import ABC, abstractmethod

from lib.ConsoleOutput import ConsoleOutput


class DataGenerator(ABC):

    def __init__(self):
        super().__init__()
        self._logger = ConsoleOutput(type(self).__name__)

    @abstractmethod
    def generate(self) -> list[str]:
        """
        Handler interface for data cluster
        """
        pass
