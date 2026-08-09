#!/usr/bin/env python3
"""Generate, inspect, or exact-rebuild Pass 217 Iteration 1 evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass217_inherited_authority_freeze_v1 import (
    BASE_COMMIT,
    build_inherited_authority_freeze,
    load_inherited_authority_freeze,
    verify_inherited_authority_freeze,
    write_inherited_authority_freeze,
)


def _emit(result: dict[str, object]) -> None:
    operations = result["cumulative_operation_inventory"]
    tree = result["repository_tree_inventory"]
    gate = result["inheritance_gate"]
    focus = result["pass219_preparation_inventory"]
    summary = {
        "base": result["base"],
        "freeze_sha256": result["freeze_sha256"],
        "tree_coverage": tree["coverage"],
        "operation_coverage": operations["coverage"],
        "known_opcode_family_anchors": operations["known_opcode_family_anchors"],
        "inheritance_gate": gate,
        "pass219_focus_status": {
            name: value["status"] for name, value in focus["families"].items()
        },
        "claim_boundary": result["claim_boundary"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"PASS217_ITERATION1_BASE_COMMIT={result['base']['commit']}")
    print(f"PASS217_ITERATION1_BASE_TREE={result['base']['tree']}")
    print(f"PASS217_ITERATION1_FREEZE_SHA256={result['freeze_sha256']}")
    print(f"PASS217_ITERATION1_INHERITANCE_STATUS={gate['status']}")
    print("PASS217_ITERATION1_INHERITED_AUTHORITY_FREEZE_OK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--base-ref", default=BASE_COMMIT)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output")
    action.add_argument("--verify")
    action.add_argument("--inspect")
    args = parser.parse_args()

    if args.inspect:
        result = load_inherited_authority_freeze(args.inspect)
    elif args.verify:
        result = verify_inherited_authority_freeze(
            Path(args.repository_root),
            Path(args.verify),
        )
    else:
        result = build_inherited_authority_freeze(
            Path(args.repository_root),
            base_ref=args.base_ref,
        )
        write_inherited_authority_freeze(result, Path(args.output))
    _emit(result)


if __name__ == "__main__":
    main()
