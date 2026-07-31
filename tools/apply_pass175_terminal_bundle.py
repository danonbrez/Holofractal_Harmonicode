#!/usr/bin/env python3
"""Materialize the bounded Pass 175 terminal source bundle on its task branch."""
from __future__ import annotations

from base64 import b64decode
from hashlib import sha256
from pathlib import Path
import io
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[1]
MONOLITHIC_BUNDLE = ROOT / "tools" / "pass175_terminal_source_bundle.b64"
PARTS = ROOT / "tools" / "pass175_terminal_bundle_parts"
EXPECTED_BASE64_LENGTH = 68336
EXPECTED_ARCHIVE_SHA256 = "623e33e34a236af92a0ec5f1337ea1f932864771fd30a1647f79bf86ba7a8bda"


def _encoded_bundle() -> str:
    part_paths = sorted(PARTS.glob("part*")) if PARTS.is_dir() else []
    if part_paths:
        encoded = "".join(path.read_text(encoding="ascii").strip() for path in part_paths)
    elif MONOLITHIC_BUNDLE.is_file():
        encoded = MONOLITHIC_BUNDLE.read_text(encoding="ascii").strip()
    else:
        raise SystemExit("Pass 175 terminal source bundle is missing")
    if len(encoded) != EXPECTED_BASE64_LENGTH:
        raise SystemExit(f"Pass 175 terminal bundle length mismatch: {len(encoded)}")
    return encoded


def main() -> int:
    archive = b64decode(_encoded_bundle(), validate=True)
    actual_sha256 = sha256(archive).hexdigest()
    if actual_sha256 != EXPECTED_ARCHIVE_SHA256:
        raise SystemExit(f"Pass 175 terminal bundle SHA-256 mismatch: {actual_sha256}")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as handle:
        for member in handle.getmembers():
            target = (ROOT / member.name).resolve()
            if ROOT not in target.parents and target != ROOT:
                raise SystemExit(f"unsafe bundle path: {member.name}")
        handle.extractall(ROOT, filter="data")
    if MONOLITHIC_BUNDLE.exists():
        MONOLITHIC_BUNDLE.unlink()
    if PARTS.exists():
        shutil.rmtree(PARTS)
    accidental = ROOT / "evidence" / "pass175" / "_unused"
    if accidental.exists():
        accidental.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
