FROM ubuntu:24.04

RUN apt update && \
    apt install -y --no-install-recommends python3 python3-pip git python3-git python3-requests openssh-client curl ca-certificates jq && \
    apt clean && \
    rm -rf /var/lib/apt/lists/

ARG PATH_TO_SCRIPT="/var/tmp/moex_data"
ARG SCRIPT_NAME="update_moex_data.py"

ARG PATH_TO_LIB="/var/tmp/moex_data/utils/lib"

COPY --from=othersource "lib" "${PATH_TO_LIB}/"
COPY "$SCRIPT_NAME" "${PATH_TO_SCRIPT}/"

WORKDIR "${PATH_TO_SCRIPT}"

RUN chmod +x "${PATH_TO_SCRIPT}/${SCRIPT_NAME}"