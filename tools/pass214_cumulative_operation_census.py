#!/usr/bin/env python3
"""Generate the final-quality Pass 214 cumulative operation/capability census."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_final_v1 import (
    build_final_cumulative_operation_census,
    load_and_validate_final_census,
    write_final_census,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--source-ref", default="HEAD")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-source-bytes", type=int, default=4 * 1024 * 1024)
    args = parser.parse_args()

    result = build_final_cumulative_operation_census(
        Path(args.repository_root),
        source_ref=args.source_ref,
        max_source_bytes=args.max_source_bytes,
    )
    output = Path(args.output)
    write_final_census(result, output)
    load_and_validate_final_census(output)
    summary = result["summary"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"PASS214_OPERATION_CENSUS_SOURCE_COMMIT={summary['source_commit']}")
    print(f"PASS214_OPERATION_CENSUS_RAW_IDENTITIES={summary['coverage']['raw_operation_identities']}")
    print(f"PASS214_OPERATION_CENSUS_ISOLATED={summary['reuse_accounting']['isolated_implementation_candidates']}")
    print(f"PASS214_OPERATION_CENSUS_SEMANTIC_GROUPS={summary['semantic_accounting']['normalized_semantic_name_groups']}")
    print(f"PASS214_OPERATION_CENSUS_SHA256={result['census_sha256']}")
    print("PASS214_CUMULATIVE_OPERATION_CENSUS_OK")


if __name__ == "__main__":
    main()
