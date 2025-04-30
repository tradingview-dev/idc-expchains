from abc import ABC, abstractmethod
from utils import execute_to_file
import requests


class Korea(ABC):

    headers = {
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

    result = dict()

    @staticmethod
    def create_result_csv():
        with open("krx_derivatives_local_descriptions.csv", "w") as file:
            file.write("key;local-description\n")

    @abstractmethod
    def get_local_description(self):
        pass

    def to_csv(self):
        """
        writing result to csv
        """
        with open("krx_derivatives_local_descriptions.csv", "a") as file:
            for key, local_description in self.result.items():
                file.write(f"{key};{local_description}\n")


class Commodity(Korea):

    def get_local_description(self):

        blds = ["dbms/MDC/STAT/standard/MDCSTAT15101", "dbms/MDC/STAT/standard/MDCSTAT15801"]

        for bld in blds:

            data = {
                'locale': 'en',
                'prodId': 'KRDRVFUEQU',
                'subProdId': '',
                'csvxls_isNo': 'false',
                'bld': bld
            }

            spots = requests.post("http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd", data=data, headers=self.headers).json()["output"]
            for spot in spots:
                self.result[spot["ISU_ENG_NM"]] = spot["ISU_NM"]


class Derivatives(Korea):

    def get_local_description(self):

        prodIds = []

        codes = requests.get(
            "http://data.krx.co.kr/comm/bldAttendant/executeForResourceBundle.cmd?baseName=krx.mdc.i18n.component&key=B107.bld&locale=en",
            headers=self.headers).json()["result"]["output"]
        for code in codes:

            if "Option" in code["name"]:
                continue

            prodIds.append(code["value"])
        for prodId in prodIds:

            data = {
                'locale': 'en',
                'prodId': prodId,
                'subProdId': prodId,
                'csvxls_isNo': 'false',
                'bld': 'dbms/MDC/STAT/standard/MDCSTAT12801'
            }

            futures_roots = requests.post("http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd", data=data, headers=self.headers).json()["output"]
            for root in futures_roots:
                self.result[root["ISU_CD"]] = root["ISU_NM"]


def korea_handler():
    cmd_line = ["bash", "-c", "curl -s 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'"
                " --data-raw 'code=gRY0jP6rQnfIF4FBiKhU6zCBs%2Fh%2FA%2BJ7QlF9gsIMcSoRtSksuLS7Bnxpl86F7dAOvXfGx9S2U5wgvoxsacATRRtmGtORI4WrGDmruVe6oXtCqUypoW0Lp6SAPP0PhVkgThCTcjIZNPI5lCTubZnhjio6AHXdxc45YVEhz4JdugHPMxvIwHadpQpCGE1HxZAXvTCprTIXuXT9XxFb88awpQ%3D%3D' "
                " | iconv -f EUC-KR"]
    execute_to_file(cmd_line, "korea_local_descriptions.csv")

    commodities = Commodity()

    derivatives = Derivatives()

    commodities.create_result_csv()

    instruments = [derivatives, commodities]

    for instrument in instruments:

        instrument.get_local_description()

        instrument.to_csv()