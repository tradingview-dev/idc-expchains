#!/bin/bash
set -ex

# The color codes are left just for a reminder
BOLD_RED='\033[1;31m'
BOLD_GREEN='\033[1;32m'
BOLD_YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

function log_info() {
  local MESSAGE=$1
  printf "${BOLD}%s${NC}\n" "$MESSAGE"
}

function log_success() {
  local MESSAGE=$1
  printf "${BOLD_GREEN}%s${NC}\n" "$MESSAGE"
}

function log_warn() {
  local MESSAGE=$1
  printf "${BOLD_YELLOW}%s${NC}\n" "$MESSAGE"
}

function log_error() {
  local MESSAGE=$1
  printf "${BOLD_RED}ERROR: %s${NC}\n" "$MESSAGE"
}

EXPCHAINS_REPO="git@git.xtools.tv:idc/idc-expchains.git"

if [ "$1" == "" ]; then
	log_info "Please specify expchains branch"
	exit 1
fi

EXPCHAINS_BRANCH="$1"

if [ "$EXPCHAINS_BRANCH" == "staging" ]; then
	log_info "Upload files to staging"
else
	log_warn "WARNING: Files will be uploaded to production storage"
fi

EXP_CHAINS_DIR="./idc-expchains"

if [ ! -d "$EXP_CHAINS_DIR" ]; then
    log_info "Clone branch ${EXPCHAINS_BRANCH} from repo ${EXPCHAINS_REPO}"
    git clone --depth 1 --single-branch -b "$EXPCHAINS_BRANCH" "$EXPCHAINS_REPO" "$EXP_CHAINS_DIR"
else
    pushd "$EXP_CHAINS_DIR"
    log_info "Update branch ${EXPCHAINS_BRANCH} from repo ${EXPCHAINS_REPO}"
    git fetch
    git checkout "$EXPCHAINS_BRANCH"
    git pull origin "$EXPCHAINS_BRANCH"
    popd
fi

mkdir -p "${EXP_CHAINS_DIR}/dictionaries/"

REQUEST_URL="https://adxservices.adx.ae/WebServices/DataServices/api/web/assets"
REQUEST_HEADERS=( -H "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0" \
               -H "Accept: application/json, text/javascript, */*; q=0.01" \
               -H "Accept-Language: en,ru;q=0.7,en-US;q=0.3" --compressed \
               -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
               -H "Origin: https://www.adx.ae' -H 'DNT: 1" \
               -H "Connection: keep-alive" \
               -H "Referer: https://www.adx.ae/" \
               -H "Pragma: no-cache" \
               -H "Cache-Control: no-cache" )

curl -s "$REQUEST_URL" "${REQUEST_HEADERS[@]}" --data-raw "Status=L&Boad=REGULAR&Del=0" | jq . -S > "${EXP_CHAINS_DIR}/dictionaries/adx_data_regular.json"
curl -s "$REQUEST_URL" "${REQUEST_HEADERS[@]}" --data-raw "Status=L&Boad=FUND&Del=0" | jq . -S > "${EXP_CHAINS_DIR}/dictionaries/adx_data_fund.json"

if [ ! -s "${EXP_CHAINS_DIR}/dictionaries/adx_data_regular.json" ] && [ ! -s "${EXP_CHAINS_DIR}/dictionaries/adx_data_fund.json" ]; then
    rm -f "${EXP_CHAINS_DIR}/dictionaries/adx_data_regular.json"
    rm -f "${EXP_CHAINS_DIR}/dictionaries/adx_data_fund.json"
    exit 1
fi

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/adx_data_regular.json"
git add "dictionaries/adx_data_fund.json"
if [ "$(git status -s)" = "" ]; then
    log_success "No changes in $EXPCHAINS_BRANCH"
else
    log_info "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit ADX descriptions"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
