FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client curl jq


COPY update_saudi_data.sh /saudi_data/

WORKDIR /saudi_data

RUN chmod +x /saudi_data/update_saudi_data.sh
