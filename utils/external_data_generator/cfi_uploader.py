import os

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from s3_utils import upload_state


class CFIUploader(DataGenerator):

    def __init__(self, branch):
        super().__init__()
        self._branch = branch


    @staticmethod
    def get_bourse_codes()-> list[str]:
        return ["21", "66", "80",
                "185", "216", "326",
                "544", "1330", "2913",
                "6184", "6362"]


    @staticmethod
    def get_env():
        environment = os.environ.get('ENVIRONMENT', None)

        if environment == "production":
            return "hub4.tradingview.com:8094"
        elif environment == "stable":
            return "udf-nyc.xstaging.tv/hub01-stable"
        else:
            return "hub0.tradingview.com:8092"


    def get_cfi(self) -> dict[str, str]:
        res = {}
        host = self.get_env()
        for code in self.get_bourse_codes():
            data = LoggableRequester(self._logger, timeout=30).request(LoggableRequester.Methods.GET, f"http://{host}/tvf/upstream/sixmdfstream/streaming/symbols?source={code}&additionalFields=TDF_ISIN,TDF_CFI").text
            for s in data.split("\n"):
                symbol = s.split(",")
                if len(symbol) < 3:
                    continue
                val, isin, cfi = symbol
                if cfi != "":
                    res[isin] = cfi
        return res


    def generate(self) -> list[str]:

        result = "CfiFromSix.csv"

        with open(result, "w") as file:
            file.write("isin;cfi_code\n")
            for isin, cfi in self.get_cfi().items():
                file.write(f"{isin};{cfi}\n")

        return [result]


def upload_cfi(branch: str):
    upload_state("cfi_dict/cfi-dict-en.json", get_bucket(branch), "cfi/cfi-dict-en.json")


def get_bucket(branch: str) -> str:
    buckets = {
        "staging": "tradingview-pub-staging",
        "master": "tradingview-pub"
    }
    return buckets[branch]


if __name__ == "__main__":
    try:
        CFIUploader("staging").generate()
        exit(0)
    except OSError:
        exit(1)
