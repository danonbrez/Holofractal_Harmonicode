"""Pass 213 Iteration 10 governed native compiled dispatch authority.

The authority executes only immutable operations recovered into the protected
compiled-ROM store. Every call is bound to the current kernel policy,
measurement, Hash216 lineage, trusted moving tensor, exact logical route,
monotonic integer timestamp, bounded read/write sets, and prior successor state.
The native ABI has no ambient state and no dynamic allocation. Successful calls
append one authenticated receipt event and advance the singleton VM81 state.
"""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
import ctypes
from dataclasses import dataclass, replace
from hashlib import sha256
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from typing import Any, Mapping, Protocol, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT,
    FULL_HYDRATION_DOMAIN,
    VM5184_G243_DOMAIN,
    ZERO_HASH216,
    ZERO_HASH72,
    CompiledROMEntry,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_moving_tensor_v1 import MovingTensorState
from hhs_runtime.core.hash72_digest_v1 import hash72_digest, verify_hash72

ITERATION = 10
RUNTIME_CLASSIFICATION = "HHS_PASS_213_GOVERNED_NATIVE_COMPILED_DISPATCH_ITERATION10"
DISPATCH_ABI_VERSION = 1
DISPATCH_PROFILE = "HHS_NATIVE_U64_V1"
MAX_OPERANDS = 8
MAX_RESULTS = 4
MAX_ACCESS_SET = 64
MAX_NAME_LENGTH = 128
MAX_CAPABILITY_TTL_NS = 24 * 60 * 60 * 1_000_000_000
UINT64_MAX = (1 << 64) - 1

SCOPE_DISPATCH_EXECUTE = "dispatch.execute"
SCOPE_DISPATCH_READ = "dispatch.read"
DISPATCH_SCOPES = {SCOPE_DISPATCH_EXECUTE, SCOPE_DISPATCH_READ}

_NATIVE_DISPATCH_IDS = {
    "hhs.native.u64.add.v1": 1,
    "hhs.native.u64.sub.v1": 2,
    "hhs.native.u64.xor.v1": 3,
    "hhs.native.u64.and.v1": 4,
    "hhs.native.u64.or.v1": 5,
    "hhs.native.u64.mul_mod.v1": 6,
    "hhs.native.u64.rotl.v1": 7,
    "hhs.native.u64.eq.v1": 8,
    "hhs.native.u64.select.v1": 9,
}


class Pass213NativeDispatchError(RuntimeError):
    """Base Iteration 10 dispatch failure."""


class Pass213NativeDispatchAuthorizationError(Pass213NativeDispatchError):
    """Dispatch capability failure."""


class Pass213NativeDispatchValidationError(Pass213NativeDispatchError):
    """Malformed or context-incompatible dispatch request."""


class Pass213NativeDispatchIntegrityError(Pass213NativeDispatchError):
    """Persistent receipt or successor-state integrity failure."""


class Pass213NativeDispatchUnavailableError(Pass213NativeDispatchError):
    """No configured process-local native dispatch authority."""


class ProtectedCompiledEntrySource(Protocol):
    def lookup_hash216(self, entry_hash216: str) -> CompiledROMEntry: ...
    def inventory_root(self) -> str: ...


def _require_hash216(value: str, code: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass213NativeDispatchValidationError(code)
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213NativeDispatchValidationError(code) from exc
    return value


def _require_hash72(value: str, code: str) -> str:
    if not isinstance(value, str) or len(value) != 72:
        raise Pass213NativeDispatchValidationError(code)
    return value


def _require_key(value: bytes, code: str) -> bytes:
    if not isinstance(value, bytes) or len(value) < 32:
        raise Pass213NativeDispatchValidationError(code)
    return value


def _strict_int(value: Any, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass213NativeDispatchValidationError(code)
    return value


def _require_name(value: str, code: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_NAME_LENGTH:
        raise Pass213NativeDispatchValidationError(code)
    return value


def _canonical_access_set(values: Sequence[str], code: str) -> tuple[str, ...]:
    items = tuple(str(value) for value in values)
    if len(items) > MAX_ACCESS_SET:
        raise Pass213NativeDispatchValidationError(code)
    for item in items:
        _require_name(item, code)
    canonical = tuple(sorted(set(items)))
    if canonical != items:
        raise Pass213NativeDispatchValidationError(code)
    return canonical


def _canonical_operands(values: Sequence[int]) -> tuple[int, ...]:
    operands = tuple(values)
    if not 1 <= len(operands) <= MAX_OPERANDS:
        raise Pass213NativeDispatchValidationError(
            "PASS213_NATIVE_DISPATCH_OPERAND_COUNT_INVALID"
        )
    for value in operands:
        if isinstance(value, bool) or not isinstance(value, int):
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_INTEGER_OPERAND_REQUIRED"
            )
        if not 0 <= value <= UINT64_MAX:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_OPERAND_OUT_OF_RANGE"
            )
    return operands


def _b64u(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _unb64u(value: str) -> bytes:
    try:
        padding = "=" * ((4 - len(value) % 4) % 4)
        return urlsafe_b64decode((value + padding).encode("ascii"))
    except Exception as exc:
        raise Pass213NativeDispatchAuthorizationError(
            "PASS213_NATIVE_DISPATCH_CAPABILITY_PAYLOAD_INVALID"
        ) from exc


def _hmac_hex(key: bytes, domain: str, payload: bytes) -> str:
    framed = (
        b"HHS-P213-ITER10-HMAC-SHA256-V1\0"
        + len(domain.encode("utf-8")).to_bytes(2, "big")
        + domain.encode("utf-8")
        + len(payload).to_bytes(8, "big")
        + payload
    )
    return hmac.new(key, framed, sha256).hexdigest()


@dataclass(frozen=True)
class NativeDispatchCapabilityClaims:
    subject: str
    scopes: tuple[str, ...]
    issued_timestamp_ns: int
    expires_timestamp_ns: int
    epoch: int
    capability_id_hash216: str


class NativeDispatchCapabilityAuthority:
    """Issues local short-lived capabilities for native dispatch operations."""

    def __init__(self, *, root_key: bytes, epoch: int = 1) -> None:
        self._root_key = _require_key(
            root_key, "PASS213_NATIVE_DISPATCH_CAPABILITY_KEY_TOO_SHORT"
        )
        self.epoch = int(epoch)
        if self.epoch < 1:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_EPOCH_INVALID"
            )

    def issue(
        self,
        *,
        subject: str,
        scopes: Sequence[str],
        ttl_seconds: int = 900,
        issued_timestamp_ns: int | None = None,
        nonce: str | None = None,
    ) -> str:
        subject = _require_name(
            subject, "PASS213_NATIVE_DISPATCH_CAPABILITY_SUBJECT_INVALID"
        )
        canonical_scopes = tuple(sorted(set(str(scope) for scope in scopes)))
        if not canonical_scopes or any(scope not in DISPATCH_SCOPES for scope in canonical_scopes):
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_SCOPE_INVALID"
            )
        ttl_ns = int(ttl_seconds) * 1_000_000_000
        if ttl_ns <= 0 or ttl_ns > MAX_CAPABILITY_TTL_NS:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_TTL_INVALID"
            )
        issued = time.time_ns() if issued_timestamp_ns is None else int(issued_timestamp_ns)
        nonce_value = nonce or secrets.token_hex(16)
        unsigned = {
            "schema": "HHS_PASS_213_NATIVE_DISPATCH_CAPABILITY_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "subject": subject,
            "scopes": canonical_scopes,
            "issued_timestamp_ns": issued,
            "expires_timestamp_ns": issued + ttl_ns,
            "epoch": self.epoch,
            "nonce": nonce_value,
        }
        capability_id = hash216(
            "native-dispatch-capability", canonical_bytes(unsigned)
        )
        payload = {**unsigned, "capability_id_hash216": capability_id}
        encoded = _b64u(canonical_bytes(payload))
        signature = _hmac_hex(
            self._root_key, "NATIVE-DISPATCH-CAPABILITY", encoded.encode("ascii")
        )
        return f"hhs213d1.{encoded}.{signature}"

    def validate(
        self,
        token: str | None,
        *,
        required_scope: str,
        now_timestamp_ns: int | None = None,
    ) -> NativeDispatchCapabilityClaims:
        if required_scope not in DISPATCH_SCOPES:
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_REQUIRED_SCOPE_INVALID"
            )
        if not isinstance(token, str):
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_MISSING"
            )
        parts = token.split(".")
        if len(parts) != 3 or parts[0] != "hhs213d1":
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_FORMAT_INVALID"
            )
        expected = _hmac_hex(
            self._root_key, "NATIVE-DISPATCH-CAPABILITY", parts[1].encode("ascii")
        )
        if not hmac.compare_digest(expected, parts[2]):
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_AUTHENTICATION_FAILED"
            )
        try:
            value = json.loads(_unb64u(parts[1]).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_PAYLOAD_INVALID"
            ) from exc
        if (
            value.get("schema") != "HHS_PASS_213_NATIVE_DISPATCH_CAPABILITY_V1"
            or value.get("contract") != CONTRACT
            or int(value.get("iteration", -1)) != ITERATION
            or int(value.get("epoch", -1)) != self.epoch
        ):
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_CONTRACT_INVALID"
            )
        scopes = tuple(str(scope) for scope in value.get("scopes", ()))
        if scopes != tuple(sorted(set(scopes))) or any(scope not in DISPATCH_SCOPES for scope in scopes):
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_SCOPE_INVALID"
            )
        if required_scope not in scopes:
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_SCOPE_DENIED"
            )
        issued = int(value["issued_timestamp_ns"])
        expires = int(value["expires_timestamp_ns"])
        now = time.time_ns() if now_timestamp_ns is None else int(now_timestamp_ns)
        if issued < 0 or expires <= issued or expires - issued > MAX_CAPABILITY_TTL_NS:
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_TIME_WINDOW_INVALID"
            )
        if now < issued or now >= expires:
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_EXPIRED_OR_NOT_YET_VALID"
            )
        unsigned = {
            key: value[key]
            for key in (
                "schema", "contract", "iteration", "subject", "scopes",
                "issued_timestamp_ns", "expires_timestamp_ns", "epoch", "nonce",
            )
        }
        expected_id = hash216(
            "native-dispatch-capability", canonical_bytes(unsigned)
        )
        if not hmac.compare_digest(
            str(value.get("capability_id_hash216", "")), expected_id
        ):
            raise Pass213NativeDispatchAuthorizationError(
                "PASS213_NATIVE_DISPATCH_CAPABILITY_ID_MISMATCH"
            )
        return NativeDispatchCapabilityClaims(
            subject=_require_name(
                str(value["subject"]),
                "PASS213_NATIVE_DISPATCH_CAPABILITY_SUBJECT_INVALID",
            ),
            scopes=scopes,
            issued_timestamp_ns=issued,
            expires_timestamp_ns=expires,
            epoch=self.epoch,
            capability_id_hash216=expected_id,
        )

    def close(self) -> None:
        self._root_key = b"\0" * len(self._root_key)


@dataclass(frozen=True)
class NativeDispatchRequest:
    entry_hash216: str
    operation_id: str
    expected_parent_hash216: str
    expected_tensor_root_hash216: str
    timestamp_ns: int
    hydration_lane: int
    operands: tuple[int, ...]
    read_set: tuple[str, ...]
    write_set: tuple[str, ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "NativeDispatchRequest":
        request = cls(
            entry_hash216=str(value["entry_hash216"]),
            operation_id=str(value["operation_id"]),
            expected_parent_hash216=str(value["expected_parent_hash216"]),
            expected_tensor_root_hash216=str(value["expected_tensor_root_hash216"]),
            timestamp_ns=_strict_int(
                value["timestamp_ns"], "PASS213_NATIVE_DISPATCH_TIMESTAMP_INVALID"
            ),
            hydration_lane=_strict_int(
                value.get("hydration_lane", 0),
                "PASS213_NATIVE_DISPATCH_HYDRATION_LANE_INVALID",
            ),
            operands=_canonical_operands(tuple(value["operands"])),
            read_set=_canonical_access_set(
                tuple(value.get("read_set", ())),
                "PASS213_NATIVE_DISPATCH_READ_SET_INVALID",
            ),
            write_set=_canonical_access_set(
                tuple(value.get("write_set", ())),
                "PASS213_NATIVE_DISPATCH_WRITE_SET_INVALID",
            ),
        )
        request.validate()
        return request

    def validate(self) -> None:
        _require_hash216(
            self.entry_hash216, "PASS213_NATIVE_DISPATCH_ENTRY_HASH_INVALID"
        )
        _require_name(
            self.operation_id, "PASS213_NATIVE_DISPATCH_OPERATION_ID_INVALID"
        )
        _require_hash216(
            self.expected_parent_hash216,
            "PASS213_NATIVE_DISPATCH_EXPECTED_PARENT_INVALID",
        )
        _require_hash216(
            self.expected_tensor_root_hash216,
            "PASS213_NATIVE_DISPATCH_EXPECTED_TENSOR_INVALID",
        )
        if self.timestamp_ns < 0:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_TIMESTAMP_INVALID"
            )
        if not 0 <= self.hydration_lane < 40:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_HYDRATION_LANE_INVALID"
            )
        _canonical_operands(self.operands)
        _canonical_access_set(
            self.read_set, "PASS213_NATIVE_DISPATCH_READ_SET_INVALID"
        )
        _canonical_access_set(
            self.write_set, "PASS213_NATIVE_DISPATCH_WRITE_SET_INVALID"
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_213_NATIVE_DISPATCH_REQUEST_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "entry_hash216": self.entry_hash216,
            "operation_id": self.operation_id,
            "expected_parent_hash216": self.expected_parent_hash216,
            "expected_tensor_root_hash216": self.expected_tensor_root_hash216,
            "timestamp_ns": self.timestamp_ns,
            "hydration_lane": self.hydration_lane,
            "operands": self.operands,
            "read_set": self.read_set,
            "write_set": self.write_set,
        }


@dataclass(frozen=True)
class DispatchRuntimeState:
    next_sequence: int
    current_state_root_hash216: str
    previous_receipt_hash72: str
    kernel_policy_hash216: str
    kernel_measurement_hash216: str
    lineage_root_hash216: str
    tensor_state: MovingTensorState
    last_timestamp_ns: int

    def validate(self) -> None:
        if self.next_sequence < 1 or self.last_timestamp_ns < 0:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_RUNTIME_SEQUENCE_INVALID"
            )
        for value, code in (
            (self.current_state_root_hash216, "PASS213_NATIVE_DISPATCH_STATE_ROOT_INVALID"),
            (self.kernel_policy_hash216, "PASS213_NATIVE_DISPATCH_POLICY_ROOT_INVALID"),
            (self.kernel_measurement_hash216, "PASS213_NATIVE_DISPATCH_MEASUREMENT_ROOT_INVALID"),
            (self.lineage_root_hash216, "PASS213_NATIVE_DISPATCH_LINEAGE_ROOT_INVALID"),
        ):
            _require_hash216(value, code)
        _require_hash72(
            self.previous_receipt_hash72,
            "PASS213_NATIVE_DISPATCH_PREVIOUS_RECEIPT_INVALID",
        )
        self.tensor_state.validate_structure()
        if self.lineage_root_hash216 != self.tensor_state.anchor.hash216_lineage_root:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_TENSOR_LINEAGE_MISMATCH"
            )
        if self.last_timestamp_ns < self.tensor_state.anchor.requested_timestamp_ns:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_TIMESTAMP_BEFORE_TRUSTED_ANCHOR"
            )

    def public_mapping(self) -> dict[str, Any]:
        return {
            "next_sequence": self.next_sequence,
            "current_state_root_hash216": self.current_state_root_hash216,
            "previous_receipt_hash72": self.previous_receipt_hash72,
            "kernel_policy_hash216": self.kernel_policy_hash216,
            "kernel_measurement_hash216": self.kernel_measurement_hash216,
            "lineage_root_hash216": self.lineage_root_hash216,
            "tensor_root_hash216": self.tensor_state.tensor_root_hash216,
            "tensor_sequence": self.tensor_state.tensor_sequence,
            "trusted_anchor_root_hash216": self.tensor_state.anchor.anchor_root_hash216,
            "last_timestamp_ns": self.last_timestamp_ns,
            "singleton_vm81_admission": True,
            "physical_mapping_exposed": False,
        }




__all__ = [
    "ITERATION", "RUNTIME_CLASSIFICATION", "DISPATCH_ABI_VERSION",
    "DISPATCH_PROFILE", "MAX_OPERANDS", "MAX_RESULTS", "MAX_ACCESS_SET",
    "MAX_NAME_LENGTH", "MAX_CAPABILITY_TTL_NS", "UINT64_MAX",
    "SCOPE_DISPATCH_EXECUTE", "SCOPE_DISPATCH_READ", "DISPATCH_SCOPES",
    "Pass213NativeDispatchError", "Pass213NativeDispatchAuthorizationError",
    "Pass213NativeDispatchValidationError", "Pass213NativeDispatchIntegrityError",
    "Pass213NativeDispatchUnavailableError", "ProtectedCompiledEntrySource",
    "NativeDispatchCapabilityClaims", "NativeDispatchCapabilityAuthority",
    "NativeDispatchRequest", "DispatchRuntimeState",
    "_require_hash216", "_require_hash72", "_require_key", "_strict_int",
    "_require_name", "_canonical_access_set", "_canonical_operands",
    "_hmac_hex", "_NATIVE_DISPATCH_IDS",
]
