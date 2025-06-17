import os

from lib.ConsoleOutput import ConsoleOutput
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


def finra_handler():
    logger = ConsoleOutput(os.path.splitext(os.path.basename(__file__))[0])

    factset_url = "https://info.tradingview.com/factset_finra_isins.csv"
    factset_finra_isins = "factset_finra_isins.csv"

    requester = LoggableRequester(logger, retries=5, delay=5)

    try:
        resp = requester.request(LoggableRequester.Methods.GET, factset_url, get_headers())
        file_writer(resp.text, factset_finra_isins)
        return 0
    except Exception as e:
        logger.error(e)
        return 1


if __name__ == "__main__":
    exit(finra_handler())
