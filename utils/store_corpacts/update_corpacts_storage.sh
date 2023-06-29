#!/bin/bash
set -e

EXPCHAINS_REPO="git@xgit.tradingview.com:idc/idc-expchains.git"

if [ "$1" == "" ]; then
	echo "Please specify expchains branch"
	exit -1
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
FILE="${EXP_CHAINS_DIR}/dictionaries/CorpActs.tab"

tmpfile=$(mktemp /tmp/corpacts.XXXXXX)


URLS=("https://esignalreport.com/update/CorpActs.tab" "http://fs2.esignal.com/CorpActs.tab")

for url in "${URLS[@]}"; do
  curl -s --compressed --retry 3 --max-time 480 -o "${tmpfile}" --url "$url" && break
done

mv "${tmpfile}" "${FILE}"
FILE_SIZE=$(stat --printf '%s' "${FILE}")

if [ "$FILE_SIZE" -lt "400000" ]; then
    	echo "ERROR: Resulting file ${FILE} is too small ${FILE_SIZE}"
    	exit 1
fi

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/CorpActs.tab"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit CorpActs.tab"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd

