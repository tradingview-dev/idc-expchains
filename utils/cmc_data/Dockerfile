FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends ruby-dev build-essential git openssh-client curl ruby2.7 wget unzip && \
    gem install ffi -v 1.16.3 && \
    gem install typhoeus && \
    cd /bin && \
    wget -O jq "https://github.com/jqlang/jq/releases/download/jq-1.5/jq-linux64" && \
    chmod 755 jq

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip \

COPY cmc_properties.rb /cmc_data/
COPY update_defi_typespec.sh /cmc_data/

RUN chmod +x /cmc_data/cmc_properties.rb && \
    chmod +x /cmc_data/update_defi_typespec.sh

WORKDIR /cmc_data