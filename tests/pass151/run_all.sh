#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="$ROOT"
python3 -m compileall -q "$ROOT/hhs_runtime/pass151" "$ROOT/tools/hhs151.py"
gcc -std=c11 -Wall -Wextra -Werror -I"$ROOT/hhs_runtime/pass151" "$ROOT/hhs_runtime/pass151/hhs151_native.c" "$ROOT/tests/pass151/test_native.c" -o "$ROOT/tests/pass151/test_native"
"$ROOT/tests/pass151/test_native"
python3 "$ROOT/tests/pass151/run_pass151_tests.py"
python3 "$ROOT/tools/hhs151.py" --root "$ROOT" hhs151_contract_compile >/dev/null
python3 "$ROOT/tools/hhs151.py" --root "$ROOT" hhs151_replay >/dev/null
python3 "$ROOT/tools/hhs151.py" --root "$ROOT" hhs151_export_evidence >/dev/null
