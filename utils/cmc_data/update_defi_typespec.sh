#!/bin/bash
set -e

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

EXPCHAINS_REPO="git@git.xtools.tv:idc/idc-expchains.git"

if [ "$1" == "" ]; then
	echo "Please specify expchains branch"
	exit 1
fi

if [ "$CMC_ID" == "" ]; then
	echo "Please specify CMC_ID env"
	exit 1
fi

EXPCHAINS_BRANCH="$1"

if [ "$EXPCHAINS_BRANCH" == "staging" ]; then
	echo "Upload files to staging"
else
	echo "WARNING: Files will be uploaded to production storage"
fi


CURRENCIES_BUCKET="tradingview-currencies"
if [ "$EXPCHAINS_BRANCH" == "staging" ] ; then
  CURRENCIES_BUCKET="tradingview-currencies-staging"
fi

EXP_CHAINS_DIR="./idc-expchains"

if [ ! -d "$EXP_CHAINS_DIR" ]; then
    echo "Clone branch ${EXPCHAINS_BRANCH} from repo ${EXPCHAINS_REPO}"
    git clone --depth 1 --single-branch -b $EXPCHAINS_BRANCH "$EXPCHAINS_REPO" "$EXP_CHAINS_DIR"
else
    pushd "$EXP_CHAINS_DIR"
    echo "Update branch ${EXPCHAINS_BRANCH} from repo ${EXPCHAINS_REPO}"
    git fetch
    git checkout $EXPCHAINS_BRANCH
    git pull origin $EXPCHAINS_BRANCH
    popd
fi

mkdir -p "${EXP_CHAINS_DIR}/dictionaries/"
FILE="${EXP_CHAINS_DIR}/dictionaries/defi_typespec.csv"

tmpfile=$(mktemp /tmp/cmc_data.XXXXXX)

curl "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?convert=BTC&start=1&sort=market_cap&limit=5000&CMC_PRO_API_KEY=${CMC_ID}" \
	> "coinmarketcap_snapshot_1_5000.json"
curl "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?convert=BTC&start=5001&sort=market_cap&limit=5000&CMC_PRO_API_KEY=${CMC_ID}" \
	> "coinmarketcap_snapshot_5001_10000.json"
jq -s '.[0].data + .[1].data | {"data": .}' "coinmarketcap_snapshot_1_5000.json" "coinmarketcap_snapshot_5001_10000.json" \
    > "coinmarketcap_snapshot.json"

curl --compressed "s3.amazonaws.com/${CURRENCIES_BUCKET}/currencies.json" \
    > "currencies.json"

ruby cmc_properties.rb -f "coinmarketcap_snapshot.json" -c "currencies.json" -o "$tmpfile"
mv "${tmpfile}" "${FILE}"

#FILE_SIZE=$(stat --printf '%s' "${FILE}")

#if [ "$FILE_SIZE" -lt "2000000" ]; then
#    	echo "ERROR: Resulting file ${FILE} is too small ${FILE_SIZE}"
#    	exit 1
#fi

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/defi_typespec.csv"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit defi_typespec.csv"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
