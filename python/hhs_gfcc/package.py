from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import zipfile

from .core import digest256, write_json

ARCHIVE_NAME = "hhs_pass_152_golden_fractal_correspondence_constructor_full_inherited_pass_history_nucleus.zip"


def _included(path: Path, repo: Path, output: Path) -> bool:
    relative = path.relative_to(repo)
    if any(part in {".git", "__pycache__", ".pytest_cache", ".mypy_cache"} for part in relative.parts):
        return False
    if path == output:
        return False
    if path.suffix in {".pyc", ".pyo"}:
        return False
    return path.is_file()


def package_repository(repo: Path) -> dict[str, Any]:
    subsystem = repo / "native_projects" / "hhs_gfcc_pass152"
    dist = subsystem / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    output = dist / ARCHIVE_NAME
    files = sorted((path for path in repo.rglob("*") if _included(path, repo, output)), key=lambda p: p.relative_to(repo).as_posix())
    manifest_entries = []
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(repo).as_posix()
            data = path.read_bytes()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            manifest_entries.append({"path": relative, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    archive_bytes = output.read_bytes()
    result = {
        "schema": "HHS_PASS_152_GFCC_ARCHIVE_MANIFEST_V1",
        "filename": output.name,
        "path": output.relative_to(repo).as_posix(),
        "byte_size": len(archive_bytes),
        "sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "expanded_file_count": len(manifest_entries),
        "expanded_byte_size": sum(entry["size"] for entry in manifest_entries),
        "entries_digest": digest256(manifest_entries),
        "complete_inherited_repository_tree": True,
    }
    write_json(subsystem / "manifest" / "archive_manifest.json", result)
    return result


__all__ = ["ARCHIVE_NAME", "package_repository"]
