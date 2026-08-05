"""Pass 213 Iteration 9 governed API/CLI projection authority.

The surface is deliberately projection-only. Canonical compiled-ROM bytes,
protected memory, recovery carriers, cryptographic keys, tensor permutation
parameters, physical mappings, RFC 3161 DER material, and uncommitted state
never enter the public projection database.
"""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import stat
import threading
import time
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT,
    FULL_HYDRATION_DOMAIN,
    VM5184_G243_DOMAIN,
    ZERO_HASH216,
    canonical_bytes,
    hash216,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest, verify_hash72

ITERATION = 9
RUNTIME_CLASSIFICATION = "HHS_PASS_213_GOVERNED_API_CLI_PROJECTION_ITERATION9"
CAPABILITY_SCHEMA = "HHS_PASS_213_GOVERNED_CAPABILITY_V1"
RESPONSE_SCHEMA = "HHS_PASS_213_GOVERNED_SURFACE_RESPONSE_V1"
PROJECTION_SCHEMA = "HHS_PASS_213_PUBLIC_PROJECTION_EVENT_V1"
MAX_CAPABILITY_TTL_NS = 24 * 60 * 60 * 1_000_000_000
MAX_PUBLIC_DEPTH = 12
MAX_PUBLIC_ITEMS = 256
MAX_PUBLIC_TEXT = 4096

KIND_COMPILED_ROM = "COMPILED_ROM"
KIND_INVENTORY = "INVENTORY"
KIND_MOVING_TENSOR = "MOVING_TENSOR"
KIND_TIMESTAMP_ANCHOR = "TIMESTAMP_ANCHOR"
KIND_RECEIPT = "RECEIPT"
KINDS = {
    KIND_COMPILED_ROM,
    KIND_INVENTORY,
    KIND_MOVING_TENSOR,
    KIND_TIMESTAMP_ANCHOR,
    KIND_RECEIPT,
}

SCOPE_COMPILED_READ = "compiled.read"
SCOPE_INVENTORY_VERIFY = "inventory.verify"
SCOPE_TENSOR_READ = "tensor.read"
SCOPE_TENSOR_VERIFY = "tensor.verify"
SCOPE_TIMESTAMP_READ = "timestamp.read"
SCOPE_INTEGRITY_VERIFY = "integrity.verify"
SCOPE_RECEIPT_READ = "receipt.read"
ALLOWED_SCOPES = {
    SCOPE_COMPILED_READ,
    SCOPE_INVENTORY_VERIFY,
    SCOPE_TENSOR_READ,
    SCOPE_TENSOR_VERIFY,
    SCOPE_TIMESTAMP_READ,
    SCOPE_INTEGRITY_VERIFY,
    SCOPE_RECEIPT_READ,
}

_FORBIDDEN_PUBLIC_KEYS = {
    "root_key",
    "inventory_key",
    "deletion_key",
    "admission_key",
    "memory_root_key",
    "secret_key",
    "private_key",
    "owner_token",
    "capability",
    "capability_token",
    "authentication_tag",
    "carrier_json",
    "state_json",
    "trusted_anchor_json",
    "request_der_b64",
    "response_der_b64",
    "exact_bytes",
    "payload_bytes",
    "payload_b64",
    "shard_payloads",
    "seed",
    "seed_bytes",
    "tensor_seed",
    "raw_address",
    "physical_address",
    "arena_id",
    "native_pointer",
}
_FORBIDDEN_PUBLIC_FRAGMENTS = (
    "secret",
    "private_key",
    "owner_token",
    "authentication_tag",
    "carrier_json",
    "state_json",
    "trusted_anchor_json",
    "request_der",
    "response_der",
    "exact_bytes",
    "payload_bytes",
    "tensor_seed",
    "raw_address",
    "physical_address",
    "native_pointer",
)


class Pass213SurfaceError(RuntimeError):
    """Base governed-surface failure."""


class Pass213SurfaceAuthorizationError(Pass213SurfaceError):
    """Capability validation or scope failure."""


class Pass213SurfaceValidationError(Pass213SurfaceError):
    """Malformed request or unsafe projection failure."""


class Pass213SurfaceNotFoundError(Pass213SurfaceError):
    """Requested public projection does not exist."""


class Pass213SurfaceIntegrityError(Pass213SurfaceError):
    """Persistent projection continuity or authentication failure."""


def _require_key(value: bytes, code: str) -> bytes:
    if not isinstance(value, bytes) or len(value) < 32:
        raise Pass213SurfaceValidationError(code)
    return value


def _require_hash216(value: str, code: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass213SurfaceValidationError(code)
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213SurfaceValidationError(code) from exc
    return value


def _require_text(value: str, code: str, *, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise Pass213SurfaceValidationError(code)
    return value


def _b64u(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _unb64u(value: str, code: str) -> bytes:
    try:
        padding = "=" * ((4 - len(value) % 4) % 4)
        return urlsafe_b64decode((value + padding).encode("ascii"))
    except Exception as exc:
        raise Pass213SurfaceAuthorizationError(code) from exc


def _hmac(key: bytes, domain: str, payload: bytes) -> str:
    framed = (
        b"HHS-P213-ITER9-HMAC-SHA256-V1\0"
        + len(domain.encode("utf-8")).to_bytes(2, "big")
        + domain.encode("utf-8")
        + len(payload).to_bytes(8, "big")
        + payload
    )
    return hmac.new(key, framed, sha256).hexdigest()


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "to_mapping"):
        result = value.to_mapping()
        if isinstance(result, Mapping):
            return result
    if hasattr(value, "to_dict"):
        result = value.to_dict()
        if isinstance(result, Mapping):
            return result
    raise Pass213SurfaceValidationError("PASS213_SURFACE_MAPPING_REQUIRED")


def _forbidden_key(key: str) -> bool:
    normalized = key.strip().lower()
    if normalized in _FORBIDDEN_PUBLIC_KEYS:
        return True
    return any(fragment in normalized for fragment in _FORBIDDEN_PUBLIC_FRAGMENTS)


def assert_public_projection_safe(value: Any, *, depth: int = 0) -> None:
    """Reject public data that can disclose protected or noncanonical material."""
    if depth > MAX_PUBLIC_DEPTH:
        raise Pass213SurfaceValidationError("PASS213_SURFACE_PUBLIC_DEPTH_EXCEEDED")
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, float):
        raise Pass213SurfaceValidationError("PASS213_SURFACE_FLOAT_CANONICAL_REJECTED")
    if isinstance(value, str):
        if len(value) > MAX_PUBLIC_TEXT:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_PUBLIC_TEXT_TOO_LONG")
        return
    if isinstance(value, (bytes, bytearray, memoryview)):
        raise Pass213SurfaceValidationError("PASS213_SURFACE_PUBLIC_BYTES_REJECTED")
    if isinstance(value, Mapping):
        if len(value) > MAX_PUBLIC_ITEMS:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_PUBLIC_MAPPING_TOO_LARGE")
        for key, item in value.items():
            if not isinstance(key, str) or _forbidden_key(key):
                raise Pass213SurfaceValidationError("PASS213_SURFACE_PROTECTED_FIELD_REJECTED")
            assert_public_projection_safe(item, depth=depth + 1)
        return
    if isinstance(value, Sequence):
        if isinstance(value, (str, bytes, bytearray)):
            raise Pass213SurfaceValidationError("PASS213_SURFACE_PUBLIC_SEQUENCE_INVALID")
        if len(value) > MAX_PUBLIC_ITEMS:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_PUBLIC_SEQUENCE_TOO_LARGE")
        for item in value:
            assert_public_projection_safe(item, depth=depth + 1)
        return
    raise Pass213SurfaceValidationError("PASS213_SURFACE_PUBLIC_TYPE_REJECTED")


def sanitize_public_projection(value: Any) -> Any:
    """Return a canonical JSON-compatible public projection after strict checks."""
    assert_public_projection_safe(value)
    return json.loads(canonical_bytes(value).decode("utf-8"))


@dataclass(frozen=True)
class CapabilityClaims:
    subject: str
    scopes: tuple[str, ...]
    issued_timestamp_ns: int
    expires_timestamp_ns: int
    epoch: int
    nonce: str
    capability_id_hash216: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": CAPABILITY_SCHEMA,
            "contract": CONTRACT,
            "iteration": ITERATION,
            "subject": self.subject,
            "scopes": list(self.scopes),
            "issued_timestamp_ns": self.issued_timestamp_ns,
            "expires_timestamp_ns": self.expires_timestamp_ns,
            "epoch": self.epoch,
            "nonce": self.nonce,
            "capability_id_hash216": self.capability_id_hash216,
        }


class CapabilityAuthority:
    """Issues and validates short-lived scoped capabilities for API and CLI use."""

    def __init__(self, *, root_key: bytes, epoch: int = 1) -> None:
        self._root_key = _require_key(root_key, "PASS213_CAPABILITY_ROOT_KEY_TOO_SHORT")
        self.epoch = int(epoch)
        if self.epoch < 1:
            raise Pass213SurfaceValidationError("PASS213_CAPABILITY_EPOCH_INVALID")

    def issue(
        self,
        *,
        subject: str,
        scopes: Sequence[str],
        ttl_seconds: int = 900,
        issued_timestamp_ns: int | None = None,
        nonce: str | None = None,
    ) -> str:
        subject = _require_text(subject, "PASS213_CAPABILITY_SUBJECT_INVALID")
        canonical_scopes = tuple(sorted(set(str(scope) for scope in scopes)))
        if not canonical_scopes or any(scope not in ALLOWED_SCOPES for scope in canonical_scopes):
            raise Pass213SurfaceValidationError("PASS213_CAPABILITY_SCOPE_INVALID")
        ttl_ns = int(ttl_seconds) * 1_000_000_000
        if ttl_ns <= 0 or ttl_ns > MAX_CAPABILITY_TTL_NS:
            raise Pass213SurfaceValidationError("PASS213_CAPABILITY_TTL_INVALID")
        issued = time.time_ns() if issued_timestamp_ns is None else int(issued_timestamp_ns)
        if issued < 0:
            raise Pass213SurfaceValidationError("PASS213_CAPABILITY_ISSUED_TIME_INVALID")
        nonce_value = nonce or secrets.token_hex(16)
        _require_text(nonce_value, "PASS213_CAPABILITY_NONCE_INVALID")
        unsigned = {
            "schema": CAPABILITY_SCHEMA,
            "contract": CONTRACT,
            "iteration": ITERATION,
            "subject": subject,
            "scopes": list(canonical_scopes),
            "issued_timestamp_ns": issued,
            "expires_timestamp_ns": issued + ttl_ns,
            "epoch": self.epoch,
            "nonce": nonce_value,
        }
        capability_id = hash216("governed-surface-capability", canonical_bytes(unsigned))
        payload = {**unsigned, "capability_id_hash216": capability_id}
        encoded = _b64u(canonical_bytes(payload))
        signature = _hmac(self._root_key, "CAPABILITY", encoded.encode("ascii"))
        return f"hhs213v1.{encoded}.{signature}"

    def validate(
        self,
        token: str,
        *,
        required_scope: str,
        now_timestamp_ns: int | None = None,
    ) -> CapabilityClaims:
        if required_scope not in ALLOWED_SCOPES:
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_REQUIRED_SCOPE_INVALID")
        if not isinstance(token, str):
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_MISSING")
        parts = token.split(".")
        if len(parts) != 3 or parts[0] != "hhs213v1":
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_FORMAT_INVALID")
        expected = _hmac(self._root_key, "CAPABILITY", parts[1].encode("ascii"))
        if not hmac.compare_digest(parts[2], expected):
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_AUTHENTICATION_FAILED")
        try:
            value = json.loads(_unb64u(parts[1], "PASS213_CAPABILITY_PAYLOAD_INVALID").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_PAYLOAD_INVALID") from exc
        if (
            value.get("schema") != CAPABILITY_SCHEMA
            or value.get("contract") != CONTRACT
            or int(value.get("iteration", -1)) != ITERATION
            or int(value.get("epoch", -1)) != self.epoch
        ):
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_CONTRACT_INVALID")
        scopes = tuple(str(scope) for scope in value.get("scopes", ()))
        if tuple(sorted(set(scopes))) != scopes or any(scope not in ALLOWED_SCOPES for scope in scopes):
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_SCOPE_INVALID")
        if required_scope not in scopes:
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_SCOPE_DENIED")
        issued = int(value["issued_timestamp_ns"])
        expires = int(value["expires_timestamp_ns"])
        now = time.time_ns() if now_timestamp_ns is None else int(now_timestamp_ns)
        if issued < 0 or expires <= issued or expires - issued > MAX_CAPABILITY_TTL_NS:
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_TIME_WINDOW_INVALID")
        if now < issued or now >= expires:
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_EXPIRED_OR_NOT_YET_VALID")
        unsigned = {key: value[key] for key in (
            "schema", "contract", "iteration", "subject", "scopes",
            "issued_timestamp_ns", "expires_timestamp_ns", "epoch", "nonce",
        )}
        expected_id = hash216("governed-surface-capability", canonical_bytes(unsigned))
        if not hmac.compare_digest(str(value.get("capability_id_hash216")), expected_id):
            raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_ID_MISMATCH")
        return CapabilityClaims(
            subject=_require_text(str(value["subject"]), "PASS213_CAPABILITY_SUBJECT_INVALID"),
            scopes=scopes,
            issued_timestamp_ns=issued,
            expires_timestamp_ns=expires,
            epoch=self.epoch,
            nonce=_require_text(str(value["nonce"]), "PASS213_CAPABILITY_NONCE_INVALID"),
            capability_id_hash216=expected_id,
        )

    def close(self) -> None:
        self._root_key = b"\0" * len(self._root_key)


@dataclass(frozen=True)
class PublicProjectionRecord:
    sequence: int
    kind: str
    object_id: str
    source_root_hash216: str
    receipt_hash72: str
    published_timestamp_ns: int
    public_data: Mapping[str, Any]
    prior_event_root_hash216: str
    event_root_hash216: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": PROJECTION_SCHEMA,
            "contract": CONTRACT,
            "iteration": ITERATION,
            "sequence": self.sequence,
            "kind": self.kind,
            "object_id": self.object_id,
            "source_root_hash216": self.source_root_hash216,
            "receipt_hash72": self.receipt_hash72,
            "published_timestamp_ns": self.published_timestamp_ns,
            "public_data": self.public_data,
            "prior_event_root_hash216": self.prior_event_root_hash216,
            "event_root_hash216": self.event_root_hash216,
        }


class GovernedProjectionStore:
    """Append-only authenticated SQLite store containing public commitments only."""

    def __init__(self, *, database_path: str | Path, root_key: bytes) -> None:
        self._root_key = _require_key(root_key, "PASS213_SURFACE_STORE_KEY_TOO_SHORT")
        self._lock = threading.RLock()
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS projection_events(
              sequence INTEGER PRIMARY KEY,
              kind TEXT NOT NULL,
              object_id TEXT NOT NULL,
              source_root_hash216 TEXT NOT NULL,
              receipt_hash72 TEXT NOT NULL,
              published_timestamp_ns INTEGER NOT NULL,
              public_json TEXT NOT NULL,
              prior_event_root_hash216 TEXT NOT NULL,
              event_root_hash216 TEXT UNIQUE NOT NULL,
              authentication_tag TEXT NOT NULL,
              UNIQUE(kind, object_id));
            CREATE TABLE IF NOT EXISTS projection_meta(
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL);
            """
        )
        if self._meta("head_event_root_hash216") is None:
            with self._connection:
                self._set_meta("head_event_root_hash216", ZERO_HASH216)
        self.verify_chain()

    def _meta(self, key: str) -> str | None:
        row = self._connection.execute(
            "SELECT value FROM projection_meta WHERE key=?", (key,)
        ).fetchone()
        return None if row is None else str(row["value"])

    def _set_meta(self, key: str, value: str) -> None:
        self._connection.execute(
            "INSERT INTO projection_meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    @staticmethod
    def _unsigned(
        *, sequence: int, kind: str, object_id: str,
        source_root_hash216: str, receipt_hash72: str,
        published_timestamp_ns: int, public_data: Mapping[str, Any],
        prior_event_root_hash216: str,
    ) -> dict[str, Any]:
        return {
            "schema": PROJECTION_SCHEMA,
            "contract": CONTRACT,
            "iteration": ITERATION,
            "sequence": sequence,
            "kind": kind,
            "object_id": object_id,
            "source_root_hash216": source_root_hash216,
            "receipt_hash72": receipt_hash72,
            "published_timestamp_ns": published_timestamp_ns,
            "public_data": public_data,
            "prior_event_root_hash216": prior_event_root_hash216,
        }

    def publish(
        self,
        *,
        kind: str,
        object_id: str,
        source_root_hash216: str,
        public_data: Mapping[str, Any],
        receipt_hash72: str | None = None,
        published_timestamp_ns: int | None = None,
    ) -> PublicProjectionRecord:
        if kind not in KINDS:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_PROJECTION_KIND_INVALID")
        object_id = _require_text(object_id, "PASS213_SURFACE_OBJECT_ID_INVALID", maximum=512)
        source_root_hash216 = _require_hash216(
            source_root_hash216, "PASS213_SURFACE_SOURCE_ROOT_INVALID"
        )
        safe_data = sanitize_public_projection(dict(public_data))
        timestamp_ns = time.time_ns() if published_timestamp_ns is None else int(published_timestamp_ns)
        if timestamp_ns < 0:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_PUBLISHED_TIME_INVALID")
        receipt = receipt_hash72 or hash72_digest(
            {
                "domain": "HHS-P213-ITER9-PUBLIC-PROJECTION-RECEIPT-V1",
                "kind": kind,
            },
            bytes.fromhex(source_root_hash216),
        )
        if not isinstance(receipt, str) or len(receipt) != 72:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_RECEIPT_HASH72_INVALID")
        with self._lock:
            existing = self._connection.execute(
                "SELECT * FROM projection_events WHERE kind=? AND object_id=?",
                (kind, object_id),
            ).fetchone()
            if existing is not None:
                record = self._record(existing)
                if (
                    record.source_root_hash216 != source_root_hash216
                    or record.receipt_hash72 != receipt
                    or canonical_bytes(record.public_data) != canonical_bytes(safe_data)
                ):
                    raise Pass213SurfaceIntegrityError("PASS213_SURFACE_PROJECTION_CONFLICT")
                return record
            sequence = int(self._connection.execute(
                "SELECT COALESCE(MAX(sequence),0)+1 AS n FROM projection_events"
            ).fetchone()["n"])
            prior = str(self._meta("head_event_root_hash216"))
            unsigned = self._unsigned(
                sequence=sequence,
                kind=kind,
                object_id=object_id,
                source_root_hash216=source_root_hash216,
                receipt_hash72=receipt,
                published_timestamp_ns=timestamp_ns,
                public_data=safe_data,
                prior_event_root_hash216=prior,
            )
            event_root = hash216("governed-public-projection-event", canonical_bytes(unsigned))
            rooted = {**unsigned, "event_root_hash216": event_root}
            tag = _hmac(self._root_key, "PROJECTION-EVENT", canonical_bytes(rooted))
            with self._connection:
                self._connection.execute(
                    "INSERT INTO projection_events VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        sequence, kind, object_id, source_root_hash216, receipt,
                        timestamp_ns, canonical_bytes(safe_data).decode("utf-8"),
                        prior, event_root, tag,
                    ),
                )
                self._set_meta("head_event_root_hash216", event_root)
            return PublicProjectionRecord(
                sequence, kind, object_id, source_root_hash216, receipt,
                timestamp_ns, safe_data, prior, event_root,
            )

    def _record(self, row: sqlite3.Row) -> PublicProjectionRecord:
        return PublicProjectionRecord(
            int(row["sequence"]), str(row["kind"]), str(row["object_id"]),
            str(row["source_root_hash216"]), str(row["receipt_hash72"]),
            int(row["published_timestamp_ns"]),
            json.loads(str(row["public_json"])),
            str(row["prior_event_root_hash216"]), str(row["event_root_hash216"]),
        )

    def get(self, kind: str, object_id: str) -> PublicProjectionRecord:
        if kind not in KINDS:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_PROJECTION_KIND_INVALID")
        row = self._connection.execute(
            "SELECT * FROM projection_events WHERE kind=? AND object_id=?",
            (kind, object_id),
        ).fetchone()
        if row is None:
            raise Pass213SurfaceNotFoundError("PASS213_SURFACE_PROJECTION_NOT_FOUND")
        return self._record(row)

    def latest(self, kind: str) -> PublicProjectionRecord | None:
        row = self._connection.execute(
            "SELECT * FROM projection_events WHERE kind=? ORDER BY sequence DESC LIMIT 1",
            (kind,),
        ).fetchone()
        return None if row is None else self._record(row)

    def list_kind(self, kind: str, *, limit: int = 50) -> tuple[PublicProjectionRecord, ...]:
        if kind not in KINDS or limit < 1 or limit > 100:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_LIST_ARGUMENT_INVALID")
        return tuple(
            self._record(row)
            for row in self._connection.execute(
                "SELECT * FROM projection_events WHERE kind=? ORDER BY sequence DESC LIMIT ?",
                (kind, int(limit)),
            )
        )

    def find_receipt(self, object_id: str) -> PublicProjectionRecord:
        row = self._connection.execute(
            "SELECT * FROM projection_events WHERE object_id=? OR receipt_hash72=? "
            "ORDER BY sequence DESC LIMIT 1",
            (object_id, object_id),
        ).fetchone()
        if row is None:
            raise Pass213SurfaceNotFoundError("PASS213_SURFACE_RECEIPT_NOT_FOUND")
        return self._record(row)

    def count(self, kind: str | None = None) -> int:
        if kind is None:
            return int(self._connection.execute(
                "SELECT COUNT(*) AS n FROM projection_events"
            ).fetchone()["n"])
        return int(self._connection.execute(
            "SELECT COUNT(*) AS n FROM projection_events WHERE kind=?", (kind,)
        ).fetchone()["n"])

    def current_head(self) -> str:
        return str(self._meta("head_event_root_hash216"))

    def verify_chain(self) -> bool:
        prior = ZERO_HASH216
        rows = self._connection.execute(
            "SELECT * FROM projection_events ORDER BY sequence"
        ).fetchall()
        for expected_sequence, row in enumerate(rows, 1):
            record = self._record(row)
            assert_public_projection_safe(record.public_data)
            if record.sequence != expected_sequence or record.prior_event_root_hash216 != prior:
                raise Pass213SurfaceIntegrityError("PASS213_SURFACE_EVENT_CHAIN_DISCONTINUITY")
            unsigned = self._unsigned(
                sequence=record.sequence,
                kind=record.kind,
                object_id=record.object_id,
                source_root_hash216=record.source_root_hash216,
                receipt_hash72=record.receipt_hash72,
                published_timestamp_ns=record.published_timestamp_ns,
                public_data=record.public_data,
                prior_event_root_hash216=record.prior_event_root_hash216,
            )
            expected_root = hash216(
                "governed-public-projection-event", canonical_bytes(unsigned)
            )
            rooted = {**unsigned, "event_root_hash216": expected_root}
            expected_tag = _hmac(self._root_key, "PROJECTION-EVENT", canonical_bytes(rooted))
            if (
                not hmac.compare_digest(record.event_root_hash216, expected_root)
                or not hmac.compare_digest(str(row["authentication_tag"]), expected_tag)
            ):
                raise Pass213SurfaceIntegrityError("PASS213_SURFACE_EVENT_AUTHENTICATION_FAILED")
            if not verify_hash72(
                record.receipt_hash72,
                {
                    "domain": "HHS-P213-ITER9-PUBLIC-PROJECTION-RECEIPT-V1",
                    "kind": record.kind,
                },
                bytes.fromhex(record.source_root_hash216),
            ):
                raise Pass213SurfaceIntegrityError("PASS213_SURFACE_RECEIPT_VERIFICATION_FAILED")
            prior = record.event_root_hash216
        if not hmac.compare_digest(self.current_head(), prior):
            raise Pass213SurfaceIntegrityError("PASS213_SURFACE_HEAD_MISMATCH")
        return True

    def summary(self) -> dict[str, Any]:
        return {
            "projection_count": self.count(),
            "compiled_rom_count": self.count(KIND_COMPILED_ROM),
            "inventory_count": self.count(KIND_INVENTORY),
            "moving_tensor_count": self.count(KIND_MOVING_TENSOR),
            "timestamp_anchor_count": self.count(KIND_TIMESTAMP_ANCHOR),
            "receipt_count": self.count(KIND_RECEIPT),
            "projection_head_hash216": self.current_head(),
        }

    def close(self) -> None:
        self._root_key = b"\0" * len(self._root_key)
        self._connection.close()


class Pass213GovernedSurface:
    """Single operation dispatcher used by both HTTP and CLI transports."""

    OPERATION_CATALOG: Mapping[str, Mapping[str, Any]] = {
        "surface.status": {"scope": None, "arguments": []},
        "surface.catalog": {"scope": None, "arguments": []},
        "compiled.status": {"scope": None, "arguments": []},
        "compiled.lookup": {"scope": SCOPE_COMPILED_READ, "arguments": ["object_id"]},
        "inventory.status": {"scope": None, "arguments": []},
        "inventory.verify": {"scope": SCOPE_INVENTORY_VERIFY, "arguments": []},
        "tensor.status": {"scope": None, "arguments": []},
        "tensor.lookup": {"scope": SCOPE_TENSOR_READ, "arguments": ["object_id"]},
        "tensor.verify": {"scope": SCOPE_TENSOR_VERIFY, "arguments": []},
        "timestamp.status": {"scope": None, "arguments": []},
        "timestamp.lookup": {"scope": SCOPE_TIMESTAMP_READ, "arguments": ["object_id"]},
        "integrity.scan": {"scope": SCOPE_INTEGRITY_VERIFY, "arguments": []},
        "receipt.lookup": {"scope": SCOPE_RECEIPT_READ, "arguments": ["object_id"]},
    }

    def __init__(
        self,
        *,
        projection_store: GovernedProjectionStore,
        capability_authority: CapabilityAuthority,
    ) -> None:
        self.store = projection_store
        self.capabilities = capability_authority

    @staticmethod
    def _record_public(record: PublicProjectionRecord) -> dict[str, Any]:
        return sanitize_public_projection(record.to_mapping())

    def catalog(self) -> dict[str, Any]:
        operations = []
        for name, specification in sorted(self.OPERATION_CATALOG.items()):
            operations.append({
                "operation": name,
                "required_scope": specification["scope"],
                "public": specification["scope"] is None,
                "arguments": list(specification["arguments"]),
                "mutation_authority": False,
            })
        return {
            "operations": operations,
            "operation_count": len(operations),
            "not_exposed": [
                "compiled.compile",
                "compiled.execute",
                "memory.repair",
                "inventory.delete",
                "capability.issue-over-network",
                "protected-memory.read",
                "tensor.physical-map",
                "recovery-carrier.read",
                "timestamp.der.read",
            ],
        }

    def invoke(
        self,
        operation: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        capability: str | None = None,
        now_timestamp_ns: int | None = None,
    ) -> dict[str, Any]:
        operation = _require_text(operation, "PASS213_SURFACE_OPERATION_INVALID")
        if operation not in self.OPERATION_CATALOG:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_OPERATION_NOT_EXPOSED")
        args = dict(arguments or {})
        assert_public_projection_safe(args)
        specification = self.OPERATION_CATALOG[operation]
        expected_args = set(specification["arguments"])
        if set(args) != expected_args:
            raise Pass213SurfaceValidationError("PASS213_SURFACE_ARGUMENT_SET_INVALID")
        scope = specification["scope"]
        claims = None
        if scope is not None:
            if capability is None:
                raise Pass213SurfaceAuthorizationError("PASS213_CAPABILITY_MISSING")
            claims = self.capabilities.validate(
                capability,
                required_scope=str(scope),
                now_timestamp_ns=now_timestamp_ns,
            )
        result = self._dispatch(operation, args)
        payload = {
            "schema": RESPONSE_SCHEMA,
            "contract": CONTRACT,
            "iteration": ITERATION,
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "ok": True,
            "operation": operation,
            "authorized_scope": "PUBLIC" if scope is None else scope,
            "capability_id_hash216": (
                None if claims is None else claims.capability_id_hash216
            ),
            "result": sanitize_public_projection(result),
        }
        response_root = hash216("governed-surface-response", canonical_bytes(payload))
        receipt = hash72_digest(
            {
                "domain": "HHS-P213-ITER9-GOVERNED-SURFACE-RESPONSE-V1",
                "operation": operation,
            },
            bytes.fromhex(response_root),
        )
        return {**payload, "response_root_hash216": response_root, "receipt_hash72": receipt}

    def _dispatch(self, operation: str, args: Mapping[str, Any]) -> Mapping[str, Any]:
        if operation == "surface.status":
            return {
                "configured": True,
                "projection_only": True,
                "mutation_authority": False,
                "no_float_canonical_authority": True,
                "protected_material_exposed": False,
                **self.store.summary(),
            }
        if operation == "surface.catalog":
            return self.catalog()
        if operation == "compiled.status":
            return self._kind_status(KIND_COMPILED_ROM)
        if operation == "compiled.lookup":
            return self._record_public(self.store.get(KIND_COMPILED_ROM, str(args["object_id"])))
        if operation == "inventory.status":
            return self._kind_status(KIND_INVENTORY)
        if operation == "inventory.verify":
            return self._verify_kind(KIND_INVENTORY)
        if operation == "tensor.status":
            return self._kind_status(KIND_MOVING_TENSOR)
        if operation == "tensor.lookup":
            return self._record_public(self.store.get(KIND_MOVING_TENSOR, str(args["object_id"])))
        if operation == "tensor.verify":
            return self._verify_kind(KIND_MOVING_TENSOR)
        if operation == "timestamp.status":
            return self._kind_status(KIND_TIMESTAMP_ANCHOR)
        if operation == "timestamp.lookup":
            return self._record_public(self.store.get(KIND_TIMESTAMP_ANCHOR, str(args["object_id"])))
        if operation == "integrity.scan":
            return {
                "valid": self.store.verify_chain(),
                **self.store.summary(),
                "protected_memory_scanned": False,
                "canonical_runtime_mutated": False,
            }
        if operation == "receipt.lookup":
            return self._record_public(self.store.find_receipt(str(args["object_id"])))
        raise Pass213SurfaceValidationError("PASS213_SURFACE_OPERATION_NOT_EXPOSED")

    def _kind_status(self, kind: str) -> dict[str, Any]:
        latest = self.store.latest(kind)
        return {
            "kind": kind,
            "count": self.store.count(kind),
            "latest": None if latest is None else self._record_public(latest),
            "projection_head_hash216": self.store.current_head(),
        }

    def _verify_kind(self, kind: str) -> dict[str, Any]:
        latest = self.store.latest(kind)
        return {
            "valid": self.store.verify_chain(),
            "kind": kind,
            "count": self.store.count(kind),
            "latest_source_root_hash216": (
                ZERO_HASH216 if latest is None else latest.source_root_hash216
            ),
            "projection_head_hash216": self.store.current_head(),
        }

    def publish_compiled_rom(
        self, value: Any, *, published_timestamp_ns: int | None = None
    ) -> PublicProjectionRecord:
        item = dict(_mapping(value))
        entry = dict(item.get("entry", item))
        entry_hash = _require_hash216(
            str(entry["entry_hash216"]), "PASS213_SURFACE_ENTRY_HASH_INVALID"
        )
        route_commitment = hash216(
            "compiled-rom-public-route-commitment",
            canonical_bytes({
                "vm81_cell_id": int(entry.get("vm81_cell_id", 0)),
                "operation_slot": int(entry.get("operation_slot", 0)),
                "g243_control_id": int(entry.get("g243_control_id", 0)),
                "closure_path_root_hash216": str(
                    entry.get("closure_path_root_hash216", ZERO_HASH216)
                ),
                "native_dispatch_id_hash216": hash216(
                    "native-dispatch-public-identity",
                    str(entry.get("native_dispatch_id", "UNSPECIFIED")).encode("utf-8"),
                ),
            }),
        )
        public = {
            "entry_hash216": entry_hash,
            "operation_id": _require_text(
                str(entry["operation_id"]), "PASS213_SURFACE_OPERATION_ID_INVALID"
            ),
            "state": "PREVALIDATED_COMPILED_ROM",
            "route_commitment_hash216": route_commitment,
            "kernel_policy_hash216": _require_hash216(
                str(entry.get("kernel_policy_hash216", ZERO_HASH216)),
                "PASS213_SURFACE_KERNEL_POLICY_ROOT_INVALID",
            ),
            "parent_hash216": _require_hash216(
                str(entry.get("parent_hash216", ZERO_HASH216)),
                "PASS213_SURFACE_PARENT_ROOT_INVALID",
            ),
            "creation_group_sequence": int(entry.get("creation_group_sequence", 0)),
            "payload_exposed": False,
            "protected_memory_exposed": False,
        }
        return self.store.publish(
            kind=KIND_COMPILED_ROM,
            object_id=entry_hash,
            source_root_hash216=entry_hash,
            public_data=public,
            published_timestamp_ns=published_timestamp_ns,
        )

    def publish_inventory(
        self, value: Any, *, published_timestamp_ns: int | None = None
    ) -> PublicProjectionRecord:
        item = dict(_mapping(value))
        root = _require_hash216(
            str(item["inventory_root_hash216"]),
            "PASS213_SURFACE_INVENTORY_ROOT_INVALID",
        )
        public = {
            "inventory_root_hash216": root,
            "valid": bool(item.get("valid", True)),
            "persistent_chain_valid": bool(item.get("persistent_chain_valid", True)),
            "expected_live_count": int(item.get("expected_live_count", item.get("live_count", 0))),
            "expected_tombstone_count": int(item.get("expected_tombstone_count", item.get("tombstone_count", 0))),
            "actual_protected_count": int(item.get("actual_protected_count", 0)),
            "missing_live_count": len(item.get("missing_live_entry_hashes", ())),
            "unexpected_protected_count": len(item.get("unexpected_protected_entry_hashes", ())),
            "entry_identities_exposed": False,
        }
        return self.store.publish(
            kind=KIND_INVENTORY,
            object_id=root,
            source_root_hash216=root,
            public_data=public,
            published_timestamp_ns=published_timestamp_ns,
        )

    def publish_moving_tensor(
        self, value: Any, *, published_timestamp_ns: int | None = None
    ) -> PublicProjectionRecord:
        if hasattr(value, "validate_structure"):
            value.validate_structure()
        item = dict(_mapping(value))
        root = _require_hash216(
            str(item["tensor_root_hash216"]), "PASS213_SURFACE_TENSOR_ROOT_INVALID"
        )
        anchor = dict(item.get("anchor", {}))
        closure = dict(item.get("closure_proof", {}))
        public = {
            "tensor_root_hash216": root,
            "receipt_hash72": str(item["receipt_hash72"]),
            "tensor_sequence": int(item["tensor_sequence"]),
            "genesis_epoch": int(item["genesis_epoch"]),
            "domain_size": int(item["domain_size"]),
            "prior_tensor_root_hash216": _require_hash216(
                str(item["prior_tensor_root_hash216"]),
                "PASS213_SURFACE_TENSOR_PRIOR_ROOT_INVALID",
            ),
            "anchor_root_hash216": _require_hash216(
                str(anchor["anchor_root_hash216"]),
                "PASS213_SURFACE_TENSOR_ANCHOR_ROOT_INVALID",
            ),
            "anchor_sequence": int(anchor["anchor_sequence"]),
            "lo_shu_root_hash216": _require_hash216(
                str(item["lo_shu_root_hash216"]),
                "PASS213_SURFACE_LO_SHU_ROOT_INVALID",
            ),
            "closure_root_hash216": _require_hash216(
                str(closure["closure_root_hash216"]),
                "PASS213_SURFACE_CLOSURE_ROOT_INVALID",
            ),
            "invariants": {
                "lo_shu_magic_sum_15": True,
                "sudoku_rows_columns_regions_valid": True,
                "fibonacci_phase_exact": True,
                "closure_full_domain_bijection": True,
                "logical_physical_mapping_reversible": True,
                "no_float_canonical_authority": True,
            },
            "permutation_parameters_exposed": False,
            "physical_mapping_exposed": False,
        }
        return self.store.publish(
            kind=KIND_MOVING_TENSOR,
            object_id=root,
            source_root_hash216=root,
            receipt_hash72=str(item["receipt_hash72"]),
            public_data=public,
            published_timestamp_ns=published_timestamp_ns,
        )

    def publish_timestamp_anchor(
        self, value: Any, *, published_timestamp_ns: int | None = None
    ) -> PublicProjectionRecord:
        item = dict(_mapping(value))
        intent = dict(item["intent"])
        evidence = dict(item["evidence"])
        root = _require_hash216(
            str(item["anchor_root_hash216"]), "PASS213_SURFACE_ANCHOR_ROOT_INVALID"
        )
        public = {
            "anchor_root_hash216": root,
            "anchor_sequence": int(intent["anchor_sequence"]),
            "signed_checkpoint_root_hash216": _require_hash216(
                str(intent["signed_checkpoint_root_hash216"]),
                "PASS213_SURFACE_SIGNED_CHECKPOINT_ROOT_INVALID",
            ),
            "verifier_bundle_root_hash216": _require_hash216(
                str(intent["verifier_bundle_root_hash216"]),
                "PASS213_SURFACE_VERIFIER_BUNDLE_ROOT_INVALID",
            ),
            "hash216_lineage_root": _require_hash216(
                str(intent["hash216_lineage_root"]),
                "PASS213_SURFACE_LINEAGE_ROOT_INVALID",
            ),
            "authority_id": _require_text(
                str(intent["authority_id"]), "PASS213_SURFACE_AUTHORITY_ID_INVALID"
            ),
            "tsa_policy_oid": _require_text(
                str(evidence["tsa_policy_oid"]), "PASS213_SURFACE_TSA_POLICY_INVALID"
            ),
            "gen_time_utc": _require_text(
                str(evidence["gen_time_utc"]), "PASS213_SURFACE_TSA_TIME_INVALID"
            ),
            "tsa_subject": _require_text(
                str(evidence["tsa_subject"]), "PASS213_SURFACE_TSA_SUBJECT_INVALID",
                maximum=512,
            ),
            "trust_bundle_sha256": _require_hash216(
                str(evidence["trust_bundle_sha256"]),
                "PASS213_SURFACE_TRUST_BUNDLE_ROOT_INVALID",
            ),
            "der_material_exposed": False,
            "nonce_exposed": False,
        }
        return self.store.publish(
            kind=KIND_TIMESTAMP_ANCHOR,
            object_id=root,
            source_root_hash216=root,
            public_data=public,
            published_timestamp_ns=published_timestamp_ns,
        )

    def publish_receipt(
        self,
        *,
        object_id: str,
        source_root_hash216: str,
        receipt_hash72: str,
        classification: str,
        published_timestamp_ns: int | None = None,
    ) -> PublicProjectionRecord:
        public = {
            "object_id": _require_text(
                object_id, "PASS213_SURFACE_RECEIPT_OBJECT_ID_INVALID", maximum=512
            ),
            "source_root_hash216": _require_hash216(
                source_root_hash216, "PASS213_SURFACE_RECEIPT_SOURCE_ROOT_INVALID"
            ),
            "receipt_hash72": _require_text(
                receipt_hash72, "PASS213_SURFACE_RECEIPT_HASH_INVALID", maximum=72
            ),
            "classification": _require_text(
                classification, "PASS213_SURFACE_RECEIPT_CLASSIFICATION_INVALID"
            ),
        }
        return self.store.publish(
            kind=KIND_RECEIPT,
            object_id=object_id,
            source_root_hash216=source_root_hash216,
            receipt_hash72=receipt_hash72,
            public_data=public,
            published_timestamp_ns=published_timestamp_ns,
        )

    def close(self) -> None:
        self.store.close()
        self.capabilities.close()


_DEFAULT_LOCK = threading.RLock()
_DEFAULT_SURFACE: Pass213GovernedSurface | None = None


def _load_or_create_key(path: Path, environment_name: str) -> bytes:
    configured = os.environ.get(environment_name)
    if configured:
        try:
            value = bytes.fromhex(configured)
        except ValueError as exc:
            raise Pass213SurfaceValidationError(
                f"{environment_name}_HEX_INVALID"
            ) from exc
        return _require_key(value, f"{environment_name}_TOO_SHORT")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(descriptor, secrets.token_bytes(32).hex().encode("ascii"))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise Pass213SurfaceValidationError("PASS213_SURFACE_KEY_FILE_PERMISSIONS_INVALID")
    try:
        value = bytes.fromhex(path.read_text(encoding="ascii").strip())
    except (OSError, ValueError) as exc:
        raise Pass213SurfaceValidationError("PASS213_SURFACE_KEY_FILE_INVALID") from exc
    return _require_key(value, "PASS213_SURFACE_KEY_FILE_TOO_SHORT")


def get_default_pass213_surface() -> Pass213GovernedSurface:
    global _DEFAULT_SURFACE
    with _DEFAULT_LOCK:
        if _DEFAULT_SURFACE is None:
            root = Path(os.environ.get(
                "HHS_PASS213_SURFACE_STATE_DIR",
                str(Path.home() / ".local" / "state" / "hhs" / "pass213" / "surface"),
            )).expanduser().resolve()
            store_key = _load_or_create_key(
                root / "projection.key", "HHS_PASS213_SURFACE_KEY_HEX"
            )
            capability_key = _load_or_create_key(
                root / "capability.key", "HHS_PASS213_CAPABILITY_KEY_HEX"
            )
            _DEFAULT_SURFACE = Pass213GovernedSurface(
                projection_store=GovernedProjectionStore(
                    database_path=root / "public-projections.sqlite3",
                    root_key=store_key,
                ),
                capability_authority=CapabilityAuthority(
                    root_key=capability_key,
                    epoch=int(os.environ.get("HHS_PASS213_CAPABILITY_EPOCH", "1")),
                ),
            )
        return _DEFAULT_SURFACE


def configure_default_pass213_surface(
    surface: Pass213GovernedSurface | None,
) -> Pass213GovernedSurface | None:
    """Replace the process-local surface, primarily for application wiring/tests."""
    global _DEFAULT_SURFACE
    with _DEFAULT_LOCK:
        previous = _DEFAULT_SURFACE
        _DEFAULT_SURFACE = surface
        return previous
