FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client curl


COPY update_shanghai_data.sh /shanghai_data/

WORKDIR /shanghai_data

RUN chmod +x /shanghai_data/update_shanghai_data.sh
