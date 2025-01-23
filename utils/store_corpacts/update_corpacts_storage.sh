#!/bin/bash
set -e

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
CORPACTS_FILE="${EXP_CHAINS_DIR}/dictionaries/CorpActs.tab"
LASTCORPACTS_FILE="${EXP_CHAINS_DIR}/dictionaries/LastCorpActs.tab"

TMP_CORPACTS_FILE=$(mktemp /tmp/corpacts.XXXXXX)
TMP_LASTCORPACTS_FILE=$(mktemp /tmp/lastcorpacts.XXXXXX)


URLS=("https://esignalreport.com/update/CorpActs.tab" "http://fs2.esignal.com/CorpActs.tab")

for url in "${URLS[@]}"; do
  curl -s --compressed --retry 3 --max-time 480 -o "${TMP_CORPACTS_FILE}" --url "$url" && break
done

echo "Generating LastCorpActs.tab from CorpActs.tab..."
LASTCORPACTS_SCRIPT="${EXP_CHAINS_DIR}/bin/lastcorpacts.rb"
ruby "${LASTCORPACTS_SCRIPT}" -f "${TMP_CORPACTS_FILE}" > "${TMP_LASTCORPACTS_FILE}"
LINES=$(wc -l <"${TMP_LASTCORPACTS_FILE}")
echo "Completed. Generated ${LINES} line(s)"

mv "${TMP_CORPACTS_FILE}" "${CORPACTS_FILE}"
mv "${TMP_LASTCORPACTS_FILE}" "${LASTCORPACTS_FILE}"

FILE_SIZE=$(stat --printf '%s' "${CORPACTS_FILE}")

if [ "$FILE_SIZE" -lt "400000" ]; then
    	echo "ERROR: Resulting file ${CORPACTS_FILE} is too small ${FILE_SIZE}"
    	exit 1
fi

pushd "$EXP_CHAINS_DIR"

git add "dictionaries/CorpActs.tab"
git add "dictionaries/LastCorpActs.tab"

if [ "$(git status -s)" = "" ]; then
    echo "No changes in $EXPCHAINS_BRANCH"
else
    echo "Update expchains in $EXPCHAINS_BRANCH"
    git --no-pager -c color.ui=always diff --staged
    git commit -m "Autocommit CorpActs.tab and LastCorpActs.tab"
    git push origin "$EXPCHAINS_BRANCH"
fi



# UPLOAD TO BUCKET
pushd "dictionaries"

function log_info() {
  local MESSAGE=$1
  printf "${BOLD}%s${NC}\n" "$MESSAGE"
}

function log_success() {
  local MESSAGE=$1
  printf "${BOLD_GREEN}%s${NC}\n" "$MESSAGE"
}

function log_warn() {
  local MESSAGE=$1
  printf "${BOLD_YELLOW}%s${NC}\n" "$MESSAGE"
}

function log_error() {
  local MESSAGE=$1
  printf "${BOLD_RED}ERROR: %s${NC}\n" "$MESSAGE"
}


BASE_URL='s3://tradingview-sourcedata-storage-staging'
#case "$ENVIRONMENT" in
#    'production')
#        BASE_URL='s3://tradingview-sourcedata-storage'
#        ;;
#    'stable')
#        BASE_URL='s3://tradingview-sourcedata-storage-stable'
#        ;;
#	  'staging')
#        BASE_URL='s3://tradingview-sourcedata-storage-staging'
#        ;;
#    * )
#        log_error "Unexpected param $ENVIRONMENT"
#        exit 1;
#esac

if [[ -z "$SOURCEDATA_AWS_ACCESS_KEY_ID" ]] || [[ -z "$SOURCEDATA_AWS_SECRET_ACCESS_KEY" ]]; then
  log_error "SOURCEDATA_AWS_ACCESS_KEY_ID and SOURCEDATA_AWS_SECRET_ACCESS_KEY must be defined"
  exit 1;
fi
export AWS_ACCESS_KEY_ID="$SOURCEDATA_AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$SOURCEDATA_AWS_SECRET_ACCESS_KEY"

function is_equals() {
  local first_file=$1
  local second_file=$2
  local show_diff=$3

  HASH_LOCAL=$(sha1sum "$first_file" | cut -d' ' -f1)
  HASH_REMOTE=$(sha1sum "$second_file" | cut -d' ' -f1)

  jq . "$second_file" > "${second_file%.*}_formatted.json"
  jq . "$first_file" > "${first_file%.*}_formatted.json"
  if [ "$show_diff" = '1' ]; then
    git diff --color --no-index --exit-code -- "${second_file%.*}_formatted.json" "${first_file%.*}_formatted.json" || true
  fi

  [ "$HASH_REMOTE" = "$HASH_LOCAL" ]
}

function zip_files() {
    local files=("${!1}")
    local snapshot_path="$2"
    # tar used options:
    #  -c: create a new archive
    #  -z: filter the archive through gzip
    #  -f: use archive file or device ARCHIVE
    tar -czf "$snapshot_path" "${files[@]}"
    # zip -qum9 "$snapshot_path" "${files[@]}"
}

function upload_snapshot() {
  local snapshot_path=$1
  local snapshot_name=$2
  aws s3 cp --content-encoding=gzip "$snapshot_path" "$BASE_URL/$snapshot_name" 2>&1
}

function download_data_snapshot() {
  local src_file=$1
  local dst_file=$2
  local retval=1
  for i in {1..3}; do
    aws s3 cp "$BASE_URL/$src_file" "$dst_file" && retval=0 && break || retval=$? && [ "$i" -ne 3 ] && sleep 3
  done
  if [ "$retval" -ne 0 ]; then
    log_error "Failed to download $BASE_URL/$src_file to $dst_file"
  fi
  return $retval
}


function s3_process_snapshot() {
  # define vars
  read -ra files <<< "CorpActs.tab LastCorpActs.tab"
  local -r out_dir="./out"
  local -r snapshot_name="tvc/corpacts"
  local -r file_ext=".tar.gz"
  local -r snapshot_path="${out_dir}/${snapshot_name}${file_ext}"
  local -r remote_snapshot_path="${out_dir}/${snapshot_name}.remote${file_ext}"
  local -r show_diff="1"

  log_info "Updating $snapshot_name snapshot..."

  mkdir -p "${snapshot_path%/*}"

  # to find files by pattern and store them into arr use next line:
  # mapfile -t files < <(find ./ -maxdepth 1 -type f -name "$input")
  log_info "These files will be processed:"
  for file in "${files[@]}"; do
    log_info "$file"
  done

  download_data_snapshot "$snapshot_name$file_ext" "$remote_snapshot_path" || true

  if ! [ -e "$remote_snapshot_path" ]; then
    log_error "This is initial upload of $snapshot_name snapshot or download had been failed"
#    log_warn "Packing all related files to snapshot and uploading..."
#    zip_files files[@] "$snapshot_path"
#    upload_snapshot "$snapshot_path" "$snapshot_name$file_ext"
    return 1 # $?
  fi

  # decompress the downloaded file
  # tar used options:
  #  -x: extract files from an archive
  #  -z: filter the archive through gzip
  #  -f: use archive file or device ARCHIVE
  #  -C: change to directory DIR
  local -r remote_snapshot_dir="${remote_snapshot_path%"$file_ext"}_"
  mkdir -p "$remote_snapshot_dir" && tar -xzf "$remote_snapshot_path" -C "$remote_snapshot_dir"
  # unzip -qu "$remote_snapshot_path" -d "$remote_snapshot_dir"

  for file in "${files[@]}"; do
    log_info "Comparing $file..."
    if is_equals "$file" "$remote_snapshot_dir/$file" "$show_diff"; then
      log_success "s3: $file is not modified"
    else
      log_warn "s3: $file is modified, packing all related files to snapshot and uploading..."
      zip_files files[@] "$snapshot_path"
      upload_snapshot "$snapshot_path" "$snapshot_name$file_ext"
      break
    fi
  done
}

s3_process_snapshot()

popd
popd