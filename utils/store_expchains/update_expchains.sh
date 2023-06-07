#!/bin/bash -e

EXPCHAINS_REPO="git@xgit.tradingview.com:tv/idc-expchains.git"

if [ "$1" == "" ]; then
	echo "Please specify symbolinfo dir"
	exit 1
fi

SYMBOLINFO_DIR="$1"
EXPCHAINS_BRANCH="$2"

if [ -z "$EXPCHAINS_BRANCH" ]; then
    EXPCHAINS_BRANCH=staging
	echo "EXPCHAINS_BRANCH not defined, use staging"
fi

if [ "$EXPCHAINS_BRANCH" == "staging" ]; then
	echo "Upload files to staging"
else
	echo "WARNING: Files will be uploaded to production storage"
fi

LIST=$(find "${SYMBOLINFO_DIR}" -name '*_futures.json' -printf '%f ')

if [ -z "$LIST" ]; then
    echo "No futures groups to update expchains"
    exit 0
fi

EXP_CHAINS_DIR="./idc-expchains"

if [ ! -d "$EXP_CHAINS_DIR" ]; then
    echo "Clone branch ${EXPCHAINS_BRANCH} from repo ${EXPCHAINS_REPO}"
    git clone -b $EXPCHAINS_BRANCH "$EXPCHAINS_REPO" "$EXP_CHAINS_DIR"
else
    pushd "$EXP_CHAINS_DIR"
    echo "Update branch ${EXPCHAINS_BRANCH} from repo ${EXPCHAINS_REPO}"
    git fetch
    git checkout $EXPCHAINS_BRANCH
    git pull origin $EXPCHAINS_BRANCH
    popd
fi

mkdir -p "${EXP_CHAINS_DIR}/expchains/"
for file in $LIST; do
    expchains_file="${file%.json}.csv"
    echo "Generate expchains ${expchains_file}"
    ruby "${EXP_CHAINS_DIR}/bin/expchains.rb" generate \
        -s "${SYMBOLINFO_DIR}/$file" \
        -e "${EXP_CHAINS_DIR}/expchains/$expchains_file" \
        -m "${EXP_CHAINS_DIR}/expchains/$expchains_file"
done

pushd "$EXP_CHAINS_DIR"
git add "expchains/*"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
