FROM ubuntu:24.04
ARG PATH_TO_LIB

RUN apt update && \
    apt install -y --no-install-recommends python3 python3-pip git python3-git python3-openpyxl python3-requests python3-deepdiff python3-aiohttp python3-bs4 python3-boto3 python3-httplib2  openssh-client curl ca-certificates jq unzip && \
    apt clean && \
    rm -rf /var/lib/apt/lists/


RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip

ARG DST_SCRIPT_PATH="/var/tmp/external_data_generator"
ARG SRC_SCRIPT_PATH="external_data_generator"
ARG SCRIPT_NAME="main.py"


COPY "${SRC_SCRIPT_PATH}/*.py" "${DST_SCRIPT_PATH}/"
COPY "${SRC_SCRIPT_PATH}/*.sh" "${DST_SCRIPT_PATH}/"

WORKDIR "${DST_SCRIPT_PATH}"

RUN chmod +x "${DST_SCRIPT_PATH}/${SCRIPT_NAME}"