from deepdiff.serialization import json_dumps

from Handler import Handler
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class ADXHandler(Handler):

    def handle(self, data_cluster = None):

        BASE_URL = "https://adxservices.adx.ae/WebServices/DataServices/api/web/assets"
        adx_data_regular = "adx_data_regular.json"
        adx_data_fund = "adx_data_fund.json"

        requester = LoggableRequester(self._logger, retries=5, delay=5)

        try:
            resp = requester.request(LoggableRequester.Methods.POST, BASE_URL, get_headers(), {"Status": "L", "Boad": "REGULAR", "Del": "0"})
            file_writer(json_dumps(resp.json(), indent=4, ensure_ascii=False), adx_data_regular)

            resp = requester.request(LoggableRequester.Methods.POST, BASE_URL, get_headers(), {"Status": "L", "Boad": "FUND", "Del": "0"})
            file_writer(json_dumps(resp.json(), indent=4, ensure_ascii=False), adx_data_fund)

            return 0
        except Exception as e:
            self._logger.error(e)
            return 1


if __name__ == "__main__":
    exit(ADXHandler().handle())
