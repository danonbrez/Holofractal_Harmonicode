#!/usr/bin/env python3
"""Generate the bounded exact-head Iteration 4 callable validation manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import hash216 as pass213_hash216
from hhs_backend.runtime.hhs_pass214_callable_oracle_v1 import (
    ITERATION3_CONTRACT_BLOB,
    ITERATION3_IMPLEMENTATION_COMMIT,
    ITERATION3_IMPLEMENTATION_RECORD_BLOB,
    ITERATION3_RUNTIME_LOADER_BLOB,
    PASS213_CLOSURE,
    canonical_json,
)

SOURCE_PATH = "hhs_backend/runtime/hhs_agent_algorithm_identity_v1.py"
TARGET_PATH = "hhs_backend/runtime/hhs_agent_contribution_provenance_v1.py"


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def fixture_root(kind: str, source_commit: str, source_tree: str) -> str:
    payload = canonical_json(
        {
            "schema": "HHS_PASS_214_ITERATION_4_PASS213_VALIDATION_FIXTURE_V1",
            "kind": kind,
            "pass213_closure_commit": PASS213_CLOSURE,
            "source_commit": source_commit,
            "source_tree": source_tree,
            "production_authority_claimed": False,
        }
    ).encode("utf-8")
    return pass213_hash216("pass214-iteration4-validation-fixture", payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.repository_root.resolve()
    source_commit = git(root, "rev-parse", "HEAD")
    source_tree = git(root, "rev-parse", "HEAD^{tree}")
    source_blob = git(root, "rev-parse", f"HEAD:{SOURCE_PATH}")
    target_blob = git(root, "rev-parse", f"HEAD:{TARGET_PATH}")
    if source_blob != target_blob:
        raise SystemExit("PASS214_ITERATION4_SELECTED_WRAPPER_BLOBS_DIVERGED")
    manifest = {
        "schema": "HHS_PASS_214_ITERATION_4_CALLABLE_ORACLE_MANIFEST_V1",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "pass213_authority": {
            "closure_commit": PASS213_CLOSURE,
            "authority_profile": "PASS213_DEPENDENCY_SCOPED_VALIDATION_FIXTURE",
            "trusted_timestamp_anchor_root_hash216": fixture_root("trusted_timestamp_anchor", source_commit, source_tree),
            "moving_tensor_root_hash216": fixture_root("moving_tensor", source_commit, source_tree),
            "native_dispatch_receipt_root_hash216": fixture_root("native_dispatch_receipt", source_commit, source_tree),
            "production_authority_claimed": False,
        },
        "iteration3_binding": {
            "implementation_commit": ITERATION3_IMPLEMENTATION_COMMIT,
            "contract_blob_sha1": ITERATION3_CONTRACT_BLOB,
            "runtime_loader_blob_sha1": ITERATION3_RUNTIME_LOADER_BLOB,
            "implementation_record_blob_sha1": ITERATION3_IMPLEMENTATION_RECORD_BLOB,
        },
        "execution_policy": {
            "timeout_seconds": 120,
            "cpu_seconds": 60,
            "address_space_bytes": 2147483648,
            "max_stdout_bytes": 1048576,
            "max_captured_bytes": 65536,
        },
        "workloads": [
            {
                "workload_id": "pass214-i4-agent-identity-wrapper-equivalence",
                "source": {
                    "path": SOURCE_PATH,
                    "module": "hhs_backend.runtime.hhs_agent_algorithm_identity_v1",
                    "symbol": "self_test",
                    "git_blob_sha1": source_blob,
                },
                "target": {
                    "path": TARGET_PATH,
                    "module": "hhs_backend.runtime.hhs_agent_contribution_provenance_v1",
                    "symbol": "self_test",
                    "git_blob_sha1": target_blob,
                },
                "vectors": [{"args": [], "kwargs": {}}],
                "adapter": {"class": "IDENTITY", "config": {}},
            }
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS214_ITERATION4_MANIFEST={args.output}")
    print(f"PASS214_ITERATION4_SELECTED_BLOB={source_blob}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
