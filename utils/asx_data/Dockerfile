FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install bs4 requests

COPY update_asx_data.py /asx_data/
COPY update_asx_data.sh /asx_data/

WORKDIR /asx_data

RUN chmod +x /asx_data/update_asx_data.py && \
    chmod +x /asx_data/update_asx_data.sh