import asyncio
import json

import aiohttp

from DataGenerator import DataGenerator
from utils import get_headers, unpack_data
from s3_utils import read_state


class OtcDataGenerator(DataGenerator):

    def __init__(self, branch):
        super().__init__()
        self._branch = branch

    @staticmethod
    def __get_directory_url(page):
        pageSize = 25
        return f"https://backend.otcmarkets.com/otcapi/company-directory?page={page}&pageSize={pageSize}"

    @staticmethod
    def __get_headers():
        headers = get_headers()
        headers.update({
            "Origin": "https://www.otcmarkets.com",
            "Referer": "https://www.otcmarkets.com/",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        })
        return headers

    async def __request_all_records(self) -> list:
        semaphore = asyncio.Semaphore(1)

        async def limit_wrap(url, session):
            async with semaphore:
                return await self.__request_records(url, session)

        async with aiohttp.ClientSession() as session:
            records = []
            self._logger.info("Requesting first page of OTC data")
            pages, first_records = await self.__request_records(self.__get_directory_url(1), session)
            self._logger.info(f"Data is on {pages} pages")
            if pages is None:
                pages = 1
            records.extend([] if first_records is None else first_records)

            urls = [self.__get_directory_url(page) for page in range(2, pages + 1)]

            responses = [limit_wrap(url, session) for url in urls]
            record_chunks = await asyncio.gather(*responses)
            for _, chunk in record_chunks:
                records.extend([] if chunk is None else chunk)
            self._logger.info(f"Total loaded {len(records)} records")
            return records

    async def __request_records(self, url: str, session: aiohttp.ClientSession):
        headers = self.__get_headers()
        # self._logger.debug(f"{url} headers={headers}")
        async with session.get(url, headers=headers) as response:
            try:
                # raw_data = await response.text()
                # self._logger.debug(f"got response {response.status} {raw_data}")
                data = await response.json()
            except json.JSONDecodeError as e:
                self._logger.error(f"Error decoding JSON for {url}: {e}")
                return None, None

            try:
                self._logger.info(f"Loaded {len(data['records'])} records")
                return data["pages"], data["records"]
            except KeyError:
                self._logger.info(f"No data {url}")
                return None, None

    @staticmethod
    def __merge(prev_records, new_records, field):
        prev_dict = {r[field]: r for r in prev_records}
        new_dict = {r[field]: r for r in new_records}

        prev_dict.update(new_dict)
        result = list(prev_dict.values())
        result.sort(key=lambda r: r[field])
        return result

    def generate(self) -> list[str]:

        records = asyncio.run(self.__request_all_records())
        for r in records:
            r.pop("joined", None)
            r.pop("marketCap", None)

        out_file = "otc_data.json"

        # load_from_repo([out_file], "staging")
        # remove_repo()

        compressed_data = read_state("tradingview-sourcedata-storage-staging", "otc_data.json")
        content = unpack_data(compressed_data)
        with open(out_file, "w") as f:
            f.write(json.loads(content))
        with open(out_file, "r") as f:
            prev_data = json.load(f)
            self._logger.info(f"Previous data contains {len(prev_data)} records")
        merged_data = self.__merge(prev_data, records, "symbol")
        self._logger.info(f"Merged data contains {len(merged_data)} records")
        with open(out_file, "w") as f:
            json.dump(merged_data, f, indent=4)

        return [out_file]


if __name__ == "__main__":
    try:
        OtcDataGenerator("staging").generate()
        exit(0)
    except OSError:
        exit(1)