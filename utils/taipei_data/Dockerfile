FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install bs4 requests

COPY update_taipei_data.py /taipei_data/
COPY update_taipei_data.sh /taipei_data/

WORKDIR /taipei_data

RUN chmod +x /taipei_data/update_taipei_data.py && \
    chmod +x /taipei_data/update_taipei_data.sh