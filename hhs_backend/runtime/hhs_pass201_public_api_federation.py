"""Canonical production projection for Pass 201 public API federation."""
from __future__ import annotations

import re
from typing import Any, Dict, Mapping, Sequence

from fastapi import FastAPI

import hhs_backend.runtime.hhs_pass201_public_api_federation_v1 as _v1
from hhs_backend.runtime.hhs_pass201_public_api_federation_v1 import (
    CLASSIFICATION,
    CONTRACT,
    PUBLIC_API_PREFIX,
    VERSION,
    Pass201Error,
    PublicAPIFederation as _V1PublicAPIFederation,
)

_PATH_CONVERTER_PATTERN = re.compile(r"\{([^{}:]+):[^{}]+\}")


class PublicAPIFederation(_V1PublicAPIFederation):
    """Production federation with canonical OpenAPI path normalization."""

    @staticmethod
    def _openapi_path(path: str) -> str:
        return _PATH_CONVERTER_PATTERN.sub(r"{\1}", path)

    @staticmethod
    def _openapi_missing(app: FastAPI, routes: Sequence[Mapping[str, Any]]) -> list[Dict[str, Any]]:
        schema = app.openapi()
        paths = schema.get("paths", {}) if isinstance(schema, dict) else {}
        missing: list[Dict[str, Any]] = []
        for route in routes:
            if not route["include_in_schema"] or "WEBSOCKET" in route["methods"] or "MOUNT" in route["methods"]:
                continue
            schema_path_identity = PublicAPIFederation._openapi_path(str(route["path"]))
            schema_path = paths.get(schema_path_identity, {})
            for method in route["methods"]:
                if method in {"HEAD", "OPTIONS"}:
                    continue
                if method.lower() not in schema_path:
                    missing.append(
                        {
                            "route_id": route["route_id"],
                            "path": route["path"],
                            "openapi_path": schema_path_identity,
                            "method": method,
                        }
                    )
        return missing


PASS201_PUBLIC_API_FEDERATION = PublicAPIFederation()


def register_public_api_federation(app: FastAPI) -> Dict[str, Any]:
    return PASS201_PUBLIC_API_FEDERATION.register_all_api_routers(app)


# Importing the production projection before legacy V1 symbols are consumed
# keeps existing import paths compatible while making the normalized behavior
# canonical for the composed public server.
_v1.PASS201_PUBLIC_API_FEDERATION = PASS201_PUBLIC_API_FEDERATION
_v1.register_public_api_federation = register_public_api_federation


__all__ = [
    "CLASSIFICATION",
    "CONTRACT",
    "PUBLIC_API_PREFIX",
    "VERSION",
    "Pass201Error",
    "PublicAPIFederation",
    "PASS201_PUBLIC_API_FEDERATION",
    "register_public_api_federation",
]
