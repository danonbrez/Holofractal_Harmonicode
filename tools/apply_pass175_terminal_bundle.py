#!/usr/bin/env python3
"""Materialize the temporary Pass 175 terminal source bundle on its task branch."""
from __future__ import annotations

from base64 import b64decode
from pathlib import Path
import io
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "tools" / "pass175_terminal_source_bundle.b64"


def main() -> int:
    encoded = BUNDLE.read_text(encoding="ascii").strip()
    archive = b64decode(encoded, validate=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as handle:
        for member in handle.getmembers():
            target = (ROOT / member.name).resolve()
            if ROOT not in target.parents and target != ROOT:
                raise SystemExit(f"unsafe bundle path: {member.name}")
        handle.extractall(ROOT, filter="data")
    BUNDLE.unlink()
    accidental = ROOT / "evidence" / "pass175" / "_unused"
    if accidental.exists():
        accidental.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
