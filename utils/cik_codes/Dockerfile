FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install openpyxl
RUN pip3 install ijson
RUN pip3 install requests

COPY cik_codes.py /cik_codes/
COPY update_cik_codes.sh /cik_codes/
COPY symlistfeed_cik_delivery.py /cik_codes/

WORKDIR /cik_codes

RUN chmod +x /cik_codes/cik_codes.py && \
    chmod +x /cik_codes/update_cik_codes.sh

RUN chmod +x /cik_codes/symlistfeed_cik_delivery.py