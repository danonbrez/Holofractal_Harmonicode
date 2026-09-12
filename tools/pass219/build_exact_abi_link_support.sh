#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage: build_exact_abi_link_support.sh OUT_DIR [full|cell-wall-only]

Environment:
  CC       C compiler (default: gcc)
  CXX      C++ compiler (default: g++)
  CFLAGS   optional additional C flags
  CXXFLAGS optional additional C++ flags

Outputs:
  OUT_DIR/hhs_hash216.o                         (full mode only)
  OUT_DIR/hhs_pass219_vm81_pqc_cell_wall.o      (all modes)
EOF
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 64
fi

out_dir=$1
mode=${2:-full}
case "$mode" in
  full|cell-wall-only) ;;
  *) usage; exit 64 ;;
esac

cc=${CC:-gcc}
cxx=${CXX:-g++}
mkdir -p "$out_dir"

common_include=(
  -Ihhs_runtime/include
  -Ihhs_runtime/c
)
cxx_include=(
  "${common_include[@]}"
  -Inative_projects/hhs_pass188_bott_runtime/include
  -Inative_projects/hhs_pass189_hqlh_runtime/include
)

if [[ "$mode" == full ]]; then
  # shellcheck disable=SC2086
  "$cc" -O2 -std=c11 -Wall -Wextra -Werror -pedantic -fPIC \
    ${CFLAGS:-} "${common_include[@]}" \
    -c hhs_runtime/src/hhs_hash216.c \
    -o "$out_dir/hhs_hash216.o"
fi

# shellcheck disable=SC2086
"$cxx" -O2 -std=c++17 -Wall -Wextra -Werror -pedantic -fPIC \
  ${CXXFLAGS:-} "${cxx_include[@]}" \
  -c hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp \
  -o "$out_dir/hhs_pass219_vm81_pqc_cell_wall.o"

printf 'HHS exact ABI link support built: mode=%s CC=%s CXX=%s out=%s\n' \
  "$mode" "$cc" "$cxx" "$out_dir"
