"""Pass 134 recursive full-ancestry checkpoint compiler.

Authority rules implemented here:

* A child pass is a complete copy of every non-cache parent path plus its delta.
* System files are never deleted by a pass operation.
* Evidence archives are preserved but cannot serve as filesystem parents.
* Cache removal is allowed only for declared transient cache classes.
* Every authorized full checkpoint carries a recomputable payload manifest.
* Recovery can replay ordered overlay and unified-diff operations from the
  nearest complete ancestor and emit a full checkpoint after every operation.

The module deliberately separates operation validity from historical byte
availability. It never fabricates a missing ancestor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator, Mapping, Sequence

from .canonical import canonical_json, reject_floats
from .hash72_checkpoint import make_hash72_witness

MANIFEST_NAME = "HHS_FULL_CHECKPOINT_MANIFEST.json"
MANIFEST_SCHEMA = "HHS_FULL_ANCESTRY_CHECKPOINT_MANIFEST_V1"
BUILD_RECEIPT_SCHEMA = "HHS_PASS134_FULL_CHECKPOINT_BUILD_RECEIPT_V1"
CHAIN_RECEIPT_SCHEMA = "HHS_PASS134_RECOVERY_CHAIN_RECEIPT_V1"
FIXED_ZIP_DATETIME = (1980, 1, 1, 0, 0, 0)

CACHE_DIRS = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache",
    "node_modules", ".vite", "dist", "build", "builds", ".coverage_cache",
}
CACHE_SUFFIXES = {".pyc", ".pyo", ".so", ".dll", ".dylib", ".o", ".obj"}
EVIDENCE_DIRS = {"release_artifacts", "reports", "receipts", "evidence", "evidence_store"}
SYSTEM_DIRS = {
    "hhs_runtime", "hhs_backend", "hhs_python", "hhs_gui", "hhs_foundation",
    "hhs_graph", "tests", "contracts", "schemas", "tools", "examples", "data",
}
SYSTEM_SUFFIXES = {
    ".py", ".pyi", ".c", ".h", ".hpp", ".cc", ".cpp", ".rs", ".go",
    ".java", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".sh",
    ".ps1", ".bat", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".json",
    ".schema", ".sql", ".hhsprog", ".md", ".txt", ".csv", ".html", ".css",
}
DELETE_CONTROL_NAMES = {
    "HHS_DELETE_PATHS.json", "DELETE_PATHS.json", ".hhs-delete-paths", "tombstones.json"
}


class CheckpointError(RuntimeError):
    """Base class for deterministic checkpoint failures."""


class UnsafeArchiveError(CheckpointError):
    pass


class ParentRejectedError(CheckpointError):
    pass


class AncestryViolationError(CheckpointError):
    pass


class PatchApplicationError(CheckpointError):
    pass


@dataclass(frozen=True)
class FileRecord:
    path: str
    sha256: str
    size_bytes: int
    mode: int
    kind: str


@dataclass(frozen=True)
class ArchiveClassification:
    archive: str
    sha256: str
    total_files: int
    noncache_files: int
    cache_files: int
    system_files: int
    evidence_files: int
    has_authoritative_manifest: bool
    manifest_valid: bool
    archive_class: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class UnifiedPatchFile:
    old_path: str | None
    new_path: str
    hunks: tuple[tuple[int, int, int, int, tuple[str, ...]], ...]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_relpath(path: str | PurePosixPath) -> str:
    p = PurePosixPath(str(path).replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise UnsafeArchiveError(f"unsafe relative path: {path!r}")
    normalized = p.as_posix()
    if normalized in {".", ""}:
        raise UnsafeArchiveError(f"empty relative path: {path!r}")
    return normalized


def is_cache_path(path: str | PurePosixPath) -> bool:
    p = PurePosixPath(str(path))
    return bool(set(p.parts) & CACHE_DIRS) or p.suffix.lower() in CACHE_SUFFIXES


def is_evidence_path(path: str | PurePosixPath) -> bool:
    p = PurePosixPath(str(path))
    upper_name = p.name.upper()
    return bool(set(p.parts) & EVIDENCE_DIRS) or upper_name.startswith(("PASS_", "HHS_PASS_"))


def is_system_path(path: str | PurePosixPath) -> bool:
    p = PurePosixPath(str(path))
    if is_cache_path(p) or not p.name:
        return False
    if set(p.parts) & SYSTEM_DIRS:
        return True
    return p.suffix.lower() in SYSTEM_SUFFIXES and not is_evidence_path(p)


def file_kind(path: str) -> str:
    if is_cache_path(path):
        return "CACHE"
    if is_evidence_path(path):
        return "EVIDENCE"
    if is_system_path(path):
        return "SYSTEM"
    return "ARTIFACT"


def iter_tree_files(root: Path, *, include_manifest: bool = False) -> Iterator[Path]:
    root = root.resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if is_cache_path(rel):
            continue
        if not include_manifest and rel == MANIFEST_NAME:
            continue
        yield path


def record_file(path: Path, root: Path) -> FileRecord:
    rel = canonical_relpath(path.relative_to(root).as_posix())
    mode = stat.S_IMODE(path.stat().st_mode)
    return FileRecord(rel, sha256_file(path), path.stat().st_size, mode, file_kind(rel))


def tree_records(root: Path) -> list[FileRecord]:
    return [record_file(path, root) for path in iter_tree_files(root)]


def tree_root_from_records(records: Sequence[FileRecord]) -> str:
    rows = [
        f"{r.path}\0{r.sha256}\0{r.size_bytes}\0{r.mode:o}\0{r.kind}\n".encode("utf-8")
        for r in sorted(records, key=lambda item: item.path)
    ]
    return sha256_bytes(b"".join(rows))


def build_manifest(
    root: Path,
    *,
    pass_id: str,
    parent_pass: str | None,
    parent_tree_root: str | None,
    excluded_cache_paths: Sequence[str] = (),
) -> dict[str, Any]:
    records = tree_records(root)
    payload = {
        "schema": MANIFEST_SCHEMA,
        "pass_id": pass_id,
        "parent_pass": parent_pass,
        "parent_tree_root": parent_tree_root,
        "tree_root_sha256": tree_root_from_records(records),
        "file_count": len(records),
        "system_file_count": sum(r.kind == "SYSTEM" for r in records),
        "evidence_file_count": sum(r.kind == "EVIDENCE" for r in records),
        "cache_policy": "TRANSIENT_CACHE_CLASSES_EXCLUDED_ONLY; SYSTEM_AND_CANONICAL_EVIDENCE_PRESERVED",
        "excluded_cache_paths": sorted(set(excluded_cache_paths)),
        "files": [asdict(record) for record in records],
        "ancestry_rule": "EVERY_PARENT_NONCACHE_PATH_MUST_EXIST_IN_CHILD",
        "system_deletion_rule": "PROHIBITED",
        "status": "FULL_SYSTEM_CHECKPOINT",
    }
    payload["manifest_hash72_witness"] = make_hash72_witness(
        "hhs_pass134_full_checkpoint_manifest_v1", payload
    ).to_dict()
    return payload


def write_json(path: Path, value: Any) -> None:
    reject_floats(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_extract_zip(archive: Path, target: Path) -> None:
    root = target.resolve()
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            name = canonical_relpath(info.filename.rstrip("/")) if info.filename.rstrip("/") else None
            if name is None:
                continue
            dest = (target / name).resolve()
            if dest != root and root not in dest.parents:
                raise UnsafeArchiveError(f"ZIP traversal member: {info.filename}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise UnsafeArchiveError(f"symlink member prohibited: {info.filename}")
        zf.extractall(target)
        # Python's ZipFile.extractall does not restore POSIX executable bits.
        # Restore the recorded mode so manifest validation is byte-and-mode exact.
        for info in zf.infolist():
            raw_name = info.filename.rstrip("/")
            if not raw_name:
                continue
            name = canonical_relpath(raw_name)
            dest = (target / name).resolve()
            mode = (info.external_attr >> 16) & 0xFFFF
            permissions = stat.S_IMODE(mode)
            if permissions and dest.exists():
                os.chmod(dest, permissions)


def resolve_single_root(root: Path) -> Path:
    entries = [p for p in root.iterdir() if p.name != "__MACOSX"]
    if len(entries) == 1 and entries[0].is_dir() and not (root / MANIFEST_NAME).exists():
        return entries[0]
    return root


def copy_noncache_tree(src: Path, dst: Path) -> list[str]:
    excluded: list[str] = []
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        rel_s = rel.as_posix()
        if is_cache_path(rel_s):
            if path.is_file():
                excluded.append(rel_s)
            continue
        if path.is_symlink():
            raise UnsafeArchiveError(f"symlink prohibited in checkpoint tree: {rel_s}")
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return excluded


def parent_path_comparison(parent_root: Path, child_root: Path) -> dict[str, Any]:
    parent = {r.path: r for r in tree_records(parent_root)}
    child = {r.path: r for r in tree_records(child_root)}
    inherited = sorted(parent.keys() & child.keys())
    missing = sorted(parent.keys() - child.keys())
    changed = sorted(path for path in inherited if parent[path].sha256 != child[path].sha256)
    unchanged = sorted(path for path in inherited if parent[path].sha256 == child[path].sha256)
    added = sorted(child.keys() - parent.keys())
    return {
        "schema": "HHS_PASS134_PARENT_CHILD_PATH_COMPARISON_V1",
        "parent_files": len(parent),
        "child_files": len(child),
        "inherited_paths": len(inherited),
        "unchanged_paths": len(unchanged),
        "changed_paths": len(changed),
        "added_paths": len(added),
        "missing_parent_paths": len(missing),
        "missing_parent_path_list": missing,
        "ancestry_complete": not missing,
    }


def validate_manifest_tree(root: Path, manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest_path = root / MANIFEST_NAME
    if manifest is None:
        if not manifest_path.is_file():
            return {"ok": False, "reason": "MANIFEST_MISSING"}
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("status") != "FULL_SYSTEM_CHECKPOINT":
        return {"ok": False, "reason": "MANIFEST_SCHEMA_OR_STATUS_INVALID"}
    records = tree_records(root)
    actual_root = tree_root_from_records(records)
    listed = {entry["path"]: entry for entry in manifest.get("files", [])}
    actual = {record.path: asdict(record) for record in records}
    missing = sorted(set(listed) - set(actual))
    unlisted = sorted(set(actual) - set(listed))
    mismatched = sorted(
        path for path in set(listed) & set(actual)
        if any(listed[path].get(key) != actual[path].get(key) for key in ("sha256", "size_bytes", "mode", "kind"))
    )
    ok = (
        actual_root == manifest.get("tree_root_sha256")
        and not missing and not unlisted and not mismatched
        and manifest.get("file_count") == len(records)
    )
    return {
        "ok": ok,
        "reason": "VALID" if ok else "MANIFEST_CONTENT_MISMATCH",
        "actual_tree_root_sha256": actual_root,
        "declared_tree_root_sha256": manifest.get("tree_root_sha256"),
        "missing_paths": missing,
        "unlisted_paths": unlisted,
        "mismatched_paths": mismatched,
    }


def classify_archive(archive: Path) -> ArchiveClassification:
    if not archive.is_file():
        raise FileNotFoundError(archive)
    with tempfile.TemporaryDirectory(prefix="hhs134_inv_") as td:
        extracted = Path(td) / "tree"
        extracted.mkdir()
        safe_extract_zip(archive, extracted)
        root = resolve_single_root(extracted)
        files = [p for p in root.rglob("*") if p.is_file() and not p.is_symlink()]
        rels = [p.relative_to(root).as_posix() for p in files]
        noncache = [r for r in rels if not is_cache_path(r)]
        system = [r for r in noncache if is_system_path(r)]
        evidence = [r for r in noncache if is_evidence_path(r)]
        has_manifest = (root / MANIFEST_NAME).is_file()
        validation = validate_manifest_tree(root) if has_manifest else {"ok": False, "reason": "MANIFEST_MISSING"}
        reasons: list[str] = []
        if has_manifest:
            reasons.append("authoritative Pass 134 checkpoint manifest present")
        if not system:
            reasons.append("no system source paths present")
        if evidence and len(evidence) >= len(noncache) - 1:
            reasons.append("archive population is evidence-dominant")
        top = {PurePosixPath(r).parts[0] for r in noncache if PurePosixPath(r).parts}
        if top & SYSTEM_DIRS:
            reasons.append("system directories present")
        if has_manifest and validation["ok"]:
            archive_class = "FULL_SYSTEM_CHECKPOINT"
        elif not system and evidence:
            archive_class = "EVIDENCE_BUNDLE"
        elif system:
            archive_class = "UNAUTHORIZED_PARTIAL_OR_LEGACY_TREE"
        else:
            archive_class = "NONCHECKPOINT_ARTIFACT"
        return ArchiveClassification(
            archive=str(archive), sha256=sha256_file(archive), total_files=len(files),
            noncache_files=len(noncache), cache_files=len(rels) - len(noncache),
            system_files=len(system), evidence_files=len(evidence),
            has_authoritative_manifest=has_manifest, manifest_valid=bool(validation["ok"]),
            archive_class=archive_class, reasons=tuple(reasons),
        )


def deterministic_zip(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.unlink(missing_ok=True)
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.is_symlink() or is_cache_path(path.relative_to(root).as_posix()):
                continue
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(rel, FIXED_ZIP_DATETIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = stat.S_IMODE(path.stat().st_mode)
            info.external_attr = ((stat.S_IFREG | mode) << 16)
            info.flag_bits |= 0x800
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    os.replace(temp, output)


def _assert_no_delete_controls(delta_root: Path) -> None:
    controls = [p for p in delta_root.rglob("*") if p.is_file() and p.name in DELETE_CONTROL_NAMES]
    if controls:
        raise AncestryViolationError(
            "system deletion controls are prohibited: " + ", ".join(p.as_posix() for p in controls)
        )


def _admit_parent_archive(parent_zip: Path, *, allow_legacy_parent: bool) -> tuple[ArchiveClassification, Path, tempfile.TemporaryDirectory[str]]:
    classification = classify_archive(parent_zip)
    if classification.archive_class != "FULL_SYSTEM_CHECKPOINT" and not allow_legacy_parent:
        raise ParentRejectedError(
            f"parent rejected as {classification.archive_class}; authoritative full manifest required"
        )
    td = tempfile.TemporaryDirectory(prefix="hhs134_parent_")
    extracted = Path(td.name) / "tree"
    extracted.mkdir()
    safe_extract_zip(parent_zip, extracted)
    root = resolve_single_root(extracted)
    if classification.archive_class == "FULL_SYSTEM_CHECKPOINT":
        validation = validate_manifest_tree(root)
        if not validation["ok"]:
            td.cleanup()
            raise ParentRejectedError("parent checkpoint manifest failed recomputation")
    elif allow_legacy_parent:
        # Legacy admission is migration-only. It may be used to create the first
        # authoritative manifest but is never silently promoted.
        if classification.system_files < 1:
            td.cleanup()
            raise ParentRejectedError("legacy parent contains no system files")
    return classification, root, td


def build_full_child_checkpoint(
    parent_zip: Path,
    delta_dir: Path,
    output_zip: Path,
    *,
    pass_id: str,
    parent_pass: str,
    expected_parent_sha256: str | None = None,
    expected_parent_tree_root: str | None = None,
    allow_legacy_parent: bool = False,
) -> dict[str, Any]:
    if expected_parent_sha256 and sha256_file(parent_zip) != expected_parent_sha256:
        raise ParentRejectedError("parent archive SHA-256 mismatch")
    _assert_no_delete_controls(delta_dir)
    classification, parent_root, td = _admit_parent_archive(
        parent_zip, allow_legacy_parent=allow_legacy_parent
    )
    try:
        parent_manifest = None
        if (parent_root / MANIFEST_NAME).is_file():
            parent_manifest = json.loads((parent_root / MANIFEST_NAME).read_text(encoding="utf-8"))
            parent_tree_root = parent_manifest["tree_root_sha256"]
        else:
            parent_tree_root = tree_root_from_records(tree_records(parent_root))
        if expected_parent_tree_root and parent_tree_root != expected_parent_tree_root:
            raise ParentRejectedError("parent tree root mismatch")
        with tempfile.TemporaryDirectory(prefix="hhs134_build_") as build_td:
            work = Path(build_td) / "work"
            work.mkdir()
            excluded = copy_noncache_tree(parent_root, work)
            # Parent manifest describes its own pass and is superseded by the child manifest.
            (work / MANIFEST_NAME).unlink(missing_ok=True)
            excluded.extend(copy_noncache_tree(delta_dir, work))
            comparison = parent_path_comparison(parent_root, work)
            # The parent manifest is metadata for the parent checkpoint and is
            # intentionally replaced. Exclude it from the inherited path rule.
            if MANIFEST_NAME in comparison["missing_parent_path_list"]:
                comparison["missing_parent_path_list"].remove(MANIFEST_NAME)
                comparison["missing_parent_paths"] -= 1
                comparison["ancestry_complete"] = comparison["missing_parent_paths"] == 0
            if not comparison["ancestry_complete"]:
                raise AncestryViolationError(
                    "child omitted parent paths: " + ", ".join(comparison["missing_parent_path_list"][:20])
                )
            manifest = build_manifest(
                work, pass_id=pass_id, parent_pass=parent_pass,
                parent_tree_root=parent_tree_root, excluded_cache_paths=excluded,
            )
            write_json(work / MANIFEST_NAME, manifest)
            deterministic_zip(work, output_zip)
        child_class = classify_archive(output_zip)
        if child_class.archive_class != "FULL_SYSTEM_CHECKPOINT":
            output_zip.unlink(missing_ok=True)
            raise CheckpointError("emitted child did not validate as a full checkpoint")
        receipt = {
            "schema": BUILD_RECEIPT_SCHEMA,
            "pass_id": pass_id,
            "parent_pass": parent_pass,
            "parent_archive": asdict(classification),
            "parent_tree_root_sha256": parent_tree_root,
            "child_archive": asdict(child_class),
            "child_tree_root_sha256": manifest["tree_root_sha256"],
            "path_comparison": comparison,
            "output_zip": str(output_zip),
            "output_sha256": sha256_file(output_zip),
            "system_deletions": 0,
            "cache_policy": manifest["cache_policy"],
            "status": "FULL_ANCESTOR_COPY_VERIFIED",
        }
        receipt["receipt_hash72_witness"] = make_hash72_witness(
            "hhs_pass134_checkpoint_build_receipt_v1", receipt
        ).to_dict()
        return receipt
    finally:
        td.cleanup()


_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def _normalize_patch_path(raw: str, *, strip_components: int = 0, anchor: str | None = None) -> str | None:
    raw = raw.split("\t", 1)[0].strip()
    if raw == "/dev/null":
        return None
    p = PurePosixPath(raw)
    parts = list(p.parts)
    if parts and parts[0] in {"a", "b"}:
        parts = parts[1:]
    if anchor:
        anchor_parts = PurePosixPath(anchor).parts
        for idx in range(0, len(parts) - len(anchor_parts) + 1):
            if tuple(parts[idx:idx + len(anchor_parts)]) == anchor_parts:
                parts = parts[idx + len(anchor_parts):]
                break
        else:
            raise PatchApplicationError(f"patch path does not contain anchor {anchor!r}: {raw}")
    if strip_components:
        if len(parts) <= strip_components:
            raise PatchApplicationError(f"cannot strip {strip_components} components from {raw}")
        parts = parts[strip_components:]
    return canonical_relpath(PurePosixPath(*parts))


def parse_unified_patch(
    patch_text: str, *, strip_components: int = 0, anchor: str | None = None
) -> tuple[UnifiedPatchFile, ...]:
    if "GIT binary patch" in patch_text or "Binary files " in patch_text:
        raise PatchApplicationError("binary patch records are not replay-authoritative")
    lines = patch_text.splitlines(keepends=True)
    files: list[UnifiedPatchFile] = []
    idx = 0
    while idx < len(lines):
        if not lines[idx].startswith("--- "):
            idx += 1
            continue
        old_path = _normalize_patch_path(
            lines[idx][4:].rstrip("\n"), strip_components=strip_components, anchor=anchor
        )
        idx += 1
        if idx >= len(lines) or not lines[idx].startswith("+++ "):
            raise PatchApplicationError("missing +++ path after --- path")
        new_path = _normalize_patch_path(
            lines[idx][4:].rstrip("\n"), strip_components=strip_components, anchor=anchor
        )
        if new_path is None:
            raise AncestryViolationError("file deletion patch prohibited")
        idx += 1
        hunks: list[tuple[int, int, int, int, tuple[str, ...]]] = []
        while idx < len(lines):
            match = _HUNK_RE.match(lines[idx])
            if match:
                old_start = int(match.group(1)); old_count = int(match.group(2) or "1")
                new_start = int(match.group(3)); new_count = int(match.group(4) or "1")
                idx += 1
                body: list[str] = []
                while idx < len(lines):
                    line = lines[idx]
                    if line.startswith("@@ ") or line.startswith("--- "):
                        break
                    if line.startswith("diff --git ") or line.startswith("index "):
                        idx += 1
                        continue
                    if line.startswith("\\ No newline at end of file"):
                        idx += 1
                        continue
                    if not line or line[0] not in {" ", "+", "-"}:
                        break
                    body.append(line)
                    idx += 1
                hunks.append((old_start, old_count, new_start, new_count, tuple(body)))
                continue
            if lines[idx].startswith("--- "):
                break
            idx += 1
        if not hunks:
            raise PatchApplicationError(f"no hunks for patch path {new_path}")
        files.append(UnifiedPatchFile(old_path, new_path, tuple(hunks)))
    if not files:
        raise PatchApplicationError("no unified-diff file sections found")
    return tuple(files)


def apply_unified_patch(
    root: Path,
    patch_file: Path,
    *,
    strip_components: int = 0,
    anchor: str | None = None,
) -> dict[str, Any]:
    sections = parse_unified_patch(
        patch_file.read_text(encoding="utf-8"),
        strip_components=strip_components,
        anchor=anchor,
    )
    changed: list[str] = []
    created: list[str] = []
    for section in sections:
        target = root / section.new_path
        if section.old_path is None:
            original: list[str] = []
            created.append(section.new_path)
        else:
            old_target = root / section.old_path
            if not old_target.is_file():
                raise PatchApplicationError(f"patch input missing: {section.old_path}")
            original = old_target.read_text(encoding="utf-8").splitlines(keepends=True)
            if section.old_path != section.new_path:
                raise PatchApplicationError("renames are not admitted; preserve old path and add a new path")
        output: list[str] = []
        cursor = 0
        for old_start, old_count, new_start, new_count, body in section.hunks:
            hunk_index = 0 if old_start == 0 else old_start - 1
            if hunk_index < cursor or hunk_index > len(original):
                raise PatchApplicationError(f"invalid hunk position for {section.new_path}")
            output.extend(original[cursor:hunk_index])
            source_cursor = hunk_index
            consumed = 0
            produced = 0
            for line in body:
                marker, text = line[0], line[1:]
                if marker == " ":
                    if source_cursor >= len(original) or original[source_cursor] != text:
                        raise PatchApplicationError(f"context mismatch in {section.new_path}")
                    output.append(text); source_cursor += 1; consumed += 1; produced += 1
                elif marker == "-":
                    if source_cursor >= len(original) or original[source_cursor] != text:
                        raise PatchApplicationError(f"removal mismatch in {section.new_path}")
                    source_cursor += 1; consumed += 1
                elif marker == "+":
                    output.append(text); produced += 1
            if consumed != old_count or produced != new_count:
                raise PatchApplicationError(
                    f"hunk count mismatch in {section.new_path}: consumed={consumed}/{old_count}, produced={produced}/{new_count}"
                )
            cursor = source_cursor
        output.extend(original[cursor:])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("".join(output), encoding="utf-8")
        changed.append(section.new_path)
    return {
        "schema": "HHS_PASS134_UNIFIED_PATCH_APPLICATION_RECEIPT_V1",
        "patch": str(patch_file),
        "patch_sha256": sha256_file(patch_file),
        "changed_paths": sorted(changed),
        "created_paths": sorted(created),
        "deleted_paths": [],
        "status": "PATCH_APPLIED_WITHOUT_SYSTEM_DELETION",
    }


def recover_operation_chain(
    base_checkpoint: Path,
    operations_manifest: Path,
    output_dir: Path,
    *,
    allow_legacy_base: bool = False,
) -> dict[str, Any]:
    operations_doc = json.loads(operations_manifest.read_text(encoding="utf-8"))
    if operations_doc.get("schema") != "HHS_PASS134_RECOVERY_OPERATIONS_V1":
        raise CheckpointError("operations manifest schema mismatch")
    operations = operations_doc.get("operations")
    if not isinstance(operations, list) or not operations:
        raise CheckpointError("operations manifest contains no operations")
    output_dir.mkdir(parents=True, exist_ok=True)
    current = base_checkpoint
    receipts: list[dict[str, Any]] = []
    manifest_base = operations_manifest.parent
    for index, operation in enumerate(operations):
        pass_id = str(operation["pass_id"])
        parent_pass = str(operation["parent_pass"])
        expected_sha = operation.get("expected_parent_sha256")
        expected_root = operation.get("expected_parent_tree_root")
        kind = operation["kind"]
        with tempfile.TemporaryDirectory(prefix=f"hhs134_op_{index:03d}_") as td:
            delta = Path(td) / "delta"
            delta.mkdir()
            if kind == "OVERLAY_DIRECTORY":
                source = (manifest_base / operation["path"]).resolve()
                copy_noncache_tree(source, delta)
                op_receipt = {
                    "kind": kind,
                    "source": str(source),
                    "source_tree_root_sha256": tree_root_from_records(tree_records(source)),
                }
            elif kind == "UNIFIED_PATCH":
                # Materialize the current parent tree as the patch delta base,
                # patch it, then include only changed/created files in delta.
                classification, parent_root, parent_td = _admit_parent_archive(
                    current, allow_legacy_parent=allow_legacy_base if index == 0 else False
                )
                try:
                    work = Path(td) / "patch_work"
                    work.mkdir()
                    copy_noncache_tree(parent_root, work)
                    patch_path = (manifest_base / operation["path"]).resolve()
                    patch_receipt = apply_unified_patch(
                        work, patch_path,
                        strip_components=int(operation.get("strip_components", 0)),
                        anchor=operation.get("anchor"),
                    )
                    for rel in patch_receipt["changed_paths"]:
                        source = work / rel
                        target = delta / rel
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, target)
                    op_receipt = {"kind": kind, **patch_receipt}
                finally:
                    parent_td.cleanup()
            else:
                raise CheckpointError(f"unsupported operation kind: {kind}")
            output = output_dir / f"hhs_{pass_id.lower()}_full_checkpoint.zip"
            receipt = build_full_child_checkpoint(
                current, delta, output,
                pass_id=pass_id, parent_pass=parent_pass,
                expected_parent_sha256=expected_sha,
                expected_parent_tree_root=expected_root,
                allow_legacy_parent=allow_legacy_base if index == 0 else False,
            )
            receipt["operation"] = op_receipt
            receipts.append(receipt)
            current = output
    chain = {
        "schema": CHAIN_RECEIPT_SCHEMA,
        "base_checkpoint": str(base_checkpoint),
        "base_sha256": sha256_file(base_checkpoint),
        "operations_manifest": str(operations_manifest),
        "operations_manifest_sha256": sha256_file(operations_manifest),
        "operation_count": len(receipts),
        "receipts": receipts,
        "final_checkpoint": str(current),
        "final_sha256": sha256_file(current),
        "status": "FULL_CHECKPOINT_CHAIN_RECONSTRUCTED",
    }
    chain["chain_hash72_witness"] = make_hash72_witness(
        "hhs_pass134_recovery_chain_receipt_v1", chain
    ).to_dict()
    return chain


def locate_first_corruption(checkpoints: Sequence[Path]) -> dict[str, Any]:
    if not checkpoints:
        raise ValueError("at least one checkpoint required")
    results: list[dict[str, Any]] = []
    previous_manifest: dict[str, Any] | None = None
    first_corrupt: int | None = None
    for index, archive in enumerate(checkpoints):
        classification = classify_archive(archive)
        row: dict[str, Any] = {"index": index, "archive": str(archive), **asdict(classification)}
        if classification.archive_class != "FULL_SYSTEM_CHECKPOINT":
            row["valid"] = False
            row["reason"] = classification.archive_class
        else:
            with tempfile.TemporaryDirectory(prefix="hhs134_locate_") as td:
                extracted = Path(td) / "tree"; extracted.mkdir()
                safe_extract_zip(archive, extracted)
                root = resolve_single_root(extracted)
                manifest = json.loads((root / MANIFEST_NAME).read_text(encoding="utf-8"))
                row["valid"] = True
                row["tree_root_sha256"] = manifest["tree_root_sha256"]
                if previous_manifest is not None:
                    row["parent_root_matches"] = manifest.get("parent_tree_root") == previous_manifest.get("tree_root_sha256")
                    if not row["parent_root_matches"]:
                        row["valid"] = False
                        row["reason"] = "PARENT_TREE_ROOT_DISCONTINUITY"
                previous_manifest = manifest
        if not row["valid"] and first_corrupt is None:
            first_corrupt = index
        results.append(row)
    return {
        "schema": "HHS_PASS134_CORRUPTION_LOCALIZATION_REPORT_V1",
        "checkpoint_count": len(checkpoints),
        "first_corrupt_index": first_corrupt,
        "first_corrupt_archive": str(checkpoints[first_corrupt]) if first_corrupt is not None else None,
        "chain_valid": first_corrupt is None,
        "results": results,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hhs-pass134-checkpoint")
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory")
    inv.add_argument("archive", type=Path)
    build = sub.add_parser("build")
    build.add_argument("parent", type=Path); build.add_argument("delta", type=Path); build.add_argument("output", type=Path)
    build.add_argument("--pass-id", required=True); build.add_argument("--parent-pass", required=True)
    build.add_argument("--allow-legacy-parent", action="store_true")
    recover = sub.add_parser("recover-chain")
    recover.add_argument("base", type=Path); recover.add_argument("operations", type=Path); recover.add_argument("output_dir", type=Path)
    recover.add_argument("--allow-legacy-base", action="store_true")
    locate = sub.add_parser("locate-corruption")
    locate.add_argument("checkpoints", type=Path, nargs="+")
    args = parser.parse_args(argv)
    if args.command == "inventory":
        result = asdict(classify_archive(args.archive))
    elif args.command == "build":
        result = build_full_child_checkpoint(
            args.parent, args.delta, args.output,
            pass_id=args.pass_id, parent_pass=args.parent_pass,
            allow_legacy_parent=args.allow_legacy_parent,
        )
    elif args.command == "recover-chain":
        result = recover_operation_chain(
            args.base, args.operations, args.output_dir,
            allow_legacy_base=args.allow_legacy_base,
        )
    else:
        result = locate_first_corruption(args.checkpoints)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
