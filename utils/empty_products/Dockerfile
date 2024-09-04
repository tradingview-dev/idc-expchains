FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y git openssh-client python3 python3-pip

RUN pip3 install pandas

COPY empty_products.py /empty_products/
COPY empty_products.sh /empty_products/

WORKDIR /empty_products

RUN chmod +x /empty_products/empty_products.py && \
    chmod +x /empty_products/empty_products.sh