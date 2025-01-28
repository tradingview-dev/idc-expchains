from bs4 import BeautifulSoup
from collections import deque
import argparse
import random
import requests
import sys
import time

from httplib2.auth import tchar


class LangAndSchwarzParser:

    DELAY: int = 5
    MAX_RETRIES: int = 5
    USER_AGENTS: list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 ",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.1.178 Yowser/2.5 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
        ]
    TYPES: dict = {"x": {'stock': 'base,db61b74d98c0231d3f763734d4024967a7dec93018004b8e54bf76aac8f05311',
                         'funds': 'funds,db61b74d98c0231d3f763734d40249676d071aafe753a3d4187f9bff52b984b2',
                         'etf': 'base,db61b74d98c0231d3f763734d4024967a4936f9404f19de7d94a2d6d78a6a923',
                         'bonds': 'base,db61b74d98c0231d3f763734d4024967f76522185ef4cddfb2badef9903d4577',
                         },
                   "tc": {'stock': 'base,db61b74d98c0231d3f763734d4024967d77d9e99392bb3d6963f8af4deb84132',
                          'etf': 'base,db61b74d98c0231d3f763734d40249675a79565b7f66fc5e646b315b471ada1e',
                          'funds': 'base,db61b74d98c0231d3f763734d40249673667c40fc411581916f9920d3a1fcef8',
                          'bonds': 'base,db61b74d98c0231d3f763734d4024967e1e6dc9a5e724bd45e0492b9f6af2992',
                          'certificates': 'derivative,db61b74d98c0231d3f763734d40249679df65b6f0e9312c861b9a91a760318b3',
                          }
                   }

    current_url = ""

    symbols: list = []

    retries_symbols: deque = deque()

    def get_headers(self) -> dict:
        """
        :return: headers with random user-agent
        """
        random_number = random.randint(0, len(self.USER_AGENTS)-1)
        headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.USER_AGENTS[random_number],
            "x-requested-with": "XMLHttpRequest"
        }
        return headers

    def si_to_csv(self, exchange: str):
        """
        :param exchange: Site identifier
        :return:
        """
        if exchange == "x":
            file_name = "LSX"
        else:
            file_name = "LS"
        sorted_symbols = sorted(self.symbols, key=lambda v: None if v is None else v["tv-symbol"])
        with open(f"{file_name}.csv", "w") as file:
            file.write("tv-symbol;isin;description\n")
            for stock in sorted_symbols:
                if stock is None:
                    continue
                file.write(f'{stock["tv-symbol"]};{stock["isin"]};{stock["description"]}\n')

    def request_with_retries(self, url: str, exchange: str, func):
        """
        :param url: url for request
        :param exchange: Site identifier
        :param func: the function that will be executed if the request is successful
        :return: response to request
        """
        retries = 0
        self.current_url = url
        while retries < self.MAX_RETRIES:
            try:
                response = requests.get(url, headers=self.get_headers())
                if response.status_code == 200:
                    return func(response, exchange)
                elif response.status_code != 200:
                    retries += 1
                    print(f"{response.status_code} fail. Attempt {retries}/{self.MAX_RETRIES}. Repeat after {self.DELAY} seconds...")
                    time.sleep(self.DELAY)
                else:
                    response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Fail request: {e}")
                retries += 1
                time.sleep(self.DELAY)
        self.retries_symbols.append(url)
        print(f'{url} add to late requests. More than {self.MAX_RETRIES} attempts')

    @staticmethod
    def delete_spaces(string: str) -> str:
        """
        :param string: string to remove extra spaces
        :return: result string without extra spaces
        """
        spaces = 0
        new_string = ""
        for s in string:
            if s == " ":
                spaces += 1
            else:
                if spaces > 0:
                    new_string += " "
                spaces = 0
                new_string += s
            if spaces > 1:
                continue
        return new_string

    def si_to_tv_dict(self, si_symbol, _) -> dict:
        """
        :param si_symbol: response to request data
        :return: dict with tv-symbol
        """
        symbol = si_symbol.json()[0]
        symbol_info = {'tv-symbol': str(symbol['wkn']), 'isin': symbol['isin'],
                       'description': self.delete_spaces(symbol['displayname'])}
        return symbol_info

    def request_symbol(self, wkn: str, exchange: str):
        """
        :param wkn: exchange symbol identifier
        :param exchange: exchange identifier
        """
        url = f'https://www.ls-{exchange}.de/_rpc/json/.lstc/instrument/search/main?q={wkn}&localeId={2 if exchange == "x" else 1}'
        return self.request_with_retries(url, exchange, self.si_to_tv_dict)

    def symbols_handler(self, resp, exchange: str):
        """
        :param resp: response to request
        :param exchange: exchange identifier
        :return: total symbols list
        """
        soup = BeautifulSoup(resp.content, "html.parser")
        category = ""
        try:
            category = soup.find('h3').text
        except AttributeError:
            time.sleep(300)
            self.request_with_retries(self.current_url, exchange, self.symbols_handler)
        if category == "Stocks" or (exchange == "x" and category != "Anleihen"):
            td_tags = soup.find_all('td', class_=False)
            for tag in td_tags:
                wkn = tag.find("div")
                if not wkn.find():
                    symbol = self.request_symbol(wkn.text, exchange)
                    self.symbols.append(symbol)
                    print(symbol)
        else:
            td_tags = soup.find_all('td', class_=False)
            for tag in td_tags:
                wkn = tag.find("a")
                symbol = self.request_symbol(wkn.text, exchange)
                self.symbols.append(symbol)
                print(symbol)

    def request_last_page(self, category: str, exchange: str):
        """
        :param category: symbols category
        :param exchange: exchange identifier
        """
        endpoint, configid = self.TYPES[exchange][category].split(",")
        url = f'https://www.ls-{exchange}.de/_rpc/html/.lstc/instrument/list/{endpoint}?localeId={2 if exchange == "x" else 1}&configid={configid}&offset=0'
        return self.request_with_retries(url, exchange, self.get_last_page)

    @staticmethod
    def get_last_page(resp, _) -> str:
        """
        :param resp: response to request
        :return: count pages symbols
        """
        soup = BeautifulSoup(resp.content, "html.parser")
        try:
            max_offset = soup.find('li', class_="last").text
        except AttributeError:
            try:
                max_offset = soup.find_all('li', class_="")[-1].text
            except IndexError:
                return "1"
        return max_offset

    def parse_symbols(self, exchange: str) -> None:
        """
        :param exchange: exchange identifier
        """
        if exchange == "LS":
            exchange = "tc"
        elif exchange == "LSX":
            exchange = "x"
        for k, v in self.TYPES[exchange].items():
            max_offset = self.request_last_page(k, exchange)
            endpoint, configid = v.split(",")
            for offset in range(0, int(max_offset)*100, 100):
                url = f'https://www.ls-{exchange}.de/_rpc/html/.lstc/instrument/list/{endpoint}?localeId={2 if exchange == "x" else 1}&configid={configid}&offset={offset}'
                self.request_with_retries(url, exchange, self.symbols_handler)
        self.request_retries_symbols()
        self.si_to_csv(exchange)

    def request_retries_symbols(self):
        if len(self.retries_symbols) > 0:
            print("Парсинг символов с ошибкой:")
            while len(self.retries_symbols) > 0:
                symbol = self.retries_symbols.popleft()
                self.request_with_retries(symbol, "", self.si_to_tv_dict)


def lang_and_shwarz_handler(exchange):
    symbols_parser = LangAndSchwarzParser()
    symbols_parser.parse_symbols(exchange)