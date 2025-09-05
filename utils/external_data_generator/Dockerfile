FROM python:3.12-alpine

RUN apk add --no-cache bash git openssh-client curl ca-certificates jq unzip aws-cli && \
    update-ca-certificates && \
    pip install --no-cache-dir --root-user-action=ignore pipenv

ARG DST_SCRIPT_PATH="/var/tmp/external_data_generator"
ARG SRC_SCRIPT_PATH="/utils/external_data_generator"
ARG SCRIPT_NAME="main.py"

ARG DST_LIB_PATH="/var/tmp/external_data_generator/lib"

COPY Pipfile Pipfile.lock "${DST_SCRIPT_PATH}"/
COPY "lib" "${DST_LIB_PATH}"/
COPY "${SRC_SCRIPT_PATH}"/* "${DST_SCRIPT_PATH}"/

WORKDIR "${DST_SCRIPT_PATH}"

RUN pipenv install --system --deploy

RUN chmod +x "${DST_SCRIPT_PATH}/${SCRIPT_NAME}"