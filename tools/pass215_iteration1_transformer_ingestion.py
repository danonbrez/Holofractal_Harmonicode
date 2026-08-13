#!/usr/bin/env python3
"""Run or validate Pass 215 Iteration 1 transformer admission incidence."""
from __future__ import annotations

import argparse
from hashlib import sha1
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass215_iteration1_transformer_ingestion_v1 import (
    FROZEN_PROFILE_GIT_BLOB_SHA1,
    Pass215Iteration1ValidationError,
    build_incidence_evidence,
    load_manifest,
    validate_incidence_evidence,
)


def git_blob_sha1(path: Path) -> str:
    raw = Path(path).read_bytes()
    framed = f"blob {len(raw)}\0".encode("ascii") + raw
    return sha1(framed).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest")
    parser.add_argument("--base-directory")
    parser.add_argument(
        "--profile",
        default=str(ROOT / "contracts/pass215/PASS_215_BENCHMARK_PROFILE.json"),
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--validate")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.validate:
        record = json.loads(Path(args.validate).read_text(encoding="utf-8"))
        validate_incidence_evidence(record)
        output.write_text(
            json.dumps(
                {
                    "schema": "HHS_PASS_215_ITERATION_1_VALIDATION_V1",
                    "valid": True,
                    "evidence_root_hash216": record["evidence_root_hash216"],
                    "receipt_hash72": record["receipt_hash72"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print("PASS215_ITERATION1_EVIDENCE_VALID")
        return

    if not args.manifest:
        raise SystemExit("--manifest is required unless --validate is supplied")
    manifest_path = Path(args.manifest).resolve()
    base_directory = (
        Path(args.base_directory).resolve()
        if args.base_directory
        else manifest_path.parent
    )
    profile_path = Path(args.profile).resolve()
    profile_blob = git_blob_sha1(profile_path)
    if profile_blob != FROZEN_PROFILE_GIT_BLOB_SHA1:
        raise Pass215Iteration1ValidationError(
            "PASS215_I1_FROZEN_PROFILE_FILE_MODIFIED"
        )
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if profile.get("schema") != "HHS_PASS_215_BENCHMARK_PROFILE_V1":
        raise Pass215Iteration1ValidationError("PASS215_I1_FROZEN_PROFILE_SCHEMA_INVALID")
    if profile.get("post_hoc_redefinition_forbidden") is not True:
        raise Pass215Iteration1ValidationError("PASS215_I1_PROFILE_REDEFINITION_GUARD_MISSING")

    manifest = load_manifest(manifest_path)
    evidence = build_incidence_evidence(
        manifest,
        base_directory=base_directory,
        frozen_profile_blob_sha1=profile_blob,
    )
    output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    aggregate = evidence["aggregate"]
    print(f"PASS215_ITERATION1_MODEL_ID={evidence['model_id']}")
    print(f"PASS215_ITERATION1_SOURCE_BYTES={aggregate['source_bytes']}")
    print(f"PASS215_ITERATION1_TIER1_BYTES={aggregate['tier_1_bytes']}")
    print(f"PASS215_ITERATION1_TIER2_BYTES={aggregate['tier_2_bytes']}")
    print(f"PASS215_ITERATION1_TIER3_BYTES={aggregate['tier_3_bytes']}")
    print(f"PASS215_ITERATION1_EVIDENCE_ROOT_HASH216={evidence['evidence_root_hash216']}")
    print(f"PASS215_ITERATION1_RECEIPT_HASH72={evidence['receipt_hash72']}")
    print("PASS215_ITERATION1_INGESTION_INCIDENCE_OK")


if __name__ == "__main__":
    main()
