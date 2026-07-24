from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import os
import zipfile

from .core import CONTRACT_ID, digest256, stable, write_json
from .manifest import validate_archive

ARCHIVE_NAME = "hhs_pass_152_golden_fractal_correspondence_constructor_full_inherited_pass_history_nucleus.zip"
_INTERNAL_MANIFEST = "native_projects/hhs_gfcc_pass152/manifest/archive_content_manifest.json"
_EXTERNAL_MANIFEST = "native_projects/hhs_gfcc_pass152/manifest/archive_manifest.json"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _included(path: Path, repo: Path, output: Path) -> bool:
    relative = path.relative_to(repo)
    if any(part in {".git", "__pycache__", ".pytest_cache", ".mypy_cache"} for part in relative.parts):
        return False
    if path == output or relative.as_posix() == _EXTERNAL_MANIFEST:
        return False
    if path.suffix in {".pyc", ".pyo", ".zip"}:
        return False
    return path.is_file()


def _zip_info(relative: str, mode: int = 0o100644) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = mode << 16
    return info


def package_repository(repo: Path, *, require_verified_report: bool = True) -> dict[str, Any]:
    repo = repo.resolve()
    subsystem = repo / "native_projects" / "hhs_gfcc_pass152"
    dist = subsystem / "dist"
    manifest_dir = subsystem / "manifest"
    report_path = subsystem / "reports" / "HHS_PASS_152_VALIDATION_REPORT.json"
    final_receipt = subsystem / "receipts" / "GFCC_FINAL_VALIDATION_RECEIPT.json"
    dist.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(parents=True, exist_ok=True)

    if require_verified_report:
        if not report_path.is_file() or not final_receipt.is_file():
            raise ValueError("HHS_GFCC_BUILD_ERROR:verified report or final receipt missing")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("terminal_classification") != "GOLDEN_FRACTAL_CORRESPONDENCE_CONSTRUCTOR_VERIFIED":
            raise ValueError("HHS_GFCC_BUILD_ERROR:archive requires verified terminal report")
        if report.get("incomplete_obligations"):
            raise ValueError("HHS_GFCC_BUILD_ERROR:archive blocked by incomplete obligations")

    output = dist / ARCHIVE_NAME
    files = sorted(
        (path for path in repo.rglob("*") if _included(path, repo, output)),
        key=lambda item: item.relative_to(repo).as_posix(),
    )
    entries: list[dict[str, Any]] = []
    payloads: list[tuple[str, bytes, int]] = []
    for path in files:
        relative = path.relative_to(repo).as_posix()
        data = path.read_bytes()
        mode = 0o100755 if os.access(path, os.X_OK) else 0o100644
        entries.append({"path": relative, "size": len(data), "sha256": _sha256(data)})
        payloads.append((relative, data, mode))

    content_manifest = stable(
        {
            "schema": "HHS_PASS_152_GFCC_ARCHIVE_CONTENT_MANIFEST_V1",
            "contract_id": CONTRACT_ID,
            "archive_name": ARCHIVE_NAME,
            "entry_count": len(entries),
            "expanded_byte_size": sum(entry["size"] for entry in entries),
            "entries_digest": digest256(entries),
            "entries": entries,
        }
    )
    content_manifest_bytes = (json.dumps(content_manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative, data, mode in payloads:
            archive.writestr(_zip_info(relative, mode), data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        archive.writestr(
            _zip_info(_INTERNAL_MANIFEST),
            content_manifest_bytes,
            compress_type=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        )

    required_paths = (
        "HHS_PASS_152_FINAL_CONTRACT.md",
        "PASS_152_RELEASE_MANIFEST.json",
        "native_projects/hhs_gfcc_pass152/PASS_152_CONTRACT.md",
        "native_projects/hhs_gfcc_pass152/reports/HHS_PASS_152_VALIDATION_REPORT.json",
        "native_projects/hhs_gfcc_pass152/receipts/GFCC_FINAL_VALIDATION_RECEIPT.json",
        "native_projects/hhs_gfcc_pass152/dist/libhhs_gfcc.a",
        "native_projects/hhs_gfcc_pass152/dist/libhhs_gfcc.so",
        "native_projects/hhs_gfcc_pass152/dist/hhs-gfcc",
        "native_projects/hhs_gfcc_pass152/dist/hhs_gfcc_shader.spv",
        _INTERNAL_MANIFEST,
    )
    validation = validate_archive(
        output,
        required_paths=required_paths,
        expected_repository_file_minimum=3275,
    )
    if not validation.get("valid"):
        raise ValueError(f"HHS_GFCC_BUILD_ERROR:archive validation failed:{validation.get('errors')}")

    with zipfile.ZipFile(output, "r") as archive:
        internal = json.loads(archive.read(_INTERNAL_MANIFEST).decode("utf-8"))
        internal_errors = []
        for entry in internal.get("entries", []):
            data = archive.read(entry["path"])
            if len(data) != entry["size"] or _sha256(data) != entry["sha256"]:
                internal_errors.append(entry["path"])
        if internal_errors:
            raise ValueError(f"HHS_GFCC_BUILD_ERROR:archive content manifest mismatch:{internal_errors[:10]}")

    result = stable(
        {
            "schema": "HHS_PASS_152_GFCC_ARCHIVE_MANIFEST_V1",
            "contract_id": CONTRACT_ID,
            "filename": output.name,
            "path": output.relative_to(repo).as_posix(),
            "byte_size": output.stat().st_size,
            "sha256": _sha256(output.read_bytes()),
            "expanded_file_count": validation["expanded_file_count"],
            "expanded_byte_size": validation["expanded_byte_size"],
            "content_entry_count": len(entries),
            "content_entries_digest": content_manifest["entries_digest"],
            "complete_inherited_repository_tree": True,
            "archive_validation": validation,
            "valid": True,
        }
    )
    write_json(manifest_dir / "archive_manifest.json", result)
    return result


__all__ = ["ARCHIVE_NAME", "package_repository"]
