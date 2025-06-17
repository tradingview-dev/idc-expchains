from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class FinraDataGenerator(DataGenerator):

    def generate(self) -> list[str]:
        url = "https://info.tradingview.com/factset_finra_isins.csv"
        isins = "factset_finra_isins.csv"

        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, get_headers())
            file_writer(resp.text, isins)
            return [isins]
        except OSError as e:
            self._logger.error(e)
            raise e


if __name__ == "__main__":
    try:
        FinraDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
