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
for GROUP in "${SI_OTHER_GROUPS[@]}"; do
    echo "Getting $GROUP"
    curl "$IDC_HOST/symbol_info?group=$GROUP" > "$SYMBOLINFO_DIR/$GROUP.json"
done <<< "${SI_OTHER_GROUPS[@]}"

"${DIR}/update_expchains.sh" "$SYMBOLINFO_DIR" "$EXPCHAINS_BRANCH"
