import re

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from utils import file_writer

class CorpactsDataGenerator(DataGenerator):

    URLS = [
        "https://esignalreport.com/update/CorpActs.tab",
        "http://fs2.esignal.com/CorpActs.tab"
    ]

    def _request_data(self, url: str) -> str:
        requester = LoggableRequester(self._logger, retries=5, delay=5)
        try:
            resp = requester.request(LoggableRequester.Methods.GET, url, {})
            return resp.text
        except IOError as e:
            self._logger.error(e)
            raise e

    def _get_data(self) -> str:
        for url in self.URLS:
            try:
                data = self._request_data(url)
                return data
            except IOError as e:
                pass
        raise Exception("Can't get data from source")

    def _calc_last_corpact(self, corpacts_data: str) -> dict[str, tuple[str, str]]:
        last_date = "19000101"
        skipping = False
        last_corpacts = dict()
        line_num = 0
        for line in corpacts_data.splitlines():
            line_num += 1
            line = line.strip()
            if re.match("^[12][0-9]{3}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[01])$", line):
                if last_date < line:
                    last_date = line
                    skipping = False
                else:
                    skipping = True
                    self._logger.warn(f"Can't switch date from {last_date} to {line}. Skipping corpacts")
                continue

            if skipping:
                self._logger.warn(f"Skipping line #{line_num}: {line}")
                continue

            match = re.match("^(.*):(.*),(.*)$", line)
            if not match:
                self._logger.error(f"Can't parse line #{line_num}: {line}")
                continue
            symbol = match[2].strip()
            factor = match[3].strip()

            if not symbol:
                self._logger.error(f"Symbol is empty #{line_num}: {line}")
                continue
            last_corpacts[symbol] = (last_date, factor)
        return last_corpacts

    @staticmethod
    def _write_last_corpacts(last_corpacts: dict[str, tuple[str, str]], path: str) -> None:
        with open(path, "w") as f:
            f.write("symbol;split-date;split-factor\n")
            for symbol, (date, factor) in last_corpacts.items():
                f.write(f"{symbol};{date};{factor}\n")

    def generate(self) -> list[str]:

        corpacts_name = "CorpActs.tab"
        corpacts_data = self._get_data()
        try:
            file_writer(corpacts_data, corpacts_name)
        except IOError as e:
            self._logger.error(e)
            raise e

        last_corpacts_name = "LastCorpActs.tab"
        last_corpacts = self._calc_last_corpact(corpacts_data)
        if len(last_corpacts) < 100_000:
            e = Exception(f"Too small resulting {last_corpacts_name}")
            self._logger.error(e)
            raise e

        self._write_last_corpacts(last_corpacts, last_corpacts_name)

        return [corpacts_name, last_corpacts_name]


if __name__ == "__main__":
    try:
        CorpactsDataGenerator().generate()
        exit(0)
    except (OSError, AttributeError):
        exit(1)