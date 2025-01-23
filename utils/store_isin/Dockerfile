FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential unzip git openssh-client curl ruby3.2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/ && \
    gem install ffi -v 1.16.3 && \
    gem install typhoeus

RUN curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip -q awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip

ARG DST_SCRIPT_PATH="/var/tmp/store_isin"

ARG UPDATER_SCRIPT="isin_updater.rb"
ARG UPDATE_SCRIPT="update_isin_storage.sh"
ARG UPLOAD_SCRIPT="store_isin_to_sourcedata.sh"

COPY "$UPDATER_SCRIPT" "${DST_SCRIPT_PATH}/"
COPY "$UPDATE_SCRIPT" "${DST_SCRIPT_PATH}/"
COPY "$UPLOAD_SCRIPT" "${DST_SCRIPT_PATH}/"

RUN chmod +x "${DST_SCRIPT_PATH}/$UPDATER_SCRIPT" && \
    chmod +x "${DST_SCRIPT_PATH}/$UPDATE_SCRIPT" && \
    chmod +x "${DST_SCRIPT_PATH}/$UPLOAD_SCRIPT"

WORKDIR "${DST_SCRIPT_PATH}"