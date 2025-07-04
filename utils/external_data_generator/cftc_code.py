import os

import pandas as pd

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester


class CFTCDataGenerator(DataGenerator):

    def _request_file(self, dst: str):
        url = "https://www.cftc.gov/strike-price-xls?col=ExchId%2CContractName&dir=ASC%2CASC"
        response = LoggableRequester(self._logger).request(LoggableRequester.Methods.GET, url)
        with open(dst, "wb") as file:
            file.write(response.content)

    def generate(self) -> list[str]:
        xlsx_filename = "strike-price-report.xlsx"

        try:
            self._request_file(xlsx_filename)
        except OSError as e:
            self._logger.error(e)
            raise e

        # Define a dictionary to map Exchange IDs to exchange names
        exchange_mapping = {
            '01': 'CBOT',
            '02': 'CME',
            '06': 'ICEUS',
            '07': 'COMEX',
            '12': 'NYMEX',
            'E': 'CBOE',
            'SG': 'SGX',
            '41': 'ICEEU'
        }

        excel_data = pd.read_excel(xlsx_filename)
        exchange_groups = excel_data.groupby('Exchange ID')

        for exchange_id, group in exchange_groups:
            if str(exchange_id) in exchange_mapping:
                exchange_name = exchange_mapping[str(exchange_id)]
                output_filename = f"cftc_{exchange_name}.csv"
                try:
                    group.to_csv(output_filename, index=False)
                except OSError as e:
                    self._logger.error(e)
                    raise e
                self._logger.info(f"CSV file for Exchange ID {exchange_id} ({exchange_name}) has been saved as {output_filename}")
            else:
                self._logger.info(f"Exchange ID {exchange_id} is not in the mapping, skipping file creation.")

        os.remove(xlsx_filename)
        return [f"cftc_{filename}.csv" for filename in exchange_mapping.values()]


if __name__ == "__main__":
    try:
        CFTCDataGenerator().generate()
        exit(0)
    except OSError:
        exit(1)
