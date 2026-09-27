"""Immutable native-kernel manifest validation with explicit successor lineage.

Pass 078 remains the frozen baseline. A later file identity is accepted only
when a repository-visible successor record binds the exact baseline identity,
exact current SHA-256/size/Git blob, ancestral validated/merge commits, and
declared evidence files. Unlisted drift remains fail-closed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Dict, Mapping

from hhs_runtime.hhs_repo_paths_v1 import repo_root

MANIFEST_NAME = "PASS_078_KERNEL_FREEZE_MANIFEST.json"
SUCCESSOR_LINEAGE_NAME = "PASS_078_KERNEL_SUCCESSOR_LINEAGE_V1.json"
EXPECTED_SCHEMA = "HHS_KERNEL_FREEZE_MANIFEST_PASS_078_V1"
EXPECTED_SUCCESSOR_SCHEMA = "HHS_PASS_078_KERNEL_SUCCESSOR_LINEAGE_V1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob(base: Path, relative: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(base), "rev-parse", f"HEAD:{relative}"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _is_ancestor(base: Path, commit: str) -> bool:
    if not commit:
        return False
    result = subprocess.run(
        ["git", "-C", str(base), "merge-base", "--is-ancestor", commit, "HEAD"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _load_successor_lineage(base: Path) -> tuple[dict[str, Mapping[str, Any]], list[dict[str, Any]]]:
    path = base / SUCCESSOR_LINEAGE_NAME
    errors: list[dict[str, Any]] = []
    if not path.is_file():
        return {}, [{"kind": "SUCCESSOR_LINEAGE_MISSING", "path": SUCCESSOR_LINEAGE_NAME}]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [{"kind": "SUCCESSOR_LINEAGE_UNREADABLE", "error": str(exc)}]
    if payload.get("schema") != EXPECTED_SUCCESSOR_SCHEMA:
        errors.append({"kind": "SUCCESSOR_LINEAGE_SCHEMA_MISMATCH", "actual": payload.get("schema")})
    if payload.get("baseline_manifest") != MANIFEST_NAME:
        errors.append({"kind": "SUCCESSOR_BASELINE_MANIFEST_MISMATCH", "actual": payload.get("baseline_manifest")})
    records: dict[str, Mapping[str, Any]] = {}
    for row in payload.get("approved_successors", []):
        if not isinstance(row, Mapping):
            errors.append({"kind": "SUCCESSOR_RECORD_INVALID"})
            continue
        relative = row.get("repository_path")
        if not isinstance(relative, str) or not relative:
            errors.append({"kind": "SUCCESSOR_PATH_INVALID", "path": relative})
            continue
        if relative in records:
            errors.append({"kind": "SUCCESSOR_PATH_DUPLICATE", "path": relative})
            continue
        records[relative] = row
    return records, errors


def _successor_reasons(
    base: Path,
    frozen: Mapping[str, Any],
    successor: Mapping[str, Any],
    *,
    actual_size: int,
    actual_sha256: str,
) -> tuple[list[str], str | None]:
    relative = str(frozen.get("path"))
    reasons: list[str] = []
    if successor.get("baseline_sha256") != frozen.get("sha256"):
        reasons.append("BASELINE_SHA256_BINDING_MISMATCH")
    if successor.get("baseline_size") != frozen.get("size"):
        reasons.append("BASELINE_SIZE_BINDING_MISMATCH")
    if successor.get("approved_current_sha256") != actual_sha256:
        reasons.append("CURRENT_SHA256_NOT_APPROVED")
    if successor.get("approved_current_size") != actual_size:
        reasons.append("CURRENT_SIZE_NOT_APPROVED")
    current_blob = _git_blob(base, relative)
    if current_blob is None or successor.get("approved_current_git_blob") != current_blob:
        reasons.append("CURRENT_GIT_BLOB_NOT_APPROVED")
    validated_head = str(successor.get("validated_implementation_head") or "")
    repair_merge = str(successor.get("repair_merge_commit") or "")
    if not _is_ancestor(base, validated_head):
        reasons.append("VALIDATED_IMPLEMENTATION_HEAD_NOT_ANCESTRAL")
    if not _is_ancestor(base, repair_merge):
        reasons.append("REPAIR_MERGE_NOT_ANCESTRAL")
    semantic_boundary = successor.get("semantic_boundary")
    if not isinstance(semantic_boundary, str) or not semantic_boundary.strip():
        reasons.append("SEMANTIC_BOUNDARY_MISSING")
    evidence = successor.get("evidence_files")
    if not isinstance(evidence, list) or not evidence:
        reasons.append("SUCCESSOR_EVIDENCE_MISSING")
    else:
        for item in evidence:
            if not isinstance(item, str) or not item or not (base / item).is_file():
                reasons.append(f"SUCCESSOR_EVIDENCE_FILE_MISSING:{item}")
    return sorted(set(reasons)), current_blob


def validate_manifest(root: Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root is not None else repo_root()
    manifest_path = base / MANIFEST_NAME
    if not manifest_path.is_file():
        return {"ok": False, "status": "MANIFEST_MISSING", "manifest": str(manifest_path)}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "status": "MANIFEST_UNREADABLE", "error": str(exc)}

    errors: list[dict[str, Any]] = []
    if manifest.get("schema") != EXPECTED_SCHEMA:
        errors.append({"kind": "SCHEMA_MISMATCH", "actual": manifest.get("schema")})

    successors, successor_load_errors = _load_successor_lineage(base)
    errors.extend(successor_load_errors)
    checked = []
    successor_count = 0

    for record in manifest.get("files", []):
        relative = record.get("path")
        path = base / relative if isinstance(relative, str) else None
        if path is None or not path.is_file():
            errors.append({"kind": "FROZEN_FILE_MISSING", "path": relative})
            continue
        actual_size = path.stat().st_size
        actual_sha256 = _sha256(path)
        expected_size = record.get("size")
        expected_sha256 = record.get("sha256")
        baseline_match = actual_size == expected_size and actual_sha256 == expected_sha256

        if baseline_match:
            checked.append({
                "path": relative,
                "size": actual_size,
                "sha256": actual_sha256,
                "ok": True,
                "match_mode": "PASS078_BASELINE_IDENTITY",
            })
            continue

        successor = successors.get(str(relative))
        if successor is None:
            checked.append({
                "path": relative,
                "size": actual_size,
                "sha256": actual_sha256,
                "ok": False,
                "match_mode": "UNLISTED_DRIFT",
            })
            errors.append({
                "kind": "FROZEN_FILE_MISMATCH",
                "path": relative,
                "expected_size": expected_size,
                "actual_size": actual_size,
                "expected_sha256": expected_sha256,
                "actual_sha256": actual_sha256,
            })
            continue

        reasons, current_blob = _successor_reasons(
            base,
            record,
            successor,
            actual_size=actual_size,
            actual_sha256=actual_sha256,
        )
        ok = not reasons
        checked.append({
            "path": relative,
            "size": actual_size,
            "sha256": actual_sha256,
            "git_blob": current_blob,
            "ok": ok,
            "match_mode": "EXPLICIT_VALIDATED_SUCCESSOR" if ok else "INVALID_SUCCESSOR",
            "successor_pass": successor.get("successor_pass"),
            "successor_iteration": successor.get("successor_iteration"),
            "semantic_boundary": successor.get("semantic_boundary"),
            "repair_merge_commit": successor.get("repair_merge_commit"),
            "validated_implementation_head": successor.get("validated_implementation_head"),
        })
        if ok:
            successor_count += 1
        else:
            errors.append({
                "kind": "INVALID_FROZEN_FILE_SUCCESSOR",
                "path": relative,
                "reasons": reasons,
                "actual_size": actual_size,
                "actual_sha256": actual_sha256,
                "actual_git_blob": current_blob,
            })

    if not manifest.get("files"):
        errors.append({"kind": "EMPTY_FREEZE_MANIFEST"})

    return {
        "ok": not errors,
        "status": (
            "VERIFIED_WITH_EXPLICIT_SUCCESSORS"
            if not errors and successor_count
            else "VERIFIED" if not errors else "REJECTED"
        ),
        "schema": EXPECTED_SCHEMA,
        "manifest": MANIFEST_NAME,
        "successor_lineage": SUCCESSOR_LINEAGE_NAME,
        "manifest_root_hash72": manifest.get("pass078_kernel_freeze_manifest_root_hash72"),
        "checked_file_count": len(checked),
        "approved_successor_count": successor_count,
        "checked_files": checked,
        "errors": errors,
    }


if __name__ == "__main__":
    print(json.dumps(validate_manifest(), indent=2, sort_keys=True))
