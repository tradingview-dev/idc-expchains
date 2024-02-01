#!/bin/bash
set -e

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

EXPCHAINS_REPO="git@git.xtools.tv:idc/idc-expchains.git"

if [ "$1" == "" ]; then
	echo "Please specify expchains branch"
	exit -1
fi

STAGING_BRANCH="idc-1528-add-parser-for-isins-and-descriptions-biva"
MASTER_BRANCH="staging"

EXP_CHAINS_DIR="./idc-expchains"

if [ ! -d "$EXP_CHAINS_DIR" ]; then
    echo "Clone branch ${STAGING_BRANCH} from repo ${EXPCHAINS_REPO}"
    git clone --depth 1 --single-branch -b $STAGING_BRANCH "$EXPCHAINS_REPO" "$EXP_CHAINS_DIR"
else
    pushd "$EXP_CHAINS_DIR"
    echo "Update branch ${STAGING_BRANCH} from repo ${EXPCHAINS_REPO}"
    git fetch
    git checkout $STAGING_BRANCH
    git pull origin $STAGING_BRANCH
    popd
fi

mkdir -p "${EXP_CHAINS_DIR}/dictionaries/"

python3 "$SCRIPTPATH/biva_data.py"

FILE1="${SCRIPTPATH}/biva_data.csv"

FILE_SIZE1=$(stat --printf '%s' "${FILE1}")

if [ "$FILE_SIZE1" -lt "1000" ]; then
    echo "ERROR: One or both resulting files are too small"
    exit 1
fi

mv "${FILE1}" "${EXP_CHAINS_DIR}/dictionaries/"

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/biva_data.csv"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $STAGING_BRANCH"
else
    echo "Update expchains in $STAGING_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit biva data"
    git push origin "$STAGING_BRANCH"
fi
git checkout $MASTER_BRANCH
git pull origin $MASTER_BRANCH
cp "${EXP_CHAINS_DIR}/dictionaries/biva_data.csv" .
git add "biva_data.csv"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $MASTER_BRANCH"
else
    echo "Update expchains in $MASTER_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit biva data to master"
    git push origin "$MASTER_BRANCH"
popd
