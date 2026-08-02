#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
import zipfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("HHS_PASS148_OUTPUT_DIR", str(ROOT / "release_artifacts/pass148/packages"))).resolve()
FULL_ZIP = OUT / "hhs_pass_148_native_semantic_authority_membrane_full_inherited_pass_history_nucleus.zip"
FULL_SHA = OUT / (FULL_ZIP.name + ".sha256")
EVIDENCE_ZIP = OUT / "hhs_pass_148_implementation_evidence_package.zip"
EVIDENCE_SHA = OUT / (EVIDENCE_ZIP.name + ".sha256")
VERIFY = OUT / "hhs_pass_148_archive_verification.json"
ARCHIVE_ROOT = "hhs148_work"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def transient(rel: str) -> bool:
    path = Path(rel)
    parts = path.parts
    name = path.name
    return (
        "__pycache__" in parts
        or ".pytest_cache" in parts
        or rel.endswith((".pyc", ".pyo", "-wal", "-shm", ".pass146-session.json"))
        or name == "pid"
        or (rel.startswith("release_artifacts/pass148/reference/") and rel.endswith(".sqlite3"))
        or rel == "release_artifacts/pass148/reference/external_actor_workflow_stdout.json"
        or rel == "release_artifacts/pass148/tests/dependency_scoped_junit.xml"
        or rel == "release_artifacts/pass148/manifests/PASS_148_MANIFEST_BUILD.log"
    )


def source_files() -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if transient(rel):
            continue
        rows.append((rel, path))
    return sorted(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_file(archive: zipfile.ZipFile, source: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, FIXED_DATE)
    info.create_system = 3
    mode = stat.S_IMODE(source.stat().st_mode)
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    with source.open("rb") as handle:
        archive.writestr(info, handle.read(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_zip(path: Path, rows: Iterable[tuple[str, Path]], *, prefix: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    count = 0
    with zipfile.ZipFile(path, "w", allowZip64=True) as archive:
        for rel, source in rows:
            add_file(archive, source, f"{prefix}/{rel}")
            count += 1
    return count


def evidence_files() -> list[tuple[str, Path]]:
    exact = [
        "HHS_PASS_148_NATIVE_SEMANTIC_AUTHORITY_MEMBRANE_CONTRACT.md",
        "HHS_PASS_148_IMPLEMENTATION_REPORT.md",
        "HHS_PASS_148_SEMANTIC_RULE_REGISTRY.json",
        "HHS_PASS_148_PROPOSITION_SCHEMA.json",
        "HHS_PASS_148_DERIVATION_SCHEMA.json",
        "HHS_PASS_148_PROJECTION_PROFILE_REGISTRY.json",
        "HHS_PASS_148_PROMOTION_SCHEMA.json",
        "HHS_PASS_148_CONTAMINATION_DIAGNOSTICS.json",
        "HHS_PASS_148_API_OPENAPI.json",
        "HHS_PASS_148_CLI_REFERENCE.md",
        "HHS_PASS_148_TEST_REPORT.json",
        "HHS_PASS_148_NEGATIVE_TEST_REPORT.json",
        "HHS_PASS_148_CEUAC_EVIDENCE.jsonl",
        "HHS_PASS_148_REPLAY_REPORT.json",
        "HHS_PASS_148_CAPABILITY_MANIFEST.json",
        "HHS_PASS_148_CLOSURE_RECEIPT.json",
        "HHS_PASS_148_RELEASE_MANIFEST.json",
        "PASS_148_RELEASE_MANIFEST.json",
        "PASS_148_RELEASE_NOTES.md",
        "HHS_FULL_CHECKPOINT_MANIFEST.json",
        "release_artifacts/pass148/manifests/PASS_148_INHERITANCE_MANIFEST.json",
        "release_artifacts/pass148/manifests/PASS_148_FILE_MANIFEST.json",
        "release_artifacts/pass148/tests/PASS_148_DEPENDENCY_SCOPED_TEST_REPORT.json",
        "release_artifacts/pass148/reference/internal/PASS_148_REFERENCE_WORKLOAD.json",
        "release_artifacts/pass148/reference/external_actor/PASS_148_EXTERNAL_ACTOR_WORKFLOW.json",
        "release_artifacts/pass148/reports/PASS_148_CEUAC_SUMMARY.json",
    ]
    rows: dict[str, Path] = {}
    for rel in exact:
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(rel)
        rows[rel] = path
    for path in sorted((ROOT / "release_artifacts/pass148/tests").glob("*.log")):
        rel = path.relative_to(ROOT).as_posix()
        if not transient(rel):
            rows[rel] = path
    return sorted(rows.items())


def main() -> int:
    rows = source_files()
    full_count = build_zip(FULL_ZIP, rows, prefix=ARCHIVE_ROOT)
    full_hash = sha256_file(FULL_ZIP)
    FULL_SHA.write_text(f"{full_hash}  {FULL_ZIP.name}\n", encoding="utf-8")

    expected_entries = {f"{ARCHIVE_ROOT}/{rel}" for rel, _ in rows}
    with zipfile.ZipFile(FULL_ZIP) as archive:
        bad = archive.testzip()
        observed_entries = {info.filename for info in archive.infolist() if not info.is_dir()}
        roots = sorted({name.split("/", 1)[0] for name in observed_entries})
        release_manifest_present = f"{ARCHIVE_ROOT}/HHS_PASS_148_RELEASE_MANIFEST.json" in observed_entries
        full_manifest_present = f"{ARCHIVE_ROOT}/HHS_FULL_CHECKPOINT_MANIFEST.json" in observed_entries
        missing_entries = sorted(expected_entries - observed_entries)
        unexpected_entries = sorted(observed_entries - expected_entries)

    verification = {
        "schema": "HHS_PASS148_ARCHIVE_VERIFICATION_V1",
        "archive": FULL_ZIP.name,
        "sha256": full_hash,
        "size_bytes": FULL_ZIP.stat().st_size,
        "entry_count": full_count,
        "archive_root": roots[0] + "/" if len(roots) == 1 else None,
        "single_root": roots == [ARCHIVE_ROOT],
        "zip_integrity": "VALID" if bad is None else "INVALID",
        "first_bad_entry": bad,
        "expected_entry_count": len(expected_entries),
        "missing_entries": missing_entries,
        "unexpected_entries": unexpected_entries,
        "release_manifest_present": release_manifest_present,
        "full_checkpoint_manifest_present": full_manifest_present,
        "full_inherited_pass_history_nucleus": True,
        "terminal_status": "PASS_148_INCOMPLETE",
        "valid": bad is None and roots == [ARCHIVE_ROOT] and not missing_entries and not unexpected_entries and release_manifest_present and full_manifest_present,
    }
    VERIFY.write_text(json.dumps(verification, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if not verification["valid"]:
        raise RuntimeError(json.dumps(verification, indent=2))

    evidence_rows = evidence_files()
    # Include independent archive verification and checksum witnesses in the compact package.
    transient_verification_dir = OUT / ".pass148_evidence_staging"
    transient_verification_dir.mkdir(parents=True, exist_ok=True)
    try:
        staged_verify = transient_verification_dir / VERIFY.name
        staged_verify.write_bytes(VERIFY.read_bytes())
        staged_sha = transient_verification_dir / FULL_SHA.name
        staged_sha.write_bytes(FULL_SHA.read_bytes())
        evidence_rows.extend([
            (VERIFY.name, staged_verify),
            (FULL_SHA.name, staged_sha),
        ])
        evidence_count = build_zip(EVIDENCE_ZIP, sorted(evidence_rows), prefix="hhs_pass_148_evidence")
    finally:
        for path in transient_verification_dir.glob("*"):
            path.unlink(missing_ok=True)
        transient_verification_dir.rmdir()
    evidence_hash = sha256_file(EVIDENCE_ZIP)
    EVIDENCE_SHA.write_text(f"{evidence_hash}  {EVIDENCE_ZIP.name}\n", encoding="utf-8")
    with zipfile.ZipFile(EVIDENCE_ZIP) as archive:
        evidence_bad = archive.testzip()
    if evidence_bad is not None:
        raise RuntimeError(f"evidence ZIP integrity failed at {evidence_bad}")

    print(json.dumps({
        "full_archive": str(FULL_ZIP),
        "full_sha256": full_hash,
        "full_size_bytes": FULL_ZIP.stat().st_size,
        "full_entry_count": full_count,
        "evidence_archive": str(EVIDENCE_ZIP),
        "evidence_sha256": evidence_hash,
        "evidence_size_bytes": EVIDENCE_ZIP.stat().st_size,
        "evidence_entry_count": evidence_count,
        "verification": str(VERIFY),
        "terminal_status": "PASS_148_INCOMPLETE",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
