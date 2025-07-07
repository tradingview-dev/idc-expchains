import time

from deepdiff.serialization import json_dumps

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import file_writer, get_headers


class SAUDIDataGenerator(DataGenerator):

    def generate(self) -> list[str]:
        url = 'https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory/!ut/p/z1/lc_LCsIwEAXQb-kHSG6jiXGZLhIL9hHTas1GspKAVhHx-63uWt-zGzh3mEscaYhr_TXs_CUcW7_v9o3jWyY56Fyg0LaSMMpWST5TMVJG1n0gMs1hcmkKOmXQq5i4v_KwJetAmY0XWEKD_5bHm5H4nnd9AlOLO1EJE6DAZAheVBxceO7wAB-etP5MToe6bhDSkYyiG8La9T0!/p0/IZ7_5A602H80OOMQC0604RU6VD10F2=CZ6_5A602H80OGSTA0QFSTBN9F10I5=NJgetCompanyListByMarknetAndSectors=/'
        post_data = {
            'sector': 'All',
            'symbol': '',
            'letter': ''
        }

        saudi_main_market = "saudi_main_market.json"
        saudi_nomu_parallel_market = "saudi_nomu_parallel_market.json"

        requester = LoggableRequester(self._logger, retries=5, delay=10)
        try:
            resp = requester.request(LoggableRequester.Methods.POST, url, get_headers(), {**post_data, 'marketType': 'M'})
            file_writer(json_dumps(resp.json(), indent=4, ensure_ascii=False), saudi_main_market)

            time.sleep(20) # try to avoid a bot protection

            resp = requester.request(LoggableRequester.Methods.POST, url, get_headers(), {**post_data, 'marketType': 'S'})
            file_writer(json_dumps(resp.json(), indent=4, ensure_ascii=False), saudi_nomu_parallel_market)

            return [saudi_main_market, saudi_nomu_parallel_market]
        except OSError as e:
            self._logger.error(e)
            raise e


if __name__ == "__main__":
    try:
        SAUDIDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)