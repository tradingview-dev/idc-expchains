FROM ubuntu:24.04
ARG PATH_TO_LIB

RUN apt update && \
    apt install -y --no-install-recommends python3 python3-pip git python3-git python3-requests openssh-client curl ca-certificates jq && \
    apt clean && \
    rm -rf /var/lib/apt/lists/

ARG DST_SCRIPT_PATH="/var/tmp/moex_data"
ARG SRC_SCRIPT_PATH="moex_data"
ARG SCRIPT_NAME="update_moex_data.py"

ARG DST_LIB_PATH="/var/tmp/moex_data/utils/lib"

COPY "lib" "${DST_LIB_PATH}/"
COPY "${SRC_SCRIPT_PATH}/${SCRIPT_NAME}" "${DST_SCRIPT_PATH}/"

WORKDIR "${DST_SCRIPT_PATH}"

RUN chmod +x "${DST_SCRIPT_PATH}/${SCRIPT_NAME}"