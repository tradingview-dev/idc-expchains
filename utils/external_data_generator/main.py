#!/usr/bin/env python3
# coding=utf-8

import argparse
import enum
import os
import shutil
import tarfile
import tempfile

from adx import ADXDataGenerator
from asx import ASXDataGenerator
from biva import BivaDataGenerator
from canada import CanadaDataGenerator
from cboe import CBOEDataGenerator
from cftc_code import CFTCDataGenerator
from cme import CMEDataGenerator
from korea import KoreaDataGenerator
from lang_and_shwarz import Lang, Schwarz
from lib.ConsoleOutput import ConsoleOutput
from moex import MOEXDataGenerator
from mstar import MstarDataGenerator
from nasdaq_gids import NASDAQGIDSDataGenerator
from nasdaqtrader import NASDAQTraderDataGenerator
from nyse import NyseDataGenerator
from saudi import SAUDIDataGenerator
from shanghai import ShanghaiDataGenerator
from taipei import TaipeiDataGenerator
from tokyo import TokyoDataGenerator
from twse import TwseDataGenerator
from otc import OtcDataGenerator
from corpacts import CorpactsDataGenerator
from upload_to_bucket import run_s3_process_snapshot, run_storage_download, run_s3_upload
from utils import git_commit


class Codes(enum.IntEnum):
    OK = 0
    ERROR = 1
    WARN = 2


def main(args, logger):
    data_clusters = {
        "adx": {"handlers": [{"generator": ADXDataGenerator().generate}]},
        "asx": {"handlers": [{"generator": ASXDataGenerator().generate}]},
        "biva": {"handlers": [{"generator": BivaDataGenerator().generate}]},
        "canada": {"handlers": [{"generator": CanadaDataGenerator().generate, "state": "cse"}]},
        "LSX": {"handlers": [{"generator": Lang().generate, "state": "lsx"}]},
        "LS": {"handlers": [{"generator": Schwarz().generate, "state": "ls"}]},
        "nasdaq_gids": {"handlers": [{"generator": NASDAQGIDSDataGenerator().generate, "state": "gids"}]},
        "nasdaqtrader": {"handlers": [{"generator": NASDAQTraderDataGenerator().generate, "state": "nasdaq"}]},
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
    }
    cluster_name = args.data_cluster
    data_cluster = data_clusters.get(cluster_name)
    if not data_cluster:
        logger.error(f"Unknown data cluster: {cluster_name}")
        return Codes.ERROR

    if args.copy:
        return download_and_upload(data_cluster, cluster_name, args.branch)

    return generate_and_upload(data_cluster, cluster_name, args.branch)


def download_and_upload(data_cluster, cluster_name, git_branch):
    for handler in data_cluster['handlers']:
        state_name = handler.get('state', cluster_name)
        state_dir = handler.get('state_dir', "external")
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
            tmp_file.close()
            try:
                logger.info(f"Copying state {state_dir}/{state_name}")
                run_storage_download(state_dir, state_name, tmp_file.name)
                run_s3_upload(tmp_file.name, state_dir, state_name)

                with tempfile.TemporaryDirectory() as tmp_dir:
                    logger.info(f"Unpacking {tmp_file.name}")
                    with tarfile.open(tmp_file.name, "r") as tar:
                        tar.extractall(path=tmp_dir)
                        tar.close()
                    files = os.listdir(tmp_dir)
                    for fn in files:
                        logger.info(f"Copying {fn} from archive to working directory")
                        shutil.copy(os.path.join(tmp_dir, fn), os.path.join(".", fn))

                git_commit(files, git_branch)
            except Exception as e:
                logger.error(f"Failed to download and upload '{state_dir}/{state_name}' data CAUSED BY: {e}")
                return Codes.ERROR

    return Codes.OK


def generate_and_upload(data_cluster, cluster_name, git_branch):
    files_to_commit = []
    for handler in data_cluster['handlers']:
        try:
            files = handler['generator']()
        except Exception as e:
            logger.error(f"Failed to generate files for '{cluster_name}' data cluster CAUSED BY: {e}")
            return Codes.ERROR
        files_to_commit.extend(files)
        state_name = handler.get('state', cluster_name)
        state_dir = handler.get('state_dir', "external")
        try:
            run_s3_process_snapshot(files, state_dir, state_name)
        except Exception as e:
            logger.error(f"Failed to update {','.join(files)} files into '{state_dir}/{state_name}' state for '{cluster_name}' data cluster CAUSED BY: {e}")
            return Codes.ERROR

    try:
        git_commit(files_to_commit, git_branch)
    except Exception as e:
        logger.error(f"Failed to commit [{','.join(files_to_commit)}] files generated by '{cluster_name}' data cluster handlers CAUSED BY {e}")
        return Codes.ERROR

    return Codes.OK


if __name__ == "__main__":
    logger = ConsoleOutput(os.path.splitext(os.path.basename(__file__))[0])

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_cluster", required=True, type=str, help="Name of the data cluster which must generates")
    parser.add_argument("--branch", type=str, default="", required=False,
                        help="Branch for delivery changed files (if empty then changed files will not delivers)")
    parser.add_argument("--copy", action=argparse.BooleanOptionalAction, help="Download from prod and upload")

    try:
        exit(main(parser.parse_args(), logger))
    except Exception as e:
        logger.error(e)
        exit(Codes.ERROR)