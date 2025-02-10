import os
import tarfile
import boto3
from botocore.exceptions import NoCredentialsError

def run_s3_process_snapshot(environment, files, snapshot_name):
    ENVIRONMENT = os.environ['ENVIRONMENT']

    if ENVIRONMENT == "production":
        baseurl = 's3://tradingview-sourcedata-storage'
    elif ENVIRONMENT == "stable":
        baseurl = 's3://tradingview-sourcedata-storage-stable'
    elif ENVIRONMENT == "staging":
        baseurl = 's3://tradingview-sourcedata-storage-staging'
    else:
        print(f"Unexpected param {ENVIRONMENT}")
        return  # Exit if environment is not valid

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ['SOURCEDATA_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['SOURCEDATA_AWS_SECRET_ACCESS_KEY'],
    )

    # Define the archive name with .tar.gz extension
    archive_name = f"{snapshot_name}.tar.gz"

    # Ensure the directory where the archive will be stored exists
    archive_dir = os.path.dirname(archive_name)
    if archive_dir and not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"Created directory {archive_dir}")

    try:
        with tarfile.open(archive_name, 'w:gz') as tarf:
            for file in files:
                # Ensure the file exists before adding it to the tar archive
                if os.path.exists(file):
                    # Add file to archive with only the file name (no directory structure)
                    tarf.add(file, arcname=os.path.basename(file))
                    print(f"Added {file} to the archive.")
                else:
                    print(f"Warning: {file} does not exist and will not be added to the archive.")

        print(f"Created archive {archive_name}")

        # Extract bucket name and object key from the baseurl
        bucket_name = baseurl.split('/')[2]  # Extract the bucket name from the URL
        object_key = '/'.join(baseurl.split('/')[3:]) + 'external/' + snapshot_name + '.tar.gz'  # Build the object key

        # Upload the archive to the S3 bucket
        try:
            s3.upload_file(archive_name, bucket_name, object_key)
            print(f"Successfully uploaded {archive_name} to s3://{bucket_name}/{object_key}.")
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred while uploading to S3: {e}")

    except Exception as e:
        print(f"Error while creating tar.gz file: {e}")

    if os.path.exists(archive_name):
        os.remove(archive_name)
        print(f"Removed local archive {archive_name}.")