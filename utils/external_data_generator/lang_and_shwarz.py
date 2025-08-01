from collections import deque

from bs4 import BeautifulSoup
from bs4.element import Tag

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import get_headers


class LangAndSchwarzDataGenerator(DataGenerator):

    # private static variables
    __DELAY: int = 5
    __MAX_RETRIES: int = 5
    __TYPES: dict = {
        "x": {
            'stock': 'base,db61b74d98c0231d3f763734d4024967a7dec93018004b8e54bf76aac8f05311',
            'funds': 'funds,db61b74d98c0231d3f763734d40249676d071aafe753a3d4187f9bff52b984b2',
            'etf': 'base,db61b74d98c0231d3f763734d4024967a4936f9404f19de7d94a2d6d78a6a923',
            'bonds': 'base,db61b74d98c0231d3f763734d4024967f76522185ef4cddfb2badef9903d4577'
        },
        "tc": {
            'stock': 'base,db61b74d98c0231d3f763734d4024967d77d9e99392bb3d6963f8af4deb84132',
            'etf': 'base,db61b74d98c0231d3f763734d40249675a79565b7f66fc5e646b315b471ada1e',
            'funds': 'base,db61b74d98c0231d3f763734d40249673667c40fc411581916f9920d3a1fcef8',
            'bonds': 'base,db61b74d98c0231d3f763734d4024967e1e6dc9a5e724bd45e0492b9f6af2992',
            'certificates': 'derivative,db61b74d98c0231d3f763734d40249679df65b6f0e9312c861b9a91a760318b3'
        }
   }

    def __init__(self):
        super().__init__()
        # private non-static variables
        self.__postponed_request_queue: deque = deque()

    @staticmethod
    def __save_to_csv(symbols: list, exchange: str) -> None:
        """
        :param symbols: symbol list
        :param exchange: site identifier
        :return:
        """
        sorted_symbols = sorted(symbols)
        with open(f"{exchange}.csv", "w", encoding="utf-8") as file:
            file.write("tv-symbol\n")
            file.write("\n".join(sorted_symbols))

    @staticmethod
    def __get_symbols(content: bytes, exchange: str) -> list:
        """
        :param content:
        :param exchange: exchange identifier
        :return: total symbols list
        """
        symbols = []

        soup = BeautifulSoup(content, "html.parser")
        category = soup.find('h3').text
        td_tags: list[Tag] = soup.find_all('td', class_=False)
        if category == "Stocks" or (exchange == "x" and category != "Anleihen"):
            for tag in td_tags:
                wkn = tag.find("div")
                if not wkn.find():
                    symbols.append(wkn.text)
        else:
            for tag in td_tags:
                wkn = tag.find("a")
                symbols.append(wkn.text)

        return symbols

    def __request_page(self, endpoint: str, configid: str, exchange: str, offset=0) -> bytes:
        """
        :param endpoint:
        :param configid:
        :param exchange: exchange identifier
        :param offset:
        :return: page content
        :raise RequestException:
        """
        url = f'https://www.ls-{exchange}.de/_rpc/html/.lstc/instrument/list/{endpoint}?localeId={2 if exchange == "x" else 1}&configid={configid}&offset={offset}'
        resp = LoggableRequester(self._logger, retries=self.__MAX_RETRIES, delay=self.__DELAY).request(LoggableRequester.Methods.GET, url, get_headers())
        return resp.content

    @staticmethod
    def get_max_offset(content: bytes) -> str:
        """
        :param content: page content
        :return: count pages symbols
        """
        soup = BeautifulSoup(content, "html.parser")
        try:
            max_offset = soup.find('li', class_="last").text
        except AttributeError:
            try:
                max_offset = soup.find_all('li', class_="")[-1].text
            except IndexError:
                return "1"
        return max_offset

    def handle_exchange(self, exchange: str) -> list[str]:
        """
        """
        exchange_paths = {
            "LS": "tc",
            "LSX": "x"
        }

        symbols = []
        for k, v in self.__TYPES[exchange_paths[exchange]].items():
            try:
                endpoint, configid = v.split(",")
                content = self.__request_page(endpoint, configid, exchange_paths[exchange])
                if len(content) == 0:
                    raise ValueError("No data: page is empty")
                max_offset = self.get_max_offset(content)
            except (OSError, ValueError, KeyError) as e:
                self._logger.error(e)
                raise e
            for offset in range(0, int(max_offset) * 100, 100):
                try:
                    content = self.__request_page(endpoint, configid, exchange_paths[exchange], offset)
                    if len(content) == 0:
                        raise ValueError("No data: page is empty")
                except OSError as e:
                    self._logger.error(e)
                    raise e
                if len(content) == 0:
                    continue
                symbols.extend(self.__get_symbols(content, exchange_paths[exchange]))
        try:
            self.__save_to_csv(symbols, exchange)
        except OSError as e:
            self._logger.error(e)
            raise e
        return [f"{exchange}.csv"]

    def generate(self) -> list[str]:
        raise NotImplementedError


class Lang(LangAndSchwarzDataGenerator):

    def generate(self) -> list[str]:
        return super().handle_exchange("LSX")


class Schwarz(LangAndSchwarzDataGenerator):

    def generate(self) -> list[str]:
        return super().handle_exchange("LS")


if __name__ == "__main__":
    try:
        Lang().generate()
        Schwarz().generate()
        exit(0)
    except (OSError, KeyError, TypeError):
        exit(1)
