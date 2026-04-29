"""
HHS Immutable Manifest v1
=========================

Strict manifest guard for protected logic files.

A protected file may differ from its manifest digest only when an explicit
upgrade receipt covers the exact path and resulting digest. Missing manifests
are hard failures in strict mode.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_repo_paths_v1 import repo_root


DEFAULT_PROTECTED_FILES = [
    "HHS_SYSTEM_ANCHOR_v1.md",
    "hhs_runtime/hhs_repo_paths_v1.py",
    "hhs_runtime/hhs_filesystem_hash72_ledger_v1.py",
    "hhs_runtime/hhs_unified_hash72_ledger_v1.py",
    "hhs_runtime/hhs_git_hash72_binding_v1.py",
    "hhs_runtime/hhs_linguistic_validation_pipeline_v1.py",
    "hhs_runtime/hhs_wordnet_relation_enforcer_v1.py",
    "hhs_runtime/hhs_grammar_rule_enforcer_v1.py",
]


@dataclass(frozen=True)
class ManifestFileRecord:
    path: str
    exists: bool
    digest_hash72: str | None
    policy: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def file_digest_hash72(path: str | Path) -> str | None:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    text = p.read_text(encoding="utf-8")
    return hash72_digest(("hhs_manifest_file_digest_v1", str(p), text), width=24)


def default_manifest_path() -> Path:
    return repo_root() / "HHS_KERNEL_MANIFEST_v1.json"


def default_upgrade_receipt_path() -> Path:
    return repo_root() / "HHS_UPGRADE_RECEIPTS_v1.json"


def build_manifest(paths: List[str] | None = None) -> Dict[str, Any]:
    root = repo_root()
    selected = paths or DEFAULT_PROTECTED_FILES
    records: List[ManifestFileRecord] = []
    for rel in selected:
        p = root / rel
        records.append(
            ManifestFileRecord(
                path=rel,
                exists=p.exists(),
                digest_hash72=file_digest_hash72(p),
                policy="IMMUTABLE_WITH_EXPLICIT_UPGRADE_RECEIPT",
            )
        )
    body = {
        "schema": "HHS_IMMUTABLE_MANIFEST_V1",
        "protected_files": [r.to_dict() for r in records],
    }
    body["manifest_hash72"] = hash72_digest(("hhs_immutable_manifest_v1", body["protected_files"]), width=24)
    return body


def write_manifest(path: str | Path | None = None) -> Dict[str, Any]:
    manifest = build_manifest()
    p = Path(path) if path is not None else default_manifest_path()
    p.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return manifest


def _load_upgrade_receipts(path: str | Path | None = None) -> List[Dict[str, Any]]:
    p = Path(path) if path is not None else default_upgrade_receipt_path()
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("receipts", [])


def _upgrade_covers(path: str, actual_digest: str | None, receipts: List[Dict[str, Any]]) -> bool:
    for receipt in receipts:
        if receipt.get("path") != path:
            continue
        if receipt.get("new_digest_hash72") != actual_digest:
            continue
        expected = hash72_digest(("hhs_upgrade_receipt_v1", receipt.get("path"), receipt.get("old_digest_hash72"), receipt.get("new_digest_hash72"), receipt.get("reason")), width=24)
        if receipt.get("receipt_hash72") == expected:
            return True
    return False


def validate_manifest(path: str | Path | None = None, *, upgrade_receipt_path: str | Path | None = None) -> Dict[str, Any]:
    p = Path(path) if path is not None else default_manifest_path()
    if not p.exists():
        return {"status": "MANIFEST_MISSING", "ok": False, "mismatches": [{"path": str(p), "reason": "manifest missing"}]}

    manifest = json.loads(p.read_text(encoding="utf-8"))
    receipts = _load_upgrade_receipts(upgrade_receipt_path)
    root = repo_root()
    mismatches: List[Dict[str, Any]] = []
    covered: List[Dict[str, Any]] = []

    for record in manifest.get("protected_files", []):
        rel = record["path"]
        current = file_digest_hash72(root / rel)
        expected = record.get("digest_hash72")
        if current != expected:
            m = {"path": rel, "expected": expected, "actual": current}
            if _upgrade_covers(rel, current, receipts):
                covered.append(m)
            else:
                mismatches.append(m)

    manifest_hash_ok = manifest.get("manifest_hash72") == hash72_digest(("hhs_immutable_manifest_v1", manifest.get("protected_files", [])), width=24)
    if not manifest_hash_ok:
        mismatches.append({"path": str(p), "reason": "manifest_hash72 mismatch"})

    ok = not mismatches
    return {
        "status": "MANIFEST_OK" if ok and not covered else "MANIFEST_OK_WITH_UPGRADE_RECEIPTS" if ok else "MANIFEST_MISMATCH",
        "ok": ok,
        "covered_upgrades": covered,
        "mismatches": mismatches,
    }


def make_upgrade_receipt(path: str, old_digest_hash72: str | None, new_digest_hash72: str | None, reason: str) -> Dict[str, Any]:
    receipt_hash72 = hash72_digest(("hhs_upgrade_receipt_v1", path, old_digest_hash72, new_digest_hash72, reason), width=24)
    return {"schema": "HHS_UPGRADE_RECEIPT_V1", "path": path, "old_digest_hash72": old_digest_hash72, "new_digest_hash72": new_digest_hash72, "reason": reason, "receipt_hash72": receipt_hash72}


if __name__ == "__main__":
    print(json.dumps(validate_manifest(), indent=2, sort_keys=True))
