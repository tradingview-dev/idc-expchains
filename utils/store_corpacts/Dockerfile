FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends ruby-dev build-essential git openssh-client curl wget unzip && \
    cd /bin && \
    wget -q -O jq "https://github.com/jqlang/jq/releases/download/jq-1.5/jq-linux64" && \
    chmod 755 jq

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip

COPY update_corpacts_storage.sh /store_corpacts/

RUN chmod +x /store_corpacts/update_corpacts_storage.sh

WORKDIR /store_corpacts