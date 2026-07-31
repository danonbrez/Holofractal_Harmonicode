"""Singleton durable Pass 181 graphics vector-hydration store."""
from __future__ import annotations

import os
from pathlib import Path

from hhs_backend.runtime.hhs_graphics_vector_hydration_v1 import GraphicsVectorHydrationStore

_repo_root = Path(__file__).resolve().parents[2]
_base = Path(
    os.environ.get(
        "HHS_GRAPHICS_HYDRATION_ROOT",
        str(_repo_root / "artifacts" / "graphics_hydration"),
    )
)

GRAPHICS_VECTOR_HYDRATION = GraphicsVectorHydrationStore(_base / "vector_hydration")
