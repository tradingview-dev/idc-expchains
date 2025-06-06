#!/usr/bin/env python3
# coding=utf-8

import argparse
import sys

from utils import default_request_handler, json_request_handler, delivery, load_from_repo
from aquis import aquis_handler
from biva import biva_handler
from cboe import cboe_handler
from cme import cme_handler
from lang_and_shwarz_data import lang_and_shwarz_handler
from taipei import taipei_handler
from shanghai import shanghai_handler
from saudi import saudi_handler
from mstar import mstar_handler
from nyse import nyse_handler
from nasdaq_gids import nasdaq_gids_handler
from tokyo import tokyo_handler
from twse import twse_handler
from moex import moex_handler
from korea import korea_handler
from upload_to_bucket import run_s3_process_snapshot
from cftc_code import cftc_handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_cluster", required= True, type=str, help="Name of the data cluster which must generates")
    parser.add_argument("--branch", type=str, default="", required=False, help="Branch for delivery changed files (if empty then changed files will not delivers)")
    args = parser.parse_args()

    if args.data_cluster == "adx":
        adx_url = "https://adxservices.adx.ae/WebServices/DataServices/api/web/assets"
        adx_data_regular = "adx_data_regular.json"
        adx_data_fund = "adx_data_fund.json"
        json_request_handler(adx_url, adx_data_regular, post_data={"Status": "L", "Boad": "REGULAR", "Del": "0"})
        json_request_handler(adx_url,adx_data_fund, post_data={"Status": "L", "Boad": "FUND", "Del": "0"})
        delivery([adx_data_regular, adx_data_fund], args.branch)
        run_s3_process_snapshot(args.branch, [adx_data_regular, adx_data_fund], "adx")
    elif args.data_cluster == "asx":
        asx_descriptions = "asx_descriptions.csv"
        default_request_handler("https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file", asx_descriptions)
        delivery([asx_descriptions], args.branch)
        run_s3_process_snapshot(args.branch, [asx_descriptions], "asx")
    elif args.data_cluster == "biva":
        biva_handler()
        delivery(["biva_data.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["biva_data.csv"], "biva")
    elif args.data_cluster == "canada":
        canadian_descriptions = "canadian_descriptions.json"
        json_request_handler("http://webapi.thecse.com/trading/listed/market/security_maintenance.json", canadian_descriptions)
        delivery([canadian_descriptions], args.branch)
        run_s3_process_snapshot(args.branch, [canadian_descriptions], "cse")
    elif args.data_cluster == "finra":
        factset_finra_isins = "factset_finra_isins.csv"
        default_request_handler("https://info.tradingview.com/factset_finra_isins.csv", factset_finra_isins)
        delivery([factset_finra_isins], args.branch)
        run_s3_process_snapshot(args.branch, [factset_finra_isins], "finra")
    elif args.data_cluster == "LSX":
        lang_and_shwarz_handler(args.data_cluster)
        files = ["LSX.csv"]
        delivery(files, args.branch)
        run_s3_process_snapshot(args.branch, files, "lsx")
    elif args.data_cluster == "LS":
        lang_and_shwarz_handler(args.data_cluster)
        files = ["LS.csv"]
        delivery(files, args.branch)
        run_s3_process_snapshot(args.branch, files, "ls")
    elif args.data_cluster == "nasdaq_gids":
        nasdaq_gids_handler()
        delivery(["nasdaq_gids_symbols.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["nasdaq_gids_symbols.csv"], "gids")
    elif args.data_cluster == "nasdaqtrader":
        nasdaqtrader_descriptions = "nasdaqtrader_descriptions.txt"
        default_request_handler("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",nasdaqtrader_descriptions)
        delivery([nasdaqtrader_descriptions], args.branch)
        run_s3_process_snapshot(args.branch, [nasdaqtrader_descriptions], "nasdaq")
    elif args.data_cluster == "nyse":
        nyse_handler()
        delivery(["nyse_data.csv", "amex_data.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["nyse_data.csv"], "nyse")
        run_s3_process_snapshot(args.branch, ["amex_data.csv"], "amex")
    elif args.data_cluster == "saudi":
        saudi_handler()
        delivery(["saudi_main_market.json", "saudi_nomu_parallel_market.json"], args.branch)
        run_s3_process_snapshot(args.branch, ["saudi_main_market.json", "saudi_nomu_parallel_market.json"], "saudi")
    elif args.data_cluster == "shanghai":
        shanghai_handler()
        delivery(["sse_descriptions.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["sse_descriptions.csv"], "shanghai")
    elif args.data_cluster == "taipei":
        taipei_handler()
        delivery(["taipei_descriptions.json", "taipei_local_descriptions.json"], args.branch)
        run_s3_process_snapshot(args.branch, ["taipei_descriptions.json", "taipei_local_descriptions.json"], "taipei")
    elif args.data_cluster == "tokyo":
        tokyo_handler()
        delivery(["tokyo_local_descriptions.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["tokyo_local_descriptions.csv"], "tokyo")
    elif args.data_cluster == "twse":
        twse_handler()
        delivery(["twse_descriptions.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["twse_descriptions.csv"], "twse")
    elif args.data_cluster == "rus":
        if moex_handler() == 0:
            delivery([
                "moex_boards_securities.json",
                "moex_index_boards_securities.json",
                "moex_stock_rates.json"], args.branch)
            run_s3_process_snapshot(args.branch, [
                "moex_boards_securities.json",
                "moex_index_boards_securities.json",
                "moex_stock_rates.json"], "moex")
        else:
            print("\033[1;91mSomething went wrong... Uploading has been skipped.\033[0m", flush=True)
            return 1
    elif args.data_cluster == "korea":
        korea_handler()
        delivery(["korea_local_descriptions.csv", "krx_derivatives_local_descriptions.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["korea_local_descriptions.csv", "krx_derivatives_local_descriptions.csv"], "korea")
    elif args.data_cluster == "cftc":
        cftc_handler()
        run_s3_process_snapshot(args.branch, ["cftc_CBOT.csv",
                                              "cftc_CME.csv",
                                              "cftc_ICEUS.csv",
                                              "cftc_COMEX.csv",
                                              "cftc_NYMEX.csv",
                                              "cftc_CBOE.csv",
                                              "cftc_SGX.csv",
                                              "cftc_ICEEU.csv"
                                              ], "cftc")
    elif args.data_cluster == "aquis":
        aquis_handler()
        delivery(["aquis.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["aquis.csv"], "aquis")
    elif args.data_cluster == "mstar":
        mstar_handler()
        delivery(["mstar_descriptions.csv"], args.branch)
        run_s3_process_snapshot(args.branch, ["mstar_descriptions.csv"], "mstar")
    elif args.data_cluster == "cme":
            cme_handler("Futures")
            cme_handler("Options")
            delivery(["Options_products.csv",
                      "Futures_products.csv"], args.branch)
            run_s3_process_snapshot(args.branch, ["Options_products.csv",
                                                  "Futures_products.csv"], "cme")
    elif args.data_cluster == "cboe":
            cboe_handler()
            delivery(["cboe.csv"], args.branch)
            run_s3_process_snapshot(args.branch, ["cboe.csv"], "cboe")
    else:
        print("No data-cluster found!")

    return 0


if __name__ == "__main__":
    sys.exit(main())