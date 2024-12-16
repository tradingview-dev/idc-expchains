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

curl \
  -s \
  -H 'Referer: http://english.sse.com.cn/listed/company/' \
  'http://query.sse.com.cn/listedcompanies/companylist/downloadCompanyInfoList.do' | \
  iconv -f GB2312 -t UTF-8 | \
  sed 's/[ \t]*$//' | \
  tr ';' ',' | tr "\t" ';' | sed 's/;;/;/' | \
  sed -e 's/\s\{1,\};/;/g' -e 's/;\s\{1,\}/;/g' | \
  sed -e 's/;-/;/g' \
  > "${EXP_CHAINS_DIR}/dictionaries/sse_descriptions.csv"

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/sse_descriptions.csv"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit shanghai data"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
