"""Bounded repository-history liveness projection.

The complete pass-contract catalog is intentionally hydrated only when a user
opens the repository-history surface.  This early-sorted router owns the cheap
``/api/runtime/repository/status`` projection during Pass 201 federation so
ordinary startup and health probes never recursively index the repository.
"""
from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter

REPOSITORY = "danonbrez/Holofractal_Harmonicode"

router = APIRouter(
    prefix="/api/runtime/repository",
    tags=["runtime", "repository", "pass-history", "commit-lineage", "visual-ide"],
)


@router.get("/status")
async def bounded_repository_history_status() -> dict[str, Any]:
    """Return repository-surface liveness without indexing repository files."""
    return {
        "schema": "HHS_REPOSITORY_HISTORY_STATUS_V1",
        "ok": True,
        "repository": REPOSITORY,
        "catalog_state": "DEFERRED_UNTIL_EXPLICIT_PASS_CATALOG_REQUEST",
        "pass_count": None,
        "pass_file_count": None,
        "earliest_pass": None,
        "latest_pass": None,
        "deployed_commit": os.environ.get("SOURCE_VERSION") or os.environ.get("HEROKU_SLUG_COMMIT"),
        "pass_catalog_api": "/api/runtime/repository/passes",
        "commit_history_api": "/api/runtime/repository/commits",
        "file_read_api": "/api/runtime/repository/file",
        "ide_default_surface": "FULL_INTEGRATED_DEVELOPMENT_ENVIRONMENT",
        "history_is_supporting_surface": True,
        "history_hydration": "USER_INITIATED",
        "status_read_is_bounded": True,
        "frontend_is_authority": False,
    }


__all__ = ["REPOSITORY", "bounded_repository_history_status", "router"]
