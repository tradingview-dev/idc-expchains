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

python3 "$SCRIPTPATH/lang_and_shwartz_data.py"

FILE1="${SCRIPTPATH}/LS.csv"
FILE2="${SCRIPTPATH}/LSX.csv"

FILE_SIZE1=$(stat --printf '%s' "${FILE1}")
FILE_SIZE2=$(stat --printf '%s' "${FILE2}")

if ["$FILE_SIZE1" -lt "1000" || "$FILE_SIZE2" -lt "1000" ]; then
    echo "ERROR: One or both resulting files are too small"
    exit 1
fi

mv "${FILE1}" "${EXP_CHAINS_DIR}/dictionaries/"
mv "${FILE2}" "${EXP_CHAINS_DIR}/dictionaries/"

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/${FILE1}"
git add "dictionaries/${FILE2}"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit lang_and_shwartz_data data"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
