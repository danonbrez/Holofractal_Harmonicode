#!/usr/bin/env python3
"""Signed capability tokens for Pass 190 remote mutation authority."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import time
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from hhs_pass190 import HHSOperationError, canonical_json, hash72

CAPABILITY_SCHEMA = "HHS_PASS_190_CAPABILITY_V1"
AUTHORIZATION_SCHEME = "HHS-Capability"
_SCOPE = re.compile(r"^[a-z][a-z0-9_.:-]{0,127}$")
_MAX_LIFETIME_SECONDS = 86_400
_CLOCK_SKEW_SECONDS = 30


class CapabilityTokenError(HHSOperationError):
    """A capability credential is absent, malformed, forged, or expired."""


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    principal: str
    scopes: frozenset[str]
    issued_at: int
    expires_at: int
    nonce: str
    token_hash72: str


def _secret_bytes(secret: str | bytes) -> bytes:
    encoded = secret.encode("utf-8") if isinstance(secret, str) else bytes(secret)
    if len(encoded) < 32:
        raise CapabilityTokenError("capability secret must contain at least 32 bytes")
    return encoded


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    if not value or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise CapabilityTokenError("invalid base64url capability segment")
    padding = "=" * ((4 - len(value) % 4) % 4)
    try:
        return base64.b64decode(value + padding, altchars=b"-_", validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise CapabilityTokenError("invalid base64url capability segment") from exc


def _validated_scopes(scopes: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(sorted(set(scopes)))
    if not normalized:
        raise CapabilityTokenError("capability token requires at least one scope")
    if any(not isinstance(scope, str) or not _SCOPE.fullmatch(scope) for scope in normalized):
        raise CapabilityTokenError("invalid capability scope")
    return normalized


def issue_capability_token(
    secret: str | bytes,
    *,
    principal: str,
    scopes: Iterable[str],
    ttl_seconds: int = 900,
    now: int | None = None,
    nonce: str | None = None,
) -> str:
    """Issue one bounded HMAC-SHA256 credential with exact integer timestamps."""
    key = _secret_bytes(secret)
    if not isinstance(principal, str) or not principal or len(principal) > 256:
        raise CapabilityTokenError("invalid capability principal")
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int):
        raise CapabilityTokenError("capability lifetime must be an integer")
    if ttl_seconds < 1 or ttl_seconds > _MAX_LIFETIME_SECONDS:
        raise CapabilityTokenError("capability lifetime outside admitted range")
    issued_at = int(time.time()) if now is None else now
    if isinstance(issued_at, bool) or not isinstance(issued_at, int) or issued_at < 0:
        raise CapabilityTokenError("invalid capability issue time")
    token_nonce = nonce or secrets.token_urlsafe(18)
    if not isinstance(token_nonce, str) or not token_nonce or len(token_nonce) > 256:
        raise CapabilityTokenError("invalid capability nonce")
    payload = {
        "schema": CAPABILITY_SCHEMA,
        "principal": principal,
        "scopes": list(_validated_scopes(scopes)),
        "issued_at": issued_at,
        "expires_at": issued_at + ttl_seconds,
        "nonce": token_nonce,
    }
    encoded_payload = _b64url_encode(canonical_json(payload).encode("utf-8"))
    signature = hmac.new(key, encoded_payload.encode("ascii"), hashlib.sha256).digest()
    return encoded_payload + "." + _b64url_encode(signature)


def verify_capability_token(
    token: str,
    secret: str | bytes,
    *,
    required_scope: str | None = None,
    now: int | None = None,
) -> AuthenticatedPrincipal:
    """Verify signature, schema, lifetime, scope, and exact payload shape."""
    key = _secret_bytes(secret)
    if not isinstance(token, str) or token.count(".") != 1:
        raise CapabilityTokenError("malformed capability token")
    encoded_payload, encoded_signature = token.split(".", 1)
    supplied_signature = _b64url_decode(encoded_signature)
    expected_signature = hmac.new(key, encoded_payload.encode("ascii"), hashlib.sha256).digest()
    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise CapabilityTokenError("capability signature mismatch")
    try:
        payload = json.loads(_b64url_decode(encoded_payload))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CapabilityTokenError("invalid capability payload") from exc
    if not isinstance(payload, dict):
        raise CapabilityTokenError("capability payload must be an object")
    required_keys = {"schema", "principal", "scopes", "issued_at", "expires_at", "nonce"}
    if set(payload) != required_keys:
        raise CapabilityTokenError("capability payload shape mismatch")
    if payload["schema"] != CAPABILITY_SCHEMA:
        raise CapabilityTokenError("capability schema mismatch")
    principal = payload["principal"]
    nonce = payload["nonce"]
    issued_at = payload["issued_at"]
    expires_at = payload["expires_at"]
    scopes_value = payload["scopes"]
    if not isinstance(principal, str) or not principal or len(principal) > 256:
        raise CapabilityTokenError("invalid capability principal")
    if not isinstance(nonce, str) or not nonce or len(nonce) > 256:
        raise CapabilityTokenError("invalid capability nonce")
    if isinstance(issued_at, bool) or not isinstance(issued_at, int):
        raise CapabilityTokenError("invalid capability issue time")
    if isinstance(expires_at, bool) or not isinstance(expires_at, int):
        raise CapabilityTokenError("invalid capability expiry time")
    if expires_at <= issued_at or expires_at - issued_at > _MAX_LIFETIME_SECONDS:
        raise CapabilityTokenError("invalid capability lifetime")
    if not isinstance(scopes_value, list) or any(not isinstance(scope, str) for scope in scopes_value):
        raise CapabilityTokenError("invalid capability scopes")
    scopes = frozenset(_validated_scopes(scopes_value))
    current = int(time.time()) if now is None else now
    if isinstance(current, bool) or not isinstance(current, int) or current < 0:
        raise CapabilityTokenError("invalid verification time")
    if issued_at > current + _CLOCK_SKEW_SECONDS:
        raise CapabilityTokenError("capability token is not yet valid")
    if current >= expires_at:
        raise CapabilityTokenError("capability token expired")
    if required_scope is not None and required_scope not in scopes:
        raise CapabilityTokenError("capability scope is not authorized")
    identity: Mapping[str, Any] = {"payload": payload, "signature": encoded_signature}
    return AuthenticatedPrincipal(
        principal=principal,
        scopes=scopes,
        issued_at=issued_at,
        expires_at=expires_at,
        nonce=nonce,
        token_hash72=hash72("pass190.capability", identity),
    )


def parse_authorization_header(value: str | None) -> str:
    if value is None:
        raise CapabilityTokenError("missing capability authorization")
    prefix = AUTHORIZATION_SCHEME + " "
    if not value.startswith(prefix):
        raise CapabilityTokenError("unsupported capability authorization scheme")
    token = value[len(prefix):].strip()
    if not token:
        raise CapabilityTokenError("missing capability token")
    return token
