"""Reference Pass 163 VMRC runtime.

Implements the 81x64 Boolean snapshot, canonical Base64 snapshot compilation,
exact sparse polarity compression, immutable parameter identities, bounded
phase-gear propagation, path-dependent exact memristor state, exact
continuation keys, Hash72(D||S), inherited Hash216 operation identity,
append-only indexing, singleton authority, and deterministic replay.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass
from fractions import Fraction
from hashlib import sha256
import hmac
import json
from threading import RLock
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass150.genome import Hash216Genome

ABI_VERSION = 1
MAGIC = "HHS-P163-VMRC"
THREADS = 64
VM81_POSITIONS = 81
PORT_POSITIONS = 9
PARAMETER_POSITIONS = 72
COORDINATES = THREADS * VM81_POSITIONS
SNAPSHOT_BYTES = COORDINATES // 8
BASE64_SYMBOLS = SNAPSHOT_BYTES * 4 // 3
ZERO_HASH216 = "0" * 64
MAX_PROPAGATION_STEPS = COORDINATES
MAX_ENVELOPE_BYTES = 1 << 20

OPERATION_CLASSES = (
    "VMRC_STATUS", "VMRC_SNAPSHOT_OPEN", "VMRC_SNAPSHOT_READ",
    "VMRC_THREAD_BIND", "VMRC_THREAD_PROJECT", "VMRC_PARAMETER_REGISTER",
    "VMRC_PARAMETER_LOOKUP", "VMRC_GEAR_REGISTER", "VMRC_GEAR_PROPAGATE",
    "VMRC_MEMRISTOR_READ", "VMRC_MEMRISTOR_PROPOSE", "VMRC_CACHE_LOOKUP",
    "VMRC_CACHE_REUSE", "VMRC_CACHE_INVALIDATE", "VMRC_COMPRESS",
    "VMRC_EXPAND", "VMRC_BASE64_ENCODE", "VMRC_BASE64_DECODE",
    "VMRC_CANDIDATE_SUBMIT", "VMRC_VALIDATE", "VMRC_COMMIT",
    "VMRC_REPLAY", "VMRC_RECEIPT",
)


class VMRCError(ValueError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _require_int(name: str, value: int, lower: int, upper: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not lower <= value <= upper:
        raise VMRCError("VMRC_RESOURCE_BOUND", name)
    return value


def _fraction(value: int | str | Fraction | Sequence[int]) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes, bytearray))
        and len(value) == 2
    ):
        return Fraction(int(value[0]), int(value[1]))
    raise VMRCError("VMRC_CANONICAL_FLOAT_REJECTED")


@dataclass(frozen=True)
class SparseSnapshot:
    background: int
    exceptions: tuple[int, ...]
    version: int = 1

    def __post_init__(self) -> None:
        if self.background not in (0, 1):
            raise VMRCError("VMRC_INVALID_POLARITY")
        if self.version != 1:
            raise VMRCError("VMRC_UNSUPPORTED_VERSION")
        if tuple(sorted(set(self.exceptions))) != self.exceptions:
            raise VMRCError("VMRC_NONCANONICAL_SPARSE_COORDINATES")
        if any(
            not isinstance(index, int) or not 0 <= index < COORDINATES
            for index in self.exceptions
        ):
            raise VMRCError("VMRC_SPARSE_COORDINATE_OUT_OF_RANGE")

    def expand(self) -> "VMRCSnapshot":
        raw = bytearray([0xFF if self.background else 0x00] * SNAPSHOT_BYTES)
        snapshot = VMRCSnapshot(raw)
        for index in self.exceptions:
            snapshot._set_index(index, 1 - self.background)
        return snapshot


class VMRCSnapshot:
    __slots__ = ("_raw",)

    def __init__(self, raw: bytes | bytearray | memoryview | None = None) -> None:
        candidate = bytes(SNAPSHOT_BYTES) if raw is None else bytes(raw)
        if len(candidate) != SNAPSHOT_BYTES:
            raise VMRCError("VMRC_INCORRECT_EXPANDED_LENGTH")
        self._raw = bytearray(candidate)

    @staticmethod
    def coordinate_index(position: int, thread: int) -> int:
        _require_int("position", position, 0, VM81_POSITIONS - 1)
        _require_int("thread", thread, 0, THREADS - 1)
        return position * THREADS + thread

    def copy(self) -> "VMRCSnapshot":
        return VMRCSnapshot(self._raw)

    def to_bytes(self) -> bytes:
        return bytes(self._raw)

    def _get_index(self, index: int) -> int:
        byte_index, bit_index = divmod(index, 8)
        return (self._raw[byte_index] >> (7 - bit_index)) & 1

    def _set_index(self, index: int, value: int) -> None:
        if value not in (0, 1):
            raise VMRCError("VMRC_NONBOOLEAN_COMMIT")
        byte_index, bit_index = divmod(index, 8)
        mask = 1 << (7 - bit_index)
        if value:
            self._raw[byte_index] |= mask
        else:
            self._raw[byte_index] &= ~mask

    def get(self, position: int, thread: int) -> int:
        return self._get_index(self.coordinate_index(position, thread))

    def _authority_set(
        self,
        position: int,
        thread: int,
        value: int,
        token: object,
        authority_token: object,
    ) -> None:
        if token is not authority_token:
            raise VMRCError("VMRC_DIRECT_CANONICAL_MUTATION_DENIED")
        self._set_index(self.coordinate_index(position, thread), value)

    def thread_projection(self, thread: int) -> tuple[int, ...]:
        _require_int("thread", thread, 0, THREADS - 1)
        return tuple(self.get(position, thread) for position in range(VM81_POSITIONS))

    def position_burst(self, position: int) -> tuple[int, ...]:
        _require_int("position", position, 0, VM81_POSITIONS - 1)
        return tuple(self.get(position, thread) for thread in range(THREADS))

    def base64(self) -> str:
        encoded = b64encode(self.to_bytes()).decode("ascii")
        if len(encoded) != BASE64_SYMBOLS or "=" in encoded:
            raise RuntimeError("VMRC_BASE64_GEOMETRY_FAILURE")
        return encoded

    @classmethod
    def from_base64(cls, encoded: str) -> "VMRCSnapshot":
        if not isinstance(encoded, str) or len(encoded) != BASE64_SYMBOLS or "=" in encoded:
            raise VMRCError("VMRC_MALFORMED_BASE64")
        try:
            raw = b64decode(encoded, validate=True)
        except Exception as exc:
            raise VMRCError("VMRC_MALFORMED_BASE64") from exc
        if len(raw) != SNAPSHOT_BYTES:
            raise VMRCError("VMRC_INCORRECT_EXPANDED_LENGTH")
        if b64encode(raw).decode("ascii") != encoded:
            raise VMRCError("VMRC_NONCANONICAL_BASE64")
        return cls(raw)

    def compress(self) -> SparseSnapshot:
        ones = sum(byte.bit_count() for byte in self._raw)
        zeros = COORDINATES - ones
        background = 0 if ones <= zeros else 1
        exceptions = tuple(
            index
            for index in range(COORDINATES)
            if self._get_index(index) != background
        )
        return SparseSnapshot(background=background, exceptions=exceptions)


@dataclass(frozen=True)
class ParameterObject:
    identity: str
    type: str
    value: Any
    domain: str
    phase: int
    operator: str
    constraints: tuple[str, ...]
    provenance: str


class ParameterRegistry:
    def __init__(self) -> None:
        self._objects: dict[str, ParameterObject] = {}

    @staticmethod
    def _body(
        *,
        type: str,
        value: Any,
        domain: str,
        phase: int,
        operator: str,
        constraints: Iterable[str],
        provenance: str,
    ) -> dict[str, Any]:
        if not type or not domain or not operator or not provenance:
            raise VMRCError("VMRC_PARAMETER_FIELD_REQUIRED")
        if isinstance(value, float):
            raise VMRCError("VMRC_CANONICAL_FLOAT_REJECTED")
        _require_int("phase", phase, 0, PARAMETER_POSITIONS - 1)
        return {
            "type": type,
            "value": json.loads(canonical_bytes(value)),
            "domain": domain,
            "phase": phase,
            "operator": operator,
            "constraints": tuple(sorted(str(item) for item in constraints)),
            "provenance": provenance,
        }

    def register(self, **kwargs: Any) -> ParameterObject:
        body = self._body(**kwargs)
        identity = sha256(
            b"HHS-P163-PARAMETER-V1\0" + canonical_bytes(body)
        ).hexdigest()
        existing = self._objects.get(identity)
        if existing is not None:
            return existing
        obj = ParameterObject(identity=identity, **body)
        self._objects[identity] = obj
        return obj

    def restore(self, raw: Mapping[str, Any]) -> ParameterObject:
        expected = str(raw["identity"])
        obj = self.register(
            type=str(raw["type"]),
            value=raw["value"],
            domain=str(raw["domain"]),
            phase=int(raw["phase"]),
            operator=str(raw["operator"]),
            constraints=tuple(raw.get("constraints", ())),
            provenance=str(raw["provenance"]),
        )
        if obj.identity != expected:
            raise VMRCError("VMRC_PARAMETER_IDENTITY_MISMATCH")
        return obj

    def lookup(self, identity: str) -> ParameterObject:
        try:
            return self._objects[identity]
        except KeyError as exc:
            raise VMRCError("VMRC_PARAMETER_NOT_FOUND") from exc

    def canonical(self) -> bytes:
        return canonical_bytes(
            [asdict(self._objects[key]) for key in sorted(self._objects)]
        )

    def root(self) -> str:
        return sha256(
            b"HHS-P163-PARAMETER-DICTIONARY-V1\0" + self.canonical()
        ).hexdigest()

    def __len__(self) -> int:
        return len(self._objects)


@dataclass(frozen=True)
class PhaseGear:
    identity: str
    source: tuple[int, int]
    target: tuple[int, int]
    direction: int
    u72_offset: int
    xyzw_weights: tuple[str, str, str, str]
    operator: str
    invariant_set: str


class PhaseGearGraph:
    def __init__(self) -> None:
        self._gears: dict[str, PhaseGear] = {}

    def register(
        self,
        source: tuple[int, int],
        target: tuple[int, int],
        *,
        direction: int,
        u72_offset: int = 0,
        xyzw_weights: Sequence[int | str | Fraction | Sequence[int]] = (1, 1, 1, 1),
        operator: str = "COPY",
        invariant_set: str = "DEFAULT",
    ) -> PhaseGear:
        VMRCSnapshot.coordinate_index(*source)
        VMRCSnapshot.coordinate_index(*target)
        if direction not in (-1, 0, 1):
            raise VMRCError("VMRC_INVALID_GEAR_DIRECTION")
        _require_int("u72_offset", u72_offset, 0, 71)
        weights = tuple(str(_fraction(item)) for item in xyzw_weights)
        if len(weights) != 4:
            raise VMRCError("VMRC_INVALID_XYZW_WEIGHTS")
        body = {
            "source": source,
            "target": target,
            "direction": direction,
            "u72_offset": u72_offset,
            "xyzw_weights": weights,
            "operator": operator,
            "invariant_set": invariant_set,
        }
        identity = sha256(
            b"HHS-P163-GEAR-V1\0" + canonical_bytes(body)
        ).hexdigest()
        gear = PhaseGear(
            identity=identity,
            source=source,
            target=target,
            direction=direction,
            u72_offset=u72_offset,
            xyzw_weights=weights,
            operator=operator,
            invariant_set=invariant_set,
        )
        self._gears.setdefault(identity, gear)
        return self._gears[identity]

    def root(self) -> str:
        return sha256(
            b"HHS-P163-GEAR-GRAPH-V1\0"
            + canonical_bytes(
                [asdict(self._gears[key]) for key in sorted(self._gears)]
            )
        ).hexdigest()

    def propagate(
        self,
        snapshot: VMRCSnapshot,
        seeds: Mapping[tuple[int, int], int],
        *,
        max_steps: int = MAX_PROPAGATION_STEPS,
    ) -> dict[tuple[int, int], int]:
        if not 1 <= max_steps <= MAX_PROPAGATION_STEPS:
            raise VMRCError("VMRC_PROPAGATION_BOUND")
        result = dict(seeds)
        queue = list(sorted(seeds.items()))
        seen: set[tuple[str, int]] = set()
        steps = 0
        by_source: dict[tuple[int, int], list[PhaseGear]] = {}
        for gear in self._gears.values():
            by_source.setdefault(gear.source, []).append(gear)
        for gears in by_source.values():
            gears.sort(key=lambda item: item.identity)
        while queue:
            source, source_value = queue.pop(0)
            for gear in by_source.get(source, ()):
                marker = (gear.identity, source_value)
                if marker in seen:
                    continue
                seen.add(marker)
                steps += 1
                if steps > max_steps:
                    raise VMRCError("VMRC_UNBOUNDED_PROPAGATION_CYCLE")
                if gear.direction == 0:
                    target_value = result.get(
                        gear.target,
                        snapshot.get(*gear.target),
                    )
                elif gear.direction == 1:
                    target_value = source_value
                else:
                    target_value = 1 - source_value
                previous = result.get(
                    gear.target,
                    snapshot.get(*gear.target),
                )
                if previous != target_value:
                    result[gear.target] = target_value
                    queue.append((gear.target, target_value))
                    queue.sort()
        return result


@dataclass(frozen=True)
class MemristorEdge:
    identity: str
    source: str
    target: str
    conductance: str
    resistance: str
    polarity: int
    admitted_history: tuple[str, ...]
    reuse_count: int
    hash216_vector: str


class MemristorStore:
    def __init__(self) -> None:
        self._edges: dict[str, MemristorEdge] = {}

    def read(self, identity: str) -> MemristorEdge:
        try:
            return self._edges[identity]
        except KeyError as exc:
            raise VMRCError("VMRC_MEMRISTOR_NOT_FOUND") from exc

    def propose(
        self,
        source: str,
        target: str,
        *,
        conductance: Any,
        polarity: int,
        prior_identity: str | None = None,
    ) -> MemristorEdge:
        if not source or not target or polarity not in (-1, 1):
            raise VMRCError("VMRC_INVALID_MEMRISTOR_PROPOSAL")
        proposed = _fraction(conductance)
        if proposed <= 0:
            raise VMRCError("VMRC_INVALID_MEMRISTOR_WEIGHT")
        history: tuple[str, ...] = ()
        reuse = 0
        if prior_identity is not None:
            prior = self.read(prior_identity)
            if (prior.source, prior.target) != (source, target):
                raise VMRCError("VMRC_MEMRISTOR_EDGE_MISMATCH")
            history = prior.admitted_history + (prior.identity,)
            reuse = prior.reuse_count + 1
            proposed = _fraction(prior.conductance) + proposed
        body = {
            "source": source,
            "target": target,
            "conductance": str(proposed),
            "resistance": str(1 / proposed),
            "polarity": polarity,
            "admitted_history": history,
            "reuse_count": reuse,
        }
        positions = Hash216Genome.positions(
            canonical_bytes(body),
            sequence=len(history),
        )
        vector = Hash216Genome.root(positions)
        identity = sha256(
            b"HHS-P163-MEMRISTOR-V1\0"
            + canonical_bytes(body)
            + bytes.fromhex(vector)
        ).hexdigest()
        return MemristorEdge(
            identity=identity,
            hash216_vector=vector,
            **body,
        )

    def admit(
        self,
        edge: MemristorEdge,
        token: object,
        authority_token: object,
    ) -> MemristorEdge:
        if token is not authority_token:
            raise VMRCError("VMRC_PEER_DIRECT_COMMIT_DENIED")
        self._edges[edge.identity] = edge
        return edge


@dataclass(frozen=True)
class ContinuationKey:
    runtime_version: str
    abi_version: int
    input_root: str
    operation_root: str
    parameter_root: str
    dependency_root: str
    capability_scope: str
    output_root: str


@dataclass
class ContinuationEntry:
    key: ContinuationKey
    output_snapshot: bytes
    state: str = "VALIDATED_REUSABLE"
    reuse_count: int = 0


class ContinuationCache:
    def __init__(self) -> None:
        self._entries: dict[ContinuationKey, ContinuationEntry] = {}

    def insert(
        self,
        key: ContinuationKey,
        output_snapshot: bytes,
    ) -> ContinuationEntry:
        if len(output_snapshot) != SNAPSHOT_BYTES:
            raise VMRCError("VMRC_INCORRECT_EXPANDED_LENGTH")
        entry = ContinuationEntry(
            key=key,
            output_snapshot=bytes(output_snapshot),
        )
        self._entries[key] = entry
        return entry

    def lookup(self, key: ContinuationKey) -> ContinuationEntry:
        entry = self._entries.get(key)
        if entry is None or entry.state != "VALIDATED_REUSABLE":
            raise VMRCError("VMRC_CACHE_MISS")
        entry.reuse_count += 1
        return entry

    def invalidate(self, key: ContinuationKey) -> None:
        try:
            self._entries[key].state = "STALE"
        except KeyError as exc:
            raise VMRCError("VMRC_CACHE_MISS") from exc

    def evict(self, key: ContinuationKey) -> None:
        try:
            entry = self._entries[key]
        except KeyError as exc:
            raise VMRCError("VMRC_CACHE_MISS") from exc
        if entry.state not in ("STALE", "EVICTABLE"):
            raise VMRCError("VMRC_CACHE_ENTRY_NOT_EVICTABLE")
        entry.state = "EVICTED"
        entry.output_snapshot = b""


@dataclass(frozen=True)
class CandidateTransition:
    candidate_id: str
    epoch: int
    thread: int
    operation: str
    writes: tuple[tuple[int, int], ...]
    expected_input_hash72: str
    expected_output_hash72: str | None
    dependency_root: str
    capability_scope: str
    parameter_root: str
    phase_gear_root: str
    source_architecture: str
    target_architecture: str


@dataclass(frozen=True)
class ValidatedTransition:
    candidate: CandidateTransition
    output_snapshot: bytes
    output_hash72: str
    operation_hash216: str
    operation_positions_hash216: tuple[str, ...]
    propagated_writes: tuple[tuple[int, int, int], ...]


class _PermanentIndex:
    def __init__(self, token: object, authority_token: object) -> None:
        if token is not authority_token:
            raise VMRCError("VMRC_SECOND_PERMANENT_INDEX_DENIED")
        self._records: list[dict[str, Any]] = []
        self._head = ZERO_HASH216

    @property
    def head(self) -> str:
        return self._head

    def append(
        self,
        record: Mapping[str, Any],
        token: object,
        authority_token: object,
    ) -> dict[str, Any]:
        if token is not authority_token:
            raise VMRCError("VMRC_INDEX_ADMISSION_DENIED")
        body = {
            "sequence": len(self._records),
            "previous_head": self._head,
            **dict(record),
        }
        positions = Hash216Genome.positions(
            canonical_bytes(body),
            previous_root=self._head,
            sequence=len(self._records),
        )
        head = Hash216Genome.root(positions)
        sealed = {
            **body,
            "index_positions_hash216": list(positions),
            "index_head_hash216": head,
        }
        self._records.append(sealed)
        self._head = head
        return json.loads(canonical_bytes(sealed))

    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            json.loads(canonical_bytes(item))
            for item in self._records
        )


class _Kernel:
    def __init__(self, token: object, authority_token: object) -> None:
        if token is not authority_token:
            raise VMRCError("VMRC_SECOND_RUNTIME_AUTHORITY_DENIED")


class VMRCRuntime:
    RUNTIME_VERSION = "HHS-P163-VMRC-1.0.0"

    def __init__(self) -> None:
        self.__authority_token = object()
        self._kernel = _Kernel(
            self.__authority_token,
            self.__authority_token,
        )
        self._index = _PermanentIndex(
            self.__authority_token,
            self.__authority_token,
        )
        self._snapshot = VMRCSnapshot()
        self._parameters = ParameterRegistry()
        self._gears = PhaseGearGraph()
        self._memristors = MemristorStore()
        self._cache = ContinuationCache()
        self._epoch = 0
        self._last_operation_root = ZERO_HASH216
        self._validated: dict[str, ValidatedTransition] = {}
        self._journal: list[dict[str, Any]] = []
        self._lock = RLock()
        self._record_journal(
            "GENESIS",
            {
                "snapshot_b64": self._snapshot.base64(),
                "state_hash72": self.state_hash72,
            },
        )

    @property
    def snapshot_hash72(self) -> str:
        return hash72_digest(b"", self._snapshot.to_bytes())

    @property
    def state_hash72(self) -> str:
        return hash72_digest(
            self._parameters.canonical(),
            self._snapshot.to_bytes(),
        )

    @property
    def epoch(self) -> int:
        return self._epoch

    def status(self) -> dict[str, Any]:
        return {
            "classification": "HHS_PASS_163_LOW_LEVEL_VIRTUAL_MEMRISTOR_RAM_CACHE_IMPLEMENTED",
            "runtime_version": self.RUNTIME_VERSION,
            "abi_version": ABI_VERSION,
            "threads": THREADS,
            "vm81_positions": VM81_POSITIONS,
            "authority_positions": PORT_POSITIONS,
            "parameter_positions": PARAMETER_POSITIONS,
            "coordinates": COORDINATES,
            "snapshot_bytes": SNAPSHOT_BYTES,
            "base64_symbols": BASE64_SYMBOLS,
            "kernel_authorities": 1,
            "permanent_indexes": 1,
            "epoch": self._epoch,
            "snapshot_hash72": self.snapshot_hash72,
            "state_hash72": self.state_hash72,
            "parameter_root": self._parameters.root(),
            "phase_gear_root": self._gears.root(),
            "index_head_hash216": self._index.head,
            "mutation_authority": True,
            "peer_mutation_authority": False,
        }

    def snapshot(self) -> VMRCSnapshot:
        return self._snapshot.copy()

    def _record_journal(
        self,
        event: str,
        body: Mapping[str, Any],
    ) -> dict[str, Any]:
        previous = (
            self._journal[-1]["journal_hash"]
            if self._journal
            else ZERO_HASH216
        )
        record = {
            "sequence": len(self._journal),
            "event": event,
            "previous_hash": previous,
            **dict(body),
        }
        record_hash = sha256(
            b"HHS-P163-JOURNAL-V1\0" + canonical_bytes(record)
        ).hexdigest()
        sealed = {**record, "journal_hash": record_hash}
        self._journal.append(sealed)
        return sealed

    def _receipt(
        self,
        schema: str,
        body: Mapping[str, Any],
        *,
        snapshot: bytes | None = None,
    ) -> dict[str, Any]:
        payload = {
            "schema": schema,
            "version": 1,
            "runtime_epoch": self._epoch,
            **dict(body),
        }
        receipt_hash72 = hash72_digest(
            payload,
            self._snapshot.to_bytes() if snapshot is None else snapshot,
        )
        return {**payload, "receipt_hash72": receipt_hash72}

    def register_parameter(self, **kwargs: Any) -> dict[str, Any]:
        with self._lock:
            before_count = len(self._parameters)
            before_root = self.state_hash72
            obj = self._parameters.register(**kwargs)
            reused = len(self._parameters) == before_count
            after_root = self.state_hash72
            journal = None
            if not reused:
                journal = self._record_journal(
                    "PARAMETER_REGISTER",
                    {
                        "parameter": asdict(obj),
                        "input_hash72": before_root,
                        "output_hash72": after_root,
                    },
                )
            return {
                "parameter": asdict(obj),
                "receipt": self._receipt(
                    "P163_PARAMETER_REGISTER_RECEIPT",
                    {
                        "parameter_id": obj.identity,
                        "reused": reused,
                        "input_hash72": before_root,
                        "output_hash72": after_root,
                        "journal_hash": (
                            journal["journal_hash"]
                            if journal
                            else None
                        ),
                    },
                ),
            }

    def register_gear(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        with self._lock:
            gear = self._gears.register(*args, **kwargs)
            journal = self._record_journal(
                "GEAR_REGISTER",
                {"gear": asdict(gear)},
            )
            return {
                "gear": asdict(gear),
                "receipt": self._receipt(
                    "P163_GEAR_REGISTER_RECEIPT",
                    {
                        "gear_id": gear.identity,
                        "phase_gear_root": self._gears.root(),
                        "journal_hash": journal["journal_hash"],
                    },
                ),
            }

    def propose_memristor(self, *args: Any, **kwargs: Any) -> MemristorEdge:
        return self._memristors.propose(*args, **kwargs)

    def admit_memristor(self, edge: MemristorEdge) -> dict[str, Any]:
        with self._lock:
            admitted = self._memristors.admit(
                edge,
                self.__authority_token,
                self.__authority_token,
            )
            journal = self._record_journal(
                "MEMRISTOR_ADMIT",
                {"edge": asdict(admitted)},
            )
            index = self._index.append(
                {
                    "record_class": "MEMRISTOR_EDGE",
                    "memristor_edge_id": admitted.identity,
                    "state_hash72": self.state_hash72,
                    "hash216_operation_identity": admitted.hash216_vector,
                },
                self.__authority_token,
                self.__authority_token,
            )
            return {
                "edge": asdict(admitted),
                "index": index,
                "receipt": self._receipt(
                    "P163_MEMRISTOR_PROPOSAL_RECEIPT",
                    {
                        "edge_id": admitted.identity,
                        "journal_hash": journal["journal_hash"],
                    },
                ),
            }

    def submit_candidate(
        self,
        *,
        thread: int,
        writes: Mapping[int, int],
        operation: str,
        expected_input_hash72: str,
        expected_output_hash72: str | None = None,
        dependency_root: str = ZERO_HASH216,
        capability_scope: str = "VMRC_STATE_WRITE",
        source_architecture: str = "REFERENCE_CPU",
        target_architecture: str = "VM81",
    ) -> CandidateTransition:
        _require_int("thread", thread, 0, THREADS - 1)
        if not operation or operation not in OPERATION_CLASSES:
            raise VMRCError("VMRC_UNSUPPORTED_OPERATION")
        if not validate_hash72(expected_input_hash72):
            raise VMRCError("VMRC_INVALID_INPUT_HASH72")
        if (
            expected_output_hash72 is not None
            and not validate_hash72(expected_output_hash72)
        ):
            raise VMRCError("VMRC_INVALID_EXPECTED_HASH72")
        if not capability_scope:
            raise VMRCError("VMRC_CAPABILITY_ZERO")
        normalized: list[tuple[int, int]] = []
        for position, trit in writes.items():
            _require_int("position", position, 0, VM81_POSITIONS - 1)
            if trit not in (-1, 0, 1):
                raise VMRCError("VMRC_INVALID_OPERATIONAL_TRIT")
            normalized.append((position, trit))
        normalized.sort()
        body = {
            "epoch": self._epoch,
            "thread": thread,
            "operation": operation,
            "writes": tuple(normalized),
            "expected_input_hash72": expected_input_hash72,
            "expected_output_hash72": expected_output_hash72,
            "dependency_root": dependency_root,
            "capability_scope": capability_scope,
            "parameter_root": self._parameters.root(),
            "phase_gear_root": self._gears.root(),
            "source_architecture": source_architecture,
            "target_architecture": target_architecture,
        }
        candidate_id = sha256(
            b"HHS-P163-CANDIDATE-V1\0" + canonical_bytes(body)
        ).hexdigest()
        return CandidateTransition(candidate_id=candidate_id, **body)

    def submit_coordinate_candidate(
        self,
        *,
        thread: int,
        writes: Mapping[tuple[int, int], int],
        **kwargs: Any,
    ) -> CandidateTransition:
        local: dict[int, int] = {}
        for (position, target_thread), trit in writes.items():
            if target_thread != thread:
                raise VMRCError("VMRC_FOREIGN_LANE_MUTATION_DENIED")
            local[position] = trit
        return self.submit_candidate(
            thread=thread,
            writes=local,
            **kwargs,
        )

    def validate(self, candidate: CandidateTransition) -> dict[str, Any]:
        with self._lock:
            if candidate.epoch != self._epoch:
                raise VMRCError("VMRC_STALE_EPOCH")
            if not hmac.compare_digest(
                candidate.expected_input_hash72,
                self.state_hash72,
            ):
                raise VMRCError("VMRC_STALE_ROOT")
            if candidate.parameter_root != self._parameters.root():
                raise VMRCError("VMRC_PARAMETER_ROOT_MISMATCH")
            if candidate.phase_gear_root != self._gears.root():
                raise VMRCError("VMRC_PHASE_GEAR_ROOT_MISMATCH")
            seeds: dict[tuple[int, int], int] = {}
            for position, trit in candidate.writes:
                current = self._snapshot.get(position, candidate.thread)
                seeds[(position, candidate.thread)] = (
                    current
                    if trit == 0
                    else (1 if trit == 1 else 0)
                )
            propagated = self._gears.propagate(self._snapshot, seeds)
            output = self._snapshot.copy()
            for (position, thread), value in sorted(propagated.items()):
                output._authority_set(
                    position,
                    thread,
                    value,
                    self.__authority_token,
                    self.__authority_token,
                )
            output_root = hash72_digest(
                self._parameters.canonical(),
                output.to_bytes(),
            )
            if (
                candidate.expected_output_hash72 is not None
                and not hmac.compare_digest(
                    candidate.expected_output_hash72,
                    output_root,
                )
            ):
                raise VMRCError("VMRC_EXPECTED_OUTPUT_ROOT_MISMATCH")
            operation_body = {
                "domain": "HHS-P163-HASH216-OPERATION-V1",
                "incoming_hash72": candidate.expected_input_hash72,
                "epoch": candidate.epoch,
                "thread": candidate.thread,
                "operation": candidate.operation,
                "writes": candidate.writes,
                "parameters": candidate.parameter_root,
                "dependencies": candidate.dependency_root,
                "phase": candidate.phase_gear_root,
                "expected_output": output_root,
                "abi_version": ABI_VERSION,
                "capability": candidate.capability_scope,
                "source_architecture": candidate.source_architecture,
                "target_architecture": candidate.target_architecture,
            }
            positions = Hash216Genome.positions(
                canonical_bytes(operation_body),
                previous_root=self._last_operation_root,
                sequence=self._epoch,
            )
            operation_root = Hash216Genome.root(positions)
            validated = ValidatedTransition(
                candidate=candidate,
                output_snapshot=output.to_bytes(),
                output_hash72=output_root,
                operation_hash216=operation_root,
                operation_positions_hash216=positions,
                propagated_writes=tuple(
                    (position, thread, value)
                    for (position, thread), value in sorted(propagated.items())
                ),
            )
            self._validated[candidate.candidate_id] = validated
            return {
                "validated": {
                    "candidate": asdict(candidate),
                    "output_hash72": output_root,
                    "operation_hash216": operation_root,
                    "operation_positions_hash216": list(positions),
                    "propagated_writes": [
                        list(item)
                        for item in validated.propagated_writes
                    ],
                    "mutation_authority": False,
                    "vm81_admission": "VALIDATED_PENDING_COMMIT",
                },
                "receipt": self._receipt(
                    "P163_VALIDATION_RECEIPT",
                    {
                        "candidate_id": candidate.candidate_id,
                        "input_hash72": candidate.expected_input_hash72,
                        "output_hash72": output_root,
                        "operation_hash216": operation_root,
                        "admitted": True,
                    },
                    snapshot=output.to_bytes(),
                ),
            }

    def commit(self, candidate_id: str) -> dict[str, Any]:
        with self._lock:
            try:
                validated = self._validated.pop(candidate_id)
            except KeyError as exc:
                raise VMRCError("VMRC_VALIDATION_REQUIRED") from exc
            if (
                validated.candidate.epoch != self._epoch
                or validated.candidate.expected_input_hash72 != self.state_hash72
            ):
                raise VMRCError("VMRC_STALE_ROOT")
            input_root = self.state_hash72
            self._snapshot = VMRCSnapshot(validated.output_snapshot)
            self._epoch += 1
            self._last_operation_root = validated.operation_hash216
            if self.state_hash72 != validated.output_hash72:
                raise VMRCError("VMRC_INTERNAL_INVARIANT_FAILURE")
            journal = self._record_journal(
                "COMMIT",
                {
                    "candidate": asdict(validated.candidate),
                    "propagated_writes": validated.propagated_writes,
                    "input_hash72": input_root,
                    "output_hash72": self.state_hash72,
                    "operation_hash216": validated.operation_hash216,
                    "epoch_after": self._epoch,
                },
            )
            index = self._index.append(
                {
                    "record_class": "COMMITTED_TRANSITION",
                    "epoch": self._epoch,
                    "thread": validated.candidate.thread,
                    "hash72_snapshot_identity": self.snapshot_hash72,
                    "hash72_state_identity": self.state_hash72,
                    "hash216_operation_identity": validated.operation_hash216,
                    "parameter_root": validated.candidate.parameter_root,
                    "phase_gear_root": validated.candidate.phase_gear_root,
                    "dependency_root": validated.candidate.dependency_root,
                    "capability_scope": validated.candidate.capability_scope,
                    "architecture_backend": validated.candidate.target_architecture,
                    "continuation_eligible": True,
                    "journal_hash": journal["journal_hash"],
                },
                self.__authority_token,
                self.__authority_token,
            )
            key = ContinuationKey(
                runtime_version=self.RUNTIME_VERSION,
                abi_version=ABI_VERSION,
                input_root=input_root,
                operation_root=validated.operation_hash216,
                parameter_root=validated.candidate.parameter_root,
                dependency_root=validated.candidate.dependency_root,
                capability_scope=validated.candidate.capability_scope,
                output_root=self.state_hash72,
            )
            self._cache.insert(key, self._snapshot.to_bytes())
            return {
                "classification": "HHS_PASS_163_COMMIT_ADMITTED",
                "receipt": self._receipt(
                    "P163_COMMIT_RECEIPT",
                    {
                        "candidate_id": candidate_id,
                        "epoch": self._epoch,
                        "input_hash72": input_root,
                        "output_hash72": self.state_hash72,
                        "operation_hash216": validated.operation_hash216,
                        "index_head_hash216": index["index_head_hash216"],
                        "journal_hash": journal["journal_hash"],
                        "continuation_key": asdict(key),
                    },
                ),
                "index_record": index,
                "continuation_key": asdict(key),
            }

    def execute(self, candidate: CandidateTransition) -> dict[str, Any]:
        validation = self.validate(candidate)
        commit = self.commit(candidate.candidate_id)
        return {"validation": validation, "commit": commit}

    def cache_lookup(self, key: Mapping[str, Any]) -> dict[str, Any]:
        canonical_key = ContinuationKey(**key)
        entry = self._cache.lookup(canonical_key)
        return {
            "classification": "VMRC_CACHE_REUSE",
            "state": entry.state,
            "reuse_count": entry.reuse_count,
            "output_b64": b64encode(entry.output_snapshot).decode("ascii"),
        }

    def cache_invalidate(self, key: Mapping[str, Any]) -> None:
        self._cache.invalidate(ContinuationKey(**key))

    def base64_envelope(self, payload: Any, **metadata: Any) -> str:
        raw_payload = canonical_bytes(payload)
        if len(raw_payload) > MAX_ENVELOPE_BYTES:
            raise VMRCError("VMRC_RESOURCE_BOUND", "payload")
        required = {
            "operation_class",
            "source_architecture",
            "target_architecture",
            "runtime_epoch",
            "incoming_hash72",
            "thread_mask",
            "port_mask",
            "read_set_root",
            "write_set_root",
            "dependency_root",
            "parameter_root",
            "phase_gear_graph_root",
            "expected_expanded_state_root",
            "receipt_nonce",
        }
        missing = sorted(required - metadata.keys())
        if missing:
            raise VMRCError(
                "VMRC_ENVELOPE_FIELD_REQUIRED",
                ",".join(missing),
            )
        if metadata["operation_class"] not in OPERATION_CLASSES:
            raise VMRCError("VMRC_UNSUPPORTED_OPERATION")
        body = {
            "magic": MAGIC,
            "version": ABI_VERSION,
            **metadata,
            "payload_encoding": "BASE64_CANONICAL_JSON",
            "payload_length": len(raw_payload),
            "payload_b64": b64encode(raw_payload).decode("ascii"),
        }
        positions = Hash216Genome.positions(
            canonical_bytes(body),
            sequence=int(metadata["runtime_epoch"]),
        )
        body["hash216_operation_identity"] = Hash216Genome.root(positions)
        integrity = sha256(
            b"HHS-P163-ABI-ENVELOPE-V1\0" + canonical_bytes(body)
        ).hexdigest()
        return b64encode(
            canonical_bytes({**body, "integrity_sha256": integrity})
        ).decode("ascii")

    def decode_envelope(self, encoded: str) -> dict[str, Any]:
        if not isinstance(encoded, str) or len(encoded) > MAX_ENVELOPE_BYTES * 4:
            raise VMRCError("VMRC_RESOURCE_BOUND", "envelope")
        try:
            raw = b64decode(encoded, validate=True)
            if b64encode(raw).decode("ascii") != encoded:
                raise VMRCError("VMRC_NONCANONICAL_BASE64")
            envelope = json.loads(raw)
        except VMRCError:
            raise
        except Exception as exc:
            raise VMRCError("VMRC_MALFORMED_BASE64") from exc
        if canonical_bytes(envelope) != raw:
            raise VMRCError("VMRC_NONCANONICAL_ENVELOPE")
        if envelope.get("magic") != MAGIC or envelope.get("version") != ABI_VERSION:
            raise VMRCError("VMRC_UNSUPPORTED_VERSION")
        integrity = envelope.pop("integrity_sha256", None)
        expected_integrity = sha256(
            b"HHS-P163-ABI-ENVELOPE-V1\0" + canonical_bytes(envelope)
        ).hexdigest()
        if not isinstance(integrity, str) or not hmac.compare_digest(
            integrity,
            expected_integrity,
        ):
            raise VMRCError("VMRC_HASH_MISMATCH")
        payload_b64 = envelope.get("payload_b64")
        try:
            payload_raw = b64decode(payload_b64, validate=True)
        except Exception as exc:
            raise VMRCError("VMRC_MALFORMED_BASE64") from exc
        if len(payload_raw) != envelope.get("payload_length"):
            raise VMRCError("VMRC_INCORRECT_EXPANDED_LENGTH")
        if b64encode(payload_raw).decode("ascii") != payload_b64:
            raise VMRCError("VMRC_NONCANONICAL_BASE64")
        operation_identity = envelope.pop("hash216_operation_identity")
        positions = Hash216Genome.positions(
            canonical_bytes(envelope),
            sequence=int(envelope["runtime_epoch"]),
        )
        if operation_identity != Hash216Genome.root(positions):
            raise VMRCError("VMRC_HASH_MISMATCH")
        envelope["hash216_operation_identity"] = operation_identity
        envelope["integrity_sha256"] = integrity
        envelope["payload"] = json.loads(payload_raw)
        return envelope

    def replay(self) -> dict[str, Any]:
        registry = ParameterRegistry()
        snapshot = VMRCSnapshot()
        prior_hash = ZERO_HASH216
        epoch = 0
        for sequence, raw in enumerate(self._journal):
            record = dict(raw)
            supplied = record.pop("journal_hash")
            if (
                record.get("sequence") != sequence
                or record.get("previous_hash") != prior_hash
            ):
                raise VMRCError("VMRC_INCOMPLETE_COMMIT_JOURNAL")
            expected = sha256(
                b"HHS-P163-JOURNAL-V1\0" + canonical_bytes(record)
            ).hexdigest()
            if supplied != expected:
                raise VMRCError("VMRC_REPLAY_MISMATCH")
            event = record["event"]
            if event == "GENESIS":
                if record["snapshot_b64"] != snapshot.base64():
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
            elif event == "PARAMETER_REGISTER":
                before = hash72_digest(
                    registry.canonical(),
                    snapshot.to_bytes(),
                )
                if before != record["input_hash72"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
                registry.restore(record["parameter"])
                after = hash72_digest(
                    registry.canonical(),
                    snapshot.to_bytes(),
                )
                if after != record["output_hash72"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
            elif event == "COMMIT":
                current = hash72_digest(
                    registry.canonical(),
                    snapshot.to_bytes(),
                )
                if current != record["input_hash72"]:
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
                for position, thread, value in record["propagated_writes"]:
                    snapshot._set_index(
                        VMRCSnapshot.coordinate_index(position, thread),
                        value,
                    )
                epoch += 1
                output = hash72_digest(
                    registry.canonical(),
                    snapshot.to_bytes(),
                )
                if (
                    output != record["output_hash72"]
                    or epoch != record["epoch_after"]
                ):
                    raise VMRCError("VMRC_REPLAY_MISMATCH")
            elif event in ("GEAR_REGISTER", "MEMRISTOR_ADMIT"):
                pass
            else:
                raise VMRCError("VMRC_REPLAY_MISMATCH", event)
            prior_hash = supplied
        final = hash72_digest(
            registry.canonical(),
            snapshot.to_bytes(),
        )
        if (
            final != self.state_hash72
            or snapshot.to_bytes() != self._snapshot.to_bytes()
            or epoch != self._epoch
        ):
            raise VMRCError("VMRC_REPLAY_MISMATCH")
        return {
            "classification": "P163_REPLAY_RECEIPT",
            "records": len(self._journal),
            "epoch": epoch,
            "state_hash72": final,
            "journal_head": prior_hash,
            "deterministic_replay": True,
        }

    def journal(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            json.loads(canonical_bytes(item))
            for item in self._journal
        )

    def index_records(self) -> tuple[dict[str, Any], ...]:
        return self._index.records()
