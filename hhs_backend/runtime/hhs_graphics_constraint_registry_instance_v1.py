"""Singleton Pass 181 graphics constraint and style-profile registry."""
from __future__ import annotations

import os
from pathlib import Path

from hhs_backend.runtime.hhs_graphics_constraint_registry_v1 import GraphicsConstraintRegistry

_repo_root = Path(__file__).resolve().parents[2]
_base = Path(
    os.environ.get(
        "HHS_GRAPHICS_HYDRATION_ROOT",
        str(_repo_root / "artifacts" / "graphics_hydration"),
    )
)

GRAPHICS_CONSTRAINT_REGISTRY = GraphicsConstraintRegistry(_base / "constraint_registry")
