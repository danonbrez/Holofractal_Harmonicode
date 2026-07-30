from __future__ import annotations

import asyncio
import base64
import json
import os
import secrets
import sqlite3
import struct
import threading
import time
from dataclasses import asdict, dataclass, field, is_dataclass
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CONTRACT_ID = "HHS-P174-HPG-EH216-RAVWSC"
SCHEMA_VERSION = "1.0.0"
FRAME_WORDS = 81
WORD_BITS = 64
WORD_MASK = (1 << WORD_BITS) - 1
FRAME_BITS = FRAME_WORDS * WORD_BITS
HASH72_LEN = 72
HASH216_LEN = 216
PHASE_LOCK_PERIOD = 5184
HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
ZERO_SHA256 = "0" * 64
ZERO_HASH72 = HASH72_ALPHABET[0] * HASH72_LEN


class Pass174Error(RuntimeError):
    """Base error for explicit Pass 174 failures."""


class CanonicalizationError(Pass174Error):
    pass


class AdmissionError(Pass174Error):
    pass


class RetrievalError(Pass174Error):
    pass


class AuditError(Pass174Error):
    pass


def _normalize(value: Any) -> Any:
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, bool):
        return {"type": "boolean", "value": value}
    if isinstance(value, int):
        return {"type": "integer", "value": str(value)}
    if isinstance(value, float):
        raise CanonicalizationError("floating-point values cannot enter canonical Pass 174 identity")
    if isinstance(value, Fraction):
        return {
            "type": "rational",
            "numerator": str(value.numerator),
            "denominator": str(value.denominator),
        }
    if isinstance(value, bytes):
        return {"type": "bytes", "base64": base64.b64encode(value).decode("ascii")}
    if is_dataclass(value):
        return _normalize(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _normalize(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    raise CanonicalizationError(f"unsupported canonical value type: {type(value).__name__}")


def canonical_json(value: Any) -> str:
    return json.dumps(_normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_envelope(domain: str, value: Any) -> bytes:
    domain_bytes = domain.encode("utf-8")
    payload = canonical_json(value).encode("utf-8")
    return (
        struct.pack(">I", len(domain_bytes))
        + domain_bytes
        + struct.pack(">Q", len(payload))
        + payload
    )


def digest_hex(domain: str, value: Any) -> str:
    return sha256(canonical_envelope(domain, value)).hexdigest()


def hash72(domain: str, value: Any) -> str:
    seed = canonical_envelope(domain, value)
    output: list[str] = []
    counter = 0
    while len(output) < HASH72_LEN:
        block = sha256(seed + struct.pack(">I", counter)).digest()
        counter += 1
        for octet in block:
            output.append(HASH72_ALPHABET[octet % HASH72_LEN])
            if len(output) == HASH72_LEN:
                break
    return "".join(output)


def _rotl64(value: int, amount: int) -> int:
    amount %= WORD_BITS
    value &= WORD_MASK
    if amount == 0:
        return value
    return ((value << amount) | (value >> (WORD_BITS - amount))) & WORD_MASK


def _popcount(value: int) -> int:
    return int(value & WORD_MASK).bit_count()


@dataclass(frozen=True)
class RationalComplex:
    real: Fraction
    imaginary: Fraction


@dataclass(frozen=True)
class DirectionalInfinity:
    direction: str
    phase: int
    origin_operation: str
    branch_lineage: tuple[str, ...] = ()
    reciprocal_relation: str = ""
    admissible_continuations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.direction:
            raise CanonicalizationError("directional infinity requires a direction")
        object.__setattr__(self, "phase", self.phase % 72)


@dataclass(frozen=True)
class PhaseGearCoordinate:
    transition: int
    phase64: int
    phase72: int
    phase81: int
    phase5184: int
    lock64: bool
    lock72: bool
    lock81: bool
    complete_lock: bool

    @classmethod
    def at(cls, transition: int) -> "PhaseGearCoordinate":
        if transition < 0:
            raise ValueError("transition must be nonnegative")
        return cls(
            transition=transition,
            phase64=transition % 64,
            phase72=transition % 72,
            phase81=transition % 81,
            phase5184=transition % PHASE_LOCK_PERIOD,
            lock64=transition > 0 and transition % 64 == 0,
            lock72=transition > 0 and transition % 72 == 0,
            lock81=transition > 0 and transition % 81 == 0,
            complete_lock=transition > 0 and transition % PHASE_LOCK_PERIOD == 0,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VM81Frame5184:
    words: tuple[int, ...]
    sequence: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if len(self.words) != FRAME_WORDS:
            raise AdmissionError(f"VM81 frame requires exactly {FRAME_WORDS} words")
        normalized: list[int] = []
        for value in self.words:
            if isinstance(value, bool) or not isinstance(value, int):
                raise AdmissionError("VM81 words must be exact integers")
            if value < 0 or value > WORD_MASK:
                raise AdmissionError("VM81 word exceeds unsigned 64-bit range")
            normalized.append(value)
        object.__setattr__(self, "words", tuple(normalized))
        object.__setattr__(
            self,
            "identity",
            sha256(b"HHS174-FRAME-V1\x00" + self.to_bytes()).hexdigest(),
        )

    @classmethod
    def zero(cls, sequence: int = 0) -> "VM81Frame5184":
        return cls(words=(0,) * FRAME_WORDS, sequence=sequence)

    @classmethod
    def genesis(cls, seed: bytes | str, sequence: int = 0) -> "VM81Frame5184":
        seed_bytes = seed.encode("utf-8") if isinstance(seed, str) else bytes(seed)
        words = []
        for index in range(FRAME_WORDS):
            material = sha256(
                b"HHS174-GENESIS-WORD-V1\x00"
                + struct.pack(">I", len(seed_bytes))
                + seed_bytes
                + struct.pack(">I", index)
            ).digest()
            words.append(int.from_bytes(material[:8], "big"))
        return cls(words=tuple(words), sequence=sequence)

    def to_bytes(self) -> bytes:
        return b"".join(struct.pack(">Q", value) for value in self.words)

    def to_dict(self, *, include_bits: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema": "VM81Frame5184@1",
            "sequence": self.sequence,
            "identity": self.identity,
            "word_count": FRAME_WORDS,
            "word_bits": WORD_BITS,
            "frame_bits": FRAME_BITS,
            "words": [f"{value:016x}" for value in self.words],
        }
        if include_bits:
            result["bits"] = [f"{value:064b}" for value in self.words]
        return result


@dataclass(frozen=True)
class HarmonicOperator:
    kind: str
    parameters: tuple[tuple[str, Any], ...]
    ordered_connectors: tuple[str, ...] = ()
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        allowed = {"rotate", "xor", "add", "permute", "reciprocal", "harmonic", "mixed"}
        if self.kind not in allowed:
            raise AdmissionError(f"unsupported harmonic operator kind: {self.kind}")
        for key, value in self.parameters:
            if not isinstance(key, str) or not key:
                raise AdmissionError("operator parameter keys must be nonempty strings")
            _normalize(value)
        object.__setattr__(
            self,
            "identity",
            digest_hex(
                "HHS174-OPERATOR-IDENTITY-V1",
                {
                    "kind": self.kind,
                    "parameters": list(self.parameters),
                    "ordered_connectors": list(self.ordered_connectors),
                },
            ),
        )

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "HarmonicOperator":
        kind = str(payload.get("kind", "rotate"))
        parameters = payload.get("parameters", {})
        if not isinstance(parameters, Mapping):
            raise AdmissionError("operator parameters must be an object")
        connectors = payload.get("ordered_connectors", ())
        if not isinstance(connectors, (list, tuple)):
            raise AdmissionError("ordered_connectors must be a list")
        return cls(
            kind=kind,
            parameters=tuple((str(key), parameters[key]) for key in sorted(parameters)),
            ordered_connectors=tuple(str(item) for item in connectors),
        )

    def parameter(self, name: str, default: Any = None) -> Any:
        return dict(self.parameters).get(name, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HarmonicOperatorState@1",
            "kind": self.kind,
            "parameters": dict(self.parameters),
            "ordered_connectors": list(self.ordered_connectors),
            "identity": self.identity,
        }


@dataclass(frozen=True)
class SparseFrameDelta:
    source_identity: str
    destination_identity: str
    source_sequence: int
    destination_sequence: int
    changes: tuple[tuple[int, int], ...]
    changed_bit_masks: tuple[tuple[int, int], ...]
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        seen: set[int] = set()
        for index, value in self.changes:
            if index in seen or index < 0 or index >= FRAME_WORDS:
                raise AdmissionError("invalid or duplicate sparse delta cell")
            if value < 0 or value > WORD_MASK:
                raise AdmissionError("sparse delta word outside 64-bit range")
            seen.add(index)
        object.__setattr__(
            self,
            "identity",
            digest_hex(
                "HHS174-SPARSE-FRAME-DELTA-V1",
                {
                    "source_identity": self.source_identity,
                    "destination_identity": self.destination_identity,
                    "source_sequence": self.source_sequence,
                    "destination_sequence": self.destination_sequence,
                    "changes": list(self.changes),
                    "changed_bit_masks": list(self.changed_bit_masks),
                },
            ),
        )

    @classmethod
    def between(cls, source: VM81Frame5184, destination: VM81Frame5184) -> "SparseFrameDelta":
        changes: list[tuple[int, int]] = []
        masks: list[tuple[int, int]] = []
        for index, (before, after) in enumerate(zip(source.words, destination.words, strict=True)):
            if before != after:
                changes.append((index, after))
                masks.append((index, before ^ after))
        return cls(
            source_identity=source.identity,
            destination_identity=destination.identity,
            source_sequence=source.sequence,
            destination_sequence=destination.sequence,
            changes=tuple(changes),
            changed_bit_masks=tuple(masks),
        )

    def apply(self, source: VM81Frame5184) -> VM81Frame5184:
        if source.identity != self.source_identity or source.sequence != self.source_sequence:
            raise AdmissionError("sparse delta source frame mismatch")
        words = list(source.words)
        for index, value in self.changes:
            words[index] = value
        result = VM81Frame5184(tuple(words), self.destination_sequence)
        if result.identity != self.destination_identity:
            raise AdmissionError("sparse delta destination identity mismatch")
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "SparseFrameDelta@1",
            "identity": self.identity,
            "source_identity": self.source_identity,
            "destination_identity": self.destination_identity,
            "source_sequence": self.source_sequence,
            "destination_sequence": self.destination_sequence,
            "changes": [{"cell": index, "word": f"{value:016x}"} for index, value in self.changes],
            "changed_bit_masks": [
                {"cell": index, "mask": f"{value:016x}", "changed_bits": _popcount(value)}
                for index, value in self.changed_bit_masks
            ],
        }


@dataclass(frozen=True)
class Hash216CharacterIndex:
    position: int
    lane: int
    lane_position: int
    character: str
    previous_index: str
    next_boundary_commitment: str
    digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Hash216Array:
    predecessor_lane: str
    current_lane: str
    successor_lane: str
    value: str
    logical_identity: str
    indexes: tuple[Hash216CharacterIndex, ...]
    index_root: str

    def __post_init__(self) -> None:
        if any(len(lane) != HASH72_LEN for lane in self.lanes):
            raise AdmissionError("Hash216 requires three exact 72-character lanes")
        if self.value != "".join(self.lanes) or len(self.value) != HASH216_LEN:
            raise AdmissionError("Hash216 lane ordering or length mismatch")
        if len(self.indexes) != HASH216_LEN:
            raise AdmissionError("Hash216 requires 216 positional indexes")

    @property
    def lanes(self) -> tuple[str, str, str]:
        return self.predecessor_lane, self.current_lane, self.successor_lane

    def to_dict(self, *, include_indexes: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema": "Hash216Array@1",
            "logical_identity": self.logical_identity,
            "lane_order": ["predecessor", "current", "successor"],
            "lanes": list(self.lanes),
            "value": self.value,
            "length": len(self.value),
            "index_root": self.index_root,
            "index_count": len(self.indexes),
        }
        if include_indexes:
            result["indexes"] = [index.to_dict() for index in self.indexes]
        return result


@dataclass(frozen=True)
class Hash72ThreeStateTransition:
    previous_frame_identity: str
    current_frame_identity: str
    successor_frame_identity: str
    operator_identity: str
    ordered_connectors: tuple[str, ...]
    phase: PhaseGearCoordinate
    constraint_identity: str
    execution_path: str
    incoming_tip: str
    outgoing_tip: str
    predecessor_lane: str
    current_lane: str
    successor_lane: str
    witness_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "Hash72ThreeStateTransition@1",
            "previous_frame_identity": self.previous_frame_identity,
            "current_frame_identity": self.current_frame_identity,
            "successor_frame_identity": self.successor_frame_identity,
            "operator_identity": self.operator_identity,
            "ordered_connectors": list(self.ordered_connectors),
            "phase": self.phase.to_dict(),
            "constraint_identity": self.constraint_identity,
            "execution_path": self.execution_path,
            "incoming_tip": self.incoming_tip,
            "outgoing_tip": self.outgoing_tip,
            "lanes": [self.predecessor_lane, self.current_lane, self.successor_lane],
            "witness_identity": self.witness_identity,
        }


@dataclass(frozen=True)
class AdmissionWitness:
    genesis_valid: bool
    predecessor_valid: bool
    current_valid: bool
    continuation_valid: bool
    vm81_valid: bool
    hash72_valid: bool
    hash216_valid: bool
    aead_ready: bool

    @property
    def admitted(self) -> bool:
        return all(asdict(self).values())


@dataclass(frozen=True)
class AuditResult:
    audit_class: str
    seed_identity: str
    selected_identities: tuple[str, ...]
    passed: bool
    failed_identities: tuple[str, ...]
    assumed_corruption_fraction: Fraction
    detection_confidence: Fraction
    receipt_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "GenesisAuditResult@1",
            "audit_class": self.audit_class,
            "seed_identity": self.seed_identity,
            "selected_identities": list(self.selected_identities),
            "sample_count": len(self.selected_identities),
            "passed": self.passed,
            "failed_identities": list(self.failed_identities),
            "assumed_corruption_fraction": _normalize(self.assumed_corruption_fraction),
            "detection_confidence": _normalize(self.detection_confidence),
            "receipt_identity": self.receipt_identity,
        }


class KeyRing:
    def __init__(self, keys: Mapping[int, bytes] | None = None, current_version: int = 1) -> None:
        supplied = dict(keys or {})
        if not supplied:
            configured = os.environ.get("HHS174_AEAD_KEY_B64")
            supplied[current_version] = (
                base64.b64decode(configured, validate=True) if configured else AESGCM.generate_key(bit_length=256)
            )
        for version, key in supplied.items():
            if not isinstance(version, int) or version <= 0 or len(key) != 32:
                raise AdmissionError("Pass 174 AEAD keys require positive versions and 256-bit keys")
        if current_version not in supplied:
            raise AdmissionError("current key version is unavailable")
        self._keys = supplied
        self.current_version = current_version

    def add(self, version: int, key: bytes, *, make_current: bool = True) -> None:
        if version <= 0 or len(key) != 32:
            raise AdmissionError("invalid AEAD key")
        if version in self._keys:
            raise AdmissionError("AEAD key version already exists")
        self._keys[version] = bytes(key)
        if make_current:
            self.current_version = version

    def encrypt(self, plaintext: bytes, associated_data: bytes, nonce: bytes) -> tuple[int, bytes]:
        version = self.current_version
        return version, AESGCM(self._keys[version]).encrypt(nonce, plaintext, associated_data)

    def decrypt(self, version: int, nonce: bytes, ciphertext: bytes, associated_data: bytes) -> bytes:
        key = self._keys.get(version)
        if key is None:
            raise RetrievalError("encrypted object key version is unavailable")
        try:
            return AESGCM(key).decrypt(nonce, ciphertext, associated_data)
        except Exception as exc:  # cryptography raises InvalidTag without useful public detail
            raise RetrievalError("AEAD authentication failed") from exc


class EncryptedVectorStore:
    """SQLite-backed authenticated computational continuation store.

    Similarity or query-key matching only locates candidates.  Retrieval returns
    plaintext only after AEAD, parent/frontier, index-root, and bounded-suffix
    checks have passed.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        keyring: KeyRing | None = None,
        active_suffix_limit: int = 64,
    ) -> None:
        if active_suffix_limit <= 0 or active_suffix_limit > PHASE_LOCK_PERIOD:
            raise AdmissionError("active suffix limit must be bounded within 1..5184")
        self.active_suffix_limit = active_suffix_limit
        self.keyring = keyring or KeyRing()
        self.path = str(path) if path is not None else ":memory:"
        if self.path != ":memory:":
            Path(self.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS pass174_objects (
                    logical_identity TEXT PRIMARY KEY,
                    query_key TEXT NOT NULL,
                    parent_identity TEXT,
                    incoming_tip TEXT NOT NULL,
                    outgoing_tip TEXT NOT NULL,
                    frame_identity TEXT NOT NULL,
                    hash216_identity TEXT NOT NULL,
                    index_root TEXT NOT NULL,
                    workload_class TEXT NOT NULL,
                    key_version INTEGER NOT NULL,
                    nonce BLOB NOT NULL,
                    associated_data BLOB NOT NULL,
                    ciphertext BLOB NOT NULL,
                    sequence INTEGER NOT NULL,
                    quarantined INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(key_version, nonce)
                );
                CREATE INDEX IF NOT EXISTS pass174_query_idx
                    ON pass174_objects(query_key, incoming_tip, sequence DESC);
                CREATE INDEX IF NOT EXISTS pass174_parent_idx
                    ON pass174_objects(parent_identity);
                """
            )

    def _row(self, identity: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT * FROM pass174_objects WHERE logical_identity = ?", (identity,)
        ).fetchone()
        if row is None:
            raise RetrievalError("vector object not found")
        return row

    def all_identities(self) -> list[str]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT logical_identity FROM pass174_objects ORDER BY sequence"
            ).fetchall()
            return [str(row[0]) for row in rows]

    def query(self, query_key: str, incoming_tip: str, *, limit: int = 8) -> list[str]:
        if limit <= 0 or limit > self.active_suffix_limit:
            raise RetrievalError("query limit exceeds bounded active suffix policy")
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT logical_identity FROM pass174_objects
                WHERE query_key = ? AND incoming_tip = ? AND quarantined = 0
                ORDER BY sequence DESC LIMIT ?
                """,
                (query_key, incoming_tip, limit),
            ).fetchall()
            return [str(row[0]) for row in rows]

    def admit(
        self,
        *,
        logical_identity: str,
        query_key: str,
        parent_identity: str | None,
        incoming_tip: str,
        outgoing_tip: str,
        frame_identity: str,
        hash216_identity: str,
        index_root: str,
        workload_class: str,
        sequence: int,
        plaintext_record: Mapping[str, Any],
        witness: AdmissionWitness,
    ) -> str:
        if not witness.admitted:
            raise AdmissionError("NO CACHE WRITE WITHOUT VALIDATED CONNECTIVITY")
        if parent_identity is not None:
            with self._lock:
                parent = self._connection.execute(
                    "SELECT quarantined FROM pass174_objects WHERE logical_identity = ?", (parent_identity,)
                ).fetchone()
                if parent is None or int(parent[0]) != 0:
                    raise AdmissionError("vector object predecessor is missing or quarantined")
        canonical_plaintext = canonical_envelope("HHS174-ENCRYPTED-OBJECT-PLAINTEXT-V1", plaintext_record)
        if digest_hex("HHS174-ENCRYPTED-OBJECT-LOGICAL-ID-V1", plaintext_record) != logical_identity:
            raise AdmissionError("vector logical identity mismatch")
        associated_payload = {
            "contract_id": CONTRACT_ID,
            "schema_version": SCHEMA_VERSION,
            "logical_identity": logical_identity,
            "parent_identity": parent_identity,
            "incoming_tip": incoming_tip,
            "outgoing_tip": outgoing_tip,
            "frame_identity": frame_identity,
            "hash216_identity": hash216_identity,
            "index_root": index_root,
            "object_class": "VALIDATED_COMPUTATIONAL_CONTINUATION",
            "key_version": self.keyring.current_version,
        }
        associated_data = canonical_envelope("HHS174-AEAD-ASSOCIATED-DATA-V1", associated_payload)
        with self._lock:
            existing = self._connection.execute(
                "SELECT logical_identity FROM pass174_objects WHERE logical_identity = ?", (logical_identity,)
            ).fetchone()
            if existing is not None:
                return logical_identity
            for _ in range(8):
                nonce = secrets.token_bytes(12)
                duplicate = self._connection.execute(
                    "SELECT 1 FROM pass174_objects WHERE key_version = ? AND nonce = ?",
                    (self.keyring.current_version, nonce),
                ).fetchone()
                if duplicate is None:
                    break
            else:
                raise AdmissionError("unable to allocate unique AEAD nonce")
            key_version, ciphertext = self.keyring.encrypt(canonical_plaintext, associated_data, nonce)
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO pass174_objects(
                        logical_identity, query_key, parent_identity, incoming_tip, outgoing_tip,
                        frame_identity, hash216_identity, index_root, workload_class, key_version,
                        nonce, associated_data, ciphertext, sequence, quarantined
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (
                        logical_identity,
                        query_key,
                        parent_identity,
                        incoming_tip,
                        outgoing_tip,
                        frame_identity,
                        hash216_identity,
                        index_root,
                        workload_class,
                        key_version,
                        nonce,
                        associated_data,
                        ciphertext,
                        sequence,
                    ),
                )
        return logical_identity

    def retrieve(
        self,
        identity: str,
        *,
        expected_incoming_tip: str,
        allowed_parents: Sequence[str | None],
    ) -> dict[str, Any]:
        if len(allowed_parents) > self.active_suffix_limit:
            raise RetrievalError("active suffix validation exceeds configured bound")
        with self._lock:
            row = self._row(identity)
            if int(row["quarantined"]):
                raise RetrievalError("vector object is quarantined")
            if str(row["incoming_tip"]) != expected_incoming_tip:
                raise RetrievalError("stale Hash72 frontier")
            if row["parent_identity"] not in set(allowed_parents):
                raise RetrievalError("vector parent is outside the bounded active frontier")
            plaintext = self.keyring.decrypt(
                int(row["key_version"]),
                bytes(row["nonce"]),
                bytes(row["ciphertext"]),
                bytes(row["associated_data"]),
            )
        prefix = canonical_envelope("HHS174-ENCRYPTED-OBJECT-PLAINTEXT-V1", {})[:0]
        del prefix  # documents that the decrypted bytes are the canonical envelope itself
        try:
            domain_length = struct.unpack(">I", plaintext[:4])[0]
            cursor = 4 + domain_length
            payload_length = struct.unpack(">Q", plaintext[cursor : cursor + 8])[0]
            payload = plaintext[cursor + 8 : cursor + 8 + payload_length]
            record = json.loads(payload.decode("utf-8"))
        except Exception as exc:
            raise RetrievalError("canonical encrypted object decoding failed") from exc
        if digest_hex("HHS174-ENCRYPTED-OBJECT-LOGICAL-ID-V1", record) != identity:
            raise RetrievalError("decrypted logical identity mismatch")
        hash216 = record.get("hash216") or {}
        if hash216.get("index_root") != row["index_root"]:
            raise RetrievalError("Hash216 index root mismatch")
        return record

    def verify_object(self, identity: str) -> bool:
        with self._lock:
            row = self._row(identity)
            if int(row["quarantined"]):
                return False
            allowed = [row["parent_identity"]]
            try:
                record = self.retrieve(
                    identity,
                    expected_incoming_tip=str(row["incoming_tip"]),
                    allowed_parents=allowed,
                )
            except RetrievalError:
                return False
        hash216 = record.get("hash216") or {}
        indexes = hash216.get("indexes") or []
        if len(indexes) != HASH216_LEN:
            return False
        root = digest_hex("HHS174-HASH216-INDEX-ROOT-V1", [item.get("digest") for item in indexes])
        return root == row["index_root"]

    def quarantine(self, identity: str) -> None:
        with self._lock, self._connection:
            cursor = self._connection.execute(
                "UPDATE pass174_objects SET quarantined = 1 WHERE logical_identity = ?", (identity,)
            )
            if cursor.rowcount != 1:
                raise RetrievalError("vector object not found")

    def rotate_key(self, version: int, key: bytes) -> int:
        self.keyring.add(version, key, make_current=True)
        identities = self.all_identities()
        rotated = 0
        with self._lock:
            for identity in identities:
                row = self._row(identity)
                plaintext = self.keyring.decrypt(
                    int(row["key_version"]),
                    bytes(row["nonce"]),
                    bytes(row["ciphertext"]),
                    bytes(row["associated_data"]),
                )
                associated_payload = {
                    "contract_id": CONTRACT_ID,
                    "schema_version": SCHEMA_VERSION,
                    "logical_identity": identity,
                    "parent_identity": row["parent_identity"],
                    "incoming_tip": row["incoming_tip"],
                    "outgoing_tip": row["outgoing_tip"],
                    "frame_identity": row["frame_identity"],
                    "hash216_identity": row["hash216_identity"],
                    "index_root": row["index_root"],
                    "object_class": "VALIDATED_COMPUTATIONAL_CONTINUATION",
                    "key_version": version,
                }
                aad = canonical_envelope("HHS174-AEAD-ASSOCIATED-DATA-V1", associated_payload)
                nonce = secrets.token_bytes(12)
                _, ciphertext = self.keyring.encrypt(plaintext, aad, nonce)
                with self._connection:
                    self._connection.execute(
                        """
                        UPDATE pass174_objects
                        SET key_version = ?, nonce = ?, associated_data = ?, ciphertext = ?
                        WHERE logical_identity = ?
                        """,
                        (version, nonce, aad, ciphertext, identity),
                    )
                rotated += 1
        return rotated


@dataclass
class _Candidate:
    source: VM81Frame5184
    frame: VM81Frame5184
    operator: HarmonicOperator
    phase: PhaseGearCoordinate
    path: str
    costs: dict[str, int]
    query_key: str
    retrieved_identity: str | None = None


class Pass174Runtime:
    """Singleton-owned Pass 174 whole-frame execution component."""

    def __init__(
        self,
        *,
        genesis_seed: bytes | str = b"HHS-P174-GENESIS",
        store_path: str | Path | None = None,
        active_suffix_limit: int = 64,
        constraint_identity: str = "HHS174-BASE-CONSTRAINTS-V1",
        keyring: KeyRing | None = None,
    ) -> None:
        self._lock = threading.RLock()
        self.genesis_seed = genesis_seed.encode("utf-8") if isinstance(genesis_seed, str) else bytes(genesis_seed)
        self.genesis_identity = digest_hex("HHS174-GENESIS-IDENTITY-V1", self.genesis_seed)
        self.constraint_identity = constraint_identity
        self.store = EncryptedVectorStore(
            store_path,
            keyring=keyring,
            active_suffix_limit=active_suffix_limit,
        )
        self.active_suffix_limit = active_suffix_limit
        self.previous_frame = VM81Frame5184.zero(sequence=0)
        self.current_frame = VM81Frame5184.genesis(self.genesis_seed, sequence=0)
        self.candidate: _Candidate | None = None
        self.transition_count = 0
        self.hash72_tip = hash72(
            "HHS174-GENESIS-HASH72-TIP-V1",
            {
                "genesis_identity": self.genesis_identity,
                "previous": self.previous_frame.identity,
                "current": self.current_frame.identity,
            },
        )
        self.hash72_trace: list[dict[str, Any]] = []
        self.hash216_objects: dict[str, Hash216Array] = {}
        self.active_suffix: list[str] = []
        self.receipts: list[dict[str, Any]] = []
        self.receipt_tip = ZERO_SHA256
        self.operation_log: list[dict[str, Any]] = []
        self.efficiency: dict[str, dict[str, int]] = {}
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._boot_counter = 1
        self._last_hash216_identity: str | None = None
        self._emit(
            "P174_GENESIS_INIT",
            {
                "genesis_identity": self.genesis_identity,
                "frame_identity": self.current_frame.identity,
                "hash72_tip": self.hash72_tip,
            },
        )
        self.boot_fingerprint = self._build_boot_fingerprint()

    def _build_boot_fingerprint(self) -> dict[str, Any]:
        minus = hash72("HHS174-BOOT-LANE-MINUS-V1", self.previous_frame.identity)
        zero = hash72("HHS174-BOOT-LANE-ZERO-V1", self.current_frame.identity)
        plus = hash72("HHS174-BOOT-LANE-PLUS-V1", self.hash72_tip)
        canonical_signature = digest_hex(
            "HHS174-CANONICAL-BOOT-FINGERPRINT-V1",
            {
                "genesis_identity": self.genesis_identity,
                "previous": self.previous_frame.identity,
                "current": self.current_frame.identity,
                "hash72_tip": self.hash72_tip,
                "hash216": minus + zero + plus,
            },
        )
        entropy = secrets.token_bytes(32)
        instance_signature = digest_hex(
            "HHS174-BOOT-INSTANCE-FINGERPRINT-V1",
            {
                "canonical_signature": canonical_signature,
                "boot_counter": self._boot_counter,
                "prior_receipt_tip": self.receipt_tip,
                "entropy_challenge": entropy,
            },
        )
        fingerprint = {
            "schema": "BootFingerprint@1",
            "canonical_signature": canonical_signature,
            "instance_signature": instance_signature,
            "boot_counter": self._boot_counter,
            "genesis_identity": self.genesis_identity,
        }
        self._emit("P174_BOOT_FINGERPRINT", fingerprint)
        return fingerprint

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self._subscribers.discard(queue)

    def _publish(self, event: dict[str, Any]) -> None:
        for queue in tuple(self._subscribers):
            try:
                queue.put_nowait(dict(event))
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                    queue.put_nowait(dict(event))
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    pass

    def _emit(self, receipt_class: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        envelope = {
            "schema": "Pass174Receipt@1",
            "contract_id": CONTRACT_ID,
            "receipt_class": receipt_class,
            "sequence": len(self.receipts),
            "parent_receipt": self.receipt_tip,
            "genesis_identity": self.genesis_identity,
            "hash72_tip": self.hash72_tip,
            "canonical_timestamp_ns": time.time_ns(),
            "payload": dict(payload),
        }
        identity = digest_hex("HHS174-RECEIPT-V1", envelope)
        envelope["receipt_identity"] = identity
        self.receipts.append(envelope)
        self.receipt_tip = identity
        self._publish(
            {
                "schema": "P174WebSocketEvent@1",
                "event": receipt_class,
                "receipt_identity": identity,
                "hash72_tip": self.hash72_tip,
                "payload": dict(payload),
            }
        )
        return envelope

    @staticmethod
    def _validate_frame(frame: VM81Frame5184) -> None:
        if len(frame.words) != FRAME_WORDS or len(frame.to_bytes()) * 8 != FRAME_BITS:
            raise AdmissionError("malformed 5184-bit frame")
        if 72 * 72 - 64 * 81 != 0:
            raise AdmissionError("64:72:81 closure invariant failed")

    def _execute_kernel(
        self,
        source: VM81Frame5184,
        operator: HarmonicOperator,
        phase: PhaseGearCoordinate,
    ) -> tuple[VM81Frame5184, dict[str, int]]:
        source_words = source.words
        global_fold = 0x179971179971
        for index, value in enumerate(source_words):
            global_fold ^= _rotl64(value, index % WORD_BITS)
            global_fold = _rotl64((global_fold + value + index + 1) & WORD_MASK, 7)
        amount = operator.parameter("amount", 1)
        mask = operator.parameter("mask", WORD_MASK)
        numerator = operator.parameter("numerator", 3)
        denominator = operator.parameter("denominator", 2)
        for value, name in ((amount, "amount"), (mask, "mask"), (numerator, "numerator"), (denominator, "denominator")):
            if isinstance(value, bool) or not isinstance(value, int):
                raise AdmissionError(f"operator {name} must be an exact integer")
        if denominator == 0:
            raise AdmissionError("harmonic denominator cannot be zero")
        output: list[int] = []
        for index in range(FRAME_WORDS):
            current = source_words[index]
            left = source_words[(index - 1) % FRAME_WORDS]
            right = source_words[(index + 1) % FRAME_WORDS]
            phase_mix = (
                phase.phase64
                | (phase.phase72 << 7)
                | (phase.phase81 << 14)
                | (phase.phase5184 << 21)
            ) & WORD_MASK
            if operator.kind == "rotate":
                value = _rotl64(current ^ right ^ global_fold ^ phase_mix, amount + index + phase.phase72)
            elif operator.kind == "xor":
                value = (current ^ left ^ _rotl64(right, amount) ^ global_fold ^ mask ^ phase_mix) & WORD_MASK
            elif operator.kind == "add":
                value = (current + left + right + global_fold + amount + index + phase_mix) & WORD_MASK
            elif operator.kind == "permute":
                value = source_words[(index + amount) % FRAME_WORDS] ^ _rotl64(global_fold, index + phase.phase64)
            elif operator.kind == "reciprocal":
                reciprocal_index = (FRAME_WORDS - 1 - index + amount) % FRAME_WORDS
                value = _rotl64(source_words[reciprocal_index] ^ global_fold ^ phase_mix, 36 + index)
            elif operator.kind == "harmonic":
                value = (
                    current * numerator
                    + right * denominator
                    + left
                    + global_fold
                    + phase_mix
                ) & WORD_MASK
            else:  # mixed, connector order is part of the operator identity
                value = current
                connectors = operator.ordered_connectors or ("Xor", "Add", "Rotate")
                for connector in connectors:
                    if connector == "Xor":
                        value ^= right ^ global_fold
                    elif connector == "Add":
                        value = (value + left + amount) & WORD_MASK
                    elif connector == "Multiply":
                        value = (value * max(1, numerator)) & WORD_MASK
                    elif connector == "Reciprocal":
                        value ^= source_words[FRAME_WORDS - 1 - index]
                    elif connector == "Rotate":
                        value = _rotl64(value, amount + index)
                    elif connector == "And":
                        value &= mask
                    elif connector == "Or":
                        value |= phase_mix
                    else:
                        raise AdmissionError(f"unsupported ordered connector: {connector}")
                value ^= phase_mix
            output.append(value & WORD_MASK)
        candidate = VM81Frame5184(tuple(output), source.sequence + 1)
        self._validate_frame(candidate)
        return candidate, {
            "decoded_bytecodes": 1,
            "cell_reads": FRAME_WORDS * 3 + FRAME_WORDS,
            "cell_writes": FRAME_WORDS,
            "bit_rotations": FRAME_WORDS + FRAME_WORDS,
            "lane_permutations": FRAME_WORDS if operator.kind in {"permute", "reciprocal"} else 0,
            "modular_operations": FRAME_WORDS * 2,
            "constraint_evaluations": FRAME_WORDS + 1,
            "harmonic_relation_evaluations": FRAME_WORDS if operator.kind in {"harmonic", "mixed"} else 0,
            "closure_iterations": 1,
        }

    def _query_key(self, source: VM81Frame5184, operator: HarmonicOperator, phase: PhaseGearCoordinate) -> str:
        return digest_hex(
            "HHS174-VALIDATED-RETRIEVAL-QUERY-V1",
            {
                "source_frame": source.identity,
                "operator": operator.identity,
                "phase": phase.to_dict(),
                "constraint_identity": self.constraint_identity,
            },
        )

    def _build_transition(
        self,
        candidate: _Candidate,
    ) -> tuple[Hash72ThreeStateTransition, Hash216Array]:
        base = {
            "genesis_identity": self.genesis_identity,
            "previous_frame_identity": self.previous_frame.identity,
            "current_frame_identity": candidate.source.identity,
            "successor_frame_identity": candidate.frame.identity,
            "operator_identity": candidate.operator.identity,
            "ordered_connectors": list(candidate.operator.ordered_connectors),
            "phase": candidate.phase.to_dict(),
            "constraint_identity": self.constraint_identity,
            "execution_path": candidate.path,
            "incoming_tip": self.hash72_tip,
        }
        predecessor_lane = hash72(
            "HHS174-HASH72-PREDECESSOR-LANE-V1",
            {**base, "orientation": "predecessor", "boundary": self.previous_frame.identity},
        )
        current_lane = hash72(
            "HHS174-HASH72-CURRENT-LANE-V1",
            {**base, "orientation": "current", "boundary": candidate.source.identity},
        )
        successor_lane = hash72(
            "HHS174-HASH72-SUCCESSOR-LANE-V1",
            {**base, "orientation": "successor", "boundary": candidate.frame.identity, "clock": current_lane},
        )
        witness_identity = digest_hex(
            "HHS174-VM81-ADMISSION-WITNESS-V1",
            {**base, "lanes": [predecessor_lane, current_lane, successor_lane]},
        )
        transition = Hash72ThreeStateTransition(
            previous_frame_identity=self.previous_frame.identity,
            current_frame_identity=candidate.source.identity,
            successor_frame_identity=candidate.frame.identity,
            operator_identity=candidate.operator.identity,
            ordered_connectors=candidate.operator.ordered_connectors,
            phase=candidate.phase,
            constraint_identity=self.constraint_identity,
            execution_path=candidate.path,
            incoming_tip=self.hash72_tip,
            outgoing_tip=current_lane,
            predecessor_lane=predecessor_lane,
            current_lane=current_lane,
            successor_lane=successor_lane,
            witness_identity=witness_identity,
        )
        value = predecessor_lane + current_lane + successor_lane
        logical_identity = digest_hex(
            "HHS174-HASH216-LOGICAL-IDENTITY-V1",
            {"transition": transition.to_dict(), "value": value},
        )
        indexes = self._build_indexes(
            value=value,
            logical_identity=logical_identity,
            transition=transition,
            operator=candidate.operator,
        )
        index_root = digest_hex(
            "HHS174-HASH216-INDEX-ROOT-V1",
            [index.digest for index in indexes],
        )
        return transition, Hash216Array(
            predecessor_lane=predecessor_lane,
            current_lane=current_lane,
            successor_lane=successor_lane,
            value=value,
            logical_identity=logical_identity,
            indexes=indexes,
            index_root=index_root,
        )

    def _build_indexes(
        self,
        *,
        value: str,
        logical_identity: str,
        transition: Hash72ThreeStateTransition,
        operator: HarmonicOperator,
    ) -> tuple[Hash216CharacterIndex, ...]:
        if len(value) != HASH216_LEN:
            raise AdmissionError("Hash216 must contain 216 characters before indexing")
        previous = digest_hex(
            "HHS174-HASH216-INDEX-ANCHOR-V1",
            {"hash216_identity": logical_identity, "previous_object": self._last_hash216_identity},
        )
        indexes: list[Hash216CharacterIndex] = []
        for position, character in enumerate(value):
            lane = position // HASH72_LEN
            lane_position = position % HASH72_LEN
            next_position = (position + 1) % HASH216_LEN
            next_boundary = digest_hex(
                "HHS174-HASH216-NEXT-BOUNDARY-V1",
                {
                    "hash216_identity": logical_identity,
                    "next_position": next_position,
                    "next_character": value[next_position],
                },
            )
            envelope = {
                "contract_id": CONTRACT_ID,
                "schema_version": SCHEMA_VERSION,
                "genesis_identity": self.genesis_identity,
                "hash216_identity": logical_identity,
                "lane": lane,
                "lane_position": lane_position,
                "absolute_position": position,
                "character": character,
                "alphabet_version": "HHS_HASH72_ALPHABET_V1",
                "previous_character_index": previous,
                "next_character_boundary": next_boundary,
                "previous_hash216_identity": self._last_hash216_identity,
                "incoming_hash72_tip": transition.incoming_tip,
                "outgoing_hash72_tip": transition.outgoing_tip,
                "frame_identity": transition.successor_frame_identity,
                "operator_identity": operator.identity,
                "operator_lineage": list(operator.ordered_connectors),
                "phase": transition.phase.to_dict(),
                "constraint_identity": self.constraint_identity,
                "validation_witness": transition.witness_identity,
                "encryption_key_version": self.store.keyring.current_version,
                "object_class": "VALIDATED_COMPUTATIONAL_CONTINUATION",
            }
            digest = digest_hex("HHS174-HASH216-CHARACTER-INDEX-V1", envelope)
            indexes.append(
                Hash216CharacterIndex(
                    position=position,
                    lane=lane,
                    lane_position=lane_position,
                    character=character,
                    previous_index=previous,
                    next_boundary_commitment=next_boundary,
                    digest=digest,
                )
            )
            previous = digest
        return tuple(indexes)

    def _allowed_parents(self) -> list[str | None]:
        bounded = self.active_suffix[-self.active_suffix_limit :]
        return [None, *bounded]

    def _reconstruct_frame(self, payload: Mapping[str, Any]) -> VM81Frame5184:
        frame = payload.get("destination_frame")
        if not isinstance(frame, Mapping):
            raise RetrievalError("retrieved object lacks destination frame")
        words = frame.get("words")
        if not isinstance(words, list) or len(words) != FRAME_WORDS:
            raise RetrievalError("retrieved frame has invalid word geometry")
        try:
            values = tuple(int(str(item), 16) for item in words)
            result = VM81Frame5184(values, int(frame["sequence"]))
        except Exception as exc:
            raise RetrievalError("retrieved frame decoding failed") from exc
        if result.identity != frame.get("identity"):
            raise RetrievalError("retrieved frame identity mismatch")
        return result

    def execute(self, operator_payload: Mapping[str, Any], *, mode: str = "auto") -> dict[str, Any]:
        if mode not in {"auto", "direct", "retrieval", "hybrid"}:
            raise AdmissionError("execution mode must be auto, direct, retrieval, or hybrid")
        operator = HarmonicOperator.from_mapping(operator_payload)
        with self._lock:
            if self.candidate is not None:
                raise AdmissionError("a whole-frame candidate is already pending")
            source = self.current_frame
            phase = PhaseGearCoordinate.at(self.transition_count + 1)
            query_key = self._query_key(source, operator, phase)
            candidate_frame: VM81Frame5184 | None = None
            retrieved_identity: str | None = None
            path = "direct"
            costs: dict[str, int]
            if mode in {"auto", "retrieval", "hybrid"}:
                matches = self.store.query(query_key, self.hash72_tip, limit=min(8, self.active_suffix_limit))
                for identity in matches:
                    try:
                        record = self.store.retrieve(
                            identity,
                            expected_incoming_tip=self.hash72_tip,
                            allowed_parents=self._allowed_parents(),
                        )
                        candidate_frame = self._reconstruct_frame(record)
                        retrieved_identity = identity
                        path = "retrieval" if mode != "hybrid" else "hybrid"
                        costs = {
                            "vector_comparisons": 1,
                            "decrypted_bytes": len(canonical_json(record).encode("utf-8")),
                            "sha256_index_validations": HASH216_LEN,
                            "active_suffix_records": len(self._allowed_parents()),
                            "constraint_evaluations": FRAME_WORDS + 1,
                            "closure_iterations": 1,
                        }
                        break
                    except RetrievalError:
                        self._record_retrieval_rejection(query_key)
                if mode == "retrieval" and candidate_frame is None:
                    self._emit("P174_VECTOR_MISS", {"query_key": query_key})
                    raise RetrievalError("no valid exact retrieval candidate")
            if candidate_frame is None:
                candidate_frame, costs = self._execute_kernel(source, operator, phase)
                path = "direct" if mode != "hybrid" else "hybrid"
            self._validate_frame(candidate_frame)
            self.candidate = _Candidate(
                source=source,
                frame=candidate_frame,
                operator=operator,
                phase=phase,
                path=path,
                costs=costs,
                query_key=query_key,
                retrieved_identity=retrieved_identity,
            )
            delta = SparseFrameDelta.between(source, candidate_frame)
            candidate_receipt = self._emit(
                "P174_FRAME_CANDIDATE",
                {
                    "source_frame": source.identity,
                    "candidate_frame": candidate_frame.identity,
                    "phase": phase.to_dict(),
                    "operator": operator.to_dict(),
                    "execution_path": path,
                    "delta": delta.to_dict(),
                },
            )
            return {
                "schema": "P174FrameCandidateResult@1",
                "candidate": candidate_frame.to_dict(),
                "delta": delta.to_dict(),
                "phase": phase.to_dict(),
                "execution_path": path,
                "retrieved_identity": retrieved_identity,
                "costs": dict(costs),
                "receipt": candidate_receipt,
                "authoritative": False,
            }

    def commit(self) -> dict[str, Any]:
        with self._lock:
            candidate = self.candidate
            if candidate is None:
                raise AdmissionError("no complete candidate frame is pending")
            if candidate.source.identity != self.current_frame.identity:
                self.candidate = None
                self._emit("P174_FRAME_REJECT", {"reason": "source frame changed before commit"})
                raise AdmissionError("candidate source frame is stale")
            transition, hash216_array = self._build_transition(candidate)
            delta = SparseFrameDelta.between(candidate.source, candidate.frame)
            record = {
                "schema": "EncryptedVectorObjectPlaintext@1",
                "genesis_identity": self.genesis_identity,
                "source_frame": candidate.source.to_dict(),
                "destination_frame": candidate.frame.to_dict(),
                "operator": candidate.operator.to_dict(),
                "phase": candidate.phase.to_dict(),
                "transition": transition.to_dict(),
                "hash216": hash216_array.to_dict(include_indexes=True),
                "delta": delta.to_dict(),
                "costs": dict(candidate.costs),
                "query_key": candidate.query_key,
                "retrieved_identity": candidate.retrieved_identity,
            }
            logical_identity = digest_hex("HHS174-ENCRYPTED-OBJECT-LOGICAL-ID-V1", record)
            parent_identity = self.active_suffix[-1] if self.active_suffix else None
            witness = AdmissionWitness(
                genesis_valid=bool(self.genesis_identity),
                predecessor_valid=parent_identity is None or parent_identity in self.active_suffix,
                current_valid=candidate.source.identity == self.current_frame.identity,
                continuation_valid=candidate.frame.sequence == candidate.source.sequence + 1,
                vm81_valid=len(candidate.frame.words) == FRAME_WORDS,
                hash72_valid=len(transition.outgoing_tip) == HASH72_LEN,
                hash216_valid=len(hash216_array.value) == HASH216_LEN and len(hash216_array.indexes) == HASH216_LEN,
                aead_ready=True,
            )
            self.store.admit(
                logical_identity=logical_identity,
                query_key=candidate.query_key,
                parent_identity=parent_identity,
                incoming_tip=transition.incoming_tip,
                outgoing_tip=transition.outgoing_tip,
                frame_identity=candidate.frame.identity,
                hash216_identity=hash216_array.logical_identity,
                index_root=hash216_array.index_root,
                workload_class=candidate.operator.kind,
                sequence=self.transition_count + 1,
                plaintext_record=record,
                witness=witness,
            )
            old_current = self.current_frame
            self.previous_frame = old_current
            self.current_frame = candidate.frame
            self.transition_count += 1
            self.hash72_tip = transition.outgoing_tip
            self.hash72_trace.append(transition.to_dict())
            self.hash216_objects[hash216_array.logical_identity] = hash216_array
            self._last_hash216_identity = hash216_array.logical_identity
            self.active_suffix.append(logical_identity)
            if len(self.active_suffix) > self.active_suffix_limit:
                del self.active_suffix[: len(self.active_suffix) - self.active_suffix_limit]
            self.operation_log.append(
                {"operator": candidate.operator.to_dict(), "mode": "direct", "expected_frame": candidate.frame.identity}
            )
            self._update_efficiency(candidate, delta)
            self.candidate = None
            receipt = self._emit(
                "P174_FRAME_COMMIT",
                {
                    "source_frame": old_current.identity,
                    "destination_frame": self.current_frame.identity,
                    "phase": candidate.phase.to_dict(),
                    "hash72_tip": self.hash72_tip,
                    "hash216_identity": hash216_array.logical_identity,
                    "vector_object_identity": logical_identity,
                    "execution_path": candidate.path,
                    "changed_cells": len(delta.changes),
                    "changed_bits": sum(_popcount(mask) for _, mask in delta.changed_bit_masks),
                },
            )
            self._emit("P174_HASH72_ADVANCE", {"transition": transition.to_dict()})
            self._emit(
                "P174_HASH216_BUILD",
                {
                    "hash216_identity": hash216_array.logical_identity,
                    "index_root": hash216_array.index_root,
                    "index_count": HASH216_LEN,
                },
            )
            if candidate.phase.phase72 == 0:
                self._emit("P174_PHASE_WRAP", {"phase": candidate.phase.to_dict(), "state_reset": False})
            if candidate.phase.complete_lock:
                self._emit("P174_PHASE_LOCK_5184", {"phase": candidate.phase.to_dict(), "state_reset": False})
            return {
                "schema": "P174FrameCommitResult@1",
                "authoritative": True,
                "frame": self.current_frame.to_dict(),
                "phase": candidate.phase.to_dict(),
                "transition": transition.to_dict(),
                "hash216": hash216_array.to_dict(include_indexes=False),
                "vector_object_identity": logical_identity,
                "receipt": receipt,
            }

    def execute_and_commit(self, operator_payload: Mapping[str, Any], *, mode: str = "auto") -> dict[str, Any]:
        candidate = self.execute(operator_payload, mode=mode)
        committed = self.commit()
        return {"candidate": candidate, "committed": committed}

    def discard_candidate(self, reason: str = "explicit discard") -> dict[str, Any]:
        with self._lock:
            pending = self.candidate
            self.candidate = None
            receipt = self._emit(
                "P174_FRAME_REJECT",
                {
                    "reason": reason,
                    "candidate_frame": pending.frame.identity if pending else None,
                    "hash72_advanced": False,
                },
            )
            return {"discarded": pending is not None, "receipt": receipt}

    def _record_retrieval_rejection(self, query_key: str) -> None:
        record = self.efficiency.setdefault(query_key, self._empty_efficiency())
        record["rejected_retrieval_count"] += 1
        self._emit("P174_VECTOR_REJECT", {"query_key": query_key, "authority_created": False})

    @staticmethod
    def _empty_efficiency() -> dict[str, int]:
        return {
            "direct_runtime_cost": 0,
            "retrieval_cost": 0,
            "hybrid_cost": 0,
            "verification_cost": 0,
            "decryption_cost": 0,
            "sparse_delta_cost": 0,
            "closure_cost": 0,
            "vm81_operation_count": 0,
            "changed_cell_count": 0,
            "changed_bit_count": 0,
            "successful_retrieval_count": 0,
            "rejected_retrieval_count": 0,
            "stale_frontier_count": 0,
            "reuse_frequency": 0,
            "avoided_work": 0,
        }

    def _update_efficiency(self, candidate: _Candidate, delta: SparseFrameDelta) -> None:
        record = self.efficiency.setdefault(candidate.query_key, self._empty_efficiency())
        total_cost = sum(candidate.costs.values())
        if candidate.path == "direct":
            record["direct_runtime_cost"] += total_cost
        elif candidate.path == "retrieval":
            record["retrieval_cost"] += total_cost
            record["successful_retrieval_count"] += 1
            record["reuse_frequency"] += 1
            record["avoided_work"] += max(0, FRAME_WORDS * 8 - total_cost)
        else:
            record["hybrid_cost"] += total_cost
        record["verification_cost"] += candidate.costs.get("sha256_index_validations", 0)
        record["decryption_cost"] += candidate.costs.get("decrypted_bytes", 0)
        record["sparse_delta_cost"] += len(delta.changes)
        record["closure_cost"] += candidate.costs.get("closure_iterations", 0)
        record["vm81_operation_count"] += total_cost
        record["changed_cell_count"] += len(delta.changes)
        record["changed_bit_count"] += sum(_popcount(mask) for _, mask in delta.changed_bit_masks)
        self._emit(
            "P174_EFFICIENCY_UPDATE",
            {
                "query_key": candidate.query_key,
                "record": dict(record),
                "authority_created": False,
            },
        )

    def compare_efficiency(self, query_key: str) -> dict[str, Any]:
        record = dict(self.efficiency.get(query_key, self._empty_efficiency()))
        direct = record["direct_runtime_cost"]
        retrieval = record["retrieval_cost"]
        hybrid = record["hybrid_cost"]
        advantage = direct - retrieval if retrieval else 0
        successes = record["successful_retrieval_count"]
        failures = record["rejected_retrieval_count"]
        confidence = Fraction(successes, successes + failures + 1)
        preference = "retrieval" if retrieval and advantage > 0 else "direct"
        receipt = self._emit(
            "P174_EFFICIENCY_COMPARE",
            {
                "query_key": query_key,
                "direct_runtime_cost": direct,
                "retrieval_cost": retrieval,
                "hybrid_cost": hybrid,
                "advantage": advantage,
                "confidence": confidence,
                "preference": preference,
                "authority_created": False,
            },
        )
        return {
            "query_key": query_key,
            "record": record,
            "advantage": advantage,
            "confidence": _normalize(confidence),
            "preference": preference,
            "receipt_identity": receipt["receipt_identity"],
        }

    def efficiency_report(self) -> dict[str, Any]:
        return {
            "schema": "P174EfficiencyReport@1",
            "authority_rule": "EFFICIENCY SELECTS AMONG VALID PATHS; EFFICIENCY NEVER CREATES AUTHORITY",
            "records": [
                {"query_key": key, **dict(value)} for key, value in sorted(self.efficiency.items())
            ],
        }

    def get_hash216(self, identity: str) -> dict[str, Any]:
        item = self.hash216_objects.get(identity)
        if item is None:
            raise RetrievalError("Hash216 object not found in active runtime projection")
        return item.to_dict(include_indexes=True)

    def query_vectors(self, operator_payload: Mapping[str, Any]) -> dict[str, Any]:
        operator = HarmonicOperator.from_mapping(operator_payload)
        phase = PhaseGearCoordinate.at(self.transition_count + 1)
        query_key = self._query_key(self.current_frame, operator, phase)
        identities = self.store.query(query_key, self.hash72_tip, limit=min(8, self.active_suffix_limit))
        receipt_class = "P174_VECTOR_HIT" if identities else "P174_VECTOR_MISS"
        receipt = self._emit(receipt_class, {"query_key": query_key, "identities": identities})
        return {
            "query_key": query_key,
            "identities": identities,
            "similarity_is_authority": False,
            "receipt_identity": receipt["receipt_identity"],
        }

    def quarantine(self, identity: str) -> dict[str, Any]:
        self.store.quarantine(identity)
        receipt = self._emit("P174_VECTOR_QUARANTINE", {"identity": identity})
        return {"identity": identity, "quarantined": True, "receipt": receipt}

    def audit(
        self,
        *,
        deep: bool = False,
        sample_count: int | None = None,
        challenge: bytes | None = None,
        assumed_corruption_fraction: Fraction = Fraction(1, 100),
    ) -> AuditResult:
        identities = self.store.all_identities()
        if not identities:
            raise AuditError("no encrypted Hash216 objects are available for audit")
        audit_class = "deep" if deep else "light"
        default_count = min(len(identities), 16 if deep else 4)
        count = sample_count if sample_count is not None else default_count
        if count <= 0 or count > len(identities):
            raise AuditError("audit sample count is outside the stored object domain")
        challenge_bytes = challenge if challenge is not None else secrets.token_bytes(32)
        seed_identity = digest_hex(
            "HHS174-GENESIS-AUDIT-SEED-V1",
            {
                "genesis_identity": self.genesis_identity,
                "hash72_tip": self.hash72_tip,
                "hash216_head": self._last_hash216_identity,
                "prior_receipt": self.receipt_tip,
                "challenge": challenge_bytes,
                "audit_class": audit_class,
            },
        )
        selected_indexes: list[int] = []
        cursor = 0
        while len(selected_indexes) < count:
            block = sha256(bytes.fromhex(seed_identity) + struct.pack(">I", cursor)).digest()
            cursor += 1
            for offset in range(0, len(block), 4):
                value = int.from_bytes(block[offset : offset + 4], "big") % len(identities)
                if value not in selected_indexes:
                    selected_indexes.append(value)
                    if len(selected_indexes) == count:
                        break
        selected = tuple(identities[index] for index in selected_indexes)
        failed = tuple(identity for identity in selected if not self.store.verify_object(identity))
        confidence = Fraction(1, 1) - (Fraction(1, 1) - assumed_corruption_fraction) ** count
        challenge_receipt = self._emit(
            "P174_AUDIT_CHALLENGE",
            {
                "audit_class": audit_class,
                "seed_identity": seed_identity,
                "sample_count": count,
                "selected_identities": selected,
            },
        )
        result_receipt = self._emit(
            "P174_AUDIT_PASS" if not failed else "P174_AUDIT_FAIL",
            {
                "challenge_receipt": challenge_receipt["receipt_identity"],
                "seed_identity": seed_identity,
                "selected_identities": selected,
                "failed_identities": failed,
                "detection_confidence": confidence,
            },
        )
        if failed:
            for identity in failed:
                self.store.quarantine(identity)
        return AuditResult(
            audit_class=audit_class,
            seed_identity=seed_identity,
            selected_identities=selected,
            passed=not failed,
            failed_identities=failed,
            assumed_corruption_fraction=assumed_corruption_fraction,
            detection_confidence=confidence,
            receipt_identity=result_receipt["receipt_identity"],
        )

    def replay(self) -> dict[str, Any]:
        replay_runtime = Pass174Runtime(
            genesis_seed=self.genesis_seed,
            active_suffix_limit=self.active_suffix_limit,
            constraint_identity=self.constraint_identity,
            keyring=KeyRing(keys={1: bytes(range(32))}, current_version=1),
        )
        for entry in self.operation_log:
            operator = entry["operator"]
            replay_runtime.execute_and_commit(
                {
                    "kind": operator["kind"],
                    "parameters": operator["parameters"],
                    "ordered_connectors": operator["ordered_connectors"],
                },
                mode="direct",
            )
        match = (
            replay_runtime.current_frame.identity == self.current_frame.identity
            and replay_runtime.hash72_tip == self.hash72_tip
            and replay_runtime.transition_count == self.transition_count
        )
        receipt = self._emit(
            "P174_REPLAY",
            {
                "match": match,
                "expected_frame": self.current_frame.identity,
                "actual_frame": replay_runtime.current_frame.identity,
                "expected_hash72_tip": self.hash72_tip,
                "actual_hash72_tip": replay_runtime.hash72_tip,
                "operation_count": len(self.operation_log),
            },
        )
        if not match:
            raise AdmissionError("deterministic Pass 174 replay mismatch")
        return {
            "match": True,
            "frame_identity": self.current_frame.identity,
            "hash72_tip": self.hash72_tip,
            "operation_count": len(self.operation_log),
            "receipt": receipt,
        }

    def status(self) -> dict[str, Any]:
        phase = PhaseGearCoordinate.at(self.transition_count)
        return {
            "schema": "P174RuntimeStatus@1",
            "contract_id": CONTRACT_ID,
            "classification": "HHS_PASS_174_IMPLEMENTATION_ACTIVE_PENDING_FULL_CLOSURE",
            "runtime_authority": "singleton VM81 whole-state authority component",
            "whole_frame_authority": True,
            "frame_bits": FRAME_BITS,
            "frame_words": FRAME_WORDS,
            "word_bits": WORD_BITS,
            "current_frame_identity": self.current_frame.identity,
            "candidate_frame_identity": self.candidate.frame.identity if self.candidate else None,
            "transition_count": self.transition_count,
            "phase": phase.to_dict(),
            "hash72_tip": self.hash72_tip,
            "hash216_head": self._last_hash216_identity,
            "active_suffix_length": len(self.active_suffix),
            "active_suffix_limit": self.active_suffix_limit,
            "encrypted_object_count": len(self.store.all_identities()),
            "receipt_tip": self.receipt_tip,
            "pass174_terminal": False,
        }

    def doctor(self) -> dict[str, Any]:
        checks = {
            "frame_geometry": len(self.current_frame.words) == FRAME_WORDS and len(self.current_frame.to_bytes()) * 8 == FRAME_BITS,
            "phase_closure_equation": 72 * 72 == 64 * 81,
            "hash72_tip_length": len(self.hash72_tip) == HASH72_LEN,
            "active_suffix_bounded": len(self.active_suffix) <= self.active_suffix_limit,
            "candidate_is_non_authoritative": self.candidate is None or self.candidate.frame.identity != self.current_frame.identity,
            "all_active_objects_authenticated": all(self.store.verify_object(identity) for identity in self.active_suffix),
        }
        return {
            "schema": "P174Doctor@1",
            "healthy": all(checks.values()),
            "checks": checks,
            "repair_required": [name for name, passed in checks.items() if not passed],
        }

    def receipt(self, identity: str) -> dict[str, Any]:
        for receipt in self.receipts:
            if receipt["receipt_identity"] == identity:
                return dict(receipt)
        raise RetrievalError("Pass 174 receipt not found")
