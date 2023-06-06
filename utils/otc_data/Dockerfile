FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends ruby-dev build-essential git openssh-client curl ruby2.7 && \
    gem install typhoeus &&\
    cd /bin && \
    wget -O jq "https://github.com/jqlang/jq/releases/download/jq-1.5/jq-linux64" && \
    chmod 755 jq

COPY otc_data.rb /otc_data/
COPY update_otc_data.sh /otc_data/

RUN chmod +x /otc_data/otc_data.rb && \
    chmod +x /otc_data/update_otc_data.sh

WORKDIR /otc_data