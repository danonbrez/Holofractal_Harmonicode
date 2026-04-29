"""
HHS Immutable Manifest v1
=========================

Protects core files by recording their current Hash72 digests and validating
that future runs either match the manifest or provide an explicit upgrade policy.

This guard does not change protected files. It only observes and reports.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_repo_paths_v1 import repo_root, runtime_artifact_path


DEFAULT_PROTECTED_FILES = [
    "HHS_SYSTEM_ANCHOR_v1.md",
    "hhs_runtime/hhs_repo_paths_v1.py",
    "hhs_runtime/hhs_filesystem_hash72_ledger_v1.py",
    "hhs_runtime/hhs_unified_hash72_ledger_v1.py",
    "hhs_runtime/hhs_commit_acceptance_gate_v1.py",
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


def default_manifest_path() -> Path:
    return repo_root() / "HHS_KERNEL_MANIFEST_v1.json"


def write_manifest(path: str | Path | None = None) -> Dict[str, Any]:
    manifest = build_manifest()
    p = Path(path) if path is not None else default_manifest_path()
    p.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return manifest


def validate_manifest(path: str | Path | None = None, *, allow_missing_manifest: bool = True) -> Dict[str, Any]:
    p = Path(path) if path is not None else default_manifest_path()
    if not p.exists():
        if allow_missing_manifest:
            generated = build_manifest()
            return {
                "status": "MANIFEST_MISSING_GENERATED_REFERENCE",
                "ok": True,
                "missing_manifest": str(p),
                "generated_manifest_hash72": generated["manifest_hash72"],
                "mismatches": [],
            }
        return {"status": "MANIFEST_MISSING", "ok": False, "mismatches": [{"path": str(p), "reason": "manifest missing"}]}

    manifest = json.loads(p.read_text(encoding="utf-8"))
    root = repo_root()
    mismatches: List[Dict[str, Any]] = []
    for record in manifest.get("protected_files", []):
        rel = record["path"]
        current = file_digest_hash72(root / rel)
        if current != record.get("digest_hash72"):
            mismatches.append({
                "path": rel,
                "expected": record.get("digest_hash72"),
                "actual": current,
                "policy": record.get("policy"),
            })
    return {
        "status": "MANIFEST_OK" if not mismatches else "MANIFEST_MISMATCH",
        "ok": not mismatches,
        "manifest_path": str(p),
        "manifest_hash72": manifest.get("manifest_hash72"),
        "mismatches": mismatches,
    }


if __name__ == "__main__":
    print(json.dumps(write_manifest(), indent=2, sort_keys=True, ensure_ascii=False))
