FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client curl


COPY update_nasdaqtrader_data.sh /nasdaqtrader_data/

WORKDIR /nasdaqtrader_data

RUN chmod +x /nasdaqtrader_data/update_nasdaqtrader_data.sh
