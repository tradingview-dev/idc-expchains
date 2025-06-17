#!/usr/bin/env python3
# coding=utf-8

import argparse
import enum
import os

from biva import BivaDataGenerator
from lib.ConsoleOutput import ConsoleOutput
from moex import moex_handler
from upload_to_bucket import run_s3_process_snapshot
from utils import delivery
from adx import ADXDataGenerator
from asx import ASXDataGenerator
from canada import CanadaDataGenerator
from finra import FinraDataGenerator
from lang_and_shwarz import Lang, Schwarz
from nasdaq_gids import NASDAQGIDSDataGenerator
from nasdaqtrader import NASDAQTraderDataGenerator
from saudi import SAUDIDataGenerator
from shanghai import ShanghaiDataGenerator
from taipei import TaipeiDataGenerator
from tokyo import TokyoDataGenerator
from twse import TwseDataGenerator
from korea import korea_handler
from cftc_code import CFTCDataGenerator
from aquis import AquisDataGenerator
from cboe import CBOEDataGenerator
from mstar import MstarDataGenerator
from nyse import NyseDataGenerator


class Codes(enum.IntEnum):
    OK = 0
    ERROR = 1
    WARN = 2


def main(args, logger):

    data_clusters = {
        "adx": {"handler": ADXDataGenerator().generate, "output": ["adx_data_regular.json", "adx_data_fund.json"]},
        "asx": {"handler": ASXDataGenerator().generate, "output": ["asx_descriptions.csv"]},
        "biva": {"handler": BivaDataGenerator().generate, "output": ["biva_data.csv"]},
        "canada": {"handler": CanadaDataGenerator().generate, "output": ["canadian_descriptions.json"]},
        "finra": {"handler": FinraDataGenerator().generate, "output": ["factset_finra_isins.csv"]},
        "LSX": {"handler": Lang().generate, "output": ["LSX.csv"], "path": "lsx"},
        "LS": {"handler": Schwarz().generate, "output": ["LS.csv"], "path": "ls"},
        "nasdaq_gids": {"handler": NASDAQGIDSDataGenerator().generate, "output": ["nasdaq_gids_symbols.csv"]},
        "nasdaqtrader": {"handler": NASDAQTraderDataGenerator().generate, "output": ["nasdaqtrader_descriptions.txt"]},
        "nyse": {"handler": NyseDataGenerator().generate, "output": ["nyse_data.csv", "amex_data.csv"]},
        "saudi": {"handler": SAUDIDataGenerator().generate, "output": ["saudi_main_market.json", "saudi_nomu_parallel_market.json"]},
        "shanghai": {"handler": ShanghaiDataGenerator().generate, "output": ["sse_descriptions.csv"]},
        "taipei": {"handler": TaipeiDataGenerator().generate, "output": ["taipei_descriptions.json", "taipei_local_descriptions.json"]},
        "tokyo": {"handler": TokyoDataGenerator().generate, "output": ["tokyo_local_descriptions.csv"]},
        "twse": {"handler": TwseDataGenerator().generate, "output": ["twse_descriptions.csv"]},
        "rus": {"handler": moex_handler, "output": ["moex_boards_securities.json", "moex_index_boards_securities.json", "moex_stock_rates.json"], "path": "moex"},
        "korea": {"handler": korea_handler, "output": ["korea_local_descriptions.csv", "krx_derivatives_local_descriptions.csv"]},
        "cftc": {"handler": CFTCDataGenerator().generate, "output": ["cftc_CBOT.csv", "cftc_CME.csv", "cftc_ICEUS.csv", "cftc_COMEX.csv", "cftc_NYMEX.csv", "cftc_CBOE.csv", "cftc_SGX.csv", "cftc_ICEEU.csv"]},
        "aquis": {"handler": AquisDataGenerator().generate, "output": ["aquis.csv"]},
        "mstar": {"handler": MstarDataGenerator().generate, "output": ["mstar_descriptions.csv"]},
        "cboe": {"handler": CBOEDataGenerator().generate, "output": ["cboe.csv"]}
    }
    data_cluster = data_clusters.get(args.data_cluster)
    if data_cluster:
        if data_cluster['handler'](data_cluster) != 0:
            logger.error(f"data_cluster::{args.data_cluster} Something went wrong... Uploading has been skipped.")
            return Codes.ERROR
        # delivery(data_cluster['output'], args.branch)
        # run_s3_process_snapshot(args.branch, [
        #     "moex_boards_securities.json",
        #     "moex_index_boards_securities.json",
        #     "moex_stock_rates.json"], data_cluster.get('path', args.data_cluster))
    else:
        print("Invalid choice.")

    # if args.data_cluster == "adx":
    #     adx_url = "https://adxservices.adx.ae/WebServices/DataServices/api/web/assets"
    #     adx_data_regular = "adx_data_regular.json"
    #     adx_data_fund = "adx_data_fund.json"
    #     json_request_handler(adx_url, adx_data_regular, post_data={"Status": "L", "Boad": "REGULAR", "Del": "0"})
    #     json_request_handler(adx_url,adx_data_fund, post_data={"Status": "L", "Boad": "FUND", "Del": "0"})
    #     delivery([adx_data_regular, adx_data_fund], args.branch)
    #     run_s3_process_snapshot(args.branch, [adx_data_regular, adx_data_fund], "adx")
    # elif args.data_cluster == "asx":
    #     asx_descriptions = "asx_descriptions.csv"
    #     default_request_handler("https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file", asx_descriptions)
    #     delivery([asx_descriptions], args.branch)
    #     run_s3_process_snapshot(args.branch, [asx_descriptions], "asx")
    # elif args.data_cluster == "biva":
    #     biva_handler()
    #     delivery(["biva_data.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["biva_data.csv"], "biva")
    # elif args.data_cluster == "canada":
    #     canadian_descriptions = "canadian_descriptions.json"
    #     json_request_handler("http://webapi.thecse.com/trading/listed/market/security_maintenance.json", canadian_descriptions)
    #     delivery([canadian_descriptions], args.branch)
    #     run_s3_process_snapshot(args.branch, [canadian_descriptions], "cse")
    # elif args.data_cluster == "finra":
    #     factset_finra_isins = "factset_finra_isins.csv"
    #     default_request_handler("https://info.tradingview.com/factset_finra_isins.csv", factset_finra_isins)
    #     delivery([factset_finra_isins], args.branch)
    #     run_s3_process_snapshot(args.branch, [factset_finra_isins], "finra")
    # elif args.data_cluster == "LSX":
    #     lang_and_shwarz_handler(args.data_cluster)
    #     files = ["LSX.csv"]
    #     delivery(files, args.branch)
    #     run_s3_process_snapshot(args.branch, files, "lsx")
    # elif args.data_cluster == "LS":
    #     lang_and_shwarz_handler(args.data_cluster)
    #     files = ["LS.csv"]
    #     delivery(files, args.branch)
    #     run_s3_process_snapshot(args.branch, files, "ls")
    # elif args.data_cluster == "nasdaq_gids":
    #     nasdaq_gids_handler()
    #     delivery(["nasdaq_gids_symbols.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["nasdaq_gids_symbols.csv"], "gids")
    # elif args.data_cluster == "nasdaqtrader":
    #     nasdaqtrader_descriptions = "nasdaqtrader_descriptions.txt"
    #     default_request_handler("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",nasdaqtrader_descriptions)
    #     delivery([nasdaqtrader_descriptions], args.branch)
    #     run_s3_process_snapshot(args.branch, [nasdaqtrader_descriptions], "nasdaq")
    # elif args.data_cluster == "nyse":
    #     nyse_handler()
    #     delivery(["nyse_data.csv", "amex_data.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["nyse_data.csv"], "nyse")
    #     run_s3_process_snapshot(args.branch, ["amex_data.csv"], "amex")
    # elif args.data_cluster == "saudi":
    #     saudi_handler()
    #     delivery(["saudi_main_market.json", "saudi_nomu_parallel_market.json"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["saudi_main_market.json", "saudi_nomu_parallel_market.json"], "saudi")
    # elif args.data_cluster == "shanghai":
    #     shanghai_handler()
    #     delivery(["sse_descriptions.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["sse_descriptions.csv"], "shanghai")
    # elif args.data_cluster == "taipei":
    #     taipei_handler()
    #     delivery(["taipei_descriptions.json", "taipei_local_descriptions.json"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["taipei_descriptions.json", "taipei_local_descriptions.json"], "taipei")
    # elif args.data_cluster == "tokyo":
    #     tokyo_handler()
    #     delivery(["tokyo_local_descriptions.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["tokyo_local_descriptions.csv"], "tokyo")
    # elif args.data_cluster == "twse":
    #     twse_handler()
    #     delivery(["twse_descriptions.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["twse_descriptions.csv"], "twse")
    # elif args.data_cluster == "rus":
    #     if moex_handler() != 0:
    #         logger.error(f"data_cluster::{args.data_cluster} Something went wrong... Uploading has been skipped.")
    #         return Codes.ERROR
    #     delivery([
    #         "moex_boards_securities.json",
    #         "moex_index_boards_securities.json",
    #         "moex_stock_rates.json"], args.branch)
    #     run_s3_process_snapshot(args.branch, [
    #         "moex_boards_securities.json",
    #         "moex_index_boards_securities.json",
    #         "moex_stock_rates.json"], "moex")
    # elif args.data_cluster == "korea":
    #     korea_handler()
    #     delivery(["korea_local_descriptions.csv", "krx_derivatives_local_descriptions.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["korea_local_descriptions.csv", "krx_derivatives_local_descriptions.csv"], "korea")
    # elif args.data_cluster == "cftc":
    #     cftc_handler()
    #     run_s3_process_snapshot(args.branch, ["cftc_CBOT.csv",
    #                                           "cftc_CME.csv",
    #                                           "cftc_ICEUS.csv",
    #                                           "cftc_COMEX.csv",
    #                                           "cftc_NYMEX.csv",
    #                                           "cftc_CBOE.csv",
    #                                           "cftc_SGX.csv",
    #                                           "cftc_ICEEU.csv"
    #                                           ], "cftc")
    # elif args.data_cluster == "aquis":
    #     aquis_handler()
    #     delivery(["aquis.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["aquis.csv"], "aquis")
    # elif args.data_cluster == "mstar":
    #     mstar_handler()
    #     delivery(["mstar_descriptions.csv"], args.branch)
    #     run_s3_process_snapshot(args.branch, ["mstar_descriptions.csv"], "mstar")
    # elif args.data_cluster == "cme":
    #         cme_handler("Futures")
    #         cme_handler("Options")
    #         delivery(["Options_products.csv",
    #                   "Futures_products.csv"], args.branch)
    #         run_s3_process_snapshot(args.branch, ["Options_products.csv",
    #                                               "Futures_products.csv"], "cme")
    # elif args.data_cluster == "cboe":
    #         if cboe_handler() != 0:
    #             logger.error(f"data_cluster::{args.data_cluster} Something went wrong... Uploading has been skipped.")
    #             return Codes.ERROR
    #         delivery(["cboe.csv"], args.branch)
    #         run_s3_process_snapshot(args.branch, ["cboe.csv"], "cboe")
    # else:
    #     logger.warn("No data-cluster found!")
    #     return Codes.WARN

    return 0


if __name__ == "__main__":
    logger = ConsoleOutput(os.path.splitext(os.path.basename(__file__))[0])

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_cluster", required=True, type=str, help="Name of the data cluster which must generates")
    parser.add_argument("--branch", type=str, default="", required=False,
                        help="Branch for delivery changed files (if empty then changed files will not delivers)")

    try:
        exit(main(parser.parse_args(), logger))
    except Exception as e:
        logger.error(e)
        exit(Codes.ERROR)