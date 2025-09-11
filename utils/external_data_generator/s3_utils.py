import os
import tarfile
import tempfile
from pathlib import Path
from typing import LiteralString

import boto3
from botocore.exceptions import ClientError, ParamValidationError, NoCredentialsError

from lib.LoggableRequester import LoggableRequester
from utils import print_colored_diff


def download_state(object_key: str) -> str:
    tmp_file = tempfile.NamedTemporaryFile(suffix="".join(Path(object_key).suffixes), delete=False)
    baseurl = "https://tradingview-sourcedata-storage.xtools.tv"
    url = f"{baseurl}/{object_key}"
    try:
        resp = LoggableRequester().request(LoggableRequester.Methods.GET, url)
        with open(tmp_file.name, "wb") as f:
            f.write(resp.content)
    except OSError as e:
        raise e
    return tmp_file.name


def read_state(bucket_name: str, object_key: str, profile_name=None) -> bytes | None:
    if profile_name is not None:
        session = boto3.Session(profile_name=profile_name)
        s3_client = session.client('s3')
    else:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('SOURCEDATA_AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=os.environ.get('SOURCEDATA_AWS_SECRET_ACCESS_KEY', None)
        )
    try:
        # get object from s3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body'].read()
    except ClientError as e:
        # main handler of errors, related to s3 service
        raise e
    except ParamValidationError as e:
        # handler if incorrect arguments format
        raise e
    except Exception as e:
        # common exception handler for any unexpected cases
        raise Exception("Unexpected exception has been occurred") from e


def upload_state(file_path: str, bucket_name: str, object_key: str):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('SOURCEDATA_AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=os.environ.get('SOURCEDATA_AWS_SECRET_ACCESS_KEY', None)
    )

    try:
        # upload the archive to the s3 bucket
        s3.upload_file(file_path, bucket_name, object_key)
    except ClientError as e:
        # main handler of errors, related to s3 service
        raise e
    except ParamValidationError as e:
        # handler if incorrect arguments format
        raise e
    except NoCredentialsError as e:
        # credentials error handler
        raise Exception("aws_access_key_id and/or aws_secret_access_key", e) from e
    except Exception as e:
        # common exception handler for any unexpected cases
        raise Exception("Unexpected exception has been occurred", e) from e


def compare_with_remote(files_to_compare: list[str], remote_archive_name: str):
    diffs: list[LiteralString] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            with tarfile.open(remote_archive_name, "r") as tar:
                tar.extractall(path=tmp_dir)
            remote_files = {
                entry.name: str(os.path.join(tmp_dir, entry.name)) for entry in tar.getmembers()
            }
            for filename in files_to_compare:
                if filename in remote_files:
                    diffs.append(print_colored_diff(remote_files[filename], filename))
        except OSError as e:
            raise e
    return diffs
