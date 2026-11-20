"""Diagnose Module 195's inherited frozen-course source lineage without repinning.

The frozen corpus source and the current course are separate immutable Git
objects. This diagnostic cannot bind either as a native proof, and must never
override the existing SOURCE_BLOB_CHANGED guard.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess

from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import (
    FREEZE, ProofCorpusError,
)

SCHEMA = "HHS_PASS220_M195_FROZEN_COURSE_LINEAGE_DIAGNOSTIC_V1"
SOURCE_PATH = "whitepapers/Harmonicode Algebra - Course"


def _git_blob(root: Path, data: bytes) -> str:
    p = subprocess.run(
        ["git", "hash-object", "--stdin"], input=data, cwd=root,
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return p.stdout.decode("ascii").strip()


def diagnose_course_lineage(root: Path = Path(".")) -> dict:
    root = root.resolve()
    manifest = json.loads((root / FREEZE).read_text(encoding="utf-8"))
    matches = [entry for entry in manifest["files"]
               if entry["path"] == SOURCE_PATH]
    if len(matches) != 1:
        raise ProofCorpusError("M195_FROZEN_COURSE_ENTRY_NOT_UNIQUE")
    expected_sha = matches[0]["git_blob_sha"]
    # Read the Git object, not an untrusted reconstruction from source text.
    historical = subprocess.run(
        ["git", "cat-file", "blob", expected_sha], cwd=root,
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout
    if _git_blob(root, historical) != expected_sha:
        raise ProofCorpusError("M195_FROZEN_GIT_BLOB_IDENTITY_MISMATCH")
    current = (root / SOURCE_PATH).read_bytes()
    current_sha = _git_blob(root, current)
    # An unchanged source is not a drift event. Do not fabricate one.
    result = {
        "schema": SCHEMA, "module": 195,
        "source_path": SOURCE_PATH,
        "manifest_path": FREEZE.as_posix(),
        "historical_blob_sha": expected_sha,
        "historical_sha256": sha256(historical).hexdigest(),
        "historical_byte_count": len(historical),
        "working_blob_sha": current_sha,
        "working_sha256": sha256(current).hexdigest(),
        "working_byte_count": len(current),
        "blob_identity_matches": current_sha == expected_sha,
        "legacy_source_still_recoverable": True,
        "source_graph_binding_eligible": current_sha == expected_sha,
        "freeze_repin_performed": False,
        "course_contents_mutated": False,
        "native_proof_admitted": False,
        "canonical_vm81_admission": False,
        "hash72_minted": False, "hash216_minted": False,
    }
    if not result["blob_identity_matches"]:
        result["source_graph_status"] = "SOURCE_BLOB_CHANGED"
        result["resolution"] = "AUTHORITATIVE_SOURCE_RECONCILIATION_REQUIRED"
    else:
        result["source_graph_status"] = "SOURCE_IDENTITY_MATCH_ONLY"
        result["resolution"] = "NATIVE_PROOF_STILL_REQUIRED"
    return result


if __name__ == "__main__":
    print(json.dumps(diagnose_course_lineage(), sort_keys=True, indent=2))
