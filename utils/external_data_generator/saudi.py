import time

from deepdiff.serialization import json_dumps

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import file_writer


class SAUDIDataGenerator(DataGenerator):

    def _save_response(self, response, filename):
        resp_json = response.json()
        for record in resp_json["data"]:
            record.pop("stockValue")
            record.pop("watchlist")
            record.pop("watchListID")

        resp_json["data"].sort(key=lambda r: r["symbol"])

        file_writer(json_dumps(resp_json, indent=4, ensure_ascii=False), filename)

    def generate(self) -> list[str]:
        url = 'https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory/!ut/p/z1/lc_LCsIwEAXQb-kHSG6jiXGZLhIL9hHTas1GspKAVhHx-63uWt-zGzh3mEscaYhr_TXs_CUcW7_v9o3jWyY56Fyg0LaSMMpWST5TMVJG1n0gMs1hcmkKOmXQq5i4v_KwJetAmY0XWEKD_5bHm5H4nnd9AlOLO1EJE6DAZAheVBxceO7wAB-etP5MToe6bhDSkYyiG8La9T0!/p0/IZ7_5A602H80OOMQC0604RU6VD10F2=CZ6_5A602H80OGSTA0QFSTBN9F10I5=NJgetCompanyListByMarknetAndSectors=/'

        saudi_main_market = "saudi_main_market.json"
        saudi_nomu_parallel_market = "saudi_nomu_parallel_market.json"

        requester = LoggableRequester(self._logger, retries=5, delay=10)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0',
                'Accept': '*/*',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Referer': 'https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory/!ut/p/z1/lc_LDoIwEAXQb-EDzFzQ1rosCyqJPGqpYjeGhTEkWl0Yv190B75nN8m5k7nkqCbnm2u7by7tyTeHbt84vmWSI5oLFMpUEjoxVZzPkhApo3UfiExx6FzqIpoyqFVI7q88TMk6UGbjBZZQ4L_l8WYkvuddn0BbcSdJzAQiYDIELyoOLjx3eIAPT5qdp_PR2hptOpJBcAPgEs77/dz/d5/L0lHSkovd0RNQUZrQUVnQSEhLzROVkUvYXI!/',
                'Origin': 'https://www.saudiexchange.sa',
                'Connection': 'keep-alive',
                'Cookie': 'BIGipServerSaudiExchange.sa.app~SaudiExchange.sa_pool=2600407468.20480.0000; TS01fdeb15=0102d17fad39a6dff96415afa9aac383111c53ea0e87a221f81202e4fb8d7b1772d04fc4ba50c268cd3907f51fd8998ae3048a927c98d39018ea9b9310970ddf23395d787d7759769082d6a5ba96750d00e68c91f0; com.ibm.wps.state.preprocessors.locale.LanguageCookie=ar',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'same-origin',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Priority': 'u=4',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
            resp = requester.request(LoggableRequester.Methods.POST, url, headers, {
                'sector': 'All',
                'symbol': '',
                'letter': '',
                "marketType": 'M'
            })
            self._save_response(resp, saudi_main_market)

            time.sleep(20)

            resp = requester.request(LoggableRequester.Methods.POST, url, headers, {
                'sector': '',
                'symbol': '',
                'letter': '',
                "marketType": 'S'
            })
            self._save_response(resp, saudi_nomu_parallel_market)

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