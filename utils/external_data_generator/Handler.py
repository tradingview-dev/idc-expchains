import os
from abc import ABC, abstractmethod

from lib.ConsoleOutput import ConsoleOutput


class Handler(ABC):

    def __init__(self):
        super().__init__()
        self._logger = ConsoleOutput(type(self).__name__)

    @abstractmethod
    def handle(self, data_cluster: str = None) -> int:
        """
        Handler interface for data cluster
        """
        pass
