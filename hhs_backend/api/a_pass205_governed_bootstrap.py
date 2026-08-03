"""Install the governed Pass 205 singleton before public router federation.

Pass 201 imports API modules in lexical order. This bootstrap intentionally has
no router; it replaces the legacy route module's singleton before that module's
routes are attached to the hosted application.
"""
from __future__ import annotations

from hhs_backend.runtime.hhs_pass205_governed_continuation_v2 import (
    GOVERNED_PASS205_CONTINUATION_RUNTIME,
)
from hhs_backend.api import pass205_continuation_routes as _routes

_routes.PASS205_CONTINUATION_RUNTIME = GOVERNED_PASS205_CONTINUATION_RUNTIME

PASS205_GOVERNED_ROUTE_BINDING = {
    "schema": "HHS_PASS_205_GOVERNED_ROUTE_BINDING_V1",
    "ok": True,
    "runtime_class": GOVERNED_PASS205_CONTINUATION_RUNTIME.__class__.__name__,
    "single_vm81_mutation_authority": True,
    "reconstructive_replay": True,
}

__all__ = ["PASS205_GOVERNED_ROUTE_BINDING"]
