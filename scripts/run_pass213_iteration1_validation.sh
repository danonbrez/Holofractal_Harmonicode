#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 -m unittest -v tests.test_pass213_compiled_rom_v1
python3 -m py_compile hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py
python3 -m json.tool contracts/pass213/PASS_213_CONTRACT.json >/dev/null

echo "PASS213_ITERATION1_VALIDATION_OK"
