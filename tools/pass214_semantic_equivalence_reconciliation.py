#!/usr/bin/env python3
"""Generate Pass 214 semantic-equivalence reconciliation and reuse registry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_reusable_operation_registry_v1 import build_registry
from hhs_backend.runtime.hhs_pass214_semantic_equivalence_v1 import (
    build_semantic_equivalence_reconciliation,
    load_and_validate_reconciliation,
    write_reconciliation,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--source-ref", default="HEAD")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-source-bytes", type=int, default=4 * 1024 * 1024)
    args = parser.parse_args()

    result = build_semantic_equivalence_reconciliation(
        Path(args.repository_root),
        source_ref=args.source_ref,
        max_source_bytes=args.max_source_bytes,
    )
    output = Path(args.output)
    write_reconciliation(result, output)
    loaded = load_and_validate_reconciliation(output)
    registry = build_registry(loaded)
    summary = loaded["summary"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"PASS214_EQ_SOURCE_COMMIT={summary['source_commit']}")
    print(f"PASS214_EQ_CANDIDATE_GROUPS={summary['candidate_groups']}")
    print(f"PASS214_EQ_PROOF_EDGES={summary['proof_edges']}")
    print(f"PASS214_EQ_REUSE_ENTRIES={summary['reusable_registry_entries']}")
    print(f"PASS214_EQ_ISOLATED_COVERED={summary['isolated_candidates_covered_by_proven_clusters']}")
    print(f"PASS214_EQ_REGISTRY_BINDINGS={len(registry.list_bindings())}")
    print(f"PASS214_EQ_SHA256={loaded['reconciliation_sha256']}")
    print("PASS214_SEMANTIC_EQUIVALENCE_RECONCILIATION_OK")


if __name__ == "__main__":
    main()
