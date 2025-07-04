import csv
from datetime import datetime
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers


class TokyoDataGenerator(DataGenerator):

    # private static variables
    __BASE_URL = 'http://ca.image.jp/matsui/'
    __PAGE_TYPES = {
        'rename':      { 'type': 3,  'pages': 10 },
        'new':         { 'type': 6,  'pages': 15 },
        'consolidate': { 'type': 5,  'pages': 20 },
        'trade_unit':  { 'type': 7,  'pages': 25 },
        'base_date':   { 'type': 4,  'pages': 20 },
        'split':       { 'type': None, 'pages': 20 },  # No 'type' param for split
        'financial':   { 'type': 13, 'pages': 50, 'financial': True }
    }

    def generate(self) -> list[str]:
        results = []
        requester = LoggableRequester(self._logger, retries=5, delay=5)
        for config in self.__PAGE_TYPES.values():
            try:
                for page_number in range(1, config['pages'] + 1):
                    params = {
                        'type': config['type'],
                        'word1': '', 'word2': '',
                        'sort': 1, 'seldate': 0,
                        'serviceDatefrom': '', 'serviceDateto': '',
                        'page': page_number
                    }
                    query = urlencode({k: v for k, v in params.items() if v is not None})
                    url = f"{self.__BASE_URL}?{query}"
                    resp = requester.request(LoggableRequester.Methods.GET, url, get_headers())
                    self.__parse_table_rows(results, resp.text, config.get('financial', False))
            except (OSError, KeyError, TypeError) as e:
                self._logger.error(e)
                raise e

        tokyo_local_descriptions = "tokyo_local_descriptions.csv"
        filtered = self.__filter_latest_entries(results)
        try:
            self.__output_csv(filtered, tokyo_local_descriptions)
        except (OSError, KeyError) as e:
            self._logger.error(e)
            raise e

        return [tokyo_local_descriptions]

    @staticmethod
    def __parse_table_rows(results, html, financial=False):
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select("table.commontbl tbody tr")

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue

            try:
                symbol = cols[0].text.strip() if financial else cols[1].text.strip()
                date = cols[8].text.strip() if financial else cols[0].text.strip()
                desc_tag = cols[2].find('a') or cols[2] if not financial else cols[1].find('a') or cols[1]
                description = desc_tag.text.strip().rstrip('.') if desc_tag else ''

                results.append({'symbol': symbol, 'date': date, 'description': description})
            except (IndexError, TypeError):
                continue

    @staticmethod
    def __filter_latest_entries(results):
        today = datetime.today().strftime('%Y/%m/%d')
        filtered = {}

        for res in results:
            if res['date'] > today:
                continue

            symbol = res['symbol']
            if symbol not in filtered or filtered[symbol]['date'] < res['date']:
                filtered[symbol] = res

        return filtered

    @staticmethod
    def __output_csv(filtered_results, filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in filtered_results.values():
                writer.writerow([row['symbol'], row['description']])


if __name__ == "__main__":
    try:
        TokyoDataGenerator().generate()
        exit(0)
    except (OSError, KeyError, TypeError):
        exit(1)
