"""Immutable native-kernel manifest validation.

Validates the committed Pass 078 freeze manifest against the current frozen
native files. This module is read-only and creates no execution authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_repo_paths_v1 import repo_root

MANIFEST_NAME = "PASS_078_KERNEL_FREEZE_MANIFEST.json"
EXPECTED_SCHEMA = "HHS_KERNEL_FREEZE_MANIFEST_PASS_078_V1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(root: Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root is not None else repo_root()
    manifest_path = base / MANIFEST_NAME
    if not manifest_path.is_file():
        return {"ok": False, "status": "MANIFEST_MISSING", "manifest": str(manifest_path)}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "status": "MANIFEST_UNREADABLE", "error": str(exc)}

    errors = []
    if manifest.get("schema") != EXPECTED_SCHEMA:
        errors.append({"kind": "SCHEMA_MISMATCH", "actual": manifest.get("schema")})

    checked = []
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
        match = actual_size == expected_size and actual_sha256 == expected_sha256
        checked.append({"path": relative, "size": actual_size, "sha256": actual_sha256, "ok": match})
        if not match:
            errors.append({
                "kind": "FROZEN_FILE_MISMATCH",
                "path": relative,
                "expected_size": expected_size,
                "actual_size": actual_size,
                "expected_sha256": expected_sha256,
                "actual_sha256": actual_sha256,
            })

    if not manifest.get("files"):
        errors.append({"kind": "EMPTY_FREEZE_MANIFEST"})

    return {
        "ok": not errors,
        "status": "VERIFIED" if not errors else "REJECTED",
        "schema": EXPECTED_SCHEMA,
        "manifest": MANIFEST_NAME,
        "manifest_root_hash72": manifest.get("pass078_kernel_freeze_manifest_root_hash72"),
        "checked_file_count": len(checked),
        "checked_files": checked,
        "errors": errors,
    }


if __name__ == "__main__":
    print(json.dumps(validate_manifest(), indent=2, sort_keys=True))
