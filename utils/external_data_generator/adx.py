from deepdiff.serialization import json_dumps

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


class ADXDataGenerator(DataGenerator):

    def generate(self) -> list[str]:

        url = "https://adxservices.adx.ae/WebServices/DataServices/api/web/assets"
        adx_data_regular = "adx_data_regular.json"
        adx_data_fund = "adx_data_fund.json"

        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.POST, url, get_headers(), {"Status": "L", "Boad": "REGULAR", "Del": "0"})
            file_writer(json_dumps(resp.json(), indent=4, ensure_ascii=False), adx_data_regular)

            resp = requester.request(LoggableRequester.Methods.POST, url, get_headers(), {"Status": "L", "Boad": "FUND", "Del": "0"})
            file_writer(json_dumps(resp.json(), indent=4, ensure_ascii=False), adx_data_fund)
        except OSError as e:
            self._logger.error(e)
            raise e

        return [adx_data_regular, adx_data_fund]


if __name__ == "__main__":
    try:
        ADXDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
