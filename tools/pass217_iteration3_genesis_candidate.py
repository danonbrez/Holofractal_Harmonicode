#!/usr/bin/env python3
"""Generate or validate the Pass 217 Iteration 3 candidate bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass217_genesis_candidate_v1 import (
    validate_bundle,
    write_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write deterministic non-promotional candidate and address artifacts",
    )
    args = parser.parse_args()
    root = args.repository_root.resolve()
    if args.write:
        write_bundle(root)
    summary = validate_bundle(root)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"PASS217_ITERATION3_BUNDLE_ROOT={summary['bundle_root_sha256']}")
    print(f"PASS217_ITERATION3_CANDIDATE_SHA256={summary['candidate_sha256']}")
    print(f"PASS217_ITERATION3_INHERITANCE_STATUS={summary['inheritance_status']}")
    print("PASS217_ITERATION3_NON_PROMOTIONAL_CANDIDATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
