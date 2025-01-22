#!/usr/bin/env bash
set -eu

# The color codes are left just for a reminder
BOLD_RED='\033[1;31m'
BOLD_GREEN='\033[1;32m'
BOLD_YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

ENVIRONMENT=$1

function log_info() {
  local -r message=$1
  printf "${BOLD}%s${NC}\n" "$message"
}

function log_success() {
  local -r message=$1
  printf "${BOLD_GREEN}%s${NC}\n" "$message"
}

function log_warn() {
  local -r message=$1
  printf "${BOLD_YELLOW}%s${NC}\n" "$message"
}

function log_error() {
  local -r message=$1
  printf "${BOLD_RED}ERROR: %s${NC}\n" "$message"
}

# MAIN
if [ -z "$ENVIRONMENT" ]; then
  log_error "Required param is absent, please pass an environment name to the script (staging/stable/production)"
  exit 1;
fi

case "$ENVIRONMENT" in
    'production')
        BASE_URL='s3://tradingview-sourcedata-storage'
        ;;
    'stable')
        BASE_URL='s3://tradingview-sourcedata-storage-stable'
        ;;
	  'staging')
        BASE_URL='s3://tradingview-sourcedata-storage-staging'
        ;;
    * )
        log_error "Unexpected param $ENVIRONMENT"
        exit 1;
esac

if [[ -z "$AWS_ACCESS_KEY_ID" ]] || [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    log_error "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be defined"
    exit 1;
fi

aws --version

function show_diff() {
  local -r first_file=$1
  local -r second_file=$2
  local -r first_file_ext=${first_file#*.}
  local -r second_file_ext=${second_file#*.}

  if [ "$first_file_ext" != "$second_file_ext" ]; then
    log_warn "Unable to show diff between $first_file and $second_file: file extensions do not match"
    return 0
  fi

  local formatted_first_file="$first_file"
  local formatted_second_file="$second_file"
  if [ "$first_file_ext" = "json" ]; then
    formatted_first_file="${first_file%.*}_formatted.json"
    formatted_second_file="${second_file%.*}_formatted.json"
    jq . "$first_file" > "$formatted_first_file"
    jq . "$second_file" > "$formatted_second_file"
  fi
  git diff --color --no-index --exit-code -- "$formatted_second_file" "$formatted_first_file" || true
}

function is_equals() {
  local -r first_file=$1
  local -r second_file=$2

  HASH_LOCAL=$(sha1sum "$first_file" | cut -d' ' -f1)
  HASH_REMOTE=$(sha1sum "$second_file" | cut -d' ' -f1)

  [ "$HASH_REMOTE" = "$HASH_LOCAL" ]
}

function zip_files() {
    local files=("${!1}")
    local snapshot_path="$2"
    local -n r_file_ext="$3"

    log_info "Compressing files to $snapshot_path..."
    # Linux default utils cannot compress more than one file.
    # The reason for this is the Linux-specific compression idiom.
    # So to do this, it's necessary first archive files into a single archive, and then compress the archive.
    # Another way is to use Windows-specific idiom utils, such as ZIP:
    # zip -qum9 "$snapshot_path" "${files[@]}"
    if (( ${#files[@]} == 1 )); then
      # gzip used options:
      #  -c: write on standard output, keep original files unchanged
      #  -q: suppress all warnings
      #  -9: compress better
      r_file_ext="gz"
      gzip -cq9 "${files[@]}" > "${snapshot_path%%.*}.$r_file_ext"
    else
      # tar used options:
      #  -c: create a new archive
      #  -z: filter the archive through gzip
      #  -f: use archive file or device ARCHIVE
      r_file_ext="tar.gz"
      tar -czf "${snapshot_path%%.*}.$r_file_ext" --transform 's/.*\///' "${files[@]}"
    fi
}

function decompress_file() {
  local -r file_path="$1"
  local -r dst_dir="$2"
  local -r filename="${file_path##*/}"
  local -r file_ext="${file_path#*.}"

  log_info "Decompressing $file_path to $dst_dir..."
  case "$file_ext" in
    'tar.gz')
      # tar used options:
      #  -x: extract files from an archive
      #  -z: filter the archive through gzip
      #  -f: use archive file or device ARCHIVE
      #  -C: change to directory DIR
      tar -xzf "$file_path" -C "$dst_dir"
      ;;
    'gz')
      # gzip used options:
      #  -d: decompress
      #  -q: suppress all warnings
      #  -c: write on standard output, keep original files unchanged
      gzip -dqc "$file_path" > "${dst_dir}/${filename%.*}.json"
      ;;
    'zip')
      # zip used options:
      #  -q: quiet mode
      #  -u: update files, create if necessary
      unzip -qu "$file_path" -d "$dst_dir"
      ;;
    *)
      log_error "Decompressing failed: unexpected format $file_ext"
      exit 1;
  esac
}

function upload_snapshot() {
  local snapshot_path=$1
  local snapshot_fullname=$2
  log_info "Uploading..."
  aws s3 cp --content-encoding=gzip "$snapshot_path" "$BASE_URL/$snapshot_fullname" 2>&1
}

function download_snapshot() {
  local src_file=$1
  local dst_file=$2
  local retval=1

  log_info "Downloading..."
  for i in {1..3}; do
    aws s3 cp "$BASE_URL/$src_file" "$dst_file" && retval=0 && break || retval=$? && [ "$i" -ne 3 ] && sleep 3
  done
  if [ "$retval" -ne 0 ]; then
    log_error "Failed to download $BASE_URL/$src_file to $dst_file"
  fi
  return $retval
}

function parse_args() {
  while (( "$#" )); do
    case $1 in
      -i|--input)
        if [[ -n $2 ]]; then
          args[input]="$2"
          shift
        else
          log_error "Error: argument -i/--input is required"
          return 1
        fi
        ;;
      -s|--snapshot)
        if [[ -n $2 ]]; then
          args[snapshot]="$2"
          shift
        else
          log_error "Error: argument -s/--snapshot is required"
          return 1
        fi
        ;;
      -d|--diff)
        args[diff]=1
        if [[ -n $2 ]]; then
          args[diff]="$2"
        fi
        shift
        ;;
      *)
        log_error "Unknown option '$1'"
        return 1
        ;;
    esac
    shift
  done
}

function s3_process_snapshot() {
  declare -A args
  parse_args "$@"

  # define vars
  read -ra files <<< "${args[input]}"
  local -r out_dir="out"
  local -r snapshot_fullname="${args[snapshot]}"
  local -r filename="${snapshot_fullname##*/}"
  local -r remote_file_ext="${filename#*.}"
  local -r snapshot_path="${out_dir}/${snapshot_fullname}"
  local -r remote_snapshot_dir="${snapshot_path%."$remote_file_ext"}/remote"
  local -r remote_snapshot_path="${remote_snapshot_dir}/${filename}"
  local -r show_diff="${args[diff]}"

  log_info "Processing $snapshot_fullname snapshot..."

  mkdir -p "${remote_snapshot_dir}"

  log_info "These files will be processed:"
  for file in "${files[@]}"; do
    log_info "  - $file"
  done

  download_snapshot "$snapshot_fullname" "$remote_snapshot_path" || true

  if ! [ -e "$remote_snapshot_path" ]; then
    log_error "This is initial upload of $snapshot_fullname snapshot or download had been failed"
#    local file_ext
#    zip_files files[@] "$snapshot_path" file_ext
#    if [ "$file_ext" != "$remote_file_ext" ]; then
#      log_warn "An extension of the remote file does not match an extension of the new file"
#    fi
#    upload_snapshot "$snapshot_path" "$snapshot_fullname" || true
    return 1
  fi

  decompress_file "$remote_snapshot_path" "$remote_snapshot_dir"

  for file in "${files[@]}"; do
    log_info "Comparing $file..."
    if is_equals "$file" "$remote_snapshot_dir/${file##*/}"; then
      log_success "s3: $file is not modified"
    else
      if [ "$show_diff" = '1' ]; then
        show_diff "$file" "$remote_snapshot_dir/${file##*/}"
      fi
      log_warn "s3: $file is modified, packing all related files to snapshot and uploading..."
      local file_ext
      zip_files files[@] "$snapshot_path" file_ext
      if [ "$file_ext" != "$remote_file_ext" ]; then
        log_warn "An extension of the remote packed file does not match an extension of the new packed file"
      fi
      upload_snapshot "$snapshot_path" "$snapshot_fullname"
      break
    fi
  done

  log_success "Processing $snapshot_fullname snapshot is DONE"
}

cd ./idc-expchains
# shellcheck disable=SC2046
# shellcheck disable=SC2005
FILES_TO_STORE=$(echo $(ls expchains/*))
s3_process_snapshot -i "$FILES_TO_STORE" -s "tvc/expchains.tar.gz" -d 1