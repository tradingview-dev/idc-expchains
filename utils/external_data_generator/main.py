#!/usr/bin/env python3
# coding=utf-8

import argparse

from utils import default_request_handler, json_request_handler, delivery
from biva import biva_handler
from lang_and_shwarz_data import lang_and_shwarz_handler
from taipei import taipei_handler
from shanghai import shanghai_handler
from saudi import saudi_handler
from nyse import nyse_handler
from nasdaq_gids import nasdaq_gids_handler
from nse_emerge import nse_emerge_handler
from upload_to_bucket import run_s3_process_snapshot


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
        run_s3_process_snapshot(args.branch, "adx_data_regular.json adx_data_fund.json", "adx")
    elif args.data_cluster == "asx":
        asx_descriptions = "asx_descriptions.json"
        default_request_handler("https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file", asx_descriptions)
        delivery([asx_descriptions], args.branch)
        run_s3_process_snapshot(args.branch, "asx_descriptions.json", "asx")
    elif args.data_cluster == "biva":
        biva_handler()
        delivery(["biva_data.csv"], args.branch)
        run_s3_process_snapshot(args.branch, "biva_data.json", "biva")
    elif args.data_cluster == "canada":
        canadian_descriptions = "canadian_descriptions.json"
        json_request_handler("http://webapi.thecse.com/trading/listed/market/security_maintenance.json", canadian_descriptions)
        delivery([canadian_descriptions], args.branch)
        run_s3_process_snapshot(args.branch, "canadian_descriptions.json", "cse")
    elif args.data_cluster == "finra":
        factset_finra_isins = "factset_finra_isins.csv"
        default_request_handler("https://info.tradingview.com/factset_finra_isins.csv", factset_finra_isins)
        run_s3_process_snapshot(args.branch, "factset_finra_isins.json", "finra")
        delivery([factset_finra_isins], args.branch)
    elif args.data_cluster == "LSX":
        lang_and_shwarz_handler(args.data_cluster)
        delivery(["LSX.csv"], args.branch)
        run_s3_process_snapshot(args.branch, "LSX.csv", "lsx")
    elif args.data_cluster == "LS":
        lang_and_shwarz_handler(args.data_cluster)
        delivery(["LS.csv"], args.branch)
        run_s3_process_snapshot(args.branch, "LSX.cs", "ls")
    elif args.data_cluster == "nse_emerge":
        nse_raw_listing = "nse_raw_listing.csv"
        default_request_handler("https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv", nse_raw_listing)
        nse_emerge_handler()
        delivery([nse_raw_listing], args.branch)
        run_s3_process_snapshot(args.branch, nse_raw_listing, "nse")
    elif args.data_cluster == "nasdaq_gids":
        nasdaq_gids_handler()
        delivery(["nasdaq_gids_symbols.csv"], args.branch)
        run_s3_process_snapshot(args.branch, "nasdaq_gids_symbols.csv", "gids")
    elif args.data_cluster == "nasdaqtrader":
        nasdaqtrader_descriptions = "nasdaqtrader_descriptions.txt"
        default_request_handler("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",nasdaqtrader_descriptions)
        delivery([nasdaqtrader_descriptions], args.branch)
        run_s3_process_snapshot(args.branch, nasdaqtrader_descriptions, "nasdaq")
    elif args.data_cluster == "nyse":
        nyse_handler()
        delivery(["nyse_data.csv", "amex_data.csv"], args.branch)
        run_s3_process_snapshot(args.branch, "nyse_data.csv", "nyse")
        run_s3_process_snapshot(args.branch, "amex_data.csv", "amex")
    elif args.data_cluster == "saudi":
        saudi_handler()
        delivery(["saudi_main_market.json", "saudi_nomu_parallel_market.json"], args.branch)
        run_s3_process_snapshot(args.branch, "saudi_main_market.json saudi_nomu_parallel_market.json", "amex")
    elif args.data_cluster == "shanghai":
        shanghai_handler()
        delivery(["sse_descriptions.csv"], args.branch)
        run_s3_process_snapshot(args.branch, "sse_descriptions.csv", "sse",".tar.gz", 1)
    elif args.data_cluster == "taipei":
        taipei_handler()
        delivery(["taipei_descriptions.json", "taipei_local_descriptions.json"], args.branch)
        run_s3_process_snapshot(args.branch, "taipei_descriptions.json taipei_local_descriptions.json", "sse")
    else:
        print("No data-cluster found!")


if __name__ == "__main__":
    main()