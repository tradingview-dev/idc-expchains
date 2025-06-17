import os

from deepdiff.serialization import json_dumps

from lib.ConsoleOutput import ConsoleOutput
from lib.LoggableRequester import LoggableRequester
from utils import get_headers, file_writer


def canada_handler():
    logger = ConsoleOutput(os.path.splitext(os.path.basename(__file__))[0])

    canada_url = "http://webapi.thecse.com/trading/listed/market/security_maintenance.json"
    canadian_descriptions = "canadian_descriptions.json"

    requester = LoggableRequester(logger, retries=5, delay=5)

    try:
        resp = requester.request(LoggableRequester.Methods.GET, canada_url, get_headers())
        file_writer(json_dumps(resp.json(), indent=4, ensure_ascii=False), canadian_descriptions)
        return 0
    except Exception as e:
        logger.error(e)
        return 1


if __name__ == "__main__":
    exit(canada_handler())
