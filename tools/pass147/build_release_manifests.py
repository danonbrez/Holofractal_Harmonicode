#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from hhs_runtime.pass145.canonical import canonical_json, hash72

PARENT_NAME = "hhs_pass_146_boundary_constructed_network_security_full_inherited_pass_history_nucleus.zip"
EXPECTED_PARENT = "08dc2a5ca0ae66deea17bd862485d20891a84caff86f8c82329d02588dacd80d"
PARENT_ROOT = "hhs146_work/"
ART = ROOT / "release_artifacts/pass147/manifests"
INHERITANCE = ART / "PASS_147_INHERITANCE_MANIFEST.json"
FILES = ART / "PASS_147_FILE_MANIFEST.json"
RELEASE = ROOT / "PASS_147_RELEASE_MANIFEST.json"
FULL = ROOT / "HHS_FULL_CHECKPOINT_MANIFEST.json"
SELF = {p.relative_to(ROOT).as_posix() for p in (INHERITANCE, FILES, RELEASE, FULL)}


def transient(rel: str) -> bool:
    parts = Path(rel).parts
    name = Path(rel).name
    return (
        "__pycache__" in parts
        or ".pytest_cache" in parts
        or rel.endswith((".pyc", ".pyo", "-wal", "-shm"))
        or rel.endswith(".pass146-session.json")
        or name in {"pid"}
        or rel == "release_artifacts/pass147/tests/dependency_scoped_pytest.log"
        or rel == "release_artifacts/pass147/tests/dependency_scoped_junit.xml"
        or rel == "release_artifacts/pass147/manifests/PASS_147_MANIFEST_BUILD.log"
    )


def resolve_parent() -> Path:
    configured = os.environ.get("HHS_PASS146_ARCHIVE")
    candidates = [Path(configured)] if configured else []
    candidates.extend(parent / PARENT_NAME for parent in (ROOT, *ROOT.parents))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(PARENT_NAME)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_root(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for path, value in sorted(files.items()):
        digest.update(path.encode("utf-8")); digest.update(b"\0"); digest.update(value.encode("ascii")); digest.update(b"\n")
    return digest.hexdigest()


def write(path: Path, label: str, payload: dict) -> dict:
    value = dict(payload)
    value.pop("manifest_hash72", None)
    value["manifest_hash72"] = hash72(label, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")
    return value


def current_map(*, exclude_self: bool) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if transient(rel) or (exclude_self and rel in SELF):
            continue
        out[rel] = sha(path.read_bytes())
    return out


def main() -> int:
    parent = resolve_parent()
    parent_hash = sha(parent.read_bytes())
    parent_files: dict[str, str] = {}
    with zipfile.ZipFile(parent) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"parent archive integrity failed at {bad}")
        for info in archive.infolist():
            if info.is_dir() or not info.filename.startswith(PARENT_ROOT):
                continue
            rel = info.filename[len(PARENT_ROOT):]
            if rel and not transient(rel):
                parent_files[rel] = sha(archive.read(info))

    observed_files = current_map(exclude_self=False)
    missing = sorted(set(parent_files) - set(observed_files))
    unchanged = sorted(path for path in parent_files if observed_files.get(path) == parent_files[path])
    repaired = sorted(path for path in parent_files if path in observed_files and observed_files[path] != parent_files[path])
    # The full checkpoint manifest is regenerated later in this function.  It is
    # therefore an intentional inherited repair even though its parent bytes are
    # still present at the moment the initial comparison is evaluated.
    full_rel = FULL.relative_to(ROOT).as_posix()
    if full_rel in parent_files and full_rel not in repaired:
        repaired.append(full_rel); repaired.sort()
        if full_rel in unchanged:
            unchanged.remove(full_rel)
    additive = sorted(set(observed_files) - set(parent_files))

    manifest_files = current_map(exclude_self=True)
    inheritance = write(INHERITANCE, "hhs_pass147_inheritance_manifest_v1", {
        "schema": "HHS_PASS147_INHERITANCE_MANIFEST_V1",
        "parent_archive": parent.name,
        "parent_observed_sha256": parent_hash,
        "parent_expected_sha256": EXPECTED_PARENT,
        "parent_hash_equal": parent_hash == EXPECTED_PARENT,
        "parent_authoritative_file_count": len(parent_files),
        "unchanged_inherited_file_count": len(unchanged),
        "repaired_inherited_file_count": len(repaired),
        "missing_inherited_file_count": len(missing),
        "additive_pass147_file_count": len(additive),
        "repaired_inherited_files": repaired,
        "missing_inherited_files": missing,
        "additive_pass147_files": additive,
        "full_inherited_pass_history_nucleus": not missing,
        "pass_local_delta": False,
        "parent_tree_sha256": tree_root(parent_files),
        "child_nonself_tree_sha256": tree_root(manifest_files),
    })

    file_rows = []
    evidence_count = 0
    for rel, digest in sorted(manifest_files.items()):
        path = ROOT / rel
        kind = "EVIDENCE" if rel.startswith("release_artifacts/") or rel.endswith(("_RECEIPT.json", "_REPORT.json", "_MANIFEST.json")) else "SYSTEM"
        if kind == "EVIDENCE":
            evidence_count += 1
        file_rows.append({"path": rel, "sha256": digest, "size_bytes": path.stat().st_size, "mode": stat.S_IMODE(path.stat().st_mode), "kind": kind})
    file_manifest = write(FILES, "hhs_pass147_file_manifest_v1", {
        "schema": "HHS_PASS147_FILE_MANIFEST_V1",
        "file_count": len(file_rows),
        "evidence_file_count": evidence_count,
        "tree_sha256": tree_root(manifest_files),
        "files": file_rows,
    })

    full_payload = {
        "schema": "HHS_FULL_CHECKPOINT_MANIFEST_V2",
        "pass_id": "HHS-P147",
        "parent_pass": "HHS-P146",
        "release_scope": "FULL_INHERITED_HHS_PASS_HISTORY_NUCLEUS",
        "ancestry_rule": "EVERY_PARENT_NONCACHE_PATH_MUST_EXIST_IN_CHILD",
        "cache_policy": "TRANSIENT_CACHE_CLASSES_EXCLUDED_ONLY; SYSTEM_AND_CANONICAL_EVIDENCE_PRESERVED",
        "parent_archive_sha256": parent_hash,
        "parent_tree_sha256": tree_root(parent_files),
        "child_tree_sha256": tree_root(manifest_files),
        "file_count": len(file_rows),
        "evidence_file_count": evidence_count,
        "missing_parent_paths": missing,
        "repaired_inherited_paths": repaired,
        "files": file_rows,
    }
    full_payload["manifest_hash72_witness"] = hash72("hhs_full_checkpoint_manifest_pass147_v2", full_payload)
    FULL.write_text(canonical_json(full_payload) + "\n", encoding="utf-8")

    closure = json.loads((ROOT / "HHS_PASS_147_CLOSURE_RECEIPT.json").read_text(encoding="utf-8"))
    test_report = json.loads((ROOT / "release_artifacts/pass147/reports/PASS_147_TEST_REPORT.json").read_text(encoding="utf-8"))
    release = write(RELEASE, "hhs_pass147_release_manifest_v1", {
        "schema": "HHS_PASS147_RELEASE_MANIFEST_V1",
        "pass_id": "HHS-P147",
        "parent": "HHS-P146",
        "release_scope": "FULL_INHERITED_HHS_PASS_HISTORY_NUCLEUS",
        "parent_archive_sha256": parent_hash,
        "inheritance_manifest_hash72": inheritance["manifest_hash72"],
        "file_manifest_hash72": file_manifest["manifest_hash72"],
        "full_checkpoint_manifest_hash72": full_payload["manifest_hash72_witness"],
        "dependency_scoped_tests": test_report["dependency_scoped_tests"]["totals"],
        "external_agent_opacity_host_scope": closure["pass147_host_scope"],
        "privileged_internal_access": closure["privileged_internal_access"],
        "terminal_status": closure["terminal_status"],
        "complete_parent_files_preserved": len(missing) == 0,
        "full_nucleus_file_count_before_self_manifests": len(manifest_files),
    })
    print(json.dumps({
        "parent": len(parent_files),
        "unchanged": len(unchanged),
        "repaired": len(repaired),
        "missing": len(missing),
        "additive": len(additive),
        "release": release["terminal_status"],
    }, indent=2))
    return 0 if not missing and parent_hash == EXPECTED_PARENT else 1


if __name__ == "__main__":
    raise SystemExit(main())
