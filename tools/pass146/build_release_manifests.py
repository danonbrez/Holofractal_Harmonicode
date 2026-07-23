#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from hhs_runtime.pass145.canonical import canonical_json, hash72

PARENT_NAME = "hhs_pass_145_android_knowledge_enterprise_platform_full_inherited_pass_history_nucleus.zip"
EXPECTED_PARENT = "d9d2125501177095fd1780be2f2294ec40dd878fdb67fdd4e8b9431fa7ac4303"
PARENT_ROOT = "hhs145_work/"
ART = ROOT / "release_artifacts/pass146/manifests"
INHERITANCE = ART / "PASS_146_INHERITANCE_MANIFEST.json"
FILES = ART / "PASS_146_FILE_MANIFEST.json"
RELEASE = ROOT / "PASS_146_RELEASE_MANIFEST.json"
SELF = {x.relative_to(ROOT).as_posix() for x in (INHERITANCE, FILES, RELEASE)}


def transient(rel: str) -> bool:
    parts = Path(rel).parts
    return "__pycache__" in parts or ".pytest_cache" in parts or rel.endswith((".pyc", ".pyo", "-wal", "-shm")) or rel.endswith(".pass146-session.json") or rel.endswith(".pre_crossnode") or rel == "release_artifacts/pass146/manifests/PASS_146_MANIFEST_BUILD.log"


def resolve_parent() -> Path:
    configured = os.environ.get("HHS_PASS145_ARCHIVE")
    candidates = [Path(configured)] if configured else []
    candidates.extend(parent / PARENT_NAME for parent in (ROOT, *ROOT.parents))
    for candidate in candidates:
        if candidate.is_file(): return candidate.resolve()
    raise FileNotFoundError(PARENT_NAME)


def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def write(path: Path, label: str, payload: dict) -> dict:
    value = dict(payload); value.pop("manifest_hash72", None); value["manifest_hash72"] = hash72(label, value)
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(canonical_json(value) + "\n", encoding="utf-8"); return value


def main() -> int:
    parent = resolve_parent(); parent_hash = sha(parent.read_bytes())
    parent_files = {}
    with zipfile.ZipFile(parent) as z:
        for info in z.infolist():
            if info.is_dir() or not info.filename.startswith(PARENT_ROOT): continue
            rel = info.filename[len(PARENT_ROOT):]
            if rel and not transient(rel): parent_files[rel] = sha(z.read(info))
    current_files = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file(): continue
        rel = path.relative_to(ROOT).as_posix()
        if transient(rel) or rel in SELF: continue
        current_files[rel] = sha(path.read_bytes())
    missing = sorted(set(parent_files) - set(current_files))
    unchanged = sorted(k for k in parent_files if current_files.get(k) == parent_files[k])
    repaired = sorted(k for k in parent_files if k in current_files and current_files[k] != parent_files[k])
    additive = sorted(set(current_files) - set(parent_files))
    inheritance = write(INHERITANCE, "hhs_pass146_inheritance_manifest_v1", {
        "schema": "HHS_PASS146_INHERITANCE_MANIFEST_V1", "parent_archive": parent.name,
        "parent_observed_sha256": parent_hash, "parent_expected_sha256": EXPECTED_PARENT, "parent_hash_equal": parent_hash == EXPECTED_PARENT,
        "parent_authoritative_file_count": len(parent_files), "unchanged_inherited_file_count": len(unchanged),
        "repaired_inherited_file_count": len(repaired), "missing_inherited_file_count": len(missing), "additive_pass146_file_count": len(additive),
        "repaired_inherited_files": repaired, "missing_inherited_files": missing, "additive_pass146_files": additive,
        "full_inherited_pass_history_nucleus": not missing, "pass_local_delta": False
    })
    file_manifest = write(FILES, "hhs_pass146_file_manifest_v1", {
        "schema": "HHS_PASS146_FILE_MANIFEST_V1", "file_count": len(current_files),
        "files": [{"path": k, "sha256": current_files[k], "size_bytes": (ROOT / k).stat().st_size} for k in sorted(current_files)]
    })
    closure = json.loads((ROOT / "HHS_PASS_146_CLOSURE_RECEIPT.json").read_text())
    test_report = json.loads((ROOT / "release_artifacts/pass146/reports/PASS_146_TEST_REPORT.json").read_text())
    release = write(RELEASE, "hhs_pass146_release_manifest_v1", {
        "schema": "HHS_PASS146_RELEASE_MANIFEST_V1", "pass_id": "HHS-P146", "parent": "HHS-P145",
        "release_scope": "FULL_INHERITED_HHS_PASS_HISTORY_NUCLEUS", "parent_archive_sha256": parent_hash,
        "inheritance_manifest_hash72": inheritance["manifest_hash72"], "file_manifest_hash72": file_manifest["manifest_hash72"],
        "dependency_scoped_tests": test_report["dependency_scoped_tests"], "terminal_status": closure["terminal_status"],
        "complete_parent_files_preserved": len(missing) == 0, "full_nucleus_file_count_before_self_manifests": len(current_files)
    })
    print(json.dumps({"parent": len(parent_files), "unchanged": len(unchanged), "repaired": len(repaired), "missing": len(missing), "additive": len(additive), "release": release["terminal_status"]}, indent=2))
    return 0 if not missing and parent_hash == EXPECTED_PARENT else 1

if __name__ == "__main__": raise SystemExit(main())
