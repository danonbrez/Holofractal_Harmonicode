#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass190 import hash216

REGISTRY = ROOT / "registry" / "HHS_OPERATION_REGISTRY_V1.json"
TARGET = ROOT / "bindings" / "P190_OPERATION_SURFACE_BINDINGS_V1.json"


def generate() -> str:
    payload = json.loads(REGISTRY.read_text())
    bindings = []
    for operation in payload["operations"]:
        operation_id = operation["operation_id"]
        symbol = operation_id.replace(".", "_").replace("-", "_")
        bindings.append({
            "operation_id": operation_id,
            "gui_action_id": f"pass190.invoke.{operation_id}",
            "workflow_step_id": f"pass190.operation.{operation_id}",
            "websocket_channel": "pass190.receipts",
            "python_sdk_symbol": symbol,
            "typescript_sdk_symbol": symbol,
        })
    document = {
        "schema": "P190_OPERATION_SURFACE_BINDINGS_V1",
        "contract": payload.get("contract"),
        "registry_hash216": payload.get("registry_hash216"),
        "bindings": bindings,
    }
    document["bindings_hash216"] = hash216(
        "pass190.surface.bindings",
        {key: value for key, value in document.items() if key != "bindings_hash216"},
    )
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = generate()
    if args.check:
        if TARGET.read_text() != content:
            raise SystemExit("generated bindings are stale")
    else:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
