import subprocess
import os
import logging

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
    # Define base URL based on environment
    if environment == 'production':
        base_url = 's3://tradingview-sourcedata-storage'
    elif environment == 'stable':
        base_url = 's3://tradingview-sourcedata-storage-stable'
    elif environment == 'staging':
        base_url = 's3://tradingview-sourcedata-storage-staging'
    else:
        log_error(f"Unexpected environment: {environment}")
        return

    # Ensure that the required AWS environment variables are set
    if not os.getenv('SOURCEDATA_AWS_ACCESS_KEY_ID') or not os.getenv('SOURCEDATA_AWS_SECRET_ACCESS_KEY'):
        log_error("SOURCEDATA_AWS_ACCESS_KEY_ID and SOURCEDATA_AWS_SECRET_ACCESS_KEY must be defined")
        return

    # Prepare the command and arguments to call the shell script
    command = [
        "bash",  # Use bash to execute the script
        "upload_to_bucket.sh",  # Path to the shell script
        "-i", input_files,  # Input files as a string
        "-s", snapshot_name,  # Snapshot name
        "-x", extension,  # Extension (e.g., ".tar.gz")
        "-d", str(diff_flag)  # Show differences flag (1 or 0)
    ]

    try:
        # Run the shell script as a subprocess
        log_info(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)

        # Check for errors in the subprocess execution
        if result.returncode != 0:
            log_error(f"Error running shell script: {result.stderr}")
            return

        # Log the successful output
        log_success(f"Shell script executed successfully: {result.stdout}")

    except Exception as e:
        log_error(f"An error occurred while running the subprocess: {e}")

