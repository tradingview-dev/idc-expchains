#!/bin/bash
set -e

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

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

python3 "$SCRIPTPATH/cik_codes.py" --env "$EXPCHAINS_BRANCH"

FILE1="${SCRIPTPATH}/cik_codes.json"

FILE_SIZE1=$(stat --printf '%s' "${FILE1}")

if [ "$FILE_SIZE1" -lt "2500" ]; then
    echo "ERROR: One or both resulting files are too small"
    exit 1
fi

mv "${FILE1}" "${EXP_CHAINS_DIR}/dictionaries/"


SYMLIST_ENVIRONMENT="$1"

cp "${EXP_CHAINS_DIR}/dictionaries/cik_codes.json" "$SCRIPTPATH/cik_codes.json"
python3 "$SCRIPTPATH/symlistfeed_cik_delivery.py" --provider "dataops" --filename "cik_codes.json" --ruleset-filename "cik_codes_v1.json" --environment "$SYMLIST_ENVIRONMENT"