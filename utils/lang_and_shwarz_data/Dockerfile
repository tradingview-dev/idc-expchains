FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install bs4 requests

COPY lang_and_shwarz_data.py /lang_and_shwarz_data/
COPY update_lang_and_shwarz_data.sh /lang_and_shwarz_data/

WORKDIR /lang_and_shwarz_data

RUN chmod +x /lang_and_shwarz_data/lang_and_shwarz_data.py && \
    chmod +x /lang_and_shwarz_data/update_lang_and_shwarz_data.sh