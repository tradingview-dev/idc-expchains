import csv
import json

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, unpack_data


class CMCDataGenerator(DataGenerator):

    def __init__(self, branch):
        super().__init__()
        self._env = "prod" if branch == "master" else branch

    def get_currencies(self, currencies_url):
        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.GET,
                                     currencies_url,
                                     get_headers())

            if resp.status_code != 200:
                raise Exception("Unable to get currencies.json" + str(resp.status_code))

            return json.loads(resp.text)
        except OSError as e:
            self._logger.error(e)
            raise e

    def get_coinmarketcap_snapshot(self, cmc_id):
        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp_1 = requester.request(LoggableRequester.Methods.GET,
                                       f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?convert=BTC&start=1&sort=market_cap&limit=5000&CMC_PRO_API_KEY={cmc_id}",
                                       get_headers())
            resp_2 = requester.request(LoggableRequester.Methods.GET,
                                       f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?convert=BTC&start=5001&sort=market_cap&limit=5000&CMC_PRO_API_KEY={cmc_id}",
                                       get_headers())
            return resp_1.json()['data'] + resp_2.json()['data']
        except OSError as e:
            self._logger.error(e)
            raise e

    def generate(self) -> list[str]:
        cmc_ids = {
            "staging": "98e9877a-f3b7-4945-94f6-9f155fec4a65",
            "stable": "d2daa136-eb61-420b-8dcd-d412928f2f92",
            "prod": "d2daa136-eb61-420b-8dcd-d412928f2f92"
        }
        currencies_urls = {
            "staging": "https://tradingview-currencies-staging.xstaging.tv/currencies.json",
            "stable": "https://tradingview-currencies.tradingview.com/currencies.json",
            "prod": "https://tradingview-currencies.tradingview.com/currencies.json"
        }
        coinmarketcap_snapshot = self.get_coinmarketcap_snapshot(cmc_ids[self._env])
        currencies = self.get_currencies(currencies_urls[self._env])
        defi_typespec = "defi_typespec.csv"
        self.run(coinmarketcap_snapshot, currencies, defi_typespec)
        return [defi_typespec]

    @staticmethod
    def map_currency_id(currency: str) -> str:
        if currency.upper() == "GRT":
            return "XTVCGRAPH"
        return f"XTVC{currency.upper()}"

    @staticmethod
    def read_currency_ids(currencies) -> dict:
        result = {}
        for record in currencies:
            if "cmc-id" in record:
                result[record["id"]] = record
        return result

    def run(self, coinmarketcap_snapshot, currencies, out_file) -> None:
        defi_coins = [r for r in coinmarketcap_snapshot if "defi" in r.get("tags", [])]

        currency_ids = self.read_currency_ids(currencies)

        defi_coins_ids = []
        for record in defi_coins:
            cid = self.map_currency_id(record["symbol"])

            if cid not in currency_ids:
                self._logger.weak_warn(f"Unknown currency-id {cid}")
                continue

            currency = currency_ids[cid]
            if "id" in record:
                if str(record["id"]) != currency["cmc-id"]:
                    self._logger.weak_warn(f"{cid} is skipped due to the difference between its cmc-id="
                                           f"{record['id']} and cmc-id={currency['cmc-id']} from currencies.json"
                                           f"('{record["name"]}' vs '{currency["description"]}')")
                    continue
                defi_coins_ids.append(cid)

        defi_coins_ids.sort()

        with open(out_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["currency-id"])
            for cid in defi_coins_ids:
                writer.writerow([cid])


if __name__ == "__main__":
    try:
        CMCDataGenerator("staging").generate()
        exit(0)
    except OSError:
        exit(1)
