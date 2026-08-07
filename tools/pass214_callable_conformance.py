#!/usr/bin/env python3
"""Generate Pass 214 Iteration 2 callable-conformance and compatibility evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_callable_conformance_v1 import (
    build_callable_conformance,
    load_and_validate_callable_conformance_outputs,
    write_callable_conformance_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--iteration1-directory", type=Path, required=True)
    parser.add_argument("--source-ref", default="HEAD")
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    result = build_callable_conformance(
        args.repository_root,
        args.iteration1_directory,
        source_ref=args.source_ref,
    )
    paths = write_callable_conformance_outputs(result, args.output_directory)
    payloads = load_and_validate_callable_conformance_outputs(args.output_directory)
    summary = payloads["iteration2_summary"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"PASS214_ITERATION2_SOURCE_COMMIT={summary['source_commit']}")
    print(f"PASS214_ITERATION2_SOURCE_TREE={summary['source_tree']}")
    print(f"PASS214_ITERATION2_RECORDS={summary['coverage']['callable_records']}")
    print(f"PASS214_ITERATION2_ACTIVE_BOUND={summary['coverage']['active_static_bound']}")
    print(f"PASS214_ITERATION2_ACTIVE_UNRESOLVED={summary['coverage']['active_unresolved']}")
    print(f"PASS214_ITERATION2_EQUIVALENCE_GROUPS={summary['coverage']['static_equivalence_groups']}")
    print(f"PASS214_ITERATION2_CONFLICT_CANDIDATES={summary['coverage']['authority_conflict_candidates']}")
    print(f"PASS214_ITERATION2_EDGES={summary['coverage']['compatibility_edges']}")
    print(f"PASS214_ITERATION2_SEMANTIC_ROOT={summary['roots']['iteration2_semantic_root_hash216']}")
    print(f"PASS214_ITERATION2_RECEIPT_HASH72={summary['receipt_hash72']}")
    print("PASS214_ITERATION2_CALLABLE_CONFORMANCE_GRAPH_OK")
    for name, path in sorted(paths.items()):
        print(f"PASS214_ITERATION2_OUTPUT_{name.upper()}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
