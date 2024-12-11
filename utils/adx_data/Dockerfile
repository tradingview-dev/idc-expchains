FROM ubuntu:24.04

RUN apt update && \
    apt install -y --no-install-recommends git openssh-client curl ca-certificates jq && \
    apt clean && \
    rm -rf /var/lib/apt/lists/

ARG PATH_TO_SCRIPT="/var/tmp/adx_data"

COPY update_adx_data.sh "${PATH_TO_SCRIPT}/"

WORKDIR "${PATH_TO_SCRIPT}"

RUN chmod +x "${PATH_TO_SCRIPT}/update_adx_data.sh"
