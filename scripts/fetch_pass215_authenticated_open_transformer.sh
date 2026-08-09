#!/usr/bin/env bash
set -euo pipefail

MODEL_FILENAME='stories15M-q4_0.gguf'
MODEL_URL='https://huggingface.co/ggml-org/tiny-llamas/resolve/main/stories15M-q4_0.gguf?download=true'

cache_dir=''
expected_sha256=''
target_dir=''

usage() {
  cat <<'EOF'
Usage:
  bash scripts/fetch_pass215_authenticated_open_transformer.sh \
    --cache-dir <dir> \
    --expected-sha256 <sha256> \
    [--target-dir <dir>]
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --cache-dir)
      cache_dir="$2"
      shift 2
      ;;
    --expected-sha256)
      expected_sha256="$2"
      shift 2
      ;;
    --target-dir)
      target_dir="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ -z "$cache_dir" ] || [ -z "$expected_sha256" ]; then
  usage >&2
  exit 1
fi

verify_sha256() {
  local path="$1"
  [ -f "$path" ] && echo "$expected_sha256  $path" | sha256sum -c - >/dev/null 2>&1
}

mkdir -p "$cache_dir"
cache_file="$cache_dir/$MODEL_FILENAME"

if ! verify_sha256 "$cache_file"; then
  rm -f "$cache_file"
  tmp_file="$(mktemp "$cache_dir/${MODEL_FILENAME}.partial.XXXXXX")"
  trap 'rm -f "$tmp_file"' EXIT
  curl -L --fail --retry 8 --retry-all-errors --retry-delay 5 --retry-max-time 900 \
    -H 'User-Agent: hhs-pass215-model-fetch/1.0' \
    -o "$tmp_file" \
    "$MODEL_URL"
  echo "$expected_sha256  $tmp_file" | sha256sum -c -
  mv "$tmp_file" "$cache_file"
  trap - EXIT
fi

if [ -n "$target_dir" ]; then
  mkdir -p "$target_dir"
  target_file="$target_dir/$MODEL_FILENAME"
  if ! verify_sha256 "$target_file"; then
    install -m 0644 "$cache_file" "$target_file"
  fi
  echo "$expected_sha256  $target_file" | sha256sum -c -
  printf '%s\n' "$target_file"
else
  echo "$expected_sha256  $cache_file" | sha256sum -c -
  printf '%s\n' "$cache_file"
fi
