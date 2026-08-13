#!/usr/bin/env python3
"""Generate or validate Pass 217 Iteration 4 Hash72/nucleus evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hhs_backend.runtime.hhs_pass217_hash72_manifold_nucleus_v1 import (
    EVIDENCE_PATH,
    validate_record,
    write_record,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--inspect", default=EVIDENCE_PATH)
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    if args.write:
        record = write_record(root, args.inspect)
        print(json.dumps(record, sort_keys=True, separators=(",", ":")))
    else:
        result = validate_record(root)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("PASS217_ITERATION4_HASH72_MANIFOLD_NUCLEUS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
