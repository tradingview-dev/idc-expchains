FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends ruby-dev build-essential git openssh-client curl ruby2.7 && \
    gem install typhoeus

COPY otc_data.rb /otc_data/
COPY update_otc_data.sh /otc_data/

RUN chmod +x /otc_data/otc_data.rb && \
    chmod +x /otc_data/update_otc_data.sh

WORKDIR /otc_data