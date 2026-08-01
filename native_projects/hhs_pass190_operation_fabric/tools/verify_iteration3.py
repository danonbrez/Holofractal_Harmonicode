#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / "native/include/hhs_pass190_abi.h",
    ROOT / "native/src/hhs_pass190_abi.c",
    ROOT / "native/generated/HHS_NATIVE_ABI_MANIFEST_V1.json",
    ROOT / "native/generated/hhs_pass190_operation_table.inc",
    ROOT / "native/tests/test_hhs_pass190_abi.c",
    ROOT / "python/hhs_pass190_iteration3.py",
]
for path in required:
    if not path.exists() or path.stat().st_size == 0:
        raise SystemExit(f"missing iteration 3 artifact: {path}")

manifest = json.loads(required[2].read_text(encoding="utf-8"))
if manifest.get("operation_count") != 10 or len(manifest.get("operations", [])) != 10:
    raise SystemExit("native manifest does not cover ten operations")
if len({item["native_symbol"] for item in manifest["operations"]}) != 10:
    raise SystemExit("native symbols are not unique")
if manifest.get("full_native_parity_claimed") is not False:
    raise SystemExit("iteration 3 must not overclaim full native parity")

source = required[1].read_text(encoding="utf-8")
for forbidden in ("double ", "float ", "NAN", "INFINITY"):
    if forbidden in source:
        raise SystemExit(f"floating authority token found: {forbidden}")
print("Pass 190 iteration 3 source verification passed")
