"""Retired legacy ``hhs_runtime.main`` FastAPI constructor compatibility shim.

Pass219 I178 removes this module's independent application identity after its
public self-launch was already redirected in I174/I176. Direct execution and
legacy ``app`` imports now resolve to the single canonical Pass170 gateway.
The historical runtime implementation remains preserved in repository history;
no VM81, Hash72, Hash216, or browser/Python replacement authority is created.
"""
from __future__ import annotations

from hhs_backend.public_api_server import app

RETIREMENT_CLASSIFICATION = "PASS170_LEGACY_RUNTIME_MAIN_CONSTRUCTOR_RETIRED_I178"
CANONICAL_TARGET = "hhs_backend.public_api_server:app"
INDEPENDENT_FASTAPI_CONSTRUCTOR = False
PUBLIC_PORT_AUTHORITY = False
NEW_VM81_AUTHORITY = False
NEW_HASH72_MINT_AUTHORITY = False
HASH216_PERSISTENCE_AUTHORITY = False


def main() -> None:
    import uvicorn

    uvicorn.run(
        "hhs_backend.public_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()


__all__ = [
    "CANONICAL_TARGET",
    "HASH216_PERSISTENCE_AUTHORITY",
    "INDEPENDENT_FASTAPI_CONSTRUCTOR",
    "NEW_HASH72_MINT_AUTHORITY",
    "NEW_VM81_AUTHORITY",
    "PUBLIC_PORT_AUTHORITY",
    "RETIREMENT_CLASSIFICATION",
    "app",
    "main",
]
