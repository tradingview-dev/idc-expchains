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
EXCHANGE="$2"

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

python3 "$SCRIPTPATH/canadian_data.py"


FILE="canadian_descriptions.json"

FILE_PATH="${SCRIPTPATH}/${FILE}"

FILE_SIZE=$(stat --printf '%s' "${FILE}")

#if [ "$FILE_SIZE" -lt "1000" ]; then
#    echo "ERROR: One or both resulting files are too small"
#    exit 1
#fi

# cat "${FILE_PATH}" | head

mv "${FILE_PATH}" "${EXP_CHAINS_DIR}/dictionaries/"

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/${FILE}"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit canadian_data data"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
