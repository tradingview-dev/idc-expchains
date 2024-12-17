FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install bs4 requests

COPY update_finra_data.py /finra_data/
COPY update_finra_data.sh /finra_data/

WORKDIR /finra_data

RUN chmod +x /finra_data/update_finra_data.py && \
    chmod +x /finra_data/update_finra_data.sh