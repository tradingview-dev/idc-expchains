FROM ubuntu:24.04
ARG PATH_TO_LIB

RUN apt update && \
    apt install -y --no-install-recommends python3 python3-pip git python3-git python3-requests python3-deepdiff openssh-client curl ca-certificates jq && \
    apt clean && \
    rm -rf /var/lib/apt/lists/


ARG DST_SCRIPT_PATH="/var/tmp/external_data_generator"
ARG SRC_SCRIPT_PATH="external_data_generator"
ARG SCRIPT_NAME="main.py"


COPY "${SRC_SCRIPT_PATH}/*.py" "${DST_SCRIPT_PATH}/"

WORKDIR "${DST_SCRIPT_PATH}"

RUN chmod +x "${DST_SCRIPT_PATH}/${SCRIPT_NAME}"