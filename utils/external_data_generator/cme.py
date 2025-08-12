import os
from abc import abstractmethod, ABC

import pandas as pd

from DataGenerator import DataGenerator
from lib.ConsoleOutput import ConsoleOutput
from lib.LoggableRequester import LoggableRequester


class CmeProductsParser(ABC):

    # protected static variables
    _BASE_URL = "https://www.cmegroup.com/services/product-slate"
    _HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-endcoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.5",
        "connection": "keep-alive",
        "host": "www.cmegroup.com",
        "referer": "https://www.cmegroup.com/markets/products.html",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
    }

    def __init__(self):
        super().__init__()
        self._logger = ConsoleOutput(type(self).__name__)

    @property
    @abstractmethod
    def _get_product(self):
        pass

    @property
    @abstractmethod
    def get_filename(self):
        pass

    @abstractmethod
    def parse_symbols(self):
        pass

    def get_total_pages(self):
        """

        :return:
        :raise RequestException:
        :raise KeyError:
        """
        req_params = [
            f"sortAsc=false",
            f"sortField=oi",
            f"pageNumber=1",
            f"pageSize=500",
            f"group=",
            f"subGroup=",
            f"venues=",
            f"exch=",
            f"cleared={self._get_product}",
            f"isProtected"
        ]
        resp = LoggableRequester(self._logger, timeout=10).request(LoggableRequester.Methods.GET, f"{self._BASE_URL}?{'&'.join(req_params)}", headers=self._HEADERS)
        first_page = resp.json()
        return first_page['props']['pageTotal']


class CmeOptionsParser(CmeProductsParser):

    @property
    def _get_product(self):
        return "Options"

    @property
    def get_filename(self):
        return f"{self._get_product}_products.csv"

    def parse_symbols(self) -> None:
        with open(self.get_filename, "w", encoding="utf-8") as file:
            file.write("prodCode;name\n")
            total_pages = self.get_total_pages()
            requester = LoggableRequester(self._logger, timeout=10)
            for i in range(1, total_pages + 1):
                req_params = [
                    f"sortAsc=false",
                    f"sortField=oi",
                    f"pageNumber={i}",
                    f"pageSize=500",
                    f"group=",
                    f"subGroup=",
                    f"venues=",
                    f"exch=",
                    f"cleared={self._get_product}",
                    f"isProtected"
                ]
                page = requester.request(LoggableRequester.Methods.GET, f"{self._BASE_URL}?{'&'.join(req_params)}", headers=self._HEADERS).json()

                products = page['products']
                for product in products:
                    root = product['prodCode']
                    description = product['name']

                    file.write(f"{root};{description}\n")

            response = requester.request(LoggableRequester.Methods.GET, "https://www.cftc.gov/strike-price-xls?col=ExchId%2CContractName&dir=ASC%2CASC")
            xlsx_filename = "strike-price-report.xlsx"
            with open(xlsx_filename, "wb") as xls:
                xls.write(response.content)

            excel_data = pd.read_excel(xlsx_filename)
            roots = excel_data.groupby('Comm. Code')

            for root_id, root in roots:
                if root['OptionClass'].unique()[0] == "ONE DAY":
                    file.write(f"{root_id};{root['ContractName'].unique()[0]}\n")

            os.remove(xlsx_filename)


class CmeFuturesParser(CmeProductsParser):

    @property
    def _get_product(self):
        return "Futures"

    @property
    def get_filename(self):
        return f"{self._get_product}_products.csv"

    def parse_symbols(self) -> None:
        with open(self.get_filename, "w", encoding="utf-8") as file:
            file.write("prodCode;name;Group;Sub Group\n")
            total_pages = self.get_total_pages()
            requester = LoggableRequester(self._logger, timeout=10)
            for i in range(1, total_pages + 1):
                req_params = [
                    f"sortAsc=false",
                    f"sortField=oi",
                    f"pageNumber={i}",
                    f"pageSize=500",
                    f"group=",
                    f"subGroup=",
                    f"venues=",
                    f"exch=",
                    f"cleared={self._get_product}",
                    f"isProtected"
                ]
                page = requester.request(LoggableRequester.Methods.GET, f"{self._BASE_URL}?{'&'.join(req_params)}", headers=self._HEADERS).json()

                products = page['products']
                for product in products:
                    root = product['prodCode']
                    description = product['name']
                    group = product['group']
                    subGroup = product['subGroup']
                    Clearing = product['Clearing']

                    file.write(f"{root};{description};{group};{subGroup}\n")


class CMEDataGenerator(DataGenerator):

    def generate(self) -> list[str]:
        output = []
        parsers = [CmeOptionsParser(), CmeFuturesParser()]
        for parser in parsers:
            try:
                parser.parse_symbols()
            except OSError as e:
                self._logger.error(e)
                raise e
            output.append(parser.get_filename)
        return output


if __name__ == "__main__":
    try:
        CMEDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
