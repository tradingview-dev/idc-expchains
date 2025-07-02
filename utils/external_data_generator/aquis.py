import os
import urllib.request
from typing import List

import openpyxl
from bs4 import BeautifulSoup

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers


class AquisDataGenerator(DataGenerator):

    # private static variables
    __BASE_URI = "https://www.aquis.eu"

    def __get_aquis_symbols(self) -> List[List[str]]:
        """
        request symbols
        :return slice with symbols
        """
        symbols_info = []
        companies = LoggableRequester(self._logger, timeout=15).request(LoggableRequester.Methods.GET, f"{self.__BASE_URI}/companies", get_headers()).content
        soup = BeautifulSoup(companies, "html.parser")
        symbols = soup.find_all("a", class_="chakra-link css-pz0aee")
        for symbol in symbols:
            symbols_info.append(self.__get_symbol_params(symbol.text))
        return symbols_info

    def __get_symbol_params(self, symbol: str) -> List[str]:
        """
        :param symbol: symbol string
        :return: array with symbols params
        """
        symbol_page = LoggableRequester(self._logger).request(LoggableRequester.Methods.GET, f"{self.__BASE_URI}/companies/{symbol}", get_headers()).content
        soup = BeautifulSoup(symbol_page, "html.parser")
        isin = soup.find("p", class_="chakra-text css-4vttjp").text
        description = soup.find("h1", class_="chakra-heading css-135d5ex").text
        currency = soup.find("p", class_="chakra-text css-bjhtoj").text.split(" ")[2]
        return [description, symbol, isin, currency]

    def _get_secondary_listing_url_file(self) -> str | None:
        html = LoggableRequester(self._logger).request(LoggableRequester.Methods.GET, "https://www.aquis.eu/stock-exchange/statistics", get_headers()).content

        soup = BeautifulSoup(html, "html.parser")
        files = soup.find_all("a", class_="chakra-link css-fhzrj1")
        for file in files:
            if file.find("p").text.startswith("Secondary"):
                return file['href']

        raise AttributeError("File URL was not found")

    @staticmethod
    def _download_file(url: str, destination: str) -> None:
        """
        :param url: url where the file is downloaded from
        :param destination: the name of the file in which the downloaded file is saved
        """
        urllib.request.urlretrieve(url, destination)

    def _xlsx_to_csv(self, source: str, destination: str) -> None:
        """
        :param source: path to the source XLSX file
        :param destination: path to the resulting CSV file
        """
        workbook = openpyxl.load_workbook(source, read_only=True)

        try:
            with open(destination, 'w', newline='', encoding='utf-8') as csv_file:
                sheet = workbook.active
                for row in sheet.iter_rows(values_only=True):
                    if row[0] is not None and row[1] is not None and row[2] is not None and row[3] is not None:
                        csv_file.write(f"{row[0]};{row[1]};{row[2]};{row[3]}\n")

                for symbol in self.__get_aquis_symbols():
                    csv_file.write(f"{symbol[0]};{symbol[1]};{symbol[2]};{symbol[3]}\n")
        finally:
            workbook.close()

    def generate(self) -> list[str]:
        filename_csv = "aquis.csv"
        filename_xlsx = "aquis.xlsx"
        try:
            secondary = self._get_secondary_listing_url_file()
            self._download_file(secondary, filename_xlsx)
            self._xlsx_to_csv(filename_xlsx, filename_csv)
            os.remove(filename_xlsx)
        except (OSError, AttributeError) as e:
            self._logger.error(e)
            raise e
        return [filename_csv]


if __name__ == "__main__":
    try:
        AquisDataGenerator().generate()
        exit(0)
    except (OSError, AttributeError):
        exit(1)
