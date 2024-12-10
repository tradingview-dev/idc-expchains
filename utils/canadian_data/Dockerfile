FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install bs4 requests

COPY update_canadian_data.py /canadian_data/
COPY update_canadian_data.sh /canadian_data/

WORKDIR /canadian_data

RUN chmod +x /canadian_data/update_canadian_data.py && \
    chmod +x /canadian_data/update_canadian_data.sh