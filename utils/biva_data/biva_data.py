import aiohttp
import asyncio
import json
import requests

SIC_URL = "https://www.biva.mx/emisoras/sic?size=10000&page=0"
RI_URL = "https://www.biva.mx/emisoras/empresas?size=10000&page=0"


async def fetch_sic_isin(session, url, isin_sic_queue) -> None:
    """
    fetch International Quotation System (SIC) isins
    :param session: aiohttp.ClientSession()
    :param url: symbol's url
    :param isin_sic_queue: queue for saving the results of async parsing
    """
    async with session.get(url) as response:
        data = await response.json()
        isin_id = int(url.split("/")[5])

        try:
            serie = data["content"][0]["serie"]
            isin = data["content"][0]["isin"]

            if isin_id is not None and isin is not None:
                isin_sic_queue.put_nowait((isin_id, serie, isin))

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {url}: {e}")


async def fetch_ri_isin(session, url, isin_ri_queue) -> None:
    """
    fetch Registered Issuers isins
    :param session: aiohttp.ClientSession()
    :param url: symbol's url
    :param isin_ri_queue: queue for saving the results of async parsing
    """
    async with session.get(url) as response:
        data = await response.json()
        isin_id = int(url.split("/")[5])

        try:
            serie = data["content"][0]["serie"]
            isin = data["content"][0]["isin"]

            if isin_id is not None and isin is not None:
                isin_ri_queue.put_nowait((isin_id, serie, isin))

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {url}: {e}")
        except KeyError:
            print(f"Empty data {url}")
            return


async def get_isins(sic_urls: list, ri_urls: list) -> list:
    """
    :param urls: list of urls for creating tasks for async parsing
    :return: list of tuples with id, serie and isin
    """
    isins = []

    isin_sic_queue = asyncio.Queue()

    isin_ri_queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_sic_isin(session, url, isin_sic_queue) for url in sic_urls]
        await asyncio.gather(*tasks)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_ri_isin(session, url, isin_ri_queue) for url in ri_urls]
        await asyncio.gather(*tasks)

    while not isin_sic_queue.empty():
        isin_id, serie, isin = isin_sic_queue.get_nowait()
        isins.append((isin_id, serie, isin))

    while not isin_ri_queue.empty():
        isin_id, serie, isin = isin_ri_queue.get_nowait()
        isins.append((isin_id, serie, isin))

    return isins


def write_result(symbols: list, isins: list) -> None:
    """
    A function that matches symbols by their id and writes the tv-symbol, description and isin to a file
    :param symbols: list of tuples with id, symbol and description
    :param isins: list of tuples with id, serie and isin
    """
    with open("biva_data.csv", "w") as file:
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


def get_urls_symbols() -> tuple:
    """
    :return: two lists with urls and symbols
    """
    sic_urls = []
    ri_urls = []
    symbols = []

    SIC = requests.get(SIC_URL).json()["content"]
    RI = requests.get(RI_URL).json()["content"]

    for symbol in SIC:
        sic_urls.append(f'https://www.biva.mx/emisoras/sic/{symbol["id"]}/emisiones?size=10&page=0')
        symbols.append((symbol["id"], symbol["clave"], symbol["nombre"]))

    for symbol in RI:
        ri_urls.append(f'https://www.biva.mx/emisoras/empresas/{symbol["id"]}/emisiones?size=10&page=0&cotizacion=true')
        symbols.append((symbol["id"], symbol["clave"], symbol["nombre"]))

    return sic_urls, ri_urls, symbols


def main():

    sic_urls, ri_urls, symbols = get_urls_symbols()

    isins = asyncio.run(get_isins(sic_urls, ri_urls))

    write_result(symbols, isins)


if __name__ == "__main__":
    main()
