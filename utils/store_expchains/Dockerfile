FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends awscli git openssh-client curl ruby3.2 wget jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/

ARG DST_SCRIPT_PATH="/var/tmp/store_expchains"

ARG STORE_SCRIPT="store_expchains.sh"
ARG UPDATE_SCRIPT="update_expchains.sh"
ARG UPLOAD_SCRIPT="store_expchains_to_sourcedata.sh"

COPY "$STORE_SCRIPT" "${DST_SCRIPT_PATH}/"
COPY "$UPDATE_SCRIPT" "${DST_SCRIPT_PATH}/"
COPY "$UPLOAD_SCRIPT" "${DST_SCRIPT_PATH}/"

RUN chmod +x "${DST_SCRIPT_PATH}/$STORE_SCRIPT" && \
    chmod +x "${DST_SCRIPT_PATH}/$UPDATE_SCRIPT" && \
    chmod +x "${DST_SCRIPT_PATH}/$UPLOAD_SCRIPT"

WORKDIR "${DST_SCRIPT_PATH}"