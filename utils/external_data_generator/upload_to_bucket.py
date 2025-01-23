import subprocess
import os
import logging
import zipfile

import boto3
from botocore.exceptions import NoCredentialsError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_error(message):
    logger.error(message)


def log_info(message):
    logger.info(message)


def log_success(message):
    logger.info(f"SUCCESS: {message}")


def log_warn(message):
    logger.warning(f"WARNING: {message}")


def run_s3_process_snapshot(environment, input_files, snapshot_name, extension, diff_flag):
    # Initialize the S3 client with credentials from environment variables
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ['SOURCEDATA_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['SOURCEDATA_AWS_SECRET_ACCESS_KEY'],
    )

    # Split the input_files string into a list of file names
    files = input_files.split()

    # Define the archive name (you can use any name here, e.g., 'snapshot.zip')
    archive_name = f"{snapshot_name}.zip"

    # Create the zip file
    try:
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                # Ensure the file exists before adding it to the zip archive
                if os.path.exists(file):
                    zipf.write(file, os.path.basename(file))  # Add the file to the archive
                    print(f"Added {file} to the archive.")
                else:
                    print(f"Warning: {file} does not exist and will not be added to the archive.")

        print(f"Created archive {archive_name}")

        # Upload the archive to the S3 bucket
        try:
            s3.upload_file(archive_name, snapshot_name, archive_name)
            print(f"Successfully uploaded {archive_name} to {snapshot_name} bucket.")
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred while uploading to S3: {e}")

    except Exception as e:
        print(f"Error while creating zip file: {e}")

    # Optionally, you can remove the local archive after upload
    if os.path.exists(archive_name):
        os.remove(archive_name)
        print(f"Removed local archive {archive_name}.")

