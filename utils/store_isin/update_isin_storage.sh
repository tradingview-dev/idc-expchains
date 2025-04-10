#!/bin/bash -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

ISIN_REPO="git@git.xtools.tv:idc/idc-expchains.git"

if [ "$1" == "" ]; then
	echo "Please specify data source production or staging"
	exit 1
fi

if [ "$2" == "" ]; then
	echo "Please specify target branch master or staging"
	exit 1
fi


SOURCE="$1"
ISIN_BRANCH="$2"
INVALIDATE_CACHE="$3"

URL_PREFIX=""
MERGE_METHOD=""

if [ "$SOURCE" == "production" ]; then
    echo "WARN: isin data will be pulled from production"
    URL_PREFIX="http://idc-nyc2.tradingview.com:8073"
    MERGE_METHOD="--append"
else
    URL_PREFIX="http://idc-staging.xstaging.tv:8075"
    MERGE_METHOD="--overwrite"
fi

ISIN_DIR="./idc-expchains"

if [ ! -d "$ISIN_DIR" ]; then
    echo "Clone branch ${ISIN_BRANCH} from repo ${ISIN_REPO}"
    git clone --depth 1 --single-branch -b $ISIN_BRANCH "$ISIN_REPO" "$ISIN_DIR"
else
    pushd "$ISIN_DIR"
    echo "Update branch ${ISIN_BRANCH} from repo ${ISIN_REPO}"
    git fetch
    git checkout $ISIN_BRANCH
    git pull origin $ISIN_BRANCH
    popd
fi

if [[ "$INVALIDATE_CACHE" == "invalidate" ]]; then
  "${DIR}/isin_updater.rb" invalidate \
      -U "$URL_PREFIX"
fi

mkdir -p "${ISIN_DIR}/isin_new/"
"${DIR}/isin_updater.rb" download \
    -D "${ISIN_DIR}/isin_new" \
    -U "$URL_PREFIX"

pushd "${ISIN_DIR}"
git pull origin "$ISIN_BRANCH"
popd

mkdir -p "${ISIN_DIR}/isin/"
"${DIR}/isin_updater.rb" merge \
    --new-data "${ISIN_DIR}/isin_new" \
    --prev-data "${ISIN_DIR}/isin" \
    --target-data "${ISIN_DIR}/isin" \
    $MERGE_METHOD

pushd "${ISIN_DIR}"
rm -rf "isin_new/"

git add "isin/*"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $ISIN_BRANCH"
else
    echo "Update isin in $ISIN_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    CHANGED_FILES=$(git diff --name-only --cached | tr '\n' ' ')
    git commit -m "Autocommit $CHANGED_FILES"
    git push origin "$ISIN_BRANCH"
fi
popd
