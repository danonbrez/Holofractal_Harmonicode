#!/usr/bin/env bash
set -euo pipefail

prefix=${1:-/tmp/hhs-openssl35-aarch64}
version=${HHS_OPENSSL_VERSION:-3.5.0}
archive="/tmp/openssl-${version}.tar.gz"
source_dir="/tmp/openssl-${version}-hhs-aarch64"

if [[ -s "$prefix/lib/libcrypto.a" && -f "$prefix/include/openssl/evp.h" ]]; then
  printf 'HHS ARM64 OpenSSL already built: %s\n' "$prefix"
  exit 0
fi

rm -rf "$source_dir" "$prefix"
curl -fsSL --retry 3 --retry-delay 2 \
  "https://github.com/openssl/openssl/releases/download/openssl-${version}/openssl-${version}.tar.gz" \
  -o "$archive"
mkdir -p "$source_dir"
tar -xzf "$archive" -C "$source_dir" --strip-components=1

(
  cd "$source_dir"
  ./Configure linux-aarch64 \
    --cross-compile-prefix=aarch64-linux-gnu- \
    --prefix="$prefix" \
    --libdir=lib \
    no-shared no-tests
  make -j2 build_libs
  make install_sw
)

test -s "$prefix/lib/libcrypto.a"
test -f "$prefix/include/openssl/evp.h"
printf 'HHS ARM64 OpenSSL built: version=%s prefix=%s\n' "$version" "$prefix"
