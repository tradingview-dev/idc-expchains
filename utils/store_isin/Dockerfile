FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends ruby-dev build-essential git openssh-client curl ruby2.7 && \
    gem install typhoeus

COPY isin_updater.rb /store_isin/
COPY update_isin_storage.sh /store_isin/

RUN chmod +x /store_isin/isin_updater.rb && \
    chmod +x /store_isin/update_isin_storage.sh

WORKDIR /store_isin