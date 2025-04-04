from bs4 import BeautifulSoup
import requests



class ParseMstarDescription:

    headers = {
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

    def __init__(self, url):

        self.soup = BeautifulSoup(requests.get(url, headers=self.headers).content, "html.parser")

        self.symbols = dict()


    def parse_list_items(self):

        h2 = self.soup.find('h2', id="mstar")
        if not h2:
            print(f"Заголовок mstar не найден.")
            return

        ul = h2.find_next('ul')

        while ul:
            for li in ul.find_all('li'):

                symbol, description = li.text.split(" - ")

                symbol = symbol.split("\n")[1]

                description = description.split("\n")[0]

                if symbol[0] == ".":
                    symbol = symbol[1:]

                self.symbols[symbol] = description
            break


    @staticmethod
    def remove_multiply_spaces(description):
        prev_symbol = ""
        clean_description = ""
        for i in description:
            if i == " " and prev_symbol == " ":
                continue
            clean_description += i
            prev_symbol = i
        return clean_description


    def symbols_to_csv(self):

        with open("mstar_descriptions.csv", "w") as file:

            file.write("tv-symbol;description\n")

            for symbol in self.symbols:

                file.write(f"{symbol};{self.remove_multiply_spaces(self.symbols[symbol])}\n")


def mstar_handler():

    parser = ParseMstarDescription("https://www.cboe.com/us/indices/indicesproducts/#mstar")

    parser.parse_list_items()
    parser.symbols_to_csv()
