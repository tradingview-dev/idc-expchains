from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester


class CBOEDataGenerator(DataGenerator):

    def generate(self) -> list[str]:
        url = "https://www.cboe.com/us/equities/market_statistics/listed_symbols/csv/"
        try:
            csv = LoggableRequester(self._logger).request(LoggableRequester.Methods.GET, url).text
        except OSError as e:
            self._logger.error(e)
            raise e

        out_file = "cboe.csv"
        try:
            with open(out_file, "w", encoding="utf-8") as file:
                file.write("Name;underlying-symbol\n")
                for line in csv.split("\n"):
                    symbol = line.split(',')[0]
                    if symbol == "Name":
                        continue
                    file.write(f"{line.split(',')[0]};CBOE:{line.split(',')[0]}\n")
        except OSError as e:
            self._logger.error(e)
            raise e

        return [out_file]


if __name__ == "__main__":
    try:
        CBOEDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)