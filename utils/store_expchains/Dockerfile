FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends git openssh-client curl ruby2.7 wget && \
    cd /bin && \
    wget -O jq "https://github.com/jqlang/jq/releases/download/jq-1.5/jq-linux64" && \
    chmod 755 jq

COPY store_expchains.sh /store_expchains/
COPY update_expchains.sh /store_expchains/

RUN chmod +x /store_expchains/store_expchains.sh && \
    chmod +x /store_expchains/update_expchains.sh

WORKDIR /store_expchains