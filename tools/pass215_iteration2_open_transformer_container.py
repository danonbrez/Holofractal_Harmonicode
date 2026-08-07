#!/usr/bin/env python3
"""CLI for Pass 215 Iteration 2 real open-transformer container evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hhs_backend.runtime.hhs_pass215_iteration2_open_transformer_container_v1 import (
    build_container_evidence_from_path,
    validate_container_evidence,
)


def _write(path: Path | None, value: Any) -> None:
    encoded = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if path is None:
        print(encoded, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--container", type=Path)
    mode.add_argument("--validate", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-kind", default="local_or_fixture")
    parser.add_argument("--repo-id")
    parser.add_argument("--revision")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()

    if args.validate is not None:
        evidence = json.loads(args.validate.read_text(encoding="utf-8"))
        validate_container_evidence(evidence)
        result = {
            "schema": "HHS_PASS_215_ITERATION_2_VALIDATION_V1",
            "valid": True,
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        }
        _write(args.output, result)
        print("PASS215_ITERATION2_EVIDENCE_VALID")
        return 0

    source = {
        "kind": args.source_kind,
        "repo_id": args.repo_id,
        "revision": args.revision,
    }
    evidence = build_container_evidence_from_path(
        args.container,
        source=source,
        expected_sha256=args.expected_sha256,
    )
    _write(args.output, evidence)
    accounting = evidence["accounting"]
    storage = evidence["storage_stream_measurement"]
    canonical = evidence["canonical_quantized_stream_measurement"]
    print(f"PASS215_ITERATION2_FORMAT={evidence['container']['format']}")
    print(f"PASS215_ITERATION2_TENSORS={evidence['container']['tensor_count']}")
    print(f"PASS215_ITERATION2_FILE_BYTES={accounting['file_bytes']}")
    print(f"PASS215_ITERATION2_TENSOR_BYTES={accounting['tensor_payload_bytes']}")
    print(f"PASS215_ITERATION2_CANONICAL_TENSOR_BYTES={accounting['canonical_quantized_or_integer_tensor_bytes']}")
    print(f"PASS215_ITERATION2_OPAQUE_FLOAT_BYTES={accounting['opaque_float_tensor_bytes']}")
    print(f"PASS215_ITERATION2_STORAGE_ADMITTED_BYTES={storage['admitted_bytes']}")
    print(f"PASS215_ITERATION2_CANONICAL_ADMITTED_BYTES={canonical['admitted_bytes']}")
    print(f"PASS215_ITERATION2_EVIDENCE_ROOT_HASH216={evidence['evidence_root_hash216']}")
    print(f"PASS215_ITERATION2_RECEIPT_HASH72={evidence['receipt_hash72']}")
    print("PASS215_ITERATION2_OPEN_TRANSFORMER_CONTAINER_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
