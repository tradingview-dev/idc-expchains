#!/bin/bash -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

ISIN_REPO="git@git.xtools.tv:tv/idc-expchains.git"

if [ "$1" == "" ]; then
	echo "Please specify data source production or staging"
	exit 1
fi

if [ "$2" == "" ]; then
	echo "Please specify target branch master or staging"
	exit 1
fi


SOURCE="$1"
ISIN_BRANCH="$2"

URL_PREFIX=""
MERGE_METHOD=""
ADD_OPTIONS=""

if [ "$SOURCE" == "production" ]; then
    echo "WARN: isin data will be pulled from production"
    URL_PREFIX="http://idc-nyc2.tradingview.com:8073"
    MERGE_METHOD="-O"
    ADD_OPTIONS="--prod-filter"
else
    URL_PREFIX="http://idc-staging.tradingview.com:8071"
    MERGE_METHOD="-A"
fi

ISIN_DIR="./isin-store"

if [ ! -d "$ISIN_DIR" ]; then
    echo "Clone branch ${ISIN_BRANCH} from repo ${ISIN_REPO}"
    git clone -b $ISIN_BRANCH "$ISIN_REPO" "$ISIN_DIR"
else
    pushd "$ISIN_DIR"
    echo "Update branch ${ISIN_BRANCH} from repo ${ISIN_REPO}"
    git fetch
    git checkout $ISIN_BRANCH
    git pull origin $ISIN_BRANCH
    popd
fi

mkdir -p "${ISIN_DIR}/isin/"
"${DIR}/isin_updater.rb" \
    -D "${ISIN_DIR}/isin" \
    -U "$URL_PREFIX" \
    "$MERGE_METHOD" \
    $ADD_OPTIONS

pushd "${ISIN_DIR}"
git add "isin/*"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $ISIN_BRANCH"
else
    echo "Update isin in $ISIN_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit isin"
    git push origin "$ISIN_BRANCH"
fi
popd
