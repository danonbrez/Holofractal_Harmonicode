#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "HHS_OPERATION_REGISTRY_V1.json"
MANIFEST = ROOT / "native" / "generated" / "HHS_NATIVE_ABI_MANIFEST_V1.json"
TABLE = ROOT / "native" / "generated" / "hhs_pass190_operation_table.inc"

BINDINGS = (
    ("system.status", "hhs_p190_system_status", "VM81:status", "status-v1", False),
    ("python.len", "hhs_p190_python_len", "VM81:len", "length-v1", False),
    ("python.abs", "hhs_p190_python_abs", "VM81:abs", "int64-v1", False),
    ("python.sorted", "hhs_p190_python_sorted_i64", "VM81:sorted", "int64-array-v1", False),
    ("list.with_appended", "hhs_p190_list_with_appended_i64", "VM81:list.with_appended", "int64-array-v1", False),
    ("dict.get", "hhs_p190_dict_get_json", "VM81:dict.get", "utf8-key-json-value-v1", False),
    ("text.join", "hhs_p190_text_join", "VM81:text.join", "utf8-sequence-v1", False),
    ("math.gcd", "hhs_p190_math_gcd", "VM81:math.gcd", "int64-v1", False),
    ("pass189.context.decode", "hhs_p190_pass189_context_decode", "VM81:P189.decode", "pass189-address-v1", False),
    ("state.counter.advance", "hhs_p190_state_counter_advance", "VM81:state.counter.advance", "singleton-counter-v1", True),
)


def load_registry(path: Path = REGISTRY) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    operations = payload.get("operations", [])
    expected_ids = [item[0] for item in BINDINGS]
    actual_ids = [item.get("operation_id") for item in operations]
    if actual_ids != expected_ids:
        raise SystemExit(f"canonical operation order mismatch: {actual_ids}")
    for record, binding in zip(operations, BINDINGS):
        if record.get("VM81_binding") != binding[2]:
            raise SystemExit(f"VM81 binding mismatch for {binding[0]}")
    return payload


def manifest_text(registry: dict[str, Any]) -> str:
    operations = []
    for slot, (operation_id, symbol, vm81, profile, mutates) in enumerate(BINDINGS):
        operations.append({
            "operation_id": operation_id,
            "native_profile": profile,
            "native_symbol": symbol,
            "slot": slot,
            "mutates_state": mutates,
            "vm81_binding": vm81,
        })
    payload = {
        "abi_version": "1.0.0",
        "canonical_registry_schema": registry.get("schema"),
        "contract": "HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216",
        "full_native_parity_claimed": False,
        "iteration": 3,
        "operation_count": len(operations),
        "operations": operations,
        "schema": "HHS_NATIVE_ABI_MANIFEST_V1",
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def table_text() -> str:
    lines = [
        "/* Generated from HHS_OPERATION_REGISTRY_V1.json. Do not edit by hand. */",
        "static const hhs_p190_operation_descriptor HHS_P190_OPERATIONS[HHS_P190_OPERATION_COUNT] = {",
    ]
    for slot, (operation_id, symbol, vm81, profile, mutates) in enumerate(BINDINGS):
        comma = "," if slot + 1 < len(BINDINGS) else ""
        lines.append(
            f'    {{"{operation_id}", "{symbol}", "{vm81}", "{profile}", {slot}u, {1 if mutates else 0}u}}{comma}'
        )
    lines.append("};")
    return "\n".join(lines) + "\n"


def write_or_check(check: bool) -> None:
    registry = load_registry()
    expected = {MANIFEST: manifest_text(registry), TABLE: table_text()}
    stale = []
    for path, content in expected.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        raise SystemExit("stale native ABI generated files: " + ", ".join(stale))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    write_or_check(args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
