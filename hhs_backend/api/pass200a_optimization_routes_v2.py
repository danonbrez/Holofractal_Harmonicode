"""Bind Pass 200A route definitions to the canonical production authority."""
from __future__ import annotations

from hhs_backend.api import pass200a_optimization_routes as _routes
from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization import (
    PASS200A_OPTIMIZATION_AUTHORITY,
)

_routes.PASS200A_OPTIMIZATION_AUTHORITY = PASS200A_OPTIMIZATION_AUTHORITY
router = _routes.router
