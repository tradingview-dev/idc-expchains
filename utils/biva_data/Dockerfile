FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install aiohttp requests

COPY biva_data.py /biva_data/
COPY update_biva_data.sh /biva_data/

WORKDIR /biva_data

RUN chmod +x /biva_data/biva_data.py && \
    chmod +x /biva_data/update_biva_data.sh