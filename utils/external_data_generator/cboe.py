from requests import RequestException

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester


class CBOEDataGenerator(DataGenerator):

    def generate(self):
        url = "https://www.cboe.com/us/equities/market_statistics/listed_symbols/csv/"
        try:
            csv = LoggableRequester(self._logger).request(LoggableRequester.Methods.GET, url).text
        except RequestException as e:
            self._logger.error(e)
            return 1

        try:
            with open("cboe.csv", "w") as file:
                file.write("Name;underlying-symbol\n")
                for line in csv.split("\n"):
                    symbol = line.split(',')[0]
                    if symbol == "Name":
                        continue
                    file.write(f"{line.split(',')[0]};CBOE:{line.split(',')[0]}\n")
        except IOError as e:
            self._logger.error(e)
            return 1

        return 0
