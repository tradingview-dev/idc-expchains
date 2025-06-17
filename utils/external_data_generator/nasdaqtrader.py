from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class NASDAQTraderDataGenerator(DataGenerator):

    def generate(self):
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        descriptions = "nasdaqtrader_descriptions.txt"

        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, get_headers())
            file_writer(resp.text, descriptions)
            return 0
        except IOError as e:
            self._logger.error(e)
            return 1


if __name__ == "__main__":
    exit(NASDAQTraderDataGenerator().generate())
