from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .core import CONTRACT_ID, PASS_NUMBER, canonical_spec, stable, validate_spec


def load_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"HHS_GFCC_INVALID_SPEC:source file missing:{path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"HHS_GFCC_INVALID_SPEC:cannot parse source:{exc}") from exc
    normalized = stable(payload)
    validate_spec(normalized)
    return normalized


def canonical_spec_path(repo: Path) -> Path:
    return (
        repo
        / "native_projects"
        / "hhs_gfcc_pass152"
        / "specs"
        / "golden_correspondence.json"
    )


def load_canonical_spec(repo: Path) -> dict[str, Any]:
    loaded = load_spec(canonical_spec_path(repo))
    expected = canonical_spec(int(loaded["fibonacci_stage"]))
    if loaded != expected:
        raise ValueError(
            "HHS_GFCC_INVALID_SPEC:file specification differs from canonical interpretation"
        )
    return loaded


__all__ = [
    "CONTRACT_ID",
    "PASS_NUMBER",
    "canonical_spec",
    "canonical_spec_path",
    "load_spec",
    "load_canonical_spec",
    "validate_spec",
]
