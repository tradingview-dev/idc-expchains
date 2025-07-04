from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class NASDAQTraderDataGenerator(DataGenerator):

    def generate(self) -> list[str]:
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        descriptions = "nasdaqtrader_descriptions.txt"

        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, get_headers())
            file_writer(resp.text, descriptions)
            return [descriptions]
        except OSError as e:
            self._logger.error(e)
            raise e


if __name__ == "__main__":
    try:
        NASDAQTraderDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
