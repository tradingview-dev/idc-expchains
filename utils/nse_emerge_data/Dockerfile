FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip curl

COPY nse_emerge_data.py /nse_emerge_data/
COPY update_nse_emerge_data.sh /nse_emerge_data/

WORKDIR /nse_emerge_data

RUN chmod +x /nse_emerge_data/nse_emerge_data.py && \
    chmod +x /nse_emerge_data/update_nse_emerge_data.sh