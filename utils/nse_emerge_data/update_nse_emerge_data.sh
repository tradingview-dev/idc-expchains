#!/bin/bash
set -e

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

EXPCHAINS_REPO="git@git.xtools.tv:idc/idc-expchains.git"

if [ "$1" == "" ]; then
	echo "Please specify expchains branch"
	exit 1
fi

EXPCHAINS_BRANCH="$1"

if [ "$EXPCHAINS_BRANCH" == "staging" ]; then
	echo "Upload files to staging"
else
	echo "WARNING: Files will be uploaded to production storage"
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

curl 'https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv' \
  --compressed -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0' > "$SCRIPTPATH/nse_raw_listing.csv"

python3 "$SCRIPTPATH/nse_emerge_data.py" "$SCRIPTPATH/nse_raw_listing.csv" "$SCRIPTPATH/nse_sme_listing.csv"

FILE1="${SCRIPTPATH}/nse_sme_listing.csv"

FILE_SIZE1=$(stat --printf '%s' "${FILE1}")

if [ "$FILE_SIZE1" -lt "2500" ]; then
    echo "ERROR: Resulting files are too small"
    exit 1
fi

mv "${FILE1}" "${EXP_CHAINS_DIR}/dictionaries/"

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/nse_sme_lising.csv"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit nyse data"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
