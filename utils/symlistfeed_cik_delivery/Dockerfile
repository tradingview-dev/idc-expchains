FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install openpyxl

COPY ../../dictionaries/cik_codes.json /symlistfeed_cik_delivery/
COPY symlistfeed_cik_delivery.sh /symlistfeed_cik_delivery/
COPY symlistfeed_cik_delivery.py /symlistfeed_cik_delivery/

WORKDIR /symlistfeed_cik_delivery

RUN chmod +x /symlistfeed_cik_delivery/symlistfeed_cik_delivery.py && \
    chmod +x /symlistfeed_cik_delivery/symlistfeed_cik_delivery.sh