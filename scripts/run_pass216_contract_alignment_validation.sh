#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python tests/test_pass216_contract_alignment.py
printf '%s\n' PASS216_CONTRACT_ALIGNMENT_VALIDATION_OK
