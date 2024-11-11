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
  'https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory/!ut/p/z1/lc_LCsIwEAXQb-kHSG6jiXGZLhIL9hHTas1GspKAVhHx-63uWt-zGzh3mEscaYhr_TXs_CUcW7_v9o3jWyY56Fyg0LaSMMpWST5TMVJG1n0gMs1hcmkKOmXQq5i4v_KwJetAmY0XWEKD_5bHm5H4nnd9AlOLO1EJE6DAZAheVBxceO7wAB-etP5MToe6bhDSkYyiG8La9T0!/p0/IZ7_5A602H80OOMQC0604RU6VD10F2=CZ6_5A602H80OGSTA0QFSTBN9F10I5=NJgetCompanyListByMarknetAndSectors=/' --compressed -X POST -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'X-Requested-With: XMLHttpRequest' -H 'Origin: https://www.saudiexchange.sa' -H 'Connection: keep-alive' -H 'Referer: https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'TE: trailers' \
  --data-raw 'marketType=M&sector=All&symbol=&letter=' | jq . -S > "${EXP_CHAINS_DIR}/dictionaries/saudi_main_market.json"

curl \
  -s \
  'https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory/!ut/p/z1/lc_LCsIwEAXQb-kHSG6jiXGZLhIL9hHTas1GspKAVhHx-63uWt-zGzh3mEscaYhr_TXs_CUcW7_v9o3jWyY56Fyg0LaSMMpWST5TMVJG1n0gMs1hcmkKOmXQq5i4v_KwJetAmY0XWEKD_5bHm5H4nnd9AlOLO1EJE6DAZAheVBxceO7wAB-etP5MToe6bhDSkYyiG8La9T0!/p0/IZ7_5A602H80OOMQC0604RU6VD10F2=CZ6_5A602H80OGSTA0QFSTBN9F10I5=NJgetCompanyListByMarknetAndSectors=/' --compressed -X POST -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'X-Requested-With: XMLHttpRequest' -H 'Origin: https://www.saudiexchange.sa' -H 'Connection: keep-alive' -H 'Referer: https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'TE: trailers' \
  --data-raw 'marketType=S&sector=All&symbol=&letter=' | jq . -S > "${EXP_CHAINS_DIR}/dictionaries/saudi_nomu_parallel_market.json"

pushd "$EXP_CHAINS_DIR"
git add "dictionaries/saudi_main_market.json"
git add "dictionaries/saudi_nomu_parallel_market.json"
if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit saudi data"
    git push origin "$EXPCHAINS_BRANCH"
fi
popd
