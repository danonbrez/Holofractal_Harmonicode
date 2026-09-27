#!/usr/bin/env sh
set -eu

CC="${WASM_CC:-clang}"
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
BUILD="$ROOT/build"
OUT="$BUILD/hhs_pass179_render_command_v1.wasm"

mkdir -p "$BUILD"

"$CC" \
  --target=wasm32 \
  -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
  -ffreestanding -fno-builtin -nostdlib \
  -I"$ROOT/include" \
  "$ROOT/src/hhs_pass179_render_command_v1.c" \
  "$ROOT/wasm/hhs_pass179_render_command_wasm_v1.c" \
  -Wl,--no-entry \
  -Wl,--export-memory \
  -Wl,--initial-memory=131072 \
  -Wl,--max-memory=131072 \
  -Wl,--export=hhs179_wasm_abi_version \
  -Wl,--export=hhs179_wasm_reset \
  -Wl,--export=hhs179_wasm_identity_ptr \
  -Wl,--export=hhs179_wasm_identity_bytes \
  -Wl,--export=hhs179_wasm_command_ptr \
  -Wl,--export=hhs179_wasm_command_capacity \
  -Wl,--export=hhs179_wasm_packet_ptr \
  -Wl,--export=hhs179_wasm_packet_capacity \
  -Wl,--export=hhs179_wasm_packet_size \
  -Wl,--export=hhs179_wasm_build_packet \
  -o "$OUT"

printf '%s\n' "$OUT"
