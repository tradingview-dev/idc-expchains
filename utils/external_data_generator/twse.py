import csv

from bs4 import BeautifulSoup

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers


class TwseDataGenerator(DataGenerator):

    @staticmethod
    def __handle_page(html: str):
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select("table.h4 tr")

        results = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue

            symbol_descr = cols[0].text.strip()
            isin = cols[1].text.strip()

            if not isin or len(isin) != 12 or not isin.isalnum():
                continue

            parts = symbol_descr.split("　", 1)
            description = parts[1].strip() if len(parts) > 1 else ''
            results.append({"isin": isin, "description": description})

        return results

    def generate(self):
        url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"

        try:
            resp = LoggableRequester(self._logger, retries=5, delay=5).request(LoggableRequester.Methods.GET, url, get_headers())
            resp.encoding = 'big5-hkscs'
            results = self.__handle_page(resp.text)

            with open('twse_descriptions.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["isin", "local-description"])
                for row in results:
                    writer.writerow([row["isin"], row["description"]])

            return 0
        except Exception as e:
            self._logger.error(e)
            return 1


if __name__ == '__main__':
    exit(TwseDataGenerator().generate())
