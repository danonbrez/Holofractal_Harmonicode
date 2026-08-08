"""Pass 213 iteration 1: timestamp-bound authenticated compiled-ROM nucleus.

This module establishes the deterministic hot-path authority for prevalidated
operations. It binds immutable compiled records to ordered operation groups,
exact integer timestamp boundaries, a keyed full-domain closure permutation,
and an authenticated inventory root.

Iteration 1 contains no external I/O and no public-memory mapping. The caller
owns protected-memory placement and persistent recovery policy.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import hmac
import json
import math
from typing import Any, Mapping, Sequence

CONTRACT = "HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243"
PASS_NUMBER = 213
CONTRACT_VERSION = "1.0.0-iteration1"
RUNTIME_CLASSIFICATION = "HHS_PASS_213_COMPILED_ROM_NUCLEUS_ITERATION1"

VM81_CELLS = 81
ORDERED_OPCODES = 64
VM5184_STATES = VM81_CELLS * ORDERED_OPCODES
G243_CONTROLS = 243
HYDRATION_LANES = 40
VM5184_G243_DOMAIN = VM5184_STATES * G243_CONTROLS
FULL_HYDRATION_DOMAIN = HYDRATION_LANES * VM5184_G243_DOMAIN
ZERO_HASH216 = "0" * 64
ZERO_HASH72 = "0" * 72


class Pass213Error(RuntimeError):
    """Base Pass 213 error."""


class Pass213ValidationError(Pass213Error):
    """Raised when a candidate violates a canonical Pass 213 invariant."""


def canonical_bytes(value: Any) -> bytes:
    """Serialize a supported value to exact canonical UTF-8 JSON bytes."""
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise Pass213ValidationError("PASS213_CANONICAL_SERIALIZATION_FAILED") from exc


def hash216(domain: str, payload: bytes) -> str:
    """Return the canonical SHA-256 identity for a framed Pass 213 object."""
    domain_bytes = domain.encode("utf-8")
    framed = (
        b"HHS-P213-HASH216-V1\0"
        + len(domain_bytes).to_bytes(2, "big")
        + domain_bytes
        + len(payload).to_bytes(8, "big")
        + payload
    )
    return sha256(framed).hexdigest()


def _hmac256(key: bytes, domain: str, *parts: bytes) -> bytes:
    if not isinstance(key, bytes) or len(key) < 32:
        raise Pass213ValidationError("PASS213_KEY_TOO_SHORT")
    domain_bytes = domain.encode("utf-8")
    message = bytearray(b"HHS-P213-HMAC-SHA256-V1\0")
    message += len(domain_bytes).to_bytes(2, "big")
    message += domain_bytes
    for part in parts:
        message += len(part).to_bytes(8, "big")
        message += part
    return hmac.new(key, bytes(message), sha256).digest()


def derive_key(root_key: bytes, domain: str, *context: bytes) -> bytes:
    """Derive one domain-separated state-local 256-bit key."""
    return _hmac256(root_key, f"KDF/{domain}", *context)


def _validate_hash(value: str, field_name: str, length: int = 64) -> None:
    if not isinstance(value, str) or len(value) != length:
        raise Pass213ValidationError(f"PASS213_{field_name}_LENGTH_INVALID")
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213ValidationError(f"PASS213_{field_name}_FORMAT_INVALID") from exc


@dataclass(frozen=True)
class TimestampBoundary:
    """Exact operation-group boundary bound to lineage and monotonic order."""

    kind: str
    timestamp_ns: int
    serial: int
    genesis_epoch: int
    group_sequence: int
    parent_hash216: str
    previous_receipt_hash72: str
    kernel_measurement_hash216: str
    boundary_hash216: str = field(default="")

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "kind": self.kind,
            "timestamp_ns": self.timestamp_ns,
            "serial": self.serial,
            "genesis_epoch": self.genesis_epoch,
            "group_sequence": self.group_sequence,
            "parent_hash216": self.parent_hash216,
            "previous_receipt_hash72": self.previous_receipt_hash72,
            "kernel_measurement_hash216": self.kernel_measurement_hash216,
        }

    @classmethod
    def create(
        cls,
        *,
        kind: str,
        timestamp_ns: int,
        serial: int,
        genesis_epoch: int,
        group_sequence: int,
        parent_hash216: str,
        previous_receipt_hash72: str,
        kernel_measurement_hash216: str,
    ) -> "TimestampBoundary":
        candidate = cls(
            kind=kind,
            timestamp_ns=int(timestamp_ns),
            serial=int(serial),
            genesis_epoch=int(genesis_epoch),
            group_sequence=int(group_sequence),
            parent_hash216=parent_hash216,
            previous_receipt_hash72=previous_receipt_hash72,
            kernel_measurement_hash216=kernel_measurement_hash216,
        )
        candidate.validate()
        return cls(
            **candidate.unsigned_payload(),
            boundary_hash216=hash216(
                "timestamp-boundary",
                canonical_bytes(candidate.unsigned_payload()),
            ),
        )

    def validate(self) -> None:
        if self.kind not in {"open", "close"}:
            raise Pass213ValidationError("PASS213_BOUNDARY_KIND_INVALID")
        for value, name in (
            (self.timestamp_ns, "TIMESTAMP"),
            (self.serial, "SERIAL"),
            (self.genesis_epoch, "GENESIS_EPOCH"),
            (self.group_sequence, "GROUP_SEQUENCE"),
        ):
            if not isinstance(value, int) or value < 0:
                raise Pass213ValidationError(f"PASS213_{name}_INVALID")
        _validate_hash(self.parent_hash216, "PARENT_HASH216")
        _validate_hash(self.kernel_measurement_hash216, "KERNEL_MEASUREMENT_HASH216")
        _validate_hash(self.previous_receipt_hash72, "PREVIOUS_RECEIPT_HASH72", 72)
        if self.boundary_hash216:
            _validate_hash(self.boundary_hash216, "BOUNDARY_HASH216")
            expected = hash216(
                "timestamp-boundary",
                canonical_bytes(self.unsigned_payload()),
            )
            if not hmac.compare_digest(self.boundary_hash216, expected):
                raise Pass213ValidationError("PASS213_BOUNDARY_HASH_MISMATCH")


def validate_boundary_pair(
    opening: TimestampBoundary,
    closing: TimestampBoundary,
) -> None:
    opening.validate()
    closing.validate()
    if opening.kind != "open" or closing.kind != "close":
        raise Pass213ValidationError("PASS213_BOUNDARY_PAIR_KIND_INVALID")
    if opening.genesis_epoch != closing.genesis_epoch:
        raise Pass213ValidationError("PASS213_BOUNDARY_EPOCH_MISMATCH")
    if opening.group_sequence != closing.group_sequence:
        raise Pass213ValidationError("PASS213_BOUNDARY_SEQUENCE_MISMATCH")
    if opening.parent_hash216 != closing.parent_hash216:
        raise Pass213ValidationError("PASS213_BOUNDARY_PARENT_MISMATCH")
    if closing.timestamp_ns < opening.timestamp_ns:
        raise Pass213ValidationError("PASS213_TIMESTAMP_ORDER_INVALID")
    if closing.serial <= opening.serial:
        raise Pass213ValidationError("PASS213_BOUNDARY_SERIAL_ORDER_INVALID")


def ordered_operation_chain(
    group_key: bytes,
    opening_boundary: TimestampBoundary,
    operations: Sequence[Mapping[str, Any]],
) -> tuple[str, tuple[str, ...]]:
    """Bind every operation to its exact noncommutative group position."""
    if not operations:
        raise Pass213ValidationError("PASS213_OPERATION_GROUP_EMPTY")
    opening_boundary.validate()
    state = _hmac256(
        group_key,
        "OPERATION-GROUP-OPEN",
        canonical_bytes(asdict(opening_boundary)),
    )
    witnesses: list[str] = []
    for index, operation in enumerate(operations):
        encoded = canonical_bytes(operation)
        state = _hmac256(
            group_key,
            "ORDERED-OPERATION",
            state,
            index.to_bytes(8, "big"),
            encoded,
        )
        witnesses.append(state.hex())
    return state.hex(), tuple(witnesses)


def _coprime_multiplier(seed: bytes, domain_size: int) -> int:
    if domain_size <= 1:
        raise Pass213ValidationError("PASS213_CLOSURE_DOMAIN_INVALID")
    candidate = int.from_bytes(seed[:16], "big") % domain_size
    if candidate == 0:
        candidate = 1
    while math.gcd(candidate, domain_size) != 1:
        candidate = (candidate + 1) % domain_size
        if candidate == 0:
            candidate = 1
    return candidate


@dataclass(frozen=True)
class ClosurePath:
    """A deterministic keyed single-cycle permutation of one declared domain."""

    domain_size: int
    multiplier: int
    offset: int
    path_root_hash216: str

    @classmethod
    def derive(
        cls,
        path_key: bytes,
        domain_size: int,
        context: bytes,
    ) -> "ClosurePath":
        seed = _hmac256(
            path_key,
            "CLOSURE-PATH",
            domain_size.to_bytes(8, "big"),
            context,
        )
        multiplier = _coprime_multiplier(seed, domain_size)
        offset = int.from_bytes(seed[16:], "big") % domain_size
        payload = {
            "algorithm": "AFFINE-FULL-CYCLE-V1",
            "domain_size": domain_size,
            "multiplier": multiplier,
            "offset": offset,
        }
        return cls(
            domain_size,
            multiplier,
            offset,
            hash216("closure-path", canonical_bytes(payload)),
        )

    def cell(self, position: int) -> int:
        if not 0 <= int(position) < self.domain_size:
            raise Pass213ValidationError("PASS213_CLOSURE_POSITION_OUT_OF_RANGE")
        return (self.multiplier * int(position) + self.offset) % self.domain_size

    def position(self, cell: int) -> int:
        if not 0 <= int(cell) < self.domain_size:
            raise Pass213ValidationError("PASS213_CLOSURE_CELL_OUT_OF_RANGE")
        inverse = pow(self.multiplier, -1, self.domain_size)
        return (inverse * (int(cell) - self.offset)) % self.domain_size

    def successor(self, cell: int) -> int:
        return self.cell((self.position(cell) + 1) % self.domain_size)

    def verify_complete(
        self,
        *,
        materialize_limit: int = 2_000_000,
    ) -> Mapping[str, Any]:
        if self.domain_size > materialize_limit:
            raise Pass213ValidationError(
                "PASS213_CLOSURE_MATERIALIZE_LIMIT_EXCEEDED"
            )
        visited = [self.cell(index) for index in range(self.domain_size)]
        unique_count = len(set(visited))
        valid = (
            unique_count == self.domain_size
            and self.successor(visited[-1]) == visited[0]
        )
        return {
            "valid": valid,
            "domain_size": self.domain_size,
            "visited_count": len(visited),
            "unique_count": unique_count,
            "missing_count": self.domain_size - unique_count,
            "first_cell": visited[0],
            "last_cell": visited[-1],
            "path_root_hash216": self.path_root_hash216,
        }


@dataclass(frozen=True)
class CompiledROMEntry:
    """Immutable authenticated compiled transformation record."""

    operation_id: str
    canonical_operation: Mapping[str, Any]
    constraints: Mapping[str, Any]
    vm81_cell_id: int
    operation_slot: int
    g243_control_id: int
    native_dispatch_id: str
    kernel_policy_hash216: str
    creation_group_sequence: int
    creation_open_boundary_hash216: str
    creation_close_boundary_hash216: str
    closure_path_root_hash216: str
    closure_position: int
    parent_hash216: str
    entry_hash216: str = field(default="")

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "operation_id": self.operation_id,
            "canonical_operation": self.canonical_operation,
            "constraints": self.constraints,
            "vm81_cell_id": self.vm81_cell_id,
            "operation_slot": self.operation_slot,
            "g243_control_id": self.g243_control_id,
            "native_dispatch_id": self.native_dispatch_id,
            "kernel_policy_hash216": self.kernel_policy_hash216,
            "creation_group_sequence": self.creation_group_sequence,
            "creation_open_boundary_hash216": self.creation_open_boundary_hash216,
            "creation_close_boundary_hash216": self.creation_close_boundary_hash216,
            "closure_path_root_hash216": self.closure_path_root_hash216,
            "closure_position": self.closure_position,
            "parent_hash216": self.parent_hash216,
        }

    @property
    def vm5184_state_id(self) -> int:
        return ORDERED_OPCODES * self.vm81_cell_id + self.operation_slot

    @property
    def projection_id(self) -> int:
        return G243_CONTROLS * self.vm5184_state_id + self.g243_control_id

    @classmethod
    def create(cls, **kwargs: Any) -> "CompiledROMEntry":
        candidate = cls(**kwargs)
        candidate.validate()
        return cls(
            **candidate.unsigned_payload(),
            entry_hash216=hash216(
                "compiled-rom-entry",
                canonical_bytes(candidate.unsigned_payload()),
            ),
        )

    def validate(self) -> None:
        if not self.operation_id or not isinstance(self.operation_id, str):
            raise Pass213ValidationError("PASS213_OPERATION_ID_INVALID")
        canonical_bytes(self.canonical_operation)
        canonical_bytes(self.constraints)
        if not 0 <= self.vm81_cell_id < VM81_CELLS:
            raise Pass213ValidationError("PASS213_VM81_CELL_INVALID")
        if not 0 <= self.operation_slot < ORDERED_OPCODES:
            raise Pass213ValidationError("PASS213_OPERATION_SLOT_INVALID")
        if not 0 <= self.g243_control_id < G243_CONTROLS:
            raise Pass213ValidationError("PASS213_G243_CONTROL_INVALID")
        if not self.native_dispatch_id:
            raise Pass213ValidationError("PASS213_NATIVE_DISPATCH_ID_INVALID")
        if self.creation_group_sequence < 0 or self.closure_position < 0:
            raise Pass213ValidationError("PASS213_SEQUENCE_OR_POSITION_INVALID")
        for value, name in (
            (self.kernel_policy_hash216, "KERNEL_POLICY_HASH216"),
            (self.creation_open_boundary_hash216, "OPEN_BOUNDARY_HASH216"),
            (self.creation_close_boundary_hash216, "CLOSE_BOUNDARY_HASH216"),
            (self.closure_path_root_hash216, "CLOSURE_PATH_ROOT_HASH216"),
            (self.parent_hash216, "PARENT_HASH216"),
        ):
            _validate_hash(value, name)
        if self.entry_hash216:
            _validate_hash(self.entry_hash216, "ENTRY_HASH216")
            expected = hash216(
                "compiled-rom-entry",
                canonical_bytes(self.unsigned_payload()),
            )
            if not hmac.compare_digest(self.entry_hash216, expected):
                raise Pass213ValidationError(
                    "PASS213_COMPILED_ROM_ENTRY_HASH_MISMATCH"
                )


class CompiledROMStore:
    """Immutable compiled-ROM index for one protected runtime arena."""

    def __init__(self) -> None:
        self._entries: dict[str, CompiledROMEntry] = {}
        self._operation_index: dict[str, str] = {}

    def insert(self, entry: CompiledROMEntry) -> str:
        entry.validate()
        existing = self._entries.get(entry.entry_hash216)
        if existing is not None and existing != entry:
            raise Pass213ValidationError("PASS213_HASH_COLLISION_OR_MUTATION")
        operation_existing = self._operation_index.get(entry.operation_id)
        if (
            operation_existing is not None
            and operation_existing != entry.entry_hash216
        ):
            raise Pass213ValidationError(
                "PASS213_OPERATION_ID_ALREADY_COMPILED"
            )
        self._entries[entry.entry_hash216] = entry
        self._operation_index[entry.operation_id] = entry.entry_hash216
        return entry.entry_hash216

    def lookup_hash216(self, entry_hash216: str) -> CompiledROMEntry:
        try:
            entry = self._entries[entry_hash216]
        except KeyError as exc:
            raise Pass213ValidationError(
                "PASS213_COMPILED_ROM_ENTRY_NOT_FOUND"
            ) from exc
        entry.validate()
        return entry

    def lookup_operation(self, operation_id: str) -> CompiledROMEntry:
        try:
            return self.lookup_hash216(self._operation_index[operation_id])
        except KeyError as exc:
            raise Pass213ValidationError(
                "PASS213_COMPILED_OPERATION_NOT_FOUND"
            ) from exc

    def inventory_root(self) -> str:
        leaves = sorted(self._entries)
        payload = {
            "entry_count": len(leaves),
            "entry_hashes": leaves,
        }
        return hash216("compiled-rom-inventory", canonical_bytes(payload))

    def __len__(self) -> int:
        return len(self._entries)


def create_group_receipt(
    receipt_key: bytes,
    *,
    opening: TimestampBoundary,
    closing: TimestampBoundary,
    ordered_group_hash216: str,
    inventory_root_hash216: str,
    closure_path_root_hash216: str,
) -> Mapping[str, Any]:
    validate_boundary_pair(opening, closing)
    for value, name in (
        (ordered_group_hash216, "ORDERED_GROUP_HASH216"),
        (inventory_root_hash216, "INVENTORY_ROOT_HASH216"),
        (closure_path_root_hash216, "CLOSURE_PATH_ROOT_HASH216"),
    ):
        _validate_hash(value, name)
    payload = {
        "contract": CONTRACT,
        "pass_number": PASS_NUMBER,
        "group_sequence": opening.group_sequence,
        "genesis_epoch": opening.genesis_epoch,
        "opening_boundary_hash216": opening.boundary_hash216,
        "closing_boundary_hash216": closing.boundary_hash216,
        "ordered_group_hash216": ordered_group_hash216,
        "inventory_root_hash216": inventory_root_hash216,
        "closure_path_root_hash216": closure_path_root_hash216,
    }
    tag = _hmac256(
        receipt_key,
        "GROUP-RECEIPT",
        canonical_bytes(payload),
    ).hex()
    return {**payload, "receipt_authentication_tag": tag}


__all__ = [
    "CONTRACT",
    "PASS_NUMBER",
    "CONTRACT_VERSION",
    "RUNTIME_CLASSIFICATION",
    "VM5184_STATES",
    "G243_CONTROLS",
    "VM5184_G243_DOMAIN",
    "FULL_HYDRATION_DOMAIN",
    "ZERO_HASH216",
    "ZERO_HASH72",
    "Pass213Error",
    "Pass213ValidationError",
    "TimestampBoundary",
    "ClosurePath",
    "CompiledROMEntry",
    "CompiledROMStore",
    "canonical_bytes",
    "hash216",
    "derive_key",
    "validate_boundary_pair",
    "ordered_operation_chain",
    "create_group_receipt",
]
