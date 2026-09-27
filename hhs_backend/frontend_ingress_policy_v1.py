"""Standard browser/frontend ingress policy for the canonical HHS backend.

The native runtime remains authoritative internally.  This module only governs
ordinary HTTP browser transport at the compatibility membrane so React, Vite,
plain JavaScript, mobile WebViews, or another standard frontend can use the
same FastAPI/OpenAPI/WebSocket surfaces without weakening runtime authority.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

VERSION = "HHS_STANDARD_FRONTEND_INGRESS_POLICY_V1"

STANDARD_BROWSER_METHODS = (
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
)

EXPOSED_BROWSER_HEADERS = (
    "content-disposition",
    "etag",
    "x-hhs-runtime-cache",
    "x-hhs-runtime-cache-age-ms",
)


class FrontendIngressPolicyError(RuntimeError):
    """Raised when browser ingress configuration would widen authority unsafely."""


def _normalize_origin(value: str) -> str:
    origin = str(value or "").strip().rstrip("/")
    if not origin:
        return ""
    if origin == "*":
        raise FrontendIngressPolicyError("HHS_PRODUCTION_CORS_WILDCARD_FORBIDDEN")

    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise FrontendIngressPolicyError(
            f"HHS_CORS_ORIGIN_INVALID:{origin}"
        )
    if parsed.username or parsed.password:
        raise FrontendIngressPolicyError(
            f"HHS_CORS_ORIGIN_USERINFO_FORBIDDEN:{origin}"
        )
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise FrontendIngressPolicyError(
            f"HHS_CORS_ORIGIN_MUST_BE_SCHEME_HOST_PORT_ONLY:{origin}"
        )
    return f"{parsed.scheme}://{parsed.netloc}"


def parse_allowed_origins(raw: str | None) -> list[str]:
    """Parse an exact, duplicate-free CORS origin allowlist."""

    origins: list[str] = []
    seen: set[str] = set()
    for item in str(raw or "").split(","):
        origin = _normalize_origin(item)
        if not origin or origin in seen:
            continue
        origins.append(origin)
        seen.add(origin)
    return origins


def configured_frontend_ingress_policy(
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    env = os.environ if environ is None else environ
    origins = parse_allowed_origins(env.get("HHS_CORS_ALLOWED_ORIGINS"))
    return {
        "schema": VERSION,
        "cors_allowed_origins": origins,
        "allow_credentials": True,
        "allow_methods": list(STANDARD_BROWSER_METHODS),
        "allow_headers": ["*"],
        "expose_headers": list(EXPOSED_BROWSER_HEADERS),
        "same_origin_requires_cors": False,
        "wildcard_origin_forbidden": True,
        "frontend_authority": "REQUEST_AND_PROJECTION_ONLY",
        "backend_authority": "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1",
    }


def frontend_ingress_policy_self_test() -> dict[str, Any]:
    configured = configured_frontend_ingress_policy({
        "HHS_CORS_ALLOWED_ORIGINS": (
            "https://console.example.com,"
            "http://127.0.0.1:5173,"
            "https://console.example.com/"
        )
    })
    wildcard_rejected = False
    path_rejected = False
    try:
        parse_allowed_origins("*")
    except FrontendIngressPolicyError:
        wildcard_rejected = True
    try:
        parse_allowed_origins("https://example.com/path")
    except FrontendIngressPolicyError:
        path_rejected = True
    return {
        "schema": "HHS_STANDARD_FRONTEND_INGRESS_POLICY_SELF_TEST_V1",
        "ok": bool(
            configured["cors_allowed_origins"]
            == ["https://console.example.com", "http://127.0.0.1:5173"]
            and wildcard_rejected
            and path_rejected
        ),
        "configured": configured,
        "wildcard_rejected": wildcard_rejected,
        "path_rejected": path_rejected,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(frontend_ingress_policy_self_test(), indent=2, sort_keys=True))
