"""Pass 220 V162: read-only frozen-course Git-blob provenance diagnostic.

Never replaces the frozen corpus gate or authorizes native admission.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import FREEZE

SCHEMA = "HHS_PASS220_V162_COURSE_SOURCE_DIVERGENCE_V1"
COURSE = "whitepapers/Harmonicode Algebra - Course"


class V162CourseSourceError(ValueError):
    pass


def _git(root: Path, *argv: str) -> bytes:
    try:
        return subprocess.run(
            ["git", *argv], cwd=root, capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise V162CourseSourceError("V162_GIT_OBJECT_UNAVAILABLE") from exc


def inspect_divergence(root: Path = Path(".")) -> dict:
    root = root.resolve()
    freeze = json.loads((root / FREEZE).read_text("utf-8"))
    matches = [row for row in freeze["files"] if row["path"] == COURSE]
    if len(matches) != 1:
        raise V162CourseSourceError("V162_FROZEN_ENTRY_REQUIRED")
    expected = matches[0]["git_blob_sha"]
    if (not isinstance(expected, str) or len(expected) != 40 or
            any(ch not in "0123456789abcdef" for ch in expected)):
        raise V162CourseSourceError("V162_FROZEN_BLOB_SHA_INVALID")
    if _git(root, "cat-file", "-t", expected).strip() != b"blob":
        raise V162CourseSourceError("V162_FROZEN_OBJECT_NOT_BLOB")
    frozen = _git(root, "cat-file", "blob", expected)
    current = (root / COURSE).read_bytes()
    working = _git(root, "hash-object", "--", COURSE).decode().strip()
    committed = _git(root, "rev-parse", "HEAD:" + COURSE).decode().strip()
    if len(working) != 40 or len(committed) != 40:
        raise V162CourseSourceError("V162_GIT_IDENTITIES_INVALID")
    return {
        "schema": SCHEMA, "course_path": COURSE,
        "frozen_git_blob_sha": expected,
        "head_git_blob_sha": committed,
        "working_git_blob_sha": working,
        "frozen_bytes": len(frozen),
        "working_bytes": len(current),
        "frozen_sha256": sha256(frozen).hexdigest(),
        "working_sha256": sha256(current).hexdigest(),
        "working_tree_matches_head": working == committed,
        "freeze_matches_head": expected == committed,
        "source_integrity_gate_satisfied": expected == working,
        "native_admission_authority": False,
        "hash72_hash216_minted": False,
        "mutation_authority": False,
    }


def require_frozen_identity(root: Path = Path(".")) -> dict:
    report = inspect_divergence(root)
    if not report["source_integrity_gate_satisfied"]:
        raise V162CourseSourceError(
            "V162_COURSE_FREEZE_DIVERGENCE:"
            + report["frozen_git_blob_sha"] + ":" + report["working_git_blob_sha"]
        )
    return report
