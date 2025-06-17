import urllib.parse
from abc import ABC, abstractmethod

from DataGenerator import DataGenerator
from lib.ConsoleOutput import ConsoleOutput
from lib.LoggableRequester import LoggableRequester
from utils import file_writer


def save_to_csv(dst: str, data: dict):
    with open(dst, "w", encoding="utf-8") as file:
        file.write("key;local-description\n")
        for key, local_description in data.items():
            file.write(f"{key};{local_description}\n")


class KoreaProducts(ABC):

    # protected static variables
    _HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-endcoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.5",
        "connection": "keep-alive",
        "host": "data.krx.co.kr",
        "referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201060202",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
    }

    def __init__(self):
        super().__init__()
        self._logger = ConsoleOutput(type(self).__name__)

    @abstractmethod
    def get_local_descriptions(self) -> dict:
        pass


class Stocks(KoreaProducts):

    def get_local_descriptions(self) -> dict:
        url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
        payload = {
            "code": "gRY0jP6rQnfIF4FBiKhU6zCBs%2Fh%2FA%2BJ7QlF9gsIMcSoRtSksuLS7Bnxpl86F7dAOvXfGx9S2U5wgvoxsacATRRtmGtORI4WrGDmruVe6oXtCqUypoW0Lp6SAPP0PhVkgThCTcjIZNPI5lCTubZnhjio6AHXdxc45YVEhz4JdugHPMxvIwHadpQpCGE1HxZAXvTCprTIXuXT9XxFb88awpQ%3D%3D"
        }
        payload["code"] = urllib.parse.unquote(payload["code"])
        resp = LoggableRequester(self._logger, retries=5, delay=5).request(LoggableRequester.Methods.GET, url, self._HEADERS, payload)
        resp.encoding = 'euc-kr'
        return {"csv": resp.text}


class Commodities(KoreaProducts):

    def get_local_descriptions(self) -> dict:
        requester = LoggableRequester(self._logger, 5, delay=5)
        blds = ["dbms/MDC/STAT/standard/MDCSTAT15101", "dbms/MDC/STAT/standard/MDCSTAT15801"]
        data = {
            'locale': 'en',
            'prodId': 'KRDRVFUEQU',
            'subProdId': '',
            'csvxls_isNo': 'false'
        }
        result = {}
        for bld in blds:
            data['bld'] = bld
            resp = requester.request(LoggableRequester.Methods.POST, "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd", self._HEADERS, data)
            spots: dict = resp.json()["output"]
            for spot in spots:
                result[spot["ISU_ENG_NM"]] = spot["ISU_NM"]

        return result


class Derivatives(KoreaProducts):

    def get_local_descriptions(self) -> dict:
        requester = LoggableRequester(self._logger, delay=5)

        url = "http://data.krx.co.kr/comm/bldAttendant/executeForResourceBundle.cmd?baseName=krx.mdc.i18n.component&key=B107.bld&locale=en"
        codes = requester.request(LoggableRequester.Methods.GET, url, self._HEADERS).json()["result"]["output"]
        prodIds = []
        for code in codes:
            if "Option" in code["name"]:
                continue
            prodIds.append(code["value"])

        url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        data = {
            'locale': 'en',
            'csvxls_isNo': 'false',
            'bld': 'dbms/MDC/STAT/standard/MDCSTAT12801'
        }
        result = {}
        for prodId in prodIds:
            data['prodId'] = prodId
            data['subProdId'] = prodId
            futures_roots = requester.request(LoggableRequester.Methods.POST, url, self._HEADERS, data).json()["output"]
            for root in futures_roots:
                result[root["ISU_CD"]] = root["ISU_NM"]

        return result


class KoreaDataGenerator(DataGenerator):

    def generate(self) -> list[str]:
        descriptions = {}
        for instrument in [Derivatives(), Commodities()]:
            try:
                descriptions.update(instrument.get_local_descriptions())
            except (OSError, TypeError, KeyError) as e:
                self._logger.error(e)
                raise e

        krx_derivatives_local_descriptions = "krx_derivatives_local_descriptions.csv"
        korea_local_descriptions = "korea_local_descriptions.csv"
        try:
            save_to_csv(krx_derivatives_local_descriptions, descriptions)
            descriptions = Stocks().get_local_descriptions()["csv"]
            file_writer(descriptions, korea_local_descriptions)
        except OSError as e:
            self._logger.error(e)
            raise e

        return [krx_derivatives_local_descriptions, korea_local_descriptions]


if __name__ == "__main__":
    try:
        KoreaDataGenerator().generate()
        exit(0)
    except (OSError, KeyError, TypeError):
        exit(1)