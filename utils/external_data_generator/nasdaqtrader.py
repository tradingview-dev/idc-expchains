from Handler import Handler
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class NASDAQTraderHandler(Handler):

    def handle(self, data_cluster = None):
        nasdaqtrader_url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        nasdaqtrader_descriptions = "nasdaqtrader_descriptions.txt"

        requester = LoggableRequester(self._logger, retries=5, delay=5)

        try:
            resp = requester.request(LoggableRequester.Methods.GET, nasdaqtrader_url, get_headers())
            file_writer(resp.text, nasdaqtrader_descriptions)
            return 0
        except Exception as e:
            self._logger.error(e)
            return 1


if __name__ == "__main__":
    exit(NASDAQTraderHandler().handle())
