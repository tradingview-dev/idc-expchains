import csv

from bs4 import BeautifulSoup

from Handler import Handler
from lib.LoggableRequester import LoggableRequester
from utils import get_headers


class TwseHandler(Handler):

    @staticmethod
    def __handle_page(results, html):
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select("table.h4 tr")

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

    def handle(self, data_cluster = None):
        url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"

        resp = LoggableRequester(self._logger, retries=5, delay=5).request(LoggableRequester.Methods.GET, url, get_headers())
        resp.encoding = 'big5-hkscs'
        results = []
        self.__handle_page(results, resp.text)

        with open('twse_descriptions.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["isin", "local-description"])
            for row in results:
                writer.writerow([row["isin"], row["description"]])


if __name__ == '__main__':
    exit(TwseHandler().handle())
