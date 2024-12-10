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
EXCHANGE="$2"
FORCE="$3"

if [ "$EXPCHAINS_BRANCH" == "staging" ]; then
	echo "Upload files to staging"
else
	echo "WARNING: Files will be uploaded to production storage"
fi

python3 "$SCRIPTPATH/lang_and_shwarz_data.py" -exchange "$EXCHANGE"

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

if [[ "$EXCHANGE" == "x" ]]; then
  FILE="LSX.csv"
else
  FILE="LS.csv"
fi

FILE_PATH="${SCRIPTPATH}/${FILE}"

FILE_LINES=$(wc -l < "${FILE}")
PREV_FILE_LINES=$(wc -l < "${EXP_CHAINS_DIR}/dictionaries/${FILE}")
LINES_DELTA=$((FILE_LINES-PREV_FILE_LINES))

if [ "$LINES_DELTA" -lt "-500" ]; then
  if [ "$FORCE" == "force" ]; then
    echo "ERROR: lines delta between new and old versions of ${FILE} is ${LINES_DELTA}, too many lines removed, but update forced"
  else
    echo "ERROR: lines delta between new and old versions of ${FILE} is ${LINES_DELTA}, too many lines removed"
    exit 1
  fi
fi

mv "${FILE_PATH}" "${EXP_CHAINS_DIR}/dictionaries/"

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/${FILE}"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit lang_and_shwarz_data data"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
