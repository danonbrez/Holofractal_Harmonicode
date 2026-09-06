"""Retired legacy Heroku application constructor compatibility module.

Pass219 I177 removes this file's independent FastAPI construction authority.
The repository's deployment Procfile already targets the production application
IDE, and any residual import of ``hhs_backend.heroku_server:app`` now resolves
to the single canonical Pass170 public gateway rather than creating another
application identity or public-port surface.
"""
from __future__ import annotations

from hhs_backend.public_api_server import app

RETIREMENT_CLASSIFICATION = "PASS170_LEGACY_HEROKU_CONSTRUCTOR_RETIRED_I177"
CANONICAL_TARGET = "hhs_backend.public_api_server:app"
INDEPENDENT_FASTAPI_CONSTRUCTOR = False
PUBLIC_PORT_AUTHORITY = False
NEW_VM81_AUTHORITY = False
NEW_HASH72_MINT_AUTHORITY = False
HASH216_PERSISTENCE_AUTHORITY = False

__all__ = [
    "CANONICAL_TARGET",
    "HASH216_PERSISTENCE_AUTHORITY",
    "INDEPENDENT_FASTAPI_CONSTRUCTOR",
    "NEW_HASH72_MINT_AUTHORITY",
    "NEW_VM81_AUTHORITY",
    "PUBLIC_PORT_AUTHORITY",
    "RETIREMENT_CLASSIFICATION",
    "app",
]
