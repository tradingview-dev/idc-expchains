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

CHANNEL_HOOK_IDC=$2
CHANNEL_HOOK_HUB=$3
python3 "$SCRIPTPATH/empty_products.py" --env ${EXPCHAINS_BRANCH} --idc_hook ${CHANNEL_HOOK_IDC} --hub_hook ${CHANNEL_HOOK_HUB}

FILE1="${SCRIPTPATH}/empty_products"
FILE2="${SCRIPTPATH}/empty_products_idc"
FILE3="${SCRIPTPATH}/empty_products_not_idc"

if [ ! -f "$FILE1" ]; then
    echo "All products filled!"
    exit 0
fi


echo "$(cat $FILE1)"

if [ -e "$FILE2" ]; then
    echo "Some idc products not filled"
    CHANNEL_HOOK=$2
    CHANNEL_NAME="#symbolinfo-updater-staging-idc"
    echo $(cat $FILE2)
fi

if [ -e "$FILE3" ]; then
    echo "Some non-idc products not filled"
    echo $(cat $FILE3)
fi
