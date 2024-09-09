#!/bin/bash
set -e

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

EXPCHAINS_REPO="git@git.xtools.tv:idc/idc-expchains.git"

if [ "$1" == "" ]; then
	echo "Please specify expchains branch"
	exit -1
fi

SYMLIST_ENVIRONMENT="$1"
EXPCHAINS_BRANCH="$1"

if [ "$SYMLIST_ENVIRONMENT" == "stable" ]; then
    EXPCHAINS_BRANCH="master"
    echo "Upload files to stable"
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

cp "${EXP_CHAINS_DIR}/dictionaries/cik_codes.json" "$SCRIPTPATH/cik_codes.json"
python3 "$SCRIPTPATH/symlistfeed_cik_delivery.py" --provider "dataops" --filename "cik_codes.json" --ruleset-filename "cik_codes_v1.json" --environment "$SYMLIST_ENVIRONMENT"
