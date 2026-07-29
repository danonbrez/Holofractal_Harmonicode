from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import os

from .canonical import hash216
from .journal import atomic_write_json


def activate_version(hhs_home: str | Path, version_id: str) -> dict[str, Any]:
    root = Path(hhs_home).expanduser().resolve()
    target = root / "versions" / version_id
    if not target.is_dir():
        raise ValueError("P172_ACTIVATION_TARGET_MISSING")
    pointer = root / "current.json"
    previous = None
    if pointer.exists():
        previous = json.loads(pointer.read_text(encoding="utf-8")).get("active_version")
    payload = {
        "schema": "HHS_PASS_172_ACTIVE_VERSION_V1",
        "active_version": version_id,
        "previous_version": previous,
    }
    atomic_write_json(pointer, payload)
    return {
        "status": "SUCCESS",
        "classification": "P172_ACTIVATION_COMPLETED",
        "active_version": version_id,
        "previous_version": previous,
        "pointer_identity": hash216(payload, domain="HHS-P172-ACTIVE-POINTER-V1"),
    }
