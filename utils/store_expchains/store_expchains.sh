#!/bin/bash -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

IDC_HOST="$1"
IDC_TVC_HOST="$2"
EXPCHAINS_BRANCH="$3"


SYMBOLINFO_DIR="$DIR/symbolinfo"
mkdir -p "$SYMBOLINFO_DIR"
echo "Getting groups from $IDC_HOST"
SI_GROUPS=$(curl -s "$IDC_HOST/meta/info.json" | jq -r  '.groups | keys | .[]' | grep '_futures$')
while read -r SI_GROUP; do
    echo "Getting $SI_GROUP"
    curl -s "$IDC_HOST/symbol_info?group=$SI_GROUP" | jq . > "$SYMBOLINFO_DIR/$SI_GROUP.json"
done <<< "$SI_GROUPS"

echo "Getting groups from $IDC_TVC_HOST"
SI_TVC_GROUPS="$(curl -s "$IDC_TVC_HOST/meta/info.json" | jq -r  '.groups | keys | .[]' | grep '_futures$' || true)"
while read -r SI_TVC_GROUP; do
    if [[ -z "$SI_TVC_GROUP" ]]; then
        continue
    fi
    echo "Getting $SI_TVC_GROUP"
    curl -s "$IDC_TVC_HOST/symbol_info?group=$SI_TVC_GROUP" | jq . > "$SYMBOLINFO_DIR/$SI_TVC_GROUP.json"
done <<< "$SI_TVC_GROUPS"

echo "Getting manual groups"
SI_OTHER_GROUPS=(
  "alor_rest_futures"
  "six_cme_globex_futures"
  "six_cme_globex_mini_futures"
  "six_cme_globex_night_futures"
  "six_cme_globex_night_mini_futures"
  "six_cbot_equity_futures"
  "six_cbot_commodity_futures"
  "six_cbot_financial_futures"
  "six_cbot_equity_mini_futures"
  "six_cbot_commodity_mini_futures"
  "six_cbot_financial_mini_futures"
  "six_nymex_emissions_futures"
  "six_nymex_globex_a_futures"
  "six_nymex_globex_b_futures"
  "six_nymex_globex_mini_futures"
  "six_istanbul_futures"
  )
for GROUP in "${SI_OTHER_GROUPS[@]}"; do
    echo "Getting $GROUP"
    curl -s "$IDC_HOST/symbol_info?group=$GROUP" | jq . > "$SYMBOLINFO_DIR/$GROUP.json"
done <<< "${SI_OTHER_GROUPS[@]}"

echo "Running update_expchains.sh"
"${DIR}/update_expchains.sh" "$SYMBOLINFO_DIR" "$EXPCHAINS_BRANCH"
