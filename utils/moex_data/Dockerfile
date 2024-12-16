ARG PATH_TO_LIB="/var/tmp/idc-expchains/utils/lib"

FROM alpine AS othersource
ARG PATH_TO_LIB
COPY lib "$PATH_TO_LIB"

FROM ubuntu:24.04
ARG PATH_TO_LIB

RUN apt update && \
    apt install -y --no-install-recommends python3 python3-pip git python3-git python3-requests openssh-client curl ca-certificates jq && \
    apt clean && \
    rm -rf /var/lib/apt/lists/

ARG DST_PATH_TO_SCRIPT="/var/tmp/moex_data"
ARG SRC_PATH_TO_SCRIPT="moex_data"
ARG SCRIPT_NAME="update_moex_data.py"

ARG DST_PATH_TO_LIB="/var/tmp/moex_data/utils/lib"

COPY --from=othersource "$PATH_TO_LIB" "${DST_PATH_TO_LIB}/"
COPY "${SRC_PATH_TO_SCRIPT}/${SCRIPT_NAME}" "${DST_PATH_TO_SCRIPT}/"

WORKDIR "${DST_PATH_TO_SCRIPT}"

RUN chmod +x "${DST_PATH_TO_SCRIPT}/${SCRIPT_NAME}"