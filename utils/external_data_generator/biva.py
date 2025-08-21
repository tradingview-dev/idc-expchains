import asyncio
import json

import aiohttp

from DataGenerator import DataGenerator
from lib.ConsoleOutput import ConsoleOutput
from lib.LoggableRequester import LoggableRequester
from utils import get_headers


class BivaDataGenerator(DataGenerator):

    # private static variables
    __SIC_URL = "https://www.biva.mx/emisoras/sic?size=10000&page=0"
    __RI_URL = "https://www.biva.mx/emisoras/empresas?size=10000&page=0"

    __BLACK_LIST = ["CKDs", "SIC Deuda", "Warrants", "CERPIs"]

    async def __fetch_isin(self, session, url, isin_queue) -> None:
        """
        :param session: aiohttp.ClientSession()
        :param url: symbol's url
        :param isin_queue: queue for saving the results of async parsing
        """
        async with session.get(url, headers=get_headers()) as response:
            try:
                data = await response.json()
            except json.JSONDecodeError as e:
                self._logger.error(f"Error decoding JSON for {url}: {e}")
                return

            isin_id = int(url.split("/")[5])
            try:
                for symbol in range(len(data["content"])):
                    if data["content"][symbol]["tipoInstrumento"] in self.__BLACK_LIST:
                        continue
                    serie = data["content"][symbol]["serie"]
                    isin = data["content"][symbol]["isin"]

                    if isin_id is not None and isin is not None:
                        isin_queue.put_nowait((isin_id, serie, isin))
            except KeyError:
                self._logger.info(f"No data {url}")
                return

    async def __get_isins(self, urls: list) -> list:
        """
        :param urls: list of urls for creating tasks for an async parsing
        :return: list of tuples with id, serie and isin
        """
        isins = []

        isin_queue = asyncio.Queue()

        iterations_amount = 10
        tasks_amount = int(len(urls) / iterations_amount)
        for iteration in range(iterations_amount):
            start = iteration * tasks_amount
            finish = start + tasks_amount
            if iteration == iterations_amount - 1:
                finish = len(urls)
            self._logger.info(f"Requesting ISIN data [{start}..{finish})(from total {len(urls)})... ")
            async with aiohttp.ClientSession() as session:
                tasks = [self.__fetch_isin(session, url, isin_queue) for url in urls[start:finish]]
                await asyncio.gather(*tasks)
            self._logger.info("DONE", color=ConsoleOutput.Foreground.REGULAR_GREEN)

        while not isin_queue.empty():
            isin_id, serie, isin = isin_queue.get_nowait()
            isins.append((isin_id, serie, isin))

        return isins

    def __write_result(self, symbols: list, isins: list, dst: str) -> None:
        """
        A function that matches symbols by their id and writes the tv-symbol, description and isin to a file
        :param symbols: list of tuples with id, symbol and description
        :param isins: list of tuples with id, serie and isin
        """
        self._logger.info("Writing result... ", False)
        try:
            with open(dst, "w", encoding="utf-8") as file:
                file.write("tv-symbol;description;isin\n")
                for symbol in symbols:
                    symbol_id, symbol, description = symbol
                    if description[-1] == ".":
                        description = description[:-1]
                    for s_isin in isins:
                        isin_id, serie, isin = s_isin
                        if symbol_id == isin_id:
                            if serie == "*":
                                file.write(f"{symbol};{description};{isin}\n")
                            else:
                                file.write(f"{symbol + '/' + serie};{description};{isin}\n")
            self._logger.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)
        except (OSError, UnicodeEncodeError) as e:
            self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
            raise e

    def __get_urls_symbols(self) -> tuple:
        """
        :return: two lists with urls and symbols
        """
        urls = []
        symbols = []

        requester = LoggableRequester(self._logger, timeout=15, delay=5)

        sic = requester.request(LoggableRequester.Methods.GET, self.__SIC_URL, headers=get_headers()).json()["content"]
        self._logger.info("Parse SIC data... ", False)
        for symbol in sic:
            try:
                urls.append(f'https://www.biva.mx/emisoras/sic/{symbol["id"]}/emisiones?size=10&page=0')
                symbols.append((symbol["id"], symbol["clave"], symbol["nombre"]))
            except KeyError as e:
                self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
                raise e
        self._logger.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)

        ri = requester.request(LoggableRequester.Methods.GET, self.__RI_URL, headers=get_headers()).json()["content"]
        self._logger.info("Parse RI data... ", False)
        for symbol in ri:
            try:
                urls.append(f'https://www.biva.mx/emisoras/empresas/{symbol["id"]}/emisiones?size=10&page=0&cotizacion=true')
                symbols.append((symbol["id"], symbol["clave"], symbol["nombre"]))
            except KeyError as e:
                self._logger.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
                raise e
        self._logger.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)

        return urls, symbols

    def generate(self) -> list[str]:
        out = "biva_data.csv"
        try:
            urls, symbols = self.__get_urls_symbols()
            isins = asyncio.run(self.__get_isins(urls))
            self.__write_result(symbols, isins, out)
            return [out]
        except (OSError, KeyError, ValueError) as e:
            self._logger.error(e)
            raise e


if __name__ == "__main__":
    try:
        BivaDataGenerator().generate()
        exit(0)
    except (OSError, KeyError, ValueError):
        exit(1)
