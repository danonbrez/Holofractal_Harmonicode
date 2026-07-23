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

PARENT_NAME = "hhs_pass_147_functionally_complete_external_agent_opacity_full_inherited_pass_history_nucleus.zip"
EXPECTED_PARENT = "aecc5f67b7bff8e28c499ce1908574a177a877306f6bd55fb008f5d8bc8cd3eb"
PARENT_ROOT = "hhs147_work/"
ART = ROOT / "release_artifacts/pass148/manifests"
INHERITANCE = ART / "PASS_148_INHERITANCE_MANIFEST.json"
FILES = ART / "PASS_148_FILE_MANIFEST.json"
RELEASE = ROOT / "HHS_PASS_148_RELEASE_MANIFEST.json"
RELEASE_ALIAS = ROOT / "PASS_148_RELEASE_MANIFEST.json"
FULL = ROOT / "HHS_FULL_CHECKPOINT_MANIFEST.json"
SELF = {p.relative_to(ROOT).as_posix() for p in (INHERITANCE, FILES, RELEASE, RELEASE_ALIAS, FULL)}


def transient(rel: str) -> bool:
    path = Path(rel); parts = path.parts; name = path.name
    return (
        "__pycache__" in parts
        or ".pytest_cache" in parts
        or rel.endswith((".pyc", ".pyo", "-wal", "-shm", ".pass146-session.json"))
        or name == "pid"
        or rel.startswith("release_artifacts/pass148/reference/") and rel.endswith(".sqlite3")
        or rel == "release_artifacts/pass148/reference/external_actor_workflow_stdout.json"
        or rel == "release_artifacts/pass148/tests/dependency_scoped_junit.xml"
        or rel == "release_artifacts/pass148/manifests/PASS_148_MANIFEST_BUILD.log"
    )


def resolve_parent() -> Path:
    configured = os.environ.get("HHS_PASS147_ARCHIVE")
    candidates = [Path(configured)] if configured else []
    candidates.extend(parent / PARENT_NAME for parent in (ROOT, *ROOT.parents))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(PARENT_NAME)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_root(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for path, value in sorted(files.items()):
        digest.update(path.encode("utf-8")); digest.update(b"\0"); digest.update(value.encode("ascii")); digest.update(b"\n")
    return digest.hexdigest()


def write(path: Path, label: str, payload: dict) -> dict:
    value = dict(payload); value.pop("manifest_hash72", None)
    value["manifest_hash72"] = hash72(label, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")
    return value


def current_map(*, exclude_self: bool) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file(): continue
        rel = path.relative_to(ROOT).as_posix()
        if transient(rel) or (exclude_self and rel in SELF): continue
        result[rel] = sha_bytes(path.read_bytes())
    return result


def main() -> int:
    parent = resolve_parent(); parent_hash = sha_bytes(parent.read_bytes())
    parent_files: dict[str, str] = {}
    with zipfile.ZipFile(parent) as archive:
        bad = archive.testzip()
        if bad is not None: raise RuntimeError(f"parent archive integrity failed at {bad}")
        for info in archive.infolist():
            if info.is_dir() or not info.filename.startswith(PARENT_ROOT): continue
            rel = info.filename[len(PARENT_ROOT):]
            if rel and not transient(rel): parent_files[rel] = sha_bytes(archive.read(info))

    observed = current_map(exclude_self=False)
    missing = sorted(set(parent_files)-set(observed))
    unchanged = sorted(path for path in parent_files if observed.get(path)==parent_files[path])
    repaired = sorted(path for path in parent_files if path in observed and observed[path]!=parent_files[path])
    full_rel = FULL.relative_to(ROOT).as_posix()
    if full_rel in parent_files and full_rel not in repaired:
        repaired.append(full_rel); repaired.sort()
        if full_rel in unchanged: unchanged.remove(full_rel)
    additive = sorted(set(observed)-set(parent_files))

    manifest_files = current_map(exclude_self=True)
    inheritance = write(INHERITANCE, "hhs_pass148_inheritance_manifest_v1", {
        "schema":"HHS_PASS148_INHERITANCE_MANIFEST_V1","pass_id":"HHS-P148-NSAM",
        "parent_archive":parent.name,"parent_observed_sha256":parent_hash,"parent_expected_sha256":EXPECTED_PARENT,"parent_hash_equal":parent_hash==EXPECTED_PARENT,
        "parent_authoritative_file_count":len(parent_files),"unchanged_inherited_file_count":len(unchanged),"repaired_inherited_file_count":len(repaired),"missing_inherited_file_count":len(missing),"additive_pass148_file_count":len(additive),
        "repaired_inherited_files":repaired,"missing_inherited_files":missing,"additive_pass148_files":additive,
        "full_inherited_pass_history_nucleus":not missing,"pass_local_delta":False,"parent_tree_sha256":tree_root(parent_files),"child_nonself_tree_sha256":tree_root(manifest_files),
    })

    rows=[]; evidence_count=0
    for rel,digest in sorted(manifest_files.items()):
        path=ROOT/rel
        kind="EVIDENCE" if rel.startswith("release_artifacts/") or rel.endswith(("_RECEIPT.json","_REPORT.json","_MANIFEST.json","_EVIDENCE.jsonl")) else "SYSTEM"
        if kind=="EVIDENCE": evidence_count+=1
        rows.append({"path":rel,"sha256":digest,"size_bytes":path.stat().st_size,"mode":stat.S_IMODE(path.stat().st_mode),"kind":kind})
    file_manifest=write(FILES,"hhs_pass148_file_manifest_v1",{"schema":"HHS_PASS148_FILE_MANIFEST_V1","file_count":len(rows),"evidence_file_count":evidence_count,"tree_sha256":tree_root(manifest_files),"files":rows})

    full_payload={
        "schema":"HHS_FULL_CHECKPOINT_MANIFEST_V2","pass_id":"HHS-P148-NSAM","parent_pass":"HHS-P147","release_scope":"FULL_INHERITED_HHS_PASS_HISTORY_NUCLEUS",
        "ancestry_rule":"EVERY_PARENT_NONCACHE_PATH_MUST_EXIST_IN_CHILD","cache_policy":"TRANSIENT_CACHE_CLASSES_EXCLUDED_ONLY; SYSTEM_AND_CANONICAL_EVIDENCE_PRESERVED",
        "parent_archive_sha256":parent_hash,"parent_tree_sha256":tree_root(parent_files),"child_tree_sha256":tree_root(manifest_files),"file_count":len(rows),"evidence_file_count":evidence_count,
        "missing_parent_paths":missing,"repaired_inherited_paths":repaired,"files":rows,
    }
    full_payload["manifest_hash72_witness"]=hash72("hhs_full_checkpoint_manifest_pass148_v2",full_payload)
    FULL.write_text(canonical_json(full_payload)+"\n",encoding="utf-8")

    closure=json.loads((ROOT/"HHS_PASS_148_CLOSURE_RECEIPT.json").read_text())
    tests=json.loads((ROOT/"HHS_PASS_148_TEST_REPORT.json").read_text())
    release=write(RELEASE,"hhs_pass148_release_manifest_v1",{
        "schema":"HHS_PASS148_RELEASE_MANIFEST_V1","pass_id":"HHS-P148-NSAM","parent":"HHS-P147","release_scope":"FULL_INHERITED_HHS_PASS_HISTORY_NUCLEUS",
        "parent_archive_sha256":parent_hash,"inheritance_manifest_hash72":inheritance["manifest_hash72"],"file_manifest_hash72":file_manifest["manifest_hash72"],"full_checkpoint_manifest_hash72":full_payload["manifest_hash72_witness"],
        "dependency_scoped_tests":tests["dependency_scoped_tests"]["totals"],"negative_tests":tests["negative_tests"],"external_actor_status":tests["external_actor_status"],
        "semantic_membrane_host_scope":closure["semantic_membrane_host_scope"],"external_privileged_semantic_authority":closure["external_semantic_authority"],"terminal_status":closure["terminal_status"],
        "complete_parent_files_preserved":len(missing)==0,"full_nucleus_file_count_before_self_manifests":len(manifest_files),
    })
    RELEASE_ALIAS.write_text(canonical_json(release)+"\n",encoding="utf-8")
    print(json.dumps({"parent":len(parent_files),"unchanged":len(unchanged),"repaired":len(repaired),"missing":len(missing),"additive":len(additive),"nonself_files":len(manifest_files),"terminal_status":release["terminal_status"]},indent=2))
    return 0 if not missing and parent_hash==EXPECTED_PARENT else 1

if __name__=="__main__": raise SystemExit(main())
