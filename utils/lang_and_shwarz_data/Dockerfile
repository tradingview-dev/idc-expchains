FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install bs4 requests

COPY lang_and_shwartz_data.py /lang_and_shwartz_data/
COPY update_lang_and_shwartz_data.sh /lang_and_shwartz_data/

WORKDIR /lang_and_shwartz_data

RUN chmod +x /lang_and_shwartz_data/lang_and_shwartz_data.py && \
    chmod +x /lang_and_shwartz_data/update_lang_and_shwartz_data.sh