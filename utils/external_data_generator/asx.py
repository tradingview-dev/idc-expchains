from Handler import Handler
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class ASXHandler(Handler):

    def handle(self, data_cluster = None):

        BASE_URL = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file"
        OUT = "asx_descriptions.csv"

        requester = LoggableRequester(self._logger, retries=5, delay=5)

        try:
            resp = requester.request(LoggableRequester.Methods.GET, BASE_URL, get_headers())
            file_writer(resp.text, OUT)
            return 0
        except Exception as e:
            self._logger.error(e)
            return 1


if __name__ == "__main__":
    exit(ASXHandler().handle())
