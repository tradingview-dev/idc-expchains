FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends ruby-dev build-essential git openssh-client curl ruby2.7 wget unzip && \
    gem install ffi -v 1.16.3 && \
    gem install typhoeus && \
    cd /bin && \
    wget -q -O jq "https://github.com/jqlang/jq/releases/download/jq-1.5/jq-linux64" && \
    chmod 755 jq

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip

COPY otc_data.rb /otc_data/
COPY update_otc_data.sh /otc_data/

RUN chmod +x /otc_data/otc_data.rb && \
    chmod +x /otc_data/update_otc_data.sh

WORKDIR /otc_data