FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y git openssh-client curl jq


COPY update_adx_data.sh /adx_data/

WORKDIR /adx_data

RUN chmod +x /adx_data/update_adx_data.sh
