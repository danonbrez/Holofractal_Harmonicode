#!/usr/bin/env python3
"""CLI for Pass 215 Iteration 3 quantization-block structure evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass215_iteration3_quant_block_structure_v1 import (
    build_block_structure_evidence_from_path,
    validate_block_structure_evidence,
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
        validate_block_structure_evidence(evidence)
        result = {
            "schema": "HHS_PASS_215_ITERATION_3_VALIDATION_V1",
            "valid": True,
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        }
        _write(args.output, result)
        print("PASS215_ITERATION3_EVIDENCE_VALID")
        return 0

    source = {
        "kind": args.source_kind,
        "repo_id": args.repo_id,
        "revision": args.revision,
    }
    evidence = build_block_structure_evidence_from_path(
        args.container,
        source=source,
        expected_sha256=args.expected_sha256,
    )
    _write(args.output, evidence)
    global_record = evidence["global"]
    scale = evidence["decomposed_pass212_measurements"]["scale_stream"]
    code = evidence["decomposed_pass212_measurements"]["code_stream"]
    print(f"PASS215_ITERATION3_TENSORS={global_record['supported_tensor_count']}")
    print(f"PASS215_ITERATION3_BLOCKS={global_record['supported_block_count']}")
    print(f"PASS215_ITERATION3_RAW_COMPARED_BYTES={global_record['raw_compared_bytes']}")
    print(f"PASS215_ITERATION3_SELECTED_BYTES={global_record['selected_reversible_bytes']}")
    print(f"PASS215_ITERATION3_GAIN_BYTES={global_record['selected_gain_bytes_vs_raw']}")
    print(f"PASS215_ITERATION3_SCALE_BYTES={global_record['scale_stream_bytes']}")
    print(f"PASS215_ITERATION3_CODE_BYTES={global_record['code_stream_bytes']}")
    print(f"PASS215_ITERATION3_SCALE_PASS212_ADMITTED_BYTES={scale['admitted_bytes']}")
    print(f"PASS215_ITERATION3_CODE_PASS212_ADMITTED_BYTES={code['admitted_bytes']}")
    print(f"PASS215_ITERATION3_UNSUPPORTED_BYTES={global_record['unsupported_passthrough_bytes']}")
    print(f"PASS215_ITERATION3_EVIDENCE_ROOT_HASH216={evidence['evidence_root_hash216']}")
    print(f"PASS215_ITERATION3_RECEIPT_HASH72={evidence['receipt_hash72']}")
    print("PASS215_ITERATION3_QUANT_BLOCK_STRUCTURE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
