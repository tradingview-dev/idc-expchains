from deepdiff.serialization import json_dumps

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class CanadaDataGenerator(DataGenerator):

    def generate(self):
        url = "http://webapi.thecse.com/trading/listed/market/security_maintenance.json"
        descriptions = "canadian_descriptions.json"

        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, get_headers())
            file_writer(json_dumps(resp.json(), indent=4, ensure_ascii=False), descriptions)
            return 0
        except IOError as e:
            self._logger.error(e)
            return 1


if __name__ == "__main__":
    exit(CanadaDataGenerator().generate())
