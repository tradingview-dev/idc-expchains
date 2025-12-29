#!/usr/bin/env python3
# coding=utf-8

import argparse
import enum
import os
import shutil

from adx import ADXDataGenerator
from asx import ASXDataGenerator
from biva import BivaDataGenerator
from canada import CanadaDataGenerator
from cboe import CBOEDataGenerator
from cftc_code import CFTCDataGenerator
from cmc_defi import CMCDataGenerator
from cme import CMEDataGenerator
from corpacts import CorpactsDataGenerator
from euronextmilan import EURONEXTUnderlyingGenerator
from korea import KoreaDataGenerator
from lib.ConsoleOutput import ConsoleOutput
from moex import MOEXDataGenerator
from mstar import MstarDataGenerator
from nasdaq_gids import NASDAQGIDSDataGenerator
from nasdaqtrader import NASDAQTraderDataGenerator
from nyse import NyseDataGenerator
from otc import OtcDataGenerator
from s3_utils import download_state, upload_state, compare_with_remote
from saudi import SAUDIDataGenerator
from shanghai import ShanghaiDataGenerator
from taipei import TaipeiDataGenerator
from tokyo import TokyoDataGenerator
from twse import TwseDataGenerator
from utils import archive_files


class Codes(enum.IntEnum):
    OK = 0
    ERROR = 1
    WARN = 2


def main(args, logger):
    bucket_name = get_environment()
    cluster_name = args.data_cluster
    data_cluster = get_clusters(args).get(cluster_name)
    if not data_cluster:
        logger.error(f"Unknown data cluster: {cluster_name}")
        return Codes.ERROR

    for handler in data_cluster['handlers']:
        state_name = f"{handler.get('state', cluster_name)}.tar.gz"
        state_dir = handler.get('state_dir', "external")

        if args.copy:
            remote_state_archive = download_state(f"{state_dir}/{state_name}")
            logger.log(f"Uploading state {state_dir}/{state_name}... ", upload_state, remote_state_archive, bucket_name, f"{state_dir}/{state_name}")
            logger.info(f"Successfully uploaded {state_name} to s3://{bucket_name}/{state_dir}/{state_name}.")
            shutil.rmtree(remote_state_archive, ignore_errors=True)
            continue

        try:
            files = handler['generator']()
        except Exception as e:
            logger.error(f"Failed to generate files for '{cluster_name}' data cluster CAUSED BY: {e}")
            return Codes.ERROR

        if args.compare:
            remote_state_archive = download_state(f"{state_dir}/{state_name}")
            diffs = logger.log(f"Comparing new files with files in archive {remote_state_archive}... ", compare_with_remote, files, remote_state_archive)
            for d in diffs:
                logger.info(d)
            shutil.rmtree(remote_state_archive, ignore_errors=True)

        try:
            archive_name = logger.log("Archiving new files... ", archive_files, files, state_name)
            logger.log(f"Uploading state {state_dir}/{state_name}... ", upload_state, archive_name, bucket_name, f"{state_dir}/{state_name}")
            logger.info(f"Successfully uploaded {state_name} to s3://{bucket_name}/{state_dir}/{state_name}.")
        except Exception as e:
            logger.error(f"Failed to update {','.join(files)} files into '{state_dir}/{state_name}' state for '{cluster_name}' data cluster CAUSED BY:")
            logger.error(e)
            return Codes.ERROR

        shutil.rmtree(archive_name, ignore_errors=True)

    return Codes.OK


def get_environment() -> str:
    environment = os.environ.get('ENVIRONMENT', None)

    if environment == "production":
        bucket_name = 'tradingview-sourcedata-storage'
    elif environment == "stable":
        bucket_name = 'tradingview-sourcedata-storage-stable'
    elif environment == "staging":
        bucket_name = 'tradingview-sourcedata-storage-staging'
    else:
        raise EnvironmentError(f"Unknown ENVIRONMENT value: {environment}")

    return bucket_name


def get_clusters(args):
    return {
        "adx": {"handlers": [{"generator": ADXDataGenerator().generate}]},
        "asx": {"handlers": [{"generator": ASXDataGenerator().generate}]},
        "biva": {"handlers": [{"generator": BivaDataGenerator().generate}]},
        "canada": {"handlers": [{"generator": CanadaDataGenerator().generate, "state": "cse"}]},
        "euronext_milan": {"handlers": [{"generator": EURONEXTUnderlyingGenerator(args.branch).generate}]},
        "nasdaq_gids": {"handlers": [{"generator": NASDAQGIDSDataGenerator().generate, "state": "gids"}]},
        "nasdaqtrader": {"handlers": [{"generator": NASDAQTraderDataGenerator().generate, "state": "nasdaq"}]},
        "nasdaqomx": {"handlers": [{"generator": NASDAQOMXUnderlyingGenerator(args.branch).generate}]},
        "nyse": {"handlers": [
            {"generator": NyseDataGenerator().generate, "state": "nyse"},
            {"generator": NyseDataGenerator().generate, "state": "amex"}
        ]},
        "saudi": {"handlers": [{"generator": SAUDIDataGenerator().generate}]},
        "shanghai": {"handlers": [{"generator": ShanghaiDataGenerator().generate}]},
        "taipei": {"handlers": [{"generator": TaipeiDataGenerator().generate}]},
        "tokyo": {"handlers": [{"generator": TokyoDataGenerator().generate}]},
        "twse": {"handlers": [{"generator": TwseDataGenerator().generate}]},
        "rus": {"handlers": [{"generator": MOEXDataGenerator().generate, "state": "moex"}]},
        "korea": {"handlers": [{"generator": KoreaDataGenerator().generate}]},
        "cftc": {"handlers": [{"generator": CFTCDataGenerator().generate}]},
        "mstar": {"handlers": [{"generator": MstarDataGenerator().generate}]},
        "cme": {"handlers": [{"generator": CMEDataGenerator().generate}]},
        "cboe": {"handlers": [{"generator": CBOEDataGenerator().generate}]},
        "otc": {"handlers": [{"generator": OtcDataGenerator(args.branch).generate}]},
        "corpacts": {"handlers": [{"generator": CorpactsDataGenerator().generate, "state_dir": "tvc"}]},
        "cmc_defi": {"handlers": [{"generator": CMCDataGenerator(args.branch).generate, "state_dir": "tvc", "state": "defi"}]},
    }


if __name__ == "__main__":
    logger = ConsoleOutput(os.path.splitext(os.path.basename(__file__))[0])

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_cluster", required=True, type=str, help="Name of the data cluster which must generates")
    parser.add_argument("--branch", type=str, default="", required=False,
                        help="Branch for delivery changed files (if empty then changed files will not delivers)")
    parser.add_argument("--copy", action=argparse.BooleanOptionalAction, help="Download from prod and upload")
    parser.add_argument("--compare", action=argparse.BooleanOptionalAction, help="Compare with remote")

    try:
        exit(main(parser.parse_args(), logger))
    except Exception as e:
        logger.error(e)
        exit(Codes.ERROR)
