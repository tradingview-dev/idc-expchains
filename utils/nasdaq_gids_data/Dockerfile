FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install openpyxl

COPY nasdaq_gids_data.py /nasdaq_gids_data/
COPY update_nasdaq_gids_data.sh /nasdaq_gids_data/

WORKDIR /nasdaq_gids_data

RUN chmod +x /nasdaq_gids_data/nasdaq_gids_data.py && \
    chmod +x /nasdaq_gids_data/update_nasdaq_gids_data.sh