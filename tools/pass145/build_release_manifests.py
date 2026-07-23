#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass145.canonical import canonical_json, hash72

PARENT_NAME = "hhs_pass_144_natural_language_documentation_whitepapers_lemma_corpus_checkpoint.zip"
EXPECTED_PARENT_SHA256 = "44acd48498cf31030d67cf2184e9532755c8a4309bb49980acedc0bb783ef17e"
PARENT_ROOT = "hhs144_work/"
MANIFEST_DIR = ROOT / "release_artifacts" / "pass145" / "manifests"
INHERITANCE_PATH = MANIFEST_DIR / "PASS_145_INHERITANCE_MANIFEST.json"
FILE_PATH = MANIFEST_DIR / "PASS_145_FILE_MANIFEST.json"
RELEASE_PATH = ROOT / "PASS_145_RELEASE_MANIFEST.json"
SELF_EXCLUSIONS = {
    INHERITANCE_PATH.relative_to(ROOT).as_posix(),
    FILE_PATH.relative_to(ROOT).as_posix(),
    RELEASE_PATH.relative_to(ROOT).as_posix(),
}


def transient(rel: str) -> bool:
    parts = Path(rel).parts
    return (
        "__pycache__" in parts
        or ".pytest_cache" in parts
        or rel.endswith(".pyc")
        or rel.endswith(".pyo")
    )


def resolve_parent() -> Path:
    configured = os.environ.get("HHS_PASS144_ARCHIVE")
    candidates = [Path(configured)] if configured else []
    candidates.extend(ancestor / PARENT_NAME for ancestor in (ROOT, *ROOT.parents))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        f"Pass 144 parent archive unavailable; set HHS_PASS144_ARCHIVE or place {PARENT_NAME} in a repository ancestor"
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, label: str, payload: dict) -> None:
    body = dict(payload)
    body["manifest_hash72"] = hash72(label, payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(body) + "\n", encoding="utf-8")


def main() -> int:
    parent = resolve_parent()
    parent_sha = sha256_bytes(parent.read_bytes())
    if parent_sha != EXPECTED_PARENT_SHA256:
        raise RuntimeError(f"Parent hash mismatch: {parent_sha}")

    with zipfile.ZipFile(parent) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"Parent archive integrity failure at {bad}")
        inherited = {
            name[len(PARENT_ROOT):]: sha256_bytes(archive.read(name))
            for name in archive.namelist()
            if name.startswith(PARENT_ROOT)
            and not name.endswith("/")
            and not transient(name[len(PARENT_ROOT):])
        }

    current = {}
    file_entries = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if transient(rel) or rel in SELF_EXCLUSIONS:
            continue
        digest = sha256_bytes(path.read_bytes())
        current[rel] = digest
        file_entries.append({"path": rel, "sha256": digest, "size_bytes": path.stat().st_size})

    inherited_paths = set(inherited)
    current_paths = set(current)
    missing = sorted(inherited_paths - current_paths)
    added = sorted(current_paths - inherited_paths)
    modified = sorted(path for path in inherited_paths & current_paths if inherited[path] != current[path])
    unchanged = sorted(path for path in inherited_paths & current_paths if inherited[path] == current[path])

    inheritance_payload = {
        "schema": "HHS_PASS145_INHERITANCE_MANIFEST_V2",
        "pass_id": "HHS-P145",
        "release_scope": "FULL_INHERITED_PASS_HISTORY_NUCLEUS",
        "parent_pass": "HHS-P144",
        "parent_archive": parent.name,
        "parent_archive_sha256": parent_sha,
        "expected_parent_archive_sha256": EXPECTED_PARENT_SHA256,
        "parent_hash_valid": True,
        "transient_exclusion_policy": ["__pycache__", ".pytest_cache", "*.pyc", "*.pyo"],
        "parent_authoritative_file_count": len(inherited),
        "current_pre_manifest_file_count": len(current),
        "unchanged_inherited_file_count": len(unchanged),
        "modified_inherited_file_count": len(modified),
        "added_pass145_file_count": len(added),
        "missing_inherited_file_count": len(missing),
        "modified_inherited_paths": modified,
        "added_pass145_paths": added,
        "missing_inherited_paths": missing,
        "inheritance_valid": not missing,
        "authoritative_nucleus_rule": "N_145 = N_144 union Delta_145; no inherited authoritative file omitted",
    }
    write_json(INHERITANCE_PATH, "hhs_pass145_inheritance_manifest_v2", inheritance_payload)

    file_payload = {
        "schema": "HHS_PASS145_FILE_MANIFEST_V1",
        "pass_id": "HHS-P145",
        "root": "hhs145_work",
        "inventory_scope": "all non-transient repository files before self-referential release-manifest insertion",
        "self_excluded_paths": sorted(SELF_EXCLUSIONS),
        "file_count": len(file_entries),
        "total_size_bytes": sum(item["size_bytes"] for item in file_entries),
        "files": file_entries,
    }
    write_json(FILE_PATH, "hhs_pass145_file_manifest_v1", file_payload)

    closure = json.loads((ROOT / "release_artifacts/pass145/receipts/PASS_145_CLOSURE_RECEIPT.json").read_text(encoding="utf-8"))
    tests = json.loads((ROOT / "release_artifacts/pass145/reports/PASS_145_TEST_REPORT.json").read_text(encoding="utf-8"))
    release_payload = {
        "schema": "HHS_PASS145_RELEASE_MANIFEST_V1",
        "pass_id": "HHS-P145",
        "artifact_class": "FULL_INHERITED_HHS_PASS_HISTORY_NUCLEUS",
        "parent_pass": "HHS-P144",
        "parent_archive_sha256": parent_sha,
        "inheritance_manifest": INHERITANCE_PATH.relative_to(ROOT).as_posix(),
        "file_manifest": FILE_PATH.relative_to(ROOT).as_posix(),
        "closure_receipt": "release_artifacts/pass145/receipts/PASS_145_CLOSURE_RECEIPT.json",
        "test_report": "release_artifacts/pass145/reports/PASS_145_TEST_REPORT.json",
        "dependency_scoped_tests": tests["dependency_scoped_tests"],
        "inherited_runtime_smoke": tests["runtime_smoke"],
        "host_external_actor": "OBSERVED_WORKING",
        "host_native_binding_source_graph": "OBSERVED_WORKING",
        "android_project_source": "IMPLEMENTED",
        "installable_apk": "NOT_PRODUCED",
        "real_device_validation": "NOT_EXPOSED",
        "performance_ladder": "PARTIAL_1_AND_9_COMPLETED__81_RESOURCE_BOUNDED",
        "terminal_status": closure["terminal_status"],
        "safe_halt": closure["safe_halt"],
        "fabricated_apk": False,
        "full_nucleus_preserved": not missing,
        "known_open_blockers": closure["open_blockers"],
    }
    write_json(RELEASE_PATH, "hhs_pass145_release_manifest_v1", release_payload)

    print(json.dumps({
        "parent_files": len(inherited),
        "unchanged": len(unchanged),
        "modified": len(modified),
        "added_before_manifests": len(added),
        "missing": len(missing),
        "terminal_status": closure["terminal_status"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
