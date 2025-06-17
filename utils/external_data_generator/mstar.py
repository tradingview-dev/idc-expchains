from bs4 import BeautifulSoup

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester


class MstarDataGenerator(DataGenerator):

    # private static variables
    __HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-endcoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.5",
        "connection": "keep-alive",
        "host": "www.cboe.com",
        "referer": "https://www.cboe.com/us/indices/accessing-index-data/",
        "priority": "u=1, i",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    }

    def _get_item_list(self):
        url = "https://www.cboe.com/us/indices/indicesproducts/#mstar"
        resp = LoggableRequester(self._logger).request(LoggableRequester.Methods.GET, url, headers=self.__HEADERS)
        return BeautifulSoup(resp.content, "html.parser")

    @staticmethod
    def _parse_item_list(soup: BeautifulSoup):
        h2 = soup.find('h2', id="mstar")
        if not h2:
            raise AttributeError("Header called mstar was not found.")

        symbols = {}
        ul = h2.find_next('ul')
        while ul:
            for li in ul.find_all('li'):
                symbol, description = li.text.split(" - ")
                symbol = symbol.split("\n")[1]
                description = description.split("\n")[0]
                if symbol[0] == ".":
                    symbol = symbol[1:]

                symbols[symbol] = description
            break

        return symbols

    @staticmethod
    def __remove_multiply_spaces(description):
        prev_symbol = ""
        clean_description = ""
        for i in description:
            if i == " " and prev_symbol == " ":
                continue
            clean_description += i
            prev_symbol = i
        return clean_description

    def _symbols_to_csv(self, dst: str, symbols: dict):
        with open(dst, "w", encoding="utf-8") as file:
            file.write("tv-symbol;description\n")
            for symbol in symbols:
                file.write(f"{symbol};{self.__remove_multiply_spaces(symbols[symbol])}\n")

    def generate(self) -> list[str]:
        mstar_descriptions = "mstar_descriptions.csv"
        try:
            symbols = self._parse_item_list(self._get_item_list())
            self._symbols_to_csv(mstar_descriptions, symbols)
        except (AttributeError, OSError) as e:
            self._logger.error(e)
            raise e

        return [mstar_descriptions]


if __name__ == "__main__":
    try:
        MstarDataGenerator().generate()
        exit(0)
    except (OSError, AttributeError):
        exit(1)
