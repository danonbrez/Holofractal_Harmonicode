#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass190_iteration6_registry import ITERATION6_CONTRACT, ExpandedOperationRegistry

TARGET = ROOT / "bindings" / "P190_OPERATION_SURFACE_BINDINGS_V2.json"


def generate() -> str:
    registry = ExpandedOperationRegistry()
    native_ids = {record.operation_id for record in registry.records[:registry.payload["native_operation_count"]]}
    bindings = []
    for record in registry.records:
        operation_id = record.operation_id
        symbol = operation_id.replace(".", "_").replace("-", "_")
        bindings.append({
            "gui_action_id": f"pass190.invoke.{operation_id}",
            "native_available": operation_id in native_ids,
            "operation_id": operation_id,
            "python_sdk_symbol": symbol,
            "typescript_sdk_symbol": symbol,
            "websocket_channel": "pass190.receipts",
            "workflow_step_id": f"pass190.operation.{operation_id}",
        })
    document = {
        "bindings": bindings,
        "contract": ITERATION6_CONTRACT,
        "governed_operation_count": len(registry.records),
        "native_operation_count": registry.payload["native_operation_count"],
        "parent_contract": registry.payload["parent_contract"],
        "schema": "P190_OPERATION_SURFACE_BINDINGS_V2",
    }
    return json.dumps(document, separators=(",", ":"), sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = generate()
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != content:
            raise SystemExit("generated Iteration 6 bindings are stale")
    else:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
