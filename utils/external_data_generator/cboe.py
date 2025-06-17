import os

import requests

from lib.ConsoleOutput import ConsoleOutput


def cboe_handler():
    # private static variables
    __logger = ConsoleOutput(os.path.splitext(os.path.basename(__file__))[0])

    try:
        csv = request_listed_symbols(__logger)
    except requests.RequestException:
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
        __logger.error(e)
        return 1

    return 0


def request_listed_symbols(__logger):
    try:
        resp = requests.get("https://www.cboe.com/us/equities/market_statistics/listed_symbols/csv/")
        if not resp:
            raise requests.RequestException("No response from requested service")
        resp.raise_for_status()  # checks the response status code and raises an exception for HTTP errors (4xx or 5xx)
        return resp.text
    except requests.RequestException as e:
        __logger.error(f"Failed to get data from {e.request.url} by {e.request.method} method: {str(e)}")
        raise e
