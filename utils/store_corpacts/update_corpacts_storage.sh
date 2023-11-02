#!/bin/bash
set -e

EXPCHAINS_REPO="git@git.xtools.tv:idc/idc-expchains.git"

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
CORPACTS_FILE="${EXP_CHAINS_DIR}/dictionaries/CorpActs.tab"
LASTCORPACTS_FILE="${EXP_CHAINS_DIR}/dictionaries/LastCorpActs.tab"

TMP_CORPACTS_FILE=$(mktemp /tmp/corpacts.XXXXXX)
TMP_LASTCORPACTS_FILE=$(mktemp /tmp/lastcorpacts.XXXXXX)


URLS=("https://esignalreport.com/update/CorpActs.tab" "http://fs2.esignal.com/CorpActs.tab")

for url in "${URLS[@]}"; do
  curl -s --compressed --retry 3 --max-time 480 -o "${TMP_CORPACTS_FILE}" --url "$url" && break
done

echo "Generating LastCorpActs.tab from CorpActs.tab..."
LASTCORPACTS_SCRIPT="${EXP_CHAINS_DIR}/bin/lastcorpacts.rb"
ruby "${LASTCORPACTS_SCRIPT}" -f "${TMP_CORPACTS_FILE}" > "${TMP_LASTCORPACTS_FILE}"
LINES=$(wc -l <"${TMP_LASTCORPACTS_FILE}")
echo "Completed. Generated ${LINES} line(s)"

mv "${TMP_CORPACTS_FILE}" "${CORPACTS_FILE}"
mv "${TMP_LASTCORPACTS_FILE}" "${LASTCORPACTS_FILE}"

FILE_SIZE=$(stat --printf '%s' "${CORPACTS_FILE}")

if [ "$FILE_SIZE" -lt "400000" ]; then
    	echo "ERROR: Resulting file ${CORPACTS_FILE} is too small ${FILE_SIZE}"
    	exit 1
fi

pushd "$EXP_CHAINS_DIR"

git add "dictionaries/CorpActs.tab"
git add "dictionaries/LastCorpActs.tab"

if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit CorpActs.tab and LastCorpActs.tab"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd

