#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 2 ]; then
  echo "usage: $0 FULL_PASS132_RUNTIME.zip OUTPUT_PASS133_FULL_CHECKPOINT.zip" >&2
  exit 2
fi
PARENT="$1"
OUTPUT="$2"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python "$ROOT/tools/hhs_checkpoint_recovery.py" recover "$PARENT" "$ROOT" "$OUTPUT"
