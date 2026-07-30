"""Pass 174 harmonic phase-gear and retrieval-accelerated VM81 runtime.

This module additively extends Pass 163's singleton VM81 authority with
64:72:81 phase coordinates, authenticated whole-frame retrieval, three-lane
Hash216 arrays, 216 positional SHA-256 indexes, exact efficiency accounting,
and Genesis-rooted audits. No legacy authority is replaced.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from hashlib import sha256
import hmac
import json
import os
from pathlib import Path
from threading import RLock
from typing import Any, Mapping, Sequence

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import (
    SNAPSHOT_BYTES,
    ZERO_HASH216,
    ParameterRegistry,
    VMRCError,
    VMRCRuntime,
    VMRCSnapshot,
    canonical_bytes,
)
from .inheritance import LegacyAuthorityManifest, build_legacy_manifest

RUNTIME_VERSION = "HHS-P174-HPG-EH216-RAVWSC-VFIDE-SDLC-1.0.0"
SCHEMA_VERSION = 1
PHASE_64 = 64
PHASE_72 = 72
PHASE_81 = 81
PHASE_LOCK_PERIOD = 5184
HASH216_CHARACTERS = 216
HASH72_CHARACTERS = 72
RECIPROCAL_OFFSET = 36
PLANES = 3
DIRECTED_PHASE_RELATIONSHIPS = 144
ZERO_SHA256 = "0" * 64
DEFAULT_ACTIVE_SUFFIX_LIMIT = 72


class Pass174Error(ValueError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str).encode("utf-8")


def _require_hash72(value: str, label: str) -> str:
    if not isinstance(value, str) or not validate_hash72(value):
        raise Pass174Error("HHS_P174_INVALID_HASH72", label)
    return value


def _require_sha256(value: str, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass174Error("HHS_P174_INVALID_SHA256", label)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise Pass174Error("HHS_P174_INVALID_SHA256", label) from exc
    return value


def _exact_int(value: Any, label: str, lower: int | None = None, upper: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise Pass174Error("HHS_P174_EXACT_INTEGER_REQUIRED", label)
    if lower is not None and value < lower:
        raise Pass174Error("HHS_P174_INTEGER_RANGE", label)
    if upper is not None and value > upper:
        raise Pass174Error("HHS_P174_INTEGER_RANGE", label)
    return value


@dataclass(frozen=True)
class PhaseCoordinate:
    logical_step: int
    phase64: int
    phase72: int
    phase81: int
    phase5184: int
    lock64_72: bool
    lock72_81: bool
    full_phase_lock: bool

    @classmethod
    def at(cls, logical_step: int) -> "PhaseCoordinate":
        step = _exact_int(logical_step, "logical_step", 0)
        return cls(
            logical_step=step,
            phase64=step % PHASE_64,
            phase72=step % PHASE_72,
            phase81=step % PHASE_81,
            phase5184=step % PHASE_LOCK_PERIOD,
            lock64_72=step > 0 and step % 576 == 0,
            lock72_81=step > 0 and step % 648 == 0,
            full_phase_lock=step > 0 and step % PHASE_LOCK_PERIOD == 0,
        )


@dataclass(frozen=True)
class HarmonicGate:
    identity: str
    additive_endpoint: str
    multiplicative_endpoint: str
    connectors: tuple[str, ...]
    phase_offsets: tuple[int, ...]
    exact_weights: tuple[str, ...]
    operator_order_preserved: bool = True


@dataclass(frozen=True)
class Hash216Array:
    predecessor: str
    current: str
    successor: str
    combined: str
    character_indexes_sha256: tuple[str, ...]
    index_root_sha256: str
    logical_identity_sha256: str

    @classmethod
    def build(cls, predecessor: str, current: str, successor: str, *, genesis_identity: str, logical_step: int, operation_identity: str, legacy_foundation_root: str) -> "Hash216Array":
        predecessor = _require_hash72(predecessor, "predecessor")
        current = _require_hash72(current, "current")
        successor = _require_hash72(successor, "successor")
        _require_sha256(genesis_identity, "genesis_identity")
        _require_sha256(operation_identity, "operation_identity")
        _require_sha256(legacy_foundation_root, "legacy_foundation_root")
        combined = predecessor + current + successor
        if len(combined) != HASH216_CHARACTERS:
            raise Pass174Error("HHS_P174_HASH216_LENGTH_MISMATCH")
        logical_body = {
            "schema": "HHS_P174_HASH216_ARRAY_V1",
            "genesis_identity": genesis_identity,
            "logical_step": logical_step,
            "operation_identity": operation_identity,
            "legacy_foundation_root": legacy_foundation_root,
            "predecessor": predecessor,
            "current": current,
            "successor": successor,
        }
        logical_identity = sha256(b"HHS-P174-HASH216-ARRAY-V1\0" + _canonical(logical_body)).hexdigest()
        indexes: list[str] = []
        prior_index = ZERO_SHA256
        for absolute_position, character in enumerate(combined):
            body = {
                "schema": "HHS_P174_HASH216_CHARACTER_INDEX_V1",
                "logical_identity_sha256": logical_identity,
                "genesis_identity": genesis_identity,
                "legacy_foundation_root": legacy_foundation_root,
                "logical_step": logical_step,
                "operation_identity": operation_identity,
                "lane": absolute_position // HASH72_CHARACTERS,
                "lane_position": absolute_position % HASH72_CHARACTERS,
                "absolute_position": absolute_position,
                "character": character,
                "prior_character_index_sha256": prior_index,
            }
            current_index = sha256(b"HHS-P174-HASH216-CHARACTER-V1\0" + _canonical(body)).hexdigest()
            indexes.append(current_index)
            prior_index = current_index
        index_root = sha256(b"HHS-P174-HASH216-INDEX-ROOT-V1\0" + b"".join(bytes.fromhex(item) for item in indexes)).hexdigest()
        return cls(predecessor, current, successor, combined, tuple(indexes), index_root, logical_identity)

    def verify(self) -> None:
        if len(self.combined) != HASH216_CHARACTERS:
            raise Pass174Error("HHS_P174_HASH216_LENGTH_MISMATCH")
        if self.combined != self.predecessor + self.current + self.successor:
            raise Pass174Error("HHS_P174_HASH216_LANE_ORDER_MISMATCH")
        if len(self.character_indexes_sha256) != HASH216_CHARACTERS:
            raise Pass174Error("HHS_P174_HASH216_INDEX_COUNT_MISMATCH")
        expected = sha256(b"HHS-P174-HASH216-INDEX-ROOT-V1\0" + b"".join(bytes.fromhex(item) for item in self.character_indexes_sha256)).hexdigest()
        if not hmac.compare_digest(expected, self.index_root_sha256):
            raise Pass174Error("HHS_P174_HASH216_INDEX_ROOT_MISMATCH")


@dataclass(frozen=True)
class ExactCost:
    decode: int = 0
    frame: int = 0
    harmonic: int = 0
    constraint: int = 0
    hash72: int = 0
    hash216: int = 0
    encryption: int = 0
    retrieval: int = 0
    suffix: int = 0
    closure: int = 0

    @property
    def total(self) -> int:
        return sum(asdict(self).values())


@dataclass
class EfficiencyRecord:
    operation_key: str
    direct_count: int = 0
    retrieval_count: int = 0
    rejection_count: int = 0
    direct_units_total: int = 0
    retrieval_units_total: int = 0
    avoided_units_total: int = 0
    changed_bits_total: int = 0

    def observe_direct(self, cost: ExactCost, changed_bits: int) -> None:
        self.direct_count += 1
        self.direct_units_total += cost.total
        self.changed_bits_total += changed_bits

    def observe_retrieval(self, baseline: int, cost: ExactCost) -> None:
        self.retrieval_count += 1
        self.retrieval_units_total += cost.total
        self.avoided_units_total += max(0, baseline - cost.total)

    def observe_rejection(self) -> None:
        self.rejection_count += 1

    def to_dict(self) -> dict[str, Any]:
        observations = self.direct_count + self.retrieval_count
        return {
            **asdict(self),
            "observations": observations,
            "retrieval_priority": str(Fraction(self.avoided_units_total, max(1, observations + self.rejection_count))),
            "authority": False,
        }


@dataclass(frozen=True)
class EncryptedVectorObject:
    object_id: str
    operation_key: str
    logical_step: int
    input_hash72: str
    output_hash72: str
    operation_identity_sha256: str
    hash216: Hash216Array
    nonce_b64: str
    ciphertext_b64: str
    associated_data_sha256: str
    key_version: int
    direct_cost_units: int
    changed_bits: int
    parent_object_id: str | None


class EncryptedVectorStore:
    def __init__(self, key: bytes | None = None, *, key_version: int = 1, active_suffix_limit: int = DEFAULT_ACTIVE_SUFFIX_LIMIT) -> None:
        candidate = key or AESGCM.generate_key(bit_length=256)
        if len(candidate) not in (16, 24, 32):
            raise Pass174Error("HHS_P174_INVALID_AEAD_KEY_LENGTH")
        self._key = bytes(candidate)
        self._aead = AESGCM(self._key)
        self.key_version = _exact_int(key_version, "key_version", 1)
        self.active_suffix_limit = _exact_int(active_suffix_limit, "active_suffix_limit", 1, 5184)
        self._objects: dict[str, EncryptedVectorObject] = {}
        self._operation_index: dict[str, str] = {}
        self._order: list[str] = []
        self._quarantined: set[str] = set()
        self._lock = RLock()

    @property
    def key(self) -> bytes:
        return self._key

    def _associated_data(self, *, operation_key: str, logical_step: int, input_hash72: str, output_hash72: str, operation_identity_sha256: str, hash216: Hash216Array, legacy_foundation_root: str, genesis_identity: str, parent_object_id: str | None) -> bytes:
        return _canonical({
            "schema": "HHS_P174_ENCRYPTED_VECTOR_AAD_V1",
            "operation_key": operation_key,
            "logical_step": logical_step,
            "input_hash72": input_hash72,
            "output_hash72": output_hash72,
            "operation_identity_sha256": operation_identity_sha256,
            "hash216_identity": hash216.logical_identity_sha256,
            "hash216_index_root": hash216.index_root_sha256,
            "legacy_foundation_root": legacy_foundation_root,
            "genesis_identity": genesis_identity,
            "parent_object_id": parent_object_id,
            "key_version": self.key_version,
        })

    def admit(self, *, operation_key: str, logical_step: int, input_hash72: str, output_hash72: str, operation_identity_sha256: str, hash216: Hash216Array, output_snapshot: bytes, legacy_foundation_root: str, genesis_identity: str, direct_cost_units: int, changed_bits: int, parent_object_id: str | None) -> EncryptedVectorObject:
        if len(output_snapshot) != SNAPSHOT_BYTES:
            raise Pass174Error("HHS_P174_FRAME_LENGTH_MISMATCH")
        hash216.verify()
        aad = self._associated_data(operation_key=operation_key, logical_step=logical_step, input_hash72=input_hash72, output_hash72=output_hash72, operation_identity_sha256=operation_identity_sha256, hash216=hash216, legacy_foundation_root=legacy_foundation_root, genesis_identity=genesis_identity, parent_object_id=parent_object_id)
        plaintext = _canonical({
            "schema": "HHS_P174_VALIDATED_VECTOR_PAYLOAD_V1",
            "snapshot_b64": b64encode(output_snapshot).decode("ascii"),
            "input_hash72": input_hash72,
            "output_hash72": output_hash72,
            "hash216_identity": hash216.logical_identity_sha256,
            "operation_identity_sha256": operation_identity_sha256,
        })
        logical_plaintext_identity = sha256(b"HHS-P174-VECTOR-PLAINTEXT-V1\0" + plaintext).hexdigest()
        object_id = sha256(b"HHS-P174-VECTOR-OBJECT-V1\0" + bytes.fromhex(logical_plaintext_identity) + bytes.fromhex(hash216.index_root_sha256) + bytes.fromhex(legacy_foundation_root)).hexdigest()
        nonce = os.urandom(12)
        ciphertext = self._aead.encrypt(nonce, plaintext, aad)
        obj = EncryptedVectorObject(
            object_id=object_id,
            operation_key=operation_key,
            logical_step=logical_step,
            input_hash72=input_hash72,
            output_hash72=output_hash72,
            operation_identity_sha256=operation_identity_sha256,
            hash216=hash216,
            nonce_b64=b64encode(nonce).decode("ascii"),
            ciphertext_b64=b64encode(ciphertext).decode("ascii"),
            associated_data_sha256=sha256(aad).hexdigest(),
            key_version=self.key_version,
            direct_cost_units=direct_cost_units,
            changed_bits=changed_bits,
            parent_object_id=parent_object_id,
        )
        with self._lock:
            self._objects[object_id] = obj
            self._operation_index[operation_key] = object_id
            if object_id not in self._order:
                self._order.append(object_id)
        return obj

    def retrieve(self, operation_key: str, *, legacy_foundation_root: str, genesis_identity: str) -> tuple[EncryptedVectorObject, bytes]:
        with self._lock:
            object_id = self._operation_index.get(operation_key)
            if object_id is None:
                raise Pass174Error("HHS_P174_VECTOR_MISS")
            if object_id in self._quarantined:
                raise Pass174Error("HHS_P174_VECTOR_QUARANTINED")
            obj = self._objects[object_id]
        aad = self._associated_data(operation_key=obj.operation_key, logical_step=obj.logical_step, input_hash72=obj.input_hash72, output_hash72=obj.output_hash72, operation_identity_sha256=obj.operation_identity_sha256, hash216=obj.hash216, legacy_foundation_root=legacy_foundation_root, genesis_identity=genesis_identity, parent_object_id=obj.parent_object_id)
        if sha256(aad).hexdigest() != obj.associated_data_sha256:
            raise Pass174Error("HHS_P174_VECTOR_AAD_MISMATCH")
        try:
            plaintext = self._aead.decrypt(b64decode(obj.nonce_b64), b64decode(obj.ciphertext_b64), aad)
        except Exception as exc:
            raise Pass174Error("HHS_P174_VECTOR_AUTHENTICATION_FAILED") from exc
        payload = json.loads(plaintext)
        if payload.get("hash216_identity") != obj.hash216.logical_identity_sha256:
            raise Pass174Error("HHS_P174_VECTOR_HASH216_IDENTITY_MISMATCH")
        snapshot = b64decode(payload["snapshot_b64"])
        if len(snapshot) != SNAPSHOT_BYTES:
            raise Pass174Error("HHS_P174_FRAME_LENGTH_MISMATCH")
        return obj, snapshot

    def quarantine(self, object_id: str) -> None:
        if object_id not in self._objects:
            raise Pass174Error("HHS_P174_VECTOR_OBJECT_NOT_FOUND")
        self._quarantined.add(object_id)

    def objects(self) -> tuple[EncryptedVectorObject, ...]:
        return tuple(self._objects[item] for item in self._order)

    def active_suffix(self) -> tuple[EncryptedVectorObject, ...]:
        return tuple(self._objects[item] for item in self._order[-self.active_suffix_limit:])

    def root(self) -> str:
        root = ZERO_SHA256
        for object_id in self._order:
            root = sha256(b"HHS-P174-VECTOR-STORE-CHAIN-V1\0" + bytes.fromhex(root) + bytes.fromhex(object_id)).hexdigest()
        return root


class Pass174VMRCAuthority(VMRCRuntime):
    """Additive whole-frame retrieval admission inside the inherited singleton."""

    def commit_retrieved_snapshot(self, *, output_snapshot: bytes, expected_input_hash72: str, expected_output_hash72: str, operation_hash216: str, hash216_index_root: str, operation_key: str, legacy_foundation_root: str, source_object_id: str) -> dict[str, Any]:
        if len(output_snapshot) != SNAPSHOT_BYTES:
            raise Pass174Error("HHS_P174_FRAME_LENGTH_MISMATCH")
        _require_hash72(expected_input_hash72, "expected_input_hash72")
        _require_hash72(expected_output_hash72, "expected_output_hash72")
        for value, label in ((operation_hash216, "operation_hash216"), (hash216_index_root, "hash216_index_root"), (operation_key, "operation_key"), (legacy_foundation_root, "legacy_foundation_root"), (source_object_id, "source_object_id")):
            _require_sha256(value, label)
        with self._lock:
            if not hmac.compare_digest(self.state_hash72, expected_input_hash72):
                raise Pass174Error("HHS_P174_RETRIEVAL_STALE_ROOT")
            candidate_snapshot = VMRCSnapshot(output_snapshot)
            computed_output = hash72_digest(self._parameters.canonical(), candidate_snapshot.to_bytes())
            if not hmac.compare_digest(computed_output, expected_output_hash72):
                raise Pass174Error("HHS_P174_RETRIEVED_FRAME_HASH72_MISMATCH")
            input_root = self.state_hash72
            self._snapshot = candidate_snapshot
            self._epoch += 1
            self._last_operation_root = operation_hash216
            journal = self._record_journal("P174_RETRIEVED_WHOLE_FRAME_COMMIT", {
                "input_hash72": input_root,
                "output_hash72": expected_output_hash72,
                "operation_hash216": operation_hash216,
                "hash216_index_root": hash216_index_root,
                "operation_key": operation_key,
                "legacy_foundation_root": legacy_foundation_root,
                "source_object_id": source_object_id,
                "output_snapshot_b64": b64encode(output_snapshot).decode("ascii"),
                "epoch_after": self._epoch,
            })
            token = self._VMRCRuntime__authority_token
            index = self._index.append({
                "record_class": "P174_RETRIEVED_COMMITTED_TRANSITION",
                "epoch": self._epoch,
                "hash72_snapshot_identity": self.snapshot_hash72,
                "hash72_state_identity": self.state_hash72,
                "hash216_operation_identity": operation_hash216,
                "hash216_index_root": hash216_index_root,
                "operation_key": operation_key,
                "legacy_foundation_root": legacy_foundation_root,
                "source_object_id": source_object_id,
                "continuation_eligible": True,
                "journal_hash": journal["journal_hash"],
            }, token, token)
            return {
                "classification": "HHS_PASS_174_RETRIEVED_FRAME_COMMIT_ADMITTED",
                "mutation_authority": True,
                "input_hash72": input_root,
                "output_hash72": self.state_hash72,
                "epoch": self._epoch,
                "index_record": index,
                "receipt": self._receipt("P174_RETRIEVED_FRAME_COMMIT_RECEIPT", {
                    "source_object_id": source_object_id,
                    "operation_key": operation_key,
                    "input_hash72": input_root,
                    "output_hash72": self.state_hash72,
                    "operation_hash216": operation_hash216,
                    "hash216_index_root": hash216_index_root,
                    "legacy_foundation_root": legacy_foundation_root,
                    "journal_hash": journal["journal_hash"],
                }),
            }

    def replay(self) -> dict[str, Any]:
        registry = ParameterRegistry()
        snapshot = VMRCSnapshot()
        prior_hash = ZERO_HASH216
        epoch = 0
        for sequence, raw in enumerate(self._journal):
            record = dict(raw)
            supplied = record.pop("journal_hash")
            if record.get("sequence") != sequence or record.get("previous_hash") != prior_hash:
                raise VMRCError("VMRC_INCOMPLETE_COMMIT_JOURNAL")
            expected = sha256(b"HHS-P163-JOURNAL-V1\0" + canonical_bytes(record)).hexdigest()
            if supplied != expected:
                raise VMRCError("VMRC_REPLAY_MISMATCH")
            event = record["event"]
            if event == "GENESIS":
                if record["snapshot_b64"] != snapshot.base64():
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
            elif event == "PARAMETER_REGISTER":
                before = hash72_digest(registry.canonical(), snapshot.to_bytes())
                if before != record["input_hash72"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
                registry.restore(record["parameter"])
                if hash72_digest(registry.canonical(), snapshot.to_bytes()) != record["output_hash72"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
            elif event == "COMMIT":
                if hash72_digest(registry.canonical(), snapshot.to_bytes()) != record["input_hash72"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
                for position, thread, value in record["propagated_writes"]:
                    snapshot._set_index(VMRCSnapshot.coordinate_index(position, thread), value)
                epoch += 1
                if hash72_digest(registry.canonical(), snapshot.to_bytes()) != record["output_hash72"] or epoch != record["epoch_after"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
            elif event == "P174_RETRIEVED_WHOLE_FRAME_COMMIT":
                if hash72_digest(registry.canonical(), snapshot.to_bytes()) != record["input_hash72"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
                snapshot = VMRCSnapshot(b64decode(record["output_snapshot_b64"]))
                epoch += 1
                if hash72_digest(registry.canonical(), snapshot.to_bytes()) != record["output_hash72"] or epoch != record["epoch_after"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
            elif event in ("GEAR_REGISTER", "MEMRISTOR_ADMIT"):
                pass
            else:
                raise VMRCError("VMRC_REPLAY_MISMATCH", event)
            prior_hash = supplied
        final = hash72_digest(registry.canonical(), snapshot.to_bytes())
        if final != self.state_hash72 or snapshot.to_bytes() != self._snapshot.to_bytes() or epoch != self._epoch:
            raise VMRCError("VMRC_REPLAY_MISMATCH")
        return {
            "classification": "P174_VMRC_REPLAY_RECEIPT",
            "records": len(self._journal),
            "epoch": epoch,
            "state_hash72": final,
            "journal_head": prior_hash,
            "deterministic_replay": True,
            "retrieved_frame_events_supported": True,
        }


@dataclass
class RuntimeState:
    predecessor_hash72: str
    current_hash72: str
    last_vector_object_id: str | None = None
    receipts: list[dict[str, Any]] = field(default_factory=list)


class Pass174Runtime:
    def __init__(self, *, vmrc: Pass174VMRCAuthority | None = None, vector_store: EncryptedVectorStore | None = None, repository_root: str | Path | None = None, legacy_manifest: LegacyAuthorityManifest | None = None) -> None:
        self.vmrc = vmrc or Pass174VMRCAuthority()
        if legacy_manifest is None:
            legacy_manifest = build_legacy_manifest(Path(repository_root or Path.cwd()).resolve())
        self.legacy_manifest = legacy_manifest
        self.legacy_foundation_root = legacy_manifest.aggregate_root_sha256
        self.genesis_identity = sha256(b"HHS-P174-GENESIS-V1\0" + bytes.fromhex(self.legacy_foundation_root) + self.vmrc.snapshot().to_bytes() + self.vmrc.state_hash72.encode("ascii")).hexdigest()
        self.vector_store = vector_store or EncryptedVectorStore()
        self.state = RuntimeState(self.vmrc.state_hash72, self.vmrc.state_hash72)
        self._efficiency: dict[str, EfficiencyRecord] = {}
        self._gates: dict[str, HarmonicGate] = {}
        self._lock = RLock()
        self._record_receipt("P174_GENESIS_INIT", {
            "genesis_identity": self.genesis_identity,
            "legacy_foundation_root": self.legacy_foundation_root,
            "state_hash72": self.vmrc.state_hash72,
        })

    @property
    def phase(self) -> PhaseCoordinate:
        return PhaseCoordinate.at(self.vmrc.epoch)

    def _record_receipt(self, schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
        prior = self.state.receipts[-1]["receipt_sha256"] if self.state.receipts else ZERO_SHA256
        payload = {
            "schema": schema,
            "version": SCHEMA_VERSION,
            "runtime_version": RUNTIME_VERSION,
            "logical_step": self.vmrc.epoch,
            "phase": asdict(self.phase),
            "genesis_identity": self.genesis_identity,
            "legacy_foundation_root": self.legacy_foundation_root,
            "prior_receipt_sha256": prior,
            **dict(body),
        }
        receipt_hash72 = hash72_digest(payload, self.vmrc.snapshot().to_bytes())
        receipt = {
            **payload,
            "receipt_hash72": receipt_hash72,
            "receipt_sha256": sha256(b"HHS-P174-RECEIPT-V1\0" + receipt_hash72.encode("ascii") + _canonical(payload)).hexdigest(),
        }
        self.state.receipts.append(receipt)
        return receipt

    def status(self) -> dict[str, Any]:
        return {
            "classification": "HHS_PASS_174_HARMONIC_VISUAL_SDLC_RUNTIME_IMPLEMENTED",
            "runtime_version": RUNTIME_VERSION,
            "legacy_foundation": {
                "minimum_foundation": True,
                "maximum_inherited_pass": self.legacy_manifest.maximum_inherited_pass,
                "specification_count": self.legacy_manifest.specification_count,
                "pass_numbers_present": list(self.legacy_manifest.pass_numbers_present),
                "missing_pass_numbers": list(self.legacy_manifest.missing_pass_numbers),
                "aggregate_root_sha256": self.legacy_foundation_root,
            },
            "vmrc": self.vmrc.status(),
            "genesis_identity": self.genesis_identity,
            "phase": asdict(self.phase),
            "phase_gears": {"64": 64, "72": 72, "81": 81, "closure": 5184},
            "frame_bits": SNAPSHOT_BYTES * 8,
            "frame_bytes": SNAPSHOT_BYTES,
            "vm81_cells": 81,
            "bits_per_cell": 64,
            "hash216_characters": 216,
            "vector_objects": len(self.vector_store.objects()),
            "vector_store_root": self.vector_store.root(),
            "active_suffix": len(self.vector_store.active_suffix()),
            "efficiency_records": len(self._efficiency),
            "harmonic_gates": len(self._gates),
            "kernel_authorities": 1,
            "canonical_commit_authority": "PASS163_VM81_SINGLETON_EXTENDED_BY_PASS174_RETRIEVED_FRAME_ADMISSION",
            "peer_mutation_authority": False,
            "visual_surface": "/ide/",
        }

    def phase_controller(self) -> dict[str, Any]:
        planes: list[dict[str, Any]] = []
        for plane in range(PLANES):
            edges = []
            for phase in range(PHASE_72):
                edges.append({"source": phase, "target": (phase + RECIPROCAL_OFFSET) % PHASE_72, "orientation": "FORWARD", "weight": str(Fraction(plane + 1, PLANES))})
                edges.append({"source": (phase + RECIPROCAL_OFFSET) % PHASE_72, "target": phase, "orientation": "RECIPROCAL", "weight": str(Fraction(PLANES - plane, PLANES))})
            planes.append({"plane": plane, "state_role": ("PREDECESSOR", "CURRENT", "SUCCESSOR")[plane], "directed_relationships": edges})
        return {
            "schema": "HHS_P174_VIRTUAL_QUDIT_3_144_STATE_V1",
            "phase": asdict(self.phase),
            "planes": planes,
            "planes_count": 3,
            "directed_relationships_per_plane": 144,
            "total_directed_relationships": 432,
            "physical_quantum_claim": False,
            "software_correlated_phase_control": True,
        }

    def register_harmonic_gate(self, *, connectors: Sequence[str], phase_offsets: Sequence[int], exact_weights: Sequence[Any], additive_endpoint: str = "x+y", multiplicative_endpoint: str = "xy") -> dict[str, Any]:
        if not connectors:
            raise Pass174Error("HHS_P174_HARMONIC_CONNECTOR_REQUIRED")
        if len(connectors) != len(phase_offsets) or len(connectors) != len(exact_weights):
            raise Pass174Error("HHS_P174_HARMONIC_GATE_ARITY_MISMATCH")
        normalized_offsets = tuple(_exact_int(int(item), "phase_offset", 0, 71) for item in phase_offsets)
        weights: list[str] = []
        for item in exact_weights:
            if isinstance(item, Fraction):
                weights.append(str(item))
            elif isinstance(item, int) and not isinstance(item, bool):
                weights.append(str(Fraction(item, 1)))
            elif isinstance(item, str):
                weights.append(str(Fraction(item)))
            elif isinstance(item, Sequence) and len(item) == 2:
                weights.append(str(Fraction(int(item[0]), int(item[1]))))
            else:
                raise Pass174Error("HHS_P174_EXACT_WEIGHT_REQUIRED")
        body = {
            "additive_endpoint": additive_endpoint,
            "multiplicative_endpoint": multiplicative_endpoint,
            "connectors": tuple(str(item) for item in connectors),
            "phase_offsets": normalized_offsets,
            "exact_weights": tuple(weights),
            "operator_order_preserved": True,
        }
        identity = sha256(b"HHS-P174-HARMONIC-GATE-V1\0" + _canonical(body)).hexdigest()
        gate = HarmonicGate(identity=identity, **body)
        self._gates[identity] = gate
        return {"gate": asdict(gate), "mutation_authority": False, "receipt": self._record_receipt("P174_HARMONIC_COMPILE", {"gate_identity": identity})}

    def _operation_key(self, *, input_hash72: str, thread: int, writes: Mapping[int, int], operation: str, capability_scope: str, gate_identity: str | None) -> str:
        status = self.vmrc.status()
        body = {
            "schema": "HHS_P174_OPERATION_KEY_V1",
            "legacy_foundation_root": self.legacy_foundation_root,
            "genesis_identity": self.genesis_identity,
            "input_hash72": input_hash72,
            "thread": thread,
            "writes": sorted((int(position), int(value)) for position, value in writes.items()),
            "operation": operation,
            "capability_scope": capability_scope,
            "parameter_root": status["parameter_root"],
            "phase_gear_root": status["phase_gear_root"],
            "gate_identity": gate_identity,
        }
        return sha256(b"HHS-P174-OPERATION-KEY-V1\0" + _canonical(body)).hexdigest()

    @staticmethod
    def _changed_bits(before: bytes, after: bytes) -> int:
        return sum((left ^ right).bit_count() for left, right in zip(before, after))

    @staticmethod
    def _direct_cost(writes: Mapping[int, int], changed_bits: int) -> ExactCost:
        return ExactCost(decode=1, frame=SNAPSHOT_BYTES + changed_bits, harmonic=max(1, len(writes) * 3), constraint=max(1, len(writes) * 2), hash72=3, hash216=216, encryption=SNAPSHOT_BYTES, closure=81)

    @staticmethod
    def _retrieval_cost(active_suffix: int) -> ExactCost:
        return ExactCost(decode=1, frame=SNAPSHOT_BYTES, constraint=1, hash72=2, hash216=216, encryption=SNAPSHOT_BYTES, retrieval=1, suffix=active_suffix, closure=1)

    def execute(self, *, thread: int, writes: Mapping[int, int], operation: str = "VMRC_COMMIT", capability_scope: str = "P174_WHOLE_FRAME_STATE_WRITE", gate_identity: str | None = None, prefer_retrieval: bool = True) -> dict[str, Any]:
        with self._lock:
            if gate_identity is not None and gate_identity not in self._gates:
                raise Pass174Error("HHS_P174_HARMONIC_GATE_NOT_FOUND")
            input_hash72 = self.vmrc.state_hash72
            operation_key = self._operation_key(input_hash72=input_hash72, thread=thread, writes=writes, operation=operation, capability_scope=capability_scope, gate_identity=gate_identity)
            efficiency = self._efficiency.setdefault(operation_key, EfficiencyRecord(operation_key))
            if prefer_retrieval:
                try:
                    obj, snapshot = self.vector_store.retrieve(operation_key, legacy_foundation_root=self.legacy_foundation_root, genesis_identity=self.genesis_identity)
                    if obj.input_hash72 != input_hash72:
                        raise Pass174Error("HHS_P174_RETRIEVAL_STALE_ROOT")
                    retrieval_cost = self._retrieval_cost(len(self.vector_store.active_suffix()))
                    commit = self.vmrc.commit_retrieved_snapshot(
                        output_snapshot=snapshot,
                        expected_input_hash72=obj.input_hash72,
                        expected_output_hash72=obj.output_hash72,
                        operation_hash216=obj.operation_identity_sha256,
                        hash216_index_root=obj.hash216.index_root_sha256,
                        operation_key=operation_key,
                        legacy_foundation_root=self.legacy_foundation_root,
                        source_object_id=obj.object_id,
                    )
                    efficiency.observe_retrieval(obj.direct_cost_units, retrieval_cost)
                    self.state.predecessor_hash72 = input_hash72
                    self.state.current_hash72 = self.vmrc.state_hash72
                    self.state.last_vector_object_id = obj.object_id
                    receipt = self._record_receipt("P174_VECTOR_HIT", {
                        "object_id": obj.object_id,
                        "operation_key": operation_key,
                        "input_hash72": input_hash72,
                        "output_hash72": self.vmrc.state_hash72,
                        "cost": asdict(retrieval_cost),
                        "cost_total": retrieval_cost.total,
                    })
                    return {
                        "classification": "HHS_PASS_174_VALIDATED_RETRIEVAL_COMMITTED",
                        "path": "RETRIEVAL",
                        "operation_key": operation_key,
                        "object": self._public_object(obj),
                        "commit": commit,
                        "phase": asdict(self.phase),
                        "efficiency": efficiency.to_dict(),
                        "receipt": receipt,
                    }
                except Pass174Error as exc:
                    if exc.classification != "HHS_P174_VECTOR_MISS":
                        efficiency.observe_rejection()
                        self._record_receipt("P174_VECTOR_REJECT", {"operation_key": operation_key, "classification": exc.classification})
                        raise
            before = self.vmrc.snapshot().to_bytes()
            candidate = self.vmrc.submit_candidate(
                thread=thread,
                writes=dict(writes),
                operation=operation,
                expected_input_hash72=input_hash72,
                capability_scope=capability_scope,
                source_architecture="PASS174_HARMONIC_PIPELINE",
                target_architecture="VM81",
            )
            result = self.vmrc.execute(candidate)
            after = self.vmrc.snapshot().to_bytes()
            output_hash72 = self.vmrc.state_hash72
            changed_bits = self._changed_bits(before, after)
            direct_cost = self._direct_cost(writes, changed_bits)
            operation_identity = sha256(b"HHS-P174-OPERATION-IDENTITY-V1\0" + bytes.fromhex(operation_key) + result["commit"]["receipt"]["operation_hash216"].encode("ascii")).hexdigest()
            hash216 = Hash216Array.build(self.state.predecessor_hash72, input_hash72, output_hash72, genesis_identity=self.genesis_identity, logical_step=self.vmrc.epoch, operation_identity=operation_identity, legacy_foundation_root=self.legacy_foundation_root)
            obj = self.vector_store.admit(
                operation_key=operation_key,
                logical_step=self.vmrc.epoch,
                input_hash72=input_hash72,
                output_hash72=output_hash72,
                operation_identity_sha256=operation_identity,
                hash216=hash216,
                output_snapshot=after,
                legacy_foundation_root=self.legacy_foundation_root,
                genesis_identity=self.genesis_identity,
                direct_cost_units=direct_cost.total,
                changed_bits=changed_bits,
                parent_object_id=self.state.last_vector_object_id,
            )
            efficiency.observe_direct(direct_cost, changed_bits)
            self.state.predecessor_hash72 = input_hash72
            self.state.current_hash72 = output_hash72
            self.state.last_vector_object_id = obj.object_id
            receipt = self._record_receipt("P174_VECTOR_ADMIT", {
                "object_id": obj.object_id,
                "operation_key": operation_key,
                "input_hash72": input_hash72,
                "output_hash72": output_hash72,
                "hash216_identity": hash216.logical_identity_sha256,
                "hash216_index_root": hash216.index_root_sha256,
                "changed_bits": changed_bits,
                "cost": asdict(direct_cost),
                "cost_total": direct_cost.total,
            })
            return {
                "classification": "HHS_PASS_174_DIRECT_VM81_COMPUTATION_COMMITTED",
                "path": "DIRECT_RUNTIME",
                "operation_key": operation_key,
                "vmrc": result,
                "object": self._public_object(obj),
                "phase": asdict(self.phase),
                "efficiency": efficiency.to_dict(),
                "receipt": receipt,
            }

    @staticmethod
    def _public_object(obj: EncryptedVectorObject) -> dict[str, Any]:
        return {
            "object_id": obj.object_id,
            "operation_key": obj.operation_key,
            "logical_step": obj.logical_step,
            "input_hash72": obj.input_hash72,
            "output_hash72": obj.output_hash72,
            "operation_identity_sha256": obj.operation_identity_sha256,
            "hash216": {
                "predecessor": obj.hash216.predecessor,
                "current": obj.hash216.current,
                "successor": obj.hash216.successor,
                "combined": obj.hash216.combined,
                "character_indexes_sha256": list(obj.hash216.character_indexes_sha256),
                "index_root_sha256": obj.hash216.index_root_sha256,
                "logical_identity_sha256": obj.hash216.logical_identity_sha256,
            },
            "ciphertext_bytes": len(b64decode(obj.ciphertext_b64)),
            "associated_data_sha256": obj.associated_data_sha256,
            "key_version": obj.key_version,
            "direct_cost_units": obj.direct_cost_units,
            "changed_bits": obj.changed_bits,
            "parent_object_id": obj.parent_object_id,
            "plaintext_exposed": False,
        }

    def query(self, operation_key: str) -> dict[str, Any]:
        obj, _ = self.vector_store.retrieve(_require_sha256(operation_key, "operation_key"), legacy_foundation_root=self.legacy_foundation_root, genesis_identity=self.genesis_identity)
        return {"classification": "HHS_PASS_174_VECTOR_QUERY_HIT", "object": self._public_object(obj), "mutation_authority": False}

    def efficiency_report(self) -> dict[str, Any]:
        records = [self._efficiency[key].to_dict() for key in sorted(self._efficiency)]
        return {
            "schema": "HHS_P174_EFFICIENCY_REPORT_V1",
            "records": records,
            "record_count": len(records),
            "vector_store_root": self.vector_store.root(),
            "authority_rule": "EFFICIENCY_SELECTS_AMONG_VALID_PATHS_AND_NEVER_CREATES_AUTHORITY",
        }

    def audit(self, *, challenge: str, sample_limit: int = 16, deep: bool = False) -> dict[str, Any]:
        if not challenge:
            raise Pass174Error("HHS_P174_AUDIT_CHALLENGE_REQUIRED")
        sample_limit = _exact_int(sample_limit, "sample_limit", 1, 216)
        objects = self.vector_store.objects()
        seed = sha256(b"HHS-P174-AUDIT-SEED-V1\0" + bytes.fromhex(self.genesis_identity) + bytes.fromhex(self.legacy_foundation_root) + bytes.fromhex(self.vector_store.root()) + self.vmrc.state_hash72.encode("ascii") + challenge.encode("utf-8")).hexdigest()
        if not objects:
            receipt = self._record_receipt("P174_AUDIT_PASS", {"challenge_seed": seed, "sample_count": 0, "deep": deep, "objects": 0})
            return {"classification": "HHS_PASS_174_AUDIT_PASS", "challenge_seed": seed, "sampled_object_ids": [], "sample_count": 0, "deep": deep, "receipt": receipt}
        indexes = {0, len(objects) - 1}
        if deep:
            indexes.update(range(len(objects)))
        cursor = bytes.fromhex(seed)
        while len(indexes) < min(sample_limit, len(objects)):
            cursor = sha256(b"HHS-P174-AUDIT-SELECT-V1\0" + cursor).digest()
            indexes.add(int.from_bytes(cursor[:8], "big") % len(objects))
        sampled_ids: list[str] = []
        for index in sorted(indexes):
            obj = objects[index]
            try:
                observed, snapshot = self.vector_store.retrieve(obj.operation_key, legacy_foundation_root=self.legacy_foundation_root, genesis_identity=self.genesis_identity)
                if observed.object_id != obj.object_id or len(snapshot) != SNAPSHOT_BYTES:
                    raise Pass174Error("HHS_P174_AUDIT_OBJECT_MISMATCH")
                observed.hash216.verify()
                sampled_ids.append(obj.object_id)
            except Exception as exc:
                self.vector_store.quarantine(obj.object_id)
                self._record_receipt("P174_AUDIT_FAIL", {"challenge_seed": seed, "failed_object_id": obj.object_id, "classification": getattr(exc, "classification", type(exc).__name__)})
                raise Pass174Error("HHS_P174_AUDIT_FAILED", obj.object_id) from exc
        receipt = self._record_receipt("P174_AUDIT_PASS", {"challenge_seed": seed, "sample_count": len(sampled_ids), "sampled_object_ids": sampled_ids, "deep": deep, "objects": len(objects)})
        return {
            "classification": "HHS_PASS_174_AUDIT_PASS",
            "challenge_seed": seed,
            "sampled_object_ids": sampled_ids,
            "sample_count": len(sampled_ids),
            "deep": deep,
            "vector_store_root": self.vector_store.root(),
            "receipt": receipt,
        }

    def replay(self) -> dict[str, Any]:
        inherited = self.vmrc.replay()
        prior = ZERO_SHA256
        for receipt in self.state.receipts:
            if receipt["prior_receipt_sha256"] != prior:
                raise Pass174Error("HHS_P174_RECEIPT_REPLAY_MISMATCH")
            prior = receipt["receipt_sha256"]
        return {
            "classification": "HHS_PASS_174_REPLAY_CLOSED",
            "inherited_vmrc_replay": inherited,
            "receipt_chain_valid": True,
            "receipt_count": len(self.state.receipts),
            "final_receipt_sha256": prior,
            "final_state_hash72": self.vmrc.state_hash72,
            "vector_store_root": self.vector_store.root(),
            "legacy_foundation_root": self.legacy_foundation_root,
            "phase": asdict(self.phase),
        }
