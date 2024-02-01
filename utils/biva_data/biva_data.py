import aiohttp
import asyncio
import json
import requests


async def fetch_isin(session, url, isin_queue) -> None:
    """
    :param session: aiohttp.ClientSession()
    :param url: symbol's url
    :param isin_queue: queue for saving the results of async parsing
    """
    async with session.get(url) as response:
        data = await response.json()
        isin_id = int(url.split("/")[5])

        try:
            serie = data["content"][0]["serie"]
            isin = data["content"][0]["isin"]

            if isin_id is not None and isin is not None:
                isin_queue.put_nowait((isin_id, serie, isin))

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {url}: {e}")


async def get_isins(urls: list) -> list:
    """
    :param urls: list of urls for creating tasks for async parsing
    :return: list of tuples with id, serie and isin
    """
    isins = []

    isin_queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
            tasks = [fetch_isin(session, url, isin_queue) for url in urls]
            await asyncio.gather(*tasks)

    while not isin_queue.empty():
            isin_id, serie, isin = isin_queue.get_nowait()
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


def main():

    urls = []
    symbols = []

    SIC = requests.get("https://www.biva.mx/emisoras/sic?size=10000&page=0").json()["content"]

    for symbol in SIC:

        urls.append(f'https://www.biva.mx/emisoras/sic/{symbol["id"]}/emisiones?size=10&page=0')
        symbols.append((symbol["id"], symbol["clave"], symbol["nombre"]))

    isins = asyncio.run(get_isins(urls))

    write_result(symbols, isins)


if __name__ == "__main__":
    main()