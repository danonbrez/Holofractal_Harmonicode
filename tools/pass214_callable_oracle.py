#!/usr/bin/env python3
"""Execute and validate Pass 214 Iteration 4 repository-callable oracles."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hhs_backend.runtime.hhs_pass214_callable_oracle_v1 import (
    build_callable_oracle_bundle,
    canonical_json,
    load_and_validate_callable_oracle_outputs,
    write_callable_oracle_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--iteration2-directory", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    bundle = build_callable_oracle_bundle(
        args.repository_root,
        args.iteration2_directory,
        manifest,
    )
    paths = write_callable_oracle_outputs(bundle, args.output_directory)
    loaded = load_and_validate_callable_oracle_outputs(args.output_directory)
    summary = loaded["iteration4_summary"]
    print(canonical_json(summary))
    print(f"PASS214_ITERATION4_SOURCE_COMMIT={summary['source_commit']}")
    print(f"PASS214_ITERATION4_SOURCE_TREE={summary['source_tree']}")
    print(f"PASS214_ITERATION4_WORKLOADS={summary['coverage']['workloads']}")
    print(f"PASS214_ITERATION4_EQUIVALENCE_VERIFIED={summary['coverage']['equivalence_verified']}")
    print(f"PASS214_ITERATION4_DIVERGENT={summary['coverage']['divergent']}")
    print(f"PASS214_ITERATION4_EXECUTION_ERROR={summary['coverage']['execution_error']}")
    print(f"PASS214_ITERATION4_SEMANTIC_ROOT={summary['roots']['iteration4_semantic_root_hash216']}")
    print(f"PASS214_ITERATION4_RECEIPT_HASH72={summary['receipt_hash72']}")
    print("PASS214_ITERATION4_REPOSITORY_CALLABLE_ORACLE_OK")
    for name, path in sorted(paths.items()):
        print(f"PASS214_ITERATION4_OUTPUT_{name.upper()}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
