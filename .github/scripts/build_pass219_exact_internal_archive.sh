#!/usr/bin/env bash
set -euo pipefail

out="${1:?output archive path required}"
build_dir="${2:-/tmp/pass219-exact-internal}"
mkdir -p "$build_dir" "$(dirname "$out")"

cflags=(
  -O2 -std=c11 -Wall -Wextra -Werror -pedantic
  -Ihhs_runtime/include -Ihhs_runtime/c
)
cxxflags=(
  -O2 -std=c++17 -Wall -Wextra -Werror -pedantic
  -Ihhs_runtime/include -Ihhs_runtime/c
  -Inative_projects/hhs_pass188_bott_runtime/include
  -Inative_projects/hhs_pass189_hqlh_runtime/include
)

gcc "${cflags[@]}" -c hhs_runtime/c/hhs_runtime_exact_abi.c -o "$build_dir/hhs_runtime_exact_abi.o"
gcc "${cflags[@]}" -c hhs_runtime/src/hhs_hash216.c -o "$build_dir/hhs_hash216.o"
g++ "${cxxflags[@]}" -c hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp -o "$build_dir/hhs_pass219_vm81_pqc_cell_wall_1_30.o"
g++ "${cxxflags[@]}" -c hhs_runtime/cpp/hhs_pass219_rna_vm5184_abi_1_33.cpp -o "$build_dir/hhs_pass219_rna_vm5184_abi_1_33.o"
g++ "${cxxflags[@]}" -c hhs_runtime/cpp/hhs_pass220_rna_hash72_dna_qudit_phase_lock_1_0.cpp -o "$build_dir/hhs_pass220_rna_hash72_dna_qudit_phase_lock_1_0.o"

ar rcs "$out" \
  "$build_dir/hhs_runtime_exact_abi.o" \
  "$build_dir/hhs_hash216.o" \
  "$build_dir/hhs_pass219_vm81_pqc_cell_wall_1_30.o" \
  "$build_dir/hhs_pass219_rna_vm5184_abi_1_33.o" \
  "$build_dir/hhs_pass220_rna_hash72_dna_qudit_phase_lock_1_0.o"

test -s "$out"
