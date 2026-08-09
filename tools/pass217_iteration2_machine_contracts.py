#!/usr/bin/env python3
"""Generate or validate the Pass 217 Iteration 2 preparatory bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass217_machine_contracts_v1 import (
    write_bundle,
    validate_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the deterministic contract, schema, vector, checksum, and evidence files",
    )
    args = parser.parse_args()
    root = args.repository_root.resolve()
    if args.write:
        write_bundle(root)
    summary = validate_bundle(root)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"PASS217_ITERATION2_BUNDLE_ROOT={summary['bundle_root_sha256']}")
    print(f"PASS217_ITERATION2_INHERITANCE_STATUS={summary['inheritance_status']}")
    print("PASS217_ITERATION2_MACHINE_CONTRACTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
