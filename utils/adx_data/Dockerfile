FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends git openssh-client curl jq

ARG PATH_TO_SCRIPT=/var/tmp/expchains/utils/adx_data

COPY update_adx_data.sh ${PATH_TO_SCRIPT}/

WORKDIR ${PATH_TO_SCRIPT}/

RUN chmod +x ${PATH_TO_SCRIPT}/update_adx_data.sh
