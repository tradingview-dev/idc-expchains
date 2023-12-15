FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip

RUN pip3 install openpyxl

COPY nyse_data.py /nyse_data/
COPY update_nyse_data.sh /nyse_data/

WORKDIR /nyse_data

RUN chmod +x /nyse_data/nyse_data.py && \
    chmod +x /nyse_data/update_nyse_data.sh