#!/usr/bin/env python3
"""Create, validate, stage, and atomically activate HHS Runtime OS bundles.

Production uses this tool so the DigitalOcean host never needs npm. GitHub
builds the TypeScript/Vite tree, binds every emitted file to the exact repository
commit, and transfers the archive + manifest. The host verifies both before
candidate boot or activation.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import shutil
import stat
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA = "HHS_RUNTIME_OS_DEPLOY_BUNDLE_V1"
INTERFACE = "HHS_VISUAL_RUNTIME_OS_WORKSPACE"
INDEX_IDENTITY = "HHS Visual Runtime OS Workspace"
ASSET_PREFIX = "/assets/index-"
RELEASE_MANIFEST = ".hhs-runtime-os-manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_sha(value: str) -> str:
    value = value.strip().lower()
    if len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
        raise SystemExit(f"repository SHA must be 40 lowercase/uppercase hex characters: {value!r}")
    return value


def safe_relpath(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise SystemExit(f"unsafe bundle path: {value!r}")
    return path


def validate_dist(root: Path) -> list[dict[str, Any]]:
    root = root.resolve()
    index = root / "index.html"
    assets = root / "assets"
    if not index.is_file():
        raise SystemExit(f"Runtime OS index missing: {index}")
    if not assets.is_dir():
        raise SystemExit(f"Runtime OS assets missing: {assets}")
    html = index.read_text(encoding="utf-8")
    if INDEX_IDENTITY not in html:
        raise SystemExit("Runtime OS index identity missing")
    if ASSET_PREFIX not in html:
        raise SystemExit("Runtime OS hashed application asset reference missing")

    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"symlinks are forbidden in Runtime OS bundle: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise SystemExit(f"unsupported Runtime OS filesystem entry: {path}")
        relative = path.relative_to(root).as_posix()
        safe_relpath(relative)
        records.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    if not any(record["path"].startswith("assets/index-") for record in records):
        raise SystemExit("Runtime OS emitted asset bundle is missing")
    return records


def deterministic_archive(dist: Path, records: list[dict[str, Any]], archive: Path) -> None:
    archive.parent.mkdir(parents=True, exist_ok=True)
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as tar:
                directories: set[str] = set()
                for record in records:
                    pure = PurePosixPath(record["path"])
                    for parent in pure.parents:
                        if str(parent) != ".":
                            directories.add(parent.as_posix())
                for relative in sorted(directories, key=lambda item: (item.count("/"), item)):
                    info = tarfile.TarInfo(relative)
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    info.mtime = 0
                    tar.addfile(info)
                for record in records:
                    source = dist / record["path"]
                    info = tarfile.TarInfo(record["path"])
                    info.size = record["bytes"]
                    info.mode = 0o644
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    info.mtime = 0
                    with source.open("rb") as handle:
                        tar.addfile(info, handle)


def load_manifest(path: Path, expected_sha: str | None = None) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise SystemExit(f"unexpected Runtime OS bundle schema: {payload.get('schema')!r}")
    sha = require_sha(str(payload.get("repository_sha", "")))
    if expected_sha is not None and sha != require_sha(expected_sha):
        raise SystemExit(f"Runtime OS bundle repository SHA mismatch: {sha} != {expected_sha}")
    if payload.get("interface") != INTERFACE:
        raise SystemExit(f"unexpected Runtime OS interface: {payload.get('interface')!r}")
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("Runtime OS bundle manifest has no files")
    seen: set[str] = set()
    for record in files:
        if not isinstance(record, dict):
            raise SystemExit("invalid Runtime OS file record")
        relative = safe_relpath(str(record.get("path", ""))).as_posix()
        if relative in seen:
            raise SystemExit(f"duplicate Runtime OS bundle path: {relative}")
        seen.add(relative)
        digest = str(record.get("sha256", ""))
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest.lower()):
            raise SystemExit(f"invalid Runtime OS file digest: {relative}")
        if not isinstance(record.get("bytes"), int) or record["bytes"] < 0:
            raise SystemExit(f"invalid Runtime OS file length: {relative}")
    return payload


def verify_tree(root: Path, manifest: dict[str, Any]) -> None:
    expected = {record["path"]: record for record in manifest["files"]}
    actual: set[str] = set()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"symlink found in staged Runtime OS release: {path}")
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == RELEASE_MANIFEST:
            continue
        actual.add(relative)
        record = expected.get(relative)
        if record is None:
            raise SystemExit(f"unexpected file in Runtime OS release: {relative}")
        if path.stat().st_size != record["bytes"]:
            raise SystemExit(f"Runtime OS file length mismatch: {relative}")
        if sha256_file(path) != record["sha256"]:
            raise SystemExit(f"Runtime OS file digest mismatch: {relative}")
    missing = sorted(set(expected) - actual)
    if missing:
        raise SystemExit(f"Runtime OS release missing files: {missing[:10]}")
    validate_dist(root)


def command_create(args: argparse.Namespace) -> None:
    dist = Path(args.dist).resolve()
    archive = Path(args.archive).resolve()
    manifest_path = Path(args.manifest).resolve()
    sha = require_sha(args.repository_sha)
    records = validate_dist(dist)
    deterministic_archive(dist, records, archive)
    payload = {
        "schema": SCHEMA,
        "repository_sha": sha,
        "interface": INTERFACE,
        "frontend_stack": "typescript-react-vite",
        "legacy_harmonizer_is_public_root": False,
        "archive_sha256": sha256_file(archive),
        "archive_bytes": archive.stat().st_size,
        "file_count": len(records),
        "total_file_bytes": sum(record["bytes"] for record in records),
        "index_sha256": next(record["sha256"] for record in records if record["path"] == "index.html"),
        "files": records,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "repository_sha": sha, "archive": str(archive), "manifest": str(manifest_path), "archive_sha256": payload["archive_sha256"]}, sort_keys=True))


def extract_verified(archive: Path, destination: Path, manifest: dict[str, Any]) -> None:
    expected = {record["path"] for record in manifest["files"]}
    seen: set[str] = set()
    with tarfile.open(archive, mode="r:gz") as tar:
        for member in tar.getmembers():
            relative = safe_relpath(member.name).as_posix()
            if member.isdir():
                (destination / relative).mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile() or member.issym() or member.islnk():
                raise SystemExit(f"unsupported Runtime OS archive member: {relative}")
            if relative not in expected:
                raise SystemExit(f"archive contains unmanifested Runtime OS file: {relative}")
            if relative in seen:
                raise SystemExit(f"archive contains duplicate Runtime OS file: {relative}")
            seen.add(relative)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                raise SystemExit(f"unable to read Runtime OS archive member: {relative}")
            with target.open("wb") as handle:
                shutil.copyfileobj(source, handle)
            os.chmod(target, 0o644)
    if seen != expected:
        missing = sorted(expected - seen)
        raise SystemExit(f"archive missing Runtime OS files: {missing[:10]}")


def command_stage(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    archive = Path(args.archive).resolve()
    manifest_path = Path(args.manifest).resolve()
    sha = require_sha(args.expected_sha)
    manifest = load_manifest(manifest_path, sha)
    if not archive.is_file():
        raise SystemExit(f"Runtime OS bundle archive missing: {archive}")
    if archive.stat().st_size != manifest.get("archive_bytes"):
        raise SystemExit("Runtime OS archive length mismatch")
    if sha256_file(archive) != manifest.get("archive_sha256"):
        raise SystemExit("Runtime OS archive SHA-256 mismatch")

    releases = root / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    release = releases / sha
    if release.exists():
        stored_manifest = release / RELEASE_MANIFEST
        existing = load_manifest(stored_manifest, sha)
        if existing.get("archive_sha256") != manifest.get("archive_sha256"):
            raise SystemExit(f"existing Runtime OS release conflicts with bundle for {sha}")
        verify_tree(release, existing)
        print(str(release))
        return

    stage = Path(tempfile.mkdtemp(prefix=f".stage-{sha[:12]}-", dir=releases))
    try:
        extract_verified(archive, stage, manifest)
        verify_tree(stage, manifest)
        (stage / RELEASE_MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        for path in stage.rglob("*"):
            os.chmod(path, 0o755 if path.is_dir() else 0o644)
        os.replace(stage, release)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    print(str(release))


def release_for(root: Path, sha: str) -> Path:
    release = root.resolve() / "releases" / require_sha(sha)
    if not release.is_dir():
        raise SystemExit(f"Runtime OS release missing: {release}")
    manifest = load_manifest(release / RELEASE_MANIFEST, sha)
    verify_tree(release, manifest)
    return release


def command_verify(args: argparse.Namespace) -> None:
    release = release_for(Path(args.root), args.expected_sha)
    print(str(release))


def command_activate(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    release = release_for(root, args.expected_sha)
    root.mkdir(parents=True, exist_ok=True)
    current = root / "current"
    temp_link = root / f".current-{os.getpid()}"
    temp_link.unlink(missing_ok=True)
    os.symlink(os.path.relpath(release, root), temp_link)
    if current.exists() and not current.is_symlink():
        legacy = root / f"legacy-current-{os.getpid()}"
        os.replace(current, legacy)
    os.replace(temp_link, current)
    print(str(release))


def command_current(args: argparse.Namespace) -> None:
    current = Path(args.root).resolve() / "current"
    if not current.is_symlink():
        print("")
        return
    print(str(current.resolve()))


def command_restore(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    current = root / "current"
    if args.release:
        release = Path(args.release).resolve()
        releases = (root / "releases").resolve()
        try:
            relative = release.relative_to(releases)
        except ValueError as exc:
            raise SystemExit(f"rollback release is outside Runtime OS release root: {release}") from exc
        release_for(root, relative.name)
        temp_link = root / f".current-rollback-{os.getpid()}"
        temp_link.unlink(missing_ok=True)
        os.symlink(os.path.relpath(release, root), temp_link)
        os.replace(temp_link, current)
    else:
        if current.is_symlink() or current.is_file():
            current.unlink()
        elif current.exists():
            shutil.rmtree(current)
    print(args.release or "")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    commands = result.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--dist", required=True)
    create.add_argument("--repository-sha", required=True)
    create.add_argument("--archive", required=True)
    create.add_argument("--manifest", required=True)
    create.set_defaults(func=command_create)
    stage = commands.add_parser("stage")
    stage.add_argument("--root", required=True)
    stage.add_argument("--archive", required=True)
    stage.add_argument("--manifest", required=True)
    stage.add_argument("--expected-sha", required=True)
    stage.set_defaults(func=command_stage)
    verify = commands.add_parser("verify")
    verify.add_argument("--root", required=True)
    verify.add_argument("--expected-sha", required=True)
    verify.set_defaults(func=command_verify)
    activate = commands.add_parser("activate")
    activate.add_argument("--root", required=True)
    activate.add_argument("--expected-sha", required=True)
    activate.set_defaults(func=command_activate)
    current = commands.add_parser("current")
    current.add_argument("--root", required=True)
    current.set_defaults(func=command_current)
    restore = commands.add_parser("restore")
    restore.add_argument("--root", required=True)
    restore.add_argument("--release", default="")
    restore.set_defaults(func=command_restore)
    return result


def main() -> int:
    args = parser().parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
