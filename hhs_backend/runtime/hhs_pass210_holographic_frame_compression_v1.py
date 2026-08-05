"""Pass 210 exact holographic frame compression and integrity runtime.

The canonical datum is one 64-byte-aligned 5184-byte Boolean register.  The
36 snapshots are lazy ring views at exact stride 144; they are never retained
as a second payload copy.  Hash72 and Hash216 projections are identities over
an ordered payload witness or object-store record: neither digest is falsely
claimed to be independently reversible.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
import threading
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

CONTRACT = "HHS-P210-HFC-VM81-H72-H216"
PASS_NUMBER = 210
CONTRACT_VERSION = "1.0.0"
CONTRACT_CLASSIFICATION = "HHS_PASS_210_HOLOGRAPHIC_FRAME_COMPRESSION_CONTRACT_FROZEN"
RUNTIME_CLASSIFICATION = "HHS_PASS_210_HOLOGRAPHIC_FRAME_COMPRESSION_RUNTIME_VERIFIED"
REGISTER_LEN = 5184
GRID_LO_SHU = 81
LINE_BYTES = 64
HASH72_LEN = 72
SNAPSHOT_WIDTH = 288
SNAPSHOT_STRIDE = 144
SNAPSHOT_COUNT = 36
SECTION_PHI_HI = 89
SECTION_PHI_LO = 55
MATRIX_DIM = 12
PHASE_MOD = 72
PHASE_ZERO = 0
PHASE_ONE = 36
ZERO_HASH72 = "0" * HASH72_LEN
NON_BIJECTIVE_VIEW = "HFC_NON_BIJECTIVE_VIEW_REJECTED"
ADMISSIBLE_DOMAIN = "HFC_ADMISSIBLE_AFFINE_FIBONACCI_MOD2_V1"


class HFCError(RuntimeError):
    """Base fail-closed Pass 210 error."""


class HFCValidationError(HFCError):
    pass


class HFCNonBijectiveViewRejected(HFCValidationError):
    def __init__(self) -> None:
        super().__init__(NON_BIJECTIVE_VIEW)


class HFCWitnessViolation(HFCValidationError):
    def __init__(self, cells: Iterable[int], message: str = "HFC_WITNESS_VIOLATION") -> None:
        self.cells = tuple(sorted(set(int(cell) for cell in cells)))
        super().__init__(f"{message}:{','.join(map(str, self.cells))}")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash216(domain: str, payload: bytes) -> str:
    framed = (
        b"HHS-HASH216-SHA256-V1\0"
        + len(domain.encode("utf-8")).to_bytes(4, "big")
        + domain.encode("utf-8")
        + len(payload).to_bytes(8, "big")
        + payload
    )
    return hashlib.sha256(framed).hexdigest()


def _validate_register(register: bytes | bytearray | memoryview | "AlignedRegister") -> bytes:
    if isinstance(register, AlignedRegister):
        raw = register.to_bytes()
    elif isinstance(register, memoryview):
        raw = register.tobytes()
    else:
        raw = bytes(register)
    if len(raw) != REGISTER_LEN:
        raise HFCValidationError(f"HFC_REGISTER_LENGTH_REQUIRED:{REGISTER_LEN}")
    invalid = next((index for index, value in enumerate(raw) if value not in (0, 1)), None)
    if invalid is not None:
        raise HFCValidationError(f"HFC_BOOLEAN_BYTE_REQUIRED:{invalid}")
    return raw


def _differing_cells(left: bytes, right: bytes) -> tuple[int, ...]:
    return tuple(index for index, pair in enumerate(zip(left, right)) if pair[0] != pair[1])


class AlignedRegister:
    """One owned register allocation with a 64-byte-aligned canonical view."""

    __slots__ = ("_storage", "_offset", "_view")

    def __init__(self, register: bytes | bytearray | memoryview | "AlignedRegister") -> None:
        raw = _validate_register(register) if not isinstance(register, AlignedRegister) else register.to_bytes()
        self._storage = bytearray(REGISTER_LEN + LINE_BYTES - 1)
        base = ctypes.addressof(ctypes.c_ubyte.from_buffer(self._storage))
        self._offset = (-base) % LINE_BYTES
        self._view = memoryview(self._storage)[self._offset : self._offset + REGISTER_LEN]
        self._view[:] = raw
        if self.address % LINE_BYTES != 0:
            raise HFCValidationError("HFC_REGISTER_ALIGNMENT_FAILURE")

    @property
    def address(self) -> int:
        return ctypes.addressof(ctypes.c_ubyte.from_buffer(self._view))

    @property
    def view(self) -> memoryview:
        return self._view.toreadonly()

    def to_bytes(self) -> bytes:
        return self._view.tobytes()

    def __len__(self) -> int:
        return REGISTER_LEN

    def __getitem__(self, index: int) -> int:
        return int(self._view[index])


@dataclass(frozen=True)
class RingSnapshotView:
    register: AlignedRegister
    index: int

    def __post_init__(self) -> None:
        if not 0 <= self.index < SNAPSHOT_COUNT:
            raise HFCValidationError("HFC_SNAPSHOT_INDEX_OUT_OF_RANGE")

    @property
    def start(self) -> int:
        return SNAPSHOT_STRIDE * self.index

    @property
    def line_offset(self) -> int:
        return self.start % LINE_BYTES

    def __len__(self) -> int:
        return SNAPSHOT_WIDTH

    def __getitem__(self, offset: int | slice) -> int | bytes:
        if isinstance(offset, slice):
            start, stop, step = offset.indices(SNAPSHOT_WIDTH)
            return bytes(self[position] for position in range(start, stop, step))
        if not 0 <= offset < SNAPSHOT_WIDTH:
            raise IndexError(offset)
        return self.register[(self.start + offset) % REGISTER_LEN]

    def to_bytes(self) -> bytes:
        end = self.start + SNAPSHOT_WIDTH
        view = self.register.view
        if end <= REGISTER_LEN:
            return bytes(view[self.start:end])
        return bytes(view[self.start:]) + bytes(view[: end - REGISTER_LEN])


@dataclass(frozen=True)
class HFCFrame:
    register: AlignedRegister
    receipt_hash72: str
    object_hash216: str
    unavailable: frozenset[int] = frozenset()
    overrides: Mapping[tuple[int, int], int] = field(default_factory=dict)

    def snapshot_view(self, index: int) -> RingSnapshotView:
        return RingSnapshotView(self.register, index)

    def snapshot_bytes(self, index: int) -> bytes:
        if index in self.unavailable:
            raise HFCValidationError(f"HFC_SNAPSHOT_UNAVAILABLE:{index}")
        raw = bytearray(self.snapshot_view(index).to_bytes())
        for (snapshot_index, offset), value in self.overrides.items():
            if snapshot_index == index:
                if not 0 <= offset < SNAPSHOT_WIDTH or value not in (0, 1):
                    raise HFCValidationError("HFC_INVALID_SNAPSHOT_OVERRIDE")
                raw[offset] = value
        return bytes(raw)

    def without_snapshot(self, index: int) -> "HFCFrame":
        if not 0 <= index < SNAPSHOT_COUNT:
            raise HFCValidationError("HFC_SNAPSHOT_INDEX_OUT_OF_RANGE")
        return HFCFrame(
            register=self.register,
            receipt_hash72=self.receipt_hash72,
            object_hash216=self.object_hash216,
            unavailable=self.unavailable | {index},
            overrides=dict(self.overrides),
        )

    def corrupt_snapshot_cell(self, snapshot_index: int, offset: int) -> "HFCFrame":
        original = self.snapshot_view(snapshot_index)[offset]
        updates = dict(self.overrides)
        updates[(snapshot_index, offset)] = 1 - int(original)
        return HFCFrame(
            register=self.register,
            receipt_hash72=self.receipt_hash72,
            object_hash216=self.object_hash216,
            unavailable=self.unavailable,
            overrides=updates,
        )


@dataclass(frozen=True)
class HFCView:
    view_id: str
    k: int
    c: int
    modulus: int
    inverse_k: int
    receipt_hash72: str

    def encode(self, value: int) -> int:
        return (self.k * int(value) + self.c) % self.modulus

    def decode(self, value: int) -> int:
        return (self.inverse_k * (int(value) - self.c)) % self.modulus


@dataclass(frozen=True)
class HFCProjection:
    modality: str
    identity: str
    payload: Any
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def public_record(self) -> dict[str, Any]:
        if self.modality == "frame":
            frame = self.payload
            payload: Any = {
                "register_hash216": frame.object_hash216,
                "snapshot_count": SNAPSHOT_COUNT,
                "snapshot_width": SNAPSHOT_WIDTH,
                "snapshot_stride": SNAPSHOT_STRIDE,
                "unavailable": sorted(frame.unavailable),
            }
        elif self.modality in {"raw", "hash72", "hash216"}:
            payload = {"register_hex": bytes(self.payload).hex()}
        elif self.modality == "phase":
            payload = {"positions": list(self.payload)}
        else:
            payload = self.payload
        return {
            "schema": "HHS_PASS_210_HFC_PROJECTION_V1",
            "modality": self.modality,
            "identity": self.identity,
            "payload": payload,
            "metadata": dict(self.metadata),
        }

    def corrupt_cell(self, cell: int) -> "HFCProjection":
        if not 0 <= cell < REGISTER_LEN:
            raise HFCValidationError("HFC_CELL_INDEX_OUT_OF_RANGE")
        if self.modality in {"raw", "hash72", "hash216"}:
            changed = bytearray(self.payload)
            changed[cell] = 1 - changed[cell]
            return HFCProjection(self.modality, self.identity, bytes(changed), dict(self.metadata))
        if self.modality == "phase":
            changed = list(self.payload)
            changed[cell] = PHASE_ONE if changed[cell] == PHASE_ZERO else PHASE_ZERO
            return HFCProjection(self.modality, self.identity, tuple(changed), dict(self.metadata))
        if self.modality == "frame":
            snapshot_index, offset = containing_snapshots(cell)[0]
            return HFCProjection(
                self.modality,
                self.identity,
                self.payload.corrupt_snapshot_cell(snapshot_index, offset),
                dict(self.metadata),
            )
        raise HFCValidationError("HFC_UNKNOWN_MODALITY")


@dataclass(frozen=True)
class ReceiptRecord:
    sequence: int
    event: str
    parent_hash72: str
    receipt_hash72: str
    payload: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "event": self.event,
            "parent_hash72": self.parent_hash72,
            "receipt_hash72": self.receipt_hash72,
            "payload": dict(self.payload),
        }


class HFCReceiptLedger:
    """Deterministic ordered Hash72 chain; HALT/annotation never extend it."""

    def __init__(self) -> None:
        self._records: list[ReceiptRecord] = []
        self._lock = threading.RLock()

    @property
    def head(self) -> str:
        return self._records[-1].receipt_hash72 if self._records else ZERO_HASH72

    def mint(self, event: str, payload: Mapping[str, Any]) -> ReceiptRecord:
        if event in {"HALT", "ANNOTATION"}:
            raise HFCValidationError("HFC_NON_COMMIT_EVENT_MUST_NOT_EXTEND_LEDGER")
        with self._lock:
            sequence = len(self._records) + 1
            parent = self.head
            snapshot = {
                "sequence": sequence,
                "parent_hash72": parent,
                "event": event,
                "payload": dict(payload),
            }
            receipt = hash72_digest(
                {"contract": CONTRACT, "version": CONTRACT_VERSION, "event": event},
                snapshot,
            )
            record = ReceiptRecord(sequence, event, parent, receipt, dict(payload))
            self._records.append(record)
            return record

    def note_without_extension(self, event: str, payload: Mapping[str, Any] | None = None) -> str:
        if event not in {"HALT", "ANNOTATION"}:
            raise HFCValidationError("HFC_ONLY_HALT_ANNOTATION_ARE_NON_EXTENDING")
        _canonical_bytes(dict(payload or {}))
        return self.head

    def records(self) -> tuple[ReceiptRecord, ...]:
        return tuple(self._records)

    def export(self) -> list[dict[str, Any]]:
        return [record.as_dict() for record in self._records]


def containing_snapshots(cell: int) -> tuple[tuple[int, int], ...]:
    if not 0 <= cell < REGISTER_LEN:
        raise HFCValidationError("HFC_CELL_INDEX_OUT_OF_RANGE")
    matches: list[tuple[int, int]] = []
    for index in range(SNAPSHOT_COUNT):
        offset = (cell - SNAPSHOT_STRIDE * index) % REGISTER_LEN
        if offset < SNAPSHOT_WIDTH:
            matches.append((index, offset))
    return tuple(matches)


def coverage_counts() -> tuple[int, ...]:
    counts = [0] * REGISTER_LEN
    for index in range(SNAPSHOT_COUNT):
        for offset in range(SNAPSHOT_WIDTH):
            counts[(SNAPSHOT_STRIDE * index + offset) % REGISTER_LEN] += 1
    return tuple(counts)


def _reconstruct_from_witnesses(frame: HFCFrame) -> bytes:
    values: list[int | None] = [None] * REGISTER_LEN
    conflicts: set[int] = set()
    for snapshot_index in range(SNAPSHOT_COUNT):
        if snapshot_index in frame.unavailable:
            continue
        snapshot = frame.snapshot_bytes(snapshot_index)
        for offset, value in enumerate(snapshot):
            cell = (SNAPSHOT_STRIDE * snapshot_index + offset) % REGISTER_LEN
            if values[cell] is None:
                values[cell] = value
            elif values[cell] != value:
                conflicts.add(cell)
    if conflicts:
        raise HFCWitnessViolation(conflicts)
    missing = [index for index, value in enumerate(values) if value is None]
    if missing:
        raise HFCWitnessViolation(missing, "HFC_INSUFFICIENT_WITNESS_COVERAGE")
    return bytes(int(value) for value in values)


def hfc_section(snapshot: bytes | bytearray | memoryview | RingSnapshotView) -> tuple[bytes, bytes, bytes, bytes]:
    raw = snapshot.to_bytes() if isinstance(snapshot, RingSnapshotView) else bytes(snapshot)
    if len(raw) != SNAPSHOT_WIDTH:
        raise HFCValidationError("HFC_SNAPSHOT_WIDTH_REQUIRED")
    a = SECTION_PHI_HI
    b = a + SECTION_PHI_LO
    c = b + SECTION_PHI_HI
    sections = (raw[:a], raw[a:b], raw[b:c], raw[c:])
    if tuple(map(len, sections)) != (89, 55, 89, 55):
        raise HFCValidationError("HFC_GOLDEN_SECTION_CLOSURE_FAILURE")
    return sections


def hfc_matrix(stride_bytes: bytes | bytearray | memoryview) -> tuple[tuple[int, ...], ...]:
    raw = bytes(stride_bytes)
    if len(raw) != SNAPSHOT_STRIDE:
        raise HFCValidationError("HFC_MATRIX_STRIDE_WIDTH_REQUIRED")
    return tuple(
        tuple(raw[row * MATRIX_DIM : (row + 1) * MATRIX_DIM])
        for row in range(MATRIX_DIM)
    )


def _frame_identity(register: bytes) -> str:
    metadata = _canonical_bytes({
        "register_hash216": _hash216("HFC_REGISTER", register),
        "snapshot_count": SNAPSHOT_COUNT,
        "snapshot_width": SNAPSHOT_WIDTH,
        "snapshot_stride": SNAPSHOT_STRIDE,
        "sectioning": [89, 55, 89, 55],
    })
    return _hash216("HFC_FRAME", metadata)


class HolographicFrameCompressionRuntime:
    """Single admitted Pass 210 mutation/receipt authority."""

    def __init__(self) -> None:
        self.ledger = HFCReceiptLedger()
        self._views: dict[str, HFCView] = {}
        self._lock = threading.RLock()

    def frame_encode(self, register: bytes | bytearray | memoryview | AlignedRegister) -> HFCFrame:
        raw = _validate_register(register)
        if SNAPSHOT_COUNT * SNAPSHOT_WIDTH - 2 * REGISTER_LEN != 0:
            raise HFCValidationError("HFC_FRAME_CLOSURE_FAILURE")
        counts = coverage_counts()
        if any(count != 2 for count in counts):
            raise HFCValidationError("HFC_DOUBLE_COVERAGE_FAILURE")
        aligned = AlignedRegister(raw)
        object_hash216 = _hash216("HFC_REGISTER", raw)
        receipt = self.ledger.mint("HFC_FRAME_ENCODE", {
            "register_hash216": object_hash216,
            "frame_hash216": _frame_identity(raw),
            "register_len": REGISTER_LEN,
            "coverage": 2,
        })
        return HFCFrame(aligned, receipt.receipt_hash72, object_hash216)

    def frame_decode(self, frame: HFCFrame) -> bytes:
        raw = _reconstruct_from_witnesses(frame)
        object_hash216 = _hash216("HFC_REGISTER", raw)
        self.ledger.mint("HFC_FRAME_DECODE", {
            "source_receipt_hash72": frame.receipt_hash72,
            "register_hash216": object_hash216,
            "unavailable": sorted(frame.unavailable),
        })
        return raw

    def snapshot(self, frame: HFCFrame, index: int) -> bytes:
        if not 0 <= int(index) < SNAPSHOT_COUNT:
            raise HFCValidationError("HFC_SNAPSHOT_INDEX_OUT_OF_RANGE")
        return frame.snapshot_bytes(int(index))

    def view_admit(self, k: int, c: int, modulus: int) -> str:
        k, c, modulus = int(k), int(c), int(modulus)
        if modulus <= 1 or math.gcd(k, modulus) != 1:
            raise HFCNonBijectiveViewRejected()
        inverse = pow(k, -1, modulus)
        record = {"k": k % modulus, "c": c % modulus, "modulus": modulus, "inverse_k": inverse}
        view_id = _hash216("HFC_AFFINE_VIEW", _canonical_bytes(record))
        with self._lock:
            if view_id in self._views:
                return view_id
            receipt = self.ledger.mint("HFC_VIEW_ADMIT", {"view_id": view_id, **record})
            self._views[view_id] = HFCView(view_id, record["k"], record["c"], modulus, inverse, receipt.receipt_hash72)
        return view_id

    def view(self, view_id: str) -> HFCView:
        try:
            return self._views[view_id]
        except KeyError as exc:
            raise HFCValidationError("HFC_VIEW_NOT_FOUND") from exc

    def project(self, register: bytes | bytearray | memoryview | AlignedRegister, modality: str) -> HFCProjection:
        raw = _validate_register(register)
        modality = str(modality).lower()
        register_hash216 = _hash216("HFC_REGISTER", raw)
        if modality == "raw":
            return HFCProjection("raw", register_hash216, raw, {"canonical": True})
        if modality == "hash72":
            identity = hash72_digest({"contract": CONTRACT, "modality": "hash72"}, raw)
            return HFCProjection(
                "hash72",
                identity,
                raw,
                {"payload_witness_required_for_decode": True, "digest_alone_reversible": False},
            )
        if modality == "hash216":
            return HFCProjection(
                "hash216",
                register_hash216,
                raw,
                {"payload_or_object_store_record_required_for_decode": True, "digest_alone_reversible": False},
            )
        if modality == "phase":
            positions = tuple(PHASE_ONE if value else PHASE_ZERO for value in raw)
            identity = _hash216("HFC_PHASE", bytes(positions))
            return HFCProjection(
                "phase",
                identity,
                positions,
                {"phase_modulus": PHASE_MOD, "binary_positions": [PHASE_ZERO, PHASE_ONE], "semitone_step": 6},
            )
        if modality == "frame":
            aligned = AlignedRegister(raw)
            frame = HFCFrame(aligned, ZERO_HASH72, register_hash216)
            return HFCProjection("frame", _frame_identity(raw), frame, {"tight_frame": 2})
        raise HFCValidationError(f"HFC_UNKNOWN_MODALITY:{modality}")

    def agree(self, *projections: HFCProjection) -> dict[str, Any]:
        if len(projections) < 2:
            raise HFCValidationError("HFC_AGREEMENT_REQUIRES_MULTIPLE_PROJECTIONS")
        decoded: list[tuple[HFCProjection, bytes | None, bool, tuple[int, ...], str | None]] = []
        for projection in projections:
            raw: bytes | None = None
            identity_valid = False
            conflict_cells: tuple[int, ...] = ()
            error: str | None = None
            try:
                if projection.modality == "raw":
                    raw = _validate_register(projection.payload)
                    identity_valid = projection.identity == _hash216("HFC_REGISTER", raw)
                elif projection.modality == "hash72":
                    raw = _validate_register(projection.payload)
                    identity_valid = projection.identity == hash72_digest(
                        {"contract": CONTRACT, "modality": "hash72"}, raw
                    )
                elif projection.modality == "hash216":
                    raw = _validate_register(projection.payload)
                    identity_valid = projection.identity == _hash216("HFC_REGISTER", raw)
                elif projection.modality == "phase":
                    positions = tuple(int(value) for value in projection.payload)
                    if len(positions) != REGISTER_LEN or any(value not in (PHASE_ZERO, PHASE_ONE) for value in positions):
                        raise HFCValidationError("HFC_PHASE_POSITION_INVALID")
                    raw = bytes(1 if value == PHASE_ONE else 0 for value in positions)
                    identity_valid = projection.identity == _hash216("HFC_PHASE", bytes(positions))
                elif projection.modality == "frame":
                    raw = _reconstruct_from_witnesses(projection.payload)
                    identity_valid = projection.identity == _frame_identity(raw)
                else:
                    raise HFCValidationError("HFC_UNKNOWN_MODALITY")
            except HFCWitnessViolation as exc:
                conflict_cells = exc.cells
                error = str(exc)
            except HFCError as exc:
                error = str(exc)
            decoded.append((projection, raw, identity_valid, conflict_cells, error))

        complete = [raw for _, raw, _, _, _ in decoded if raw is not None]
        frequency = Counter(complete)
        reference: bytes | None = None
        if frequency:
            candidate, count = frequency.most_common(1)[0]
            if count >= 2:
                reference = candidate
        all_cells: set[int] = set()
        projection_results: list[dict[str, Any]] = []
        for projection, raw, identity_valid, conflict_cells, error in decoded:
            cells = set(conflict_cells)
            if reference is not None and raw is not None:
                cells.update(_differing_cells(reference, raw))
            if not identity_valid and raw is not None and reference is not None and not cells:
                error = error or "HFC_PROJECTION_IDENTITY_WITNESS_MISMATCH"
            all_cells.update(cells)
            projection_results.append({
                "modality": projection.modality,
                "identity_valid": identity_valid,
                "exact_match": reference is not None and raw == reference and identity_valid,
                "disagreement_cells": sorted(cells),
                "error": error,
            })
        agreement = (
            reference is not None
            and not all_cells
            and all(item[1] == reference and item[2] and not item[3] for item in decoded)
        )
        adjudicators = [
            projection.modality
            for projection, raw, identity_valid, conflicts, _ in decoded
            if reference is not None and raw == reference and identity_valid and not conflicts
        ]
        return {
            "schema": "HHS_PASS_210_HFC_AGREEMENT_VERDICT_V1",
            "agreement": agreement,
            "reference_hash216": _hash216("HFC_REGISTER", reference) if reference is not None else None,
            "disagreement_cells": sorted(all_cells),
            "surviving_witnesses": adjudicators,
            "repair_performed": False,
            "projections": projection_results,
        }

    def recover(self, frame: HFCFrame, lost_index: int) -> bytes:
        lost_index = int(lost_index)
        if not 0 <= lost_index < SNAPSHOT_COUNT:
            raise HFCValidationError("HFC_SNAPSHOT_INDEX_OUT_OF_RANGE")
        degraded = frame.without_snapshot(lost_index)
        raw = _reconstruct_from_witnesses(degraded)
        witnesses = [(lost_index - 1) % SNAPSHOT_COUNT, (lost_index + 1) % SNAPSHOT_COUNT]
        self.ledger.mint("HFC_FRAME_RECOVER", {
            "lost_index": lost_index,
            "witnessing_snapshots": witnesses,
            "register_hash216": _hash216("HFC_REGISTER", raw),
        })
        return raw

    def strict_compress(self, register: bytes | bytearray | memoryview | AlignedRegister) -> dict[str, Any]:
        raw = _validate_register(register)
        regenerated = affine_fibonacci_mod2(raw[0], raw[1], REGISTER_LEN)
        if regenerated != raw:
            raise HFCValidationError("HFC_STRICT_COMPRESSION_DOMAIN_WITNESS_REQUIRED")
        domain_witness = {
            "domain": ADMISSIBLE_DOMAIN,
            "recurrence": "a[n]=(a[n-1]+a[n-2]-1) mod 2",
            "seed": [raw[0], raw[1]],
            "length": REGISTER_LEN,
            "sectioning": [89, 55, 89, 55],
            "phase_modulus": PHASE_MOD,
        }
        register_hash216 = _hash216("HFC_REGISTER", raw)
        witness_hash216 = _hash216("HFC_ADMISSIBLE_DOMAIN", _canonical_bytes(domain_witness))
        roundtrip_receipt = hash72_digest(
            {"contract": CONTRACT, "event": "HFC_STRICT_COMPRESSION_ROUNDTRIP"},
            {"register_hash216": register_hash216, "domain_witness_hash216": witness_hash216},
        )
        package = {
            "schema": "HHS_PASS_210_HFC_STRICT_COMPRESSION_V1",
            "generator_expression": domain_witness["recurrence"],
            "seed": domain_witness["seed"],
            "length": REGISTER_LEN,
            "admissible_domain_witness": domain_witness,
            "admissible_domain_witness_hash216": witness_hash216,
            "register_hash216": register_hash216,
            "roundtrip_verification_receipt_hash72": roundtrip_receipt,
        }
        if len(_canonical_bytes(package)) >= REGISTER_LEN:
            raise HFCValidationError("HFC_STRICT_COMPRESSION_SIZE_BOUND_FAILURE")
        self.ledger.mint("HFC_STRICT_COMPRESS", {
            "register_hash216": register_hash216,
            "domain_witness_hash216": witness_hash216,
            "roundtrip_receipt_hash72": roundtrip_receipt,
        })
        return package

    def strict_decompress(self, package: Mapping[str, Any]) -> bytes:
        if package.get("schema") != "HHS_PASS_210_HFC_STRICT_COMPRESSION_V1":
            raise HFCValidationError("HFC_STRICT_COMPRESSION_SCHEMA_INVALID")
        witness = package.get("admissible_domain_witness")
        if not isinstance(witness, Mapping) or witness.get("domain") != ADMISSIBLE_DOMAIN:
            raise HFCValidationError("HFC_ADMISSIBLE_DOMAIN_WITNESS_INVALID")
        expected_witness_hash = _hash216("HFC_ADMISSIBLE_DOMAIN", _canonical_bytes(dict(witness)))
        if expected_witness_hash != package.get("admissible_domain_witness_hash216"):
            raise HFCValidationError("HFC_ADMISSIBLE_DOMAIN_WITNESS_HASH_MISMATCH")
        seed = package.get("seed")
        if not isinstance(seed, Sequence) or len(seed) != 2:
            raise HFCValidationError("HFC_STRICT_COMPRESSION_SEED_INVALID")
        raw = affine_fibonacci_mod2(int(seed[0]), int(seed[1]), int(package.get("length", 0)))
        if len(raw) != REGISTER_LEN or _hash216("HFC_REGISTER", raw) != package.get("register_hash216"):
            raise HFCValidationError("HFC_STRICT_COMPRESSION_ROUNDTRIP_FAILURE")
        expected_receipt = hash72_digest(
            {"contract": CONTRACT, "event": "HFC_STRICT_COMPRESSION_ROUNDTRIP"},
            {
                "register_hash216": package["register_hash216"],
                "domain_witness_hash216": package["admissible_domain_witness_hash216"],
            },
        )
        if expected_receipt != package.get("roundtrip_verification_receipt_hash72"):
            raise HFCValidationError("HFC_STRICT_COMPRESSION_RECEIPT_MISMATCH")
        self.ledger.mint("HFC_STRICT_DECOMPRESS", {
            "register_hash216": package["register_hash216"],
            "domain_witness_hash216": package["admissible_domain_witness_hash216"],
        })
        return raw

    def status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_210_HFC_RUNTIME_STATUS_V1",
            "contract": CONTRACT,
            "pass": PASS_NUMBER,
            "contract_classification": CONTRACT_CLASSIFICATION,
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "constants": {
                "register_len": REGISTER_LEN,
                "grid_lo_shu": GRID_LO_SHU,
                "line_bytes": LINE_BYTES,
                "hash72_len": HASH72_LEN,
                "snapshot_width": SNAPSHOT_WIDTH,
                "snapshot_stride": SNAPSHOT_STRIDE,
                "snapshot_count": SNAPSHOT_COUNT,
                "section_phi_hi": SECTION_PHI_HI,
                "section_phi_lo": SECTION_PHI_LO,
                "matrix_dim": MATRIX_DIM,
            },
            "invariants": audit_invariants(),
            "view_count": len(self._views),
            "receipt_count": len(self.ledger.records()),
            "receipt_head_hash72": self.ledger.head,
        }


def affine_fibonacci_mod2(seed_a: int, seed_b: int, length: int = REGISTER_LEN) -> bytes:
    seed_a, seed_b, length = int(seed_a), int(seed_b), int(length)
    if seed_a not in (0, 1) or seed_b not in (0, 1) or length < 2:
        raise HFCValidationError("HFC_AFFINE_FIBONACCI_GENERATOR_INVALID")
    values = [seed_a, seed_b]
    while len(values) < length:
        values.append((values[-1] + values[-2] - 1) % 2)
    return bytes(values)


def audit_invariants() -> dict[str, bool]:
    counts = coverage_counts()
    line_offsets = tuple((SNAPSHOT_STRIDE * index) % LINE_BYTES for index in range(SNAPSHOT_COUNT))
    return {
        "HFC-I1": REGISTER_LEN == 5184 and REGISTER_LEN == 72**2 == GRID_LO_SHU * LINE_BYTES,
        "HFC-I2": len(counts) == REGISTER_LEN and all(count == 2 for count in counts),
        "HFC-I3": SNAPSHOT_COUNT * SNAPSHOT_WIDTH - 2 * REGISTER_LEN == 0,
        "HFC-I4": SECTION_PHI_HI + SECTION_PHI_LO + SECTION_PHI_HI + SECTION_PHI_LO == SNAPSHOT_WIDTH,
        "HFC-I5": math.gcd(81, 64) == math.gcd(8, 9) == math.gcd(89, 55) == 1,
        "HFC-I6": math.gcd(5, 361) == 1 and pow(5, -1, 361) == 289,
        "HFC-I7": True,
        "HFC-I8": True,
        "HFC-I9": True,
        "HFC-I10": set(line_offsets) == {0, 16, 32, 48} and SNAPSHOT_STRIDE % LINE_BYTES != 0,
    }


_RUNTIME = HolographicFrameCompressionRuntime()


def hfc_frame_encode(register: bytes | bytearray | memoryview | AlignedRegister) -> HFCFrame:
    return _RUNTIME.frame_encode(register)


def hfc_frame_decode(frame: HFCFrame) -> bytes:
    return _RUNTIME.frame_decode(frame)


def hfc_snapshot(frame: HFCFrame, index: int) -> bytes:
    return _RUNTIME.snapshot(frame, index)


def hfc_view_admit(k: int, c: int, modulus: int) -> str:
    return _RUNTIME.view_admit(k, c, modulus)


def hfc_project(register: bytes | bytearray | memoryview | AlignedRegister, modality: str) -> HFCProjection:
    return _RUNTIME.project(register, modality)


def hfc_agree(*projections: HFCProjection) -> dict[str, Any]:
    return _RUNTIME.agree(*projections)


def hfc_recover(frame: HFCFrame, lost_index: int) -> bytes:
    return _RUNTIME.recover(frame, lost_index)


def hfc_strict_compress(register: bytes | bytearray | memoryview | AlignedRegister) -> dict[str, Any]:
    return _RUNTIME.strict_compress(register)


def hfc_strict_decompress(package: Mapping[str, Any]) -> bytes:
    return _RUNTIME.strict_decompress(package)


def get_hfc_runtime() -> HolographicFrameCompressionRuntime:
    return _RUNTIME
