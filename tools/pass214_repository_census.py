#!/usr/bin/env python3
"""Generate and validate Pass 214 iteration-one repository census evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_repository_census_v1 import (
    build_repository_census,
    load_and_validate_outputs,
    write_census_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--source-ref", default="HEAD")
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--max-source-bytes", type=int, default=4 * 1024 * 1024)
    args = parser.parse_args()

    result = build_repository_census(
        Path(args.repository_root),
        source_ref=args.source_ref,
        max_source_bytes=args.max_source_bytes,
    )
    paths = write_census_outputs(result, Path(args.output_directory))
    load_and_validate_outputs(Path(args.output_directory))
    summary = result["summary"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"PASS214_ITERATION1_SOURCE_COMMIT={summary['source_commit']}")
    print(f"PASS214_ITERATION1_SOURCE_TREE={summary['source_tree']}")
    print(f"PASS214_ITERATION1_TREE_ENTRIES={summary['coverage']['tracked_tree_entries']}")
    print(f"PASS214_ITERATION1_SYMBOLS={summary['coverage']['candidate_symbols']}")
    print(f"PASS214_ITERATION1_SEMANTIC_ROOT={summary['roots']['iteration1_semantic_root_hash216']}")
    print(f"PASS214_ITERATION1_RECEIPT_HASH72={summary['receipt_hash72']}")
    print("PASS214_ITERATION1_REPOSITORY_CENSUS_OK")
    for name, path in sorted(paths.items()):
        print(f"PASS214_ITERATION1_OUTPUT_{name.upper()}={path}")


if __name__ == "__main__":
    main()
