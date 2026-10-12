FROM python:3.12-alpine

RUN apk add --no-cache bash git openssh-client curl ca-certificates jq unzip aws-cli && \
    update-ca-certificates

ARG DST_DIR="/var/tmp/cmc_data"

COPY cmc_properties.py "$DST_DIR"/

WORKDIR "$DST_DIR"/