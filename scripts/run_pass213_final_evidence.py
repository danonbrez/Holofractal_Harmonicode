#!/usr/bin/env python3
"""Run and persist measured Pass 213 terminal evidence."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile

from hhs_backend.runtime.hhs_pass213_final_evidence_v1 import (
    run_final_evidence,
    validate_final_evidence,
)


def parse_args() -> argparse.Namespace:
    native_root = Path(os.environ.get("TMPDIR", "/tmp"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--secure-library",
        default=str(native_root / "libhhs_pass213_secure_arena.so"),
    )
    parser.add_argument(
        "--dispatch-library",
        default=str(native_root / "libhhs_pass213_native_dispatch.so"),
    )
    parser.add_argument(
        "--output",
        default="pass213-final-evidence.json",
    )
    parser.add_argument("--workdir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="pass213-final-evidence-",
        dir=args.workdir,
    ) as workdir:
        evidence = run_final_evidence(
            secure_library_path=args.secure_library,
            dispatch_library_path=args.dispatch_library,
            workdir=workdir,
        )
    validate_final_evidence(evidence)
    encoded = json.dumps(
        evidence,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    output.write_bytes(encoded + b"\n")
    digest = sha256(encoded + b"\n").hexdigest()
    summary = {
        "schema": evidence["schema"],
        "iteration": evidence["iteration"],
        "semantic_root_hash216": evidence["semantic_root_hash216"],
        "observation_root_hash216": evidence["observation_root_hash216"],
        "receipt_hash72": evidence["receipt_hash72"],
        "full_hydration_bits": evidence["semantic"]["full_hydration"][
            "full_hydration_bits"
        ],
        "compressed_payload_bytes": evidence["semantic"]["full_hydration"][
            "compressed_payload_bytes"
        ],
        "missing_shard_count": evidence["semantic"]["full_hydration"][
            "missing_shard_count"
        ],
        "dispatch_iterations": evidence["semantic"]["native_dispatch"][
            "dispatch_iterations"
        ],
        "artifact_sha256": digest,
    }
    print(
        "PASS213_FINAL_EVIDENCE_SUMMARY="
        + json.dumps(summary, sort_keys=True, separators=(",", ":"))
    )
    print("PASS213_FINAL_EVIDENCE_JSON=" + encoded.decode("utf-8"))
    print(f"PASS213_FINAL_EVIDENCE_OUTPUT={output}")
    print(f"PASS213_FINAL_EVIDENCE_SHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
