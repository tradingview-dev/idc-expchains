import gzip
import io
import json
import os

import boto3
from botocore.exceptions import ParamValidationError, NoCredentialsError, ClientError

from DataGenerator import DataGenerator
from lib.LoggableRequester import LoggableRequester
from s3_utils import upload_state


class CFIUploader(DataGenerator):

    def __init__(self, branch, mode="cfi"):
        super().__init__()
        self._branch = branch
        self._mode = mode


    @staticmethod
    def get_bourse_codes()-> list[str]:
        return ["21", "66", "80",
                "185", "216", "326",
                "544", "1330", "2913",
                "6184", "6362"]


    @staticmethod
    def get_env():
        environment = os.environ.get('ENVIRONMENT', None)

        if environment == "production":
            return "hub4.tradingview.com:8094"
        elif environment == "stable":
            return "udf-nyc.xstaging.tv/hub01-stable"
        else:
            return "hub0.tradingview.com:8092"


    def get_cfi(self) -> dict[str, str]:
        res = {}
        host = self.get_env()
        for code in self.get_bourse_codes():
            data = LoggableRequester(self._logger, timeout=30).request(LoggableRequester.Methods.GET, f"http://{host}/tvf/upstream/sixmdfstream/streaming/symbols?source={code}&additionalFields=TDF_ISIN,TDF_CFI").text
            for s in data.split("\n"):
                symbol = s.split(",")
                if len(symbol) < 3:
                    continue
                val, isin, cfi = symbol
                if cfi != "":
                    res[isin] = cfi
        return res


    def generate(self) -> list[str]:

        if self._mode == "cfi_dict_upload":

            upload_cfi(self._branch)
            return []

        result = "CfiFromSix.csv"

        with open(result, "w") as file:
            file.write("isin;cfi_code\n")
            for isin, cfi in self.get_cfi().items():
                file.write(f"{isin};{cfi}\n")

        return [result]


def upload_cfi(branch: str):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("SOURCEDATA_AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("SOURCEDATA_AWS_SECRET_ACCESS_KEY"),
    )

    bucket = get_bucket(branch)

    try:
        for filename in os.listdir("cfi_dict"):
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join("cfi_dict", filename)

            with open(filepath, "rb") as file:
                raw = file.read()

            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="w") as f:
                f.write(raw)

            buf.seek(0)

            s3.put_object(
                Bucket=bucket,
                Key=f"cfi/{filename}",
                Body=buf.getvalue(),
                ContentType="application/json",
                ContentEncoding="gzip",
            )

    except ClientError as e:
        raise e
    except ParamValidationError as e:
        raise e
    except NoCredentialsError as e:
        raise Exception("aws_access_key_id and/or aws_secret_access_key", e) from e
    except Exception as e:
        raise Exception("Unexpected exception has been occurred", e) from e

def get_bucket(branch: str) -> str:
    buckets = {
        "staging": "tradingview-pub-staging",
        "master": "tradingview-pub"
    }
    return buckets[branch]


if __name__ == "__main__":
    try:
        CFIUploader("staging").generate()
        exit(0)
    except OSError:
        exit(1)
