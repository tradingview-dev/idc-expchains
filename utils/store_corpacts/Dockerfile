FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends ruby-dev build-essential git openssh-client curl wget && \
    cd /bin && \
    wget -O jq "https://github.com/jqlang/jq/releases/download/jq-1.5/jq-linux64" && \
    chmod 755 jq

COPY update_corpacts_storage.sh /store_corpacts/

RUN chmod +x /store_corpacts/update_corpacts_storage.sh

WORKDIR /store_corpacts