#!/bin/bash -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

IDC_HOST="$1"
IDC_TVC_HOST="$2"
EXPCHAINS_BRANCH="$3"

SI_GROUPS=$(curl "$IDC_HOST/meta/info.json" | jq -r  '.groups | keys | .[]' | grep '_futures$')

SYMBOLINFO_DIR="$DIR/symbolinfo"
mkdir -p "$SYMBOLINFO_DIR"
while read -r SI_GROUP; do
    echo "Getting $SI_GROUP"
    curl "$IDC_HOST/symbol_info?group=$SI_GROUP" > "$SYMBOLINFO_DIR/$SI_GROUP.json"
done <<< "$SI_GROUPS"

SI_TVC_GROUPS="$(curl "$IDC_TVC_HOST/meta/info.json" | jq -r  '.groups | keys | .[]' | grep '_futures$')"
while read -r SI_TVC_GROUP; do
    echo "Getting $SI_TVC_GROUP"
    curl "$IDC_TVC_HOST/symbol_info?group=$SI_TVC_GROUP" > "$SYMBOLINFO_DIR/$SI_TVC_GROUP.json"
done <<< "$SI_TVC_GROUPS"

SI_OTHER_GROUPS=(moex_iss_futures nymex_cfd_futures_internal)
for GROUP in ${SI_OTHER_GROUPS[@]}; do
    echo "Getting $GROUP"
    curl "$IDC_HOST/symbol_info?group=$GROUP" > "$SYMBOLINFO_DIR/$GROUP.json"
done <<< $SI_OTHER_GROUPS


EXPCHAINS_REPO="git@xgit.tradingview.com:tv/idc-expchains.git"

if [ -z "$EXPCHAINS_BRANCH" ]; then
    EXPCHAINS_BRANCH=staging
	echo "EXPCHAINS_BRANCH not defined, use staging"
fi

if [ "$EXPCHAINS_BRANCH" == "staging" ]; then
	echo "Upload files to staging"
else
	echo "WARNING: Files will be uploaded to production storage"
fi

LIST=`find ${SYMBOLINFO_DIR} -name "*_futures.json" -printf "%f "`

if [ -z "$LIST" ]; then
    echo "No futures groups to update expchains"
    exit 0
fi

EXP_CHAINS_DIR="$DIR/.."

mkdir -p "${EXP_CHAINS_DIR}/expchains/"
for file in $LIST; do
    expchains_file="${file%.json}.csv"
    echo "Generate expchains ${expchains_file}"
    ruby "${EXP_CHAINS_DIR}/bin/expchains.rb" generate \
        -s "${SYMBOLINFO_DIR}/$file" \
        -e "${EXP_CHAINS_DIR}/expchains/$expchains_file" \
        -m "${EXP_CHAINS_DIR}/expchains/$expchains_file"
done

pushd "$EXP_CHAINS_DIR"
git add "expchains/*"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
