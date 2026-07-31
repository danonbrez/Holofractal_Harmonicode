"""Singleton Pass 181 bounded graphics optimizer instance."""
from __future__ import annotations

import os
from pathlib import Path

from hhs_backend.runtime.hhs_graphics_optimization_v1 import BoundedGraphicsOptimizer

_repo_root = Path(__file__).resolve().parents[2]
_artifact_root = Path(
    os.environ.get(
        "HHS_GRAPHICS_HYDRATION_ROOT",
        str(_repo_root / "artifacts" / "graphics_hydration"),
    )
)

GRAPHICS_OPTIMIZER = BoundedGraphicsOptimizer(_artifact_root)
