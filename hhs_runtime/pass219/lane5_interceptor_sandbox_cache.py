"""Lane 5 sandboxed bypass queue and exact 5184-bit execution cache.

The cache is a candidate-only optimization surface.  Its payload unit is the
repository's exact VM81 carrier: 5,184 serial bits == 648 little-endian bytes.

Capacity is hardware-calibrated from an explicit linear-workset benchmark
receipt.  Without such a receipt the implementation may use the already-proven
65,536-record saturation-v3 workset only as a development floor; that state is
not production calibration acceptance.

All direct/bypass traffic is queued.  Reordering is deterministic and preserves
FIFO order within a state-affecting dependency chain.  Cache/replay-compatible
heads are preferred over fresh work across independent chains.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
from threading import RLock
from typing import Any, Mapping

SCHEMA = "HHS_PASS219_LANE5_INTERCEPTOR_SANDBOX_CACHE_V1"
CALIBRATION_SCHEMA = "HHS_PASS219_LANE5_INTERCEPTOR_CACHE_CALIBRATION_V1"
QUEUE_RECEIPT_SCHEMA = "HHS_PASS219_LANE5_INTERCEPTOR_QUEUE_RECEIPT_V1"
CACHE_RECEIPT_SCHEMA = "HHS_PASS219_LANE5_INTERCEPTOR_CACHE_RECEIPT_V1"

SERIAL_BITS = 5184
RECORD_BYTES = 648
VM81_WORDS = 81
WORD_BITS = 64
BYTE_ORDER = "LITTLE_ENDIAN"
BIT_ORDER = "LSB0_PER_UINT64_CELL"

VERIFIED_FLOOR_RECORDS = 65_536
VERIFIED_FLOOR_BYTES = VERIFIED_FLOOR_RECORDS * RECORD_BYTES
DEFAULT_CALIBRATION_ENV = "HHS_PASS219_LANE5_INTERCEPT_CACHE_CALIBRATION"

MEASURED_MAXIMUM = "MEASURED_MAXIMUM"
VERIFIED_WORKSET_FLOOR = "VERIFIED_WORKSET_FLOOR"


class Lane5SandboxCacheError(RuntimeError):
    pass


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize(item)
            for key, item in sorted(value.items(), key=lambda kv: str(kv[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, (bytes, bytearray, memoryview)):
        raw = bytes(value)
        return {
            "__exact_bytes__": True,
            "length": len(raw),
            "sha256": sha256(raw).hexdigest(),
        }
    if isinstance(value, Path):
        return str(value)
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _digest(label: str, value: Any) -> str:
    return sha256(label.encode("ascii") + b"\0" + _canonical_bytes(value)).hexdigest()


def _local_environment_id() -> dict[str, Any]:
    uname = platform.uname()
    return {
        "system": uname.system,
        "release": uname.release,
        "machine": uname.machine,
        "processor": uname.processor,
        "logical_cpu_count": os.cpu_count() or 1,
    }


@dataclass(frozen=True)
class Lane5CacheCalibration:
    schema: str
    classification: str
    serial_bits: int
    record_bytes: int
    vm81_words: int
    word_bits: int
    byte_order: str
    bit_order: str
    max_records: int
    max_bytes: int
    benchmark_window_ns: int
    benchmark_id: str
    environment: dict[str, Any]
    evidence_sha256: str
    production_accepted: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def verified_floor() -> "Lane5CacheCalibration":
        body = {
            "classification": VERIFIED_WORKSET_FLOOR,
            "serial_bits": SERIAL_BITS,
            "record_bytes": RECORD_BYTES,
            "vm81_words": VM81_WORDS,
            "word_bits": WORD_BITS,
            "byte_order": BYTE_ORDER,
            "bit_order": BIT_ORDER,
            "max_records": VERIFIED_FLOOR_RECORDS,
            "max_bytes": VERIFIED_FLOOR_BYTES,
            "benchmark_window_ns": 0,
            "benchmark_id": "SATURATION_V3_WORKSET_FLOOR_65536x648",
            "environment": _local_environment_id(),
            "production_accepted": False,
        }
        return Lane5CacheCalibration(
            schema=CALIBRATION_SCHEMA,
            evidence_sha256=_digest("LANE5_CACHE_FLOOR", body),
            **body,
        )

    @staticmethod
    def from_evidence(evidence: Mapping[str, Any]) -> "Lane5CacheCalibration":
        if evidence.get("schema") != CALIBRATION_SCHEMA:
            raise Lane5SandboxCacheError("LANE5_CACHE_CALIBRATION_SCHEMA_INVALID")
        if evidence.get("classification") != MEASURED_MAXIMUM:
            raise Lane5SandboxCacheError(
                "LANE5_CACHE_CALIBRATION_MEASURED_MAXIMUM_REQUIRED"
            )
        required_exact = {
            "serial_bits": SERIAL_BITS,
            "record_bytes": RECORD_BYTES,
            "vm81_words": VM81_WORDS,
            "word_bits": WORD_BITS,
            "byte_order": BYTE_ORDER,
            "bit_order": BIT_ORDER,
        }
        for key, expected in required_exact.items():
            if evidence.get(key) != expected:
                raise Lane5SandboxCacheError(
                    f"LANE5_CACHE_CALIBRATION_CARRIER_DRIFT:{key}"
                )
        records = evidence.get("max_records")
        maximum_bytes = evidence.get("max_bytes")
        window_ns = evidence.get("benchmark_window_ns")
        if isinstance(records, bool) or not isinstance(records, int) or records <= 0:
            raise Lane5SandboxCacheError("LANE5_CACHE_CALIBRATION_RECORDS_INVALID")
        if maximum_bytes != records * RECORD_BYTES:
            raise Lane5SandboxCacheError("LANE5_CACHE_CALIBRATION_BYTES_DRIFT")
        if isinstance(window_ns, bool) or not isinstance(window_ns, int) or window_ns <= 0:
            raise Lane5SandboxCacheError("LANE5_CACHE_CALIBRATION_WINDOW_INVALID")
        environment = dict(evidence.get("environment") or {})
        if not environment:
            raise Lane5SandboxCacheError(
                "LANE5_CACHE_CALIBRATION_ENVIRONMENT_REQUIRED"
            )
        benchmark_id = str(evidence.get("benchmark_id") or "")
        if not benchmark_id:
            raise Lane5SandboxCacheError(
                "LANE5_CACHE_CALIBRATION_BENCHMARK_ID_REQUIRED"
            )
        receipt_body = {
            "classification": MEASURED_MAXIMUM,
            **required_exact,
            "max_records": records,
            "max_bytes": maximum_bytes,
            "benchmark_window_ns": window_ns,
            "benchmark_id": benchmark_id,
            "environment": environment,
            "production_accepted": True,
        }
        declared = str(evidence.get("evidence_sha256") or "")
        computed = _digest("LANE5_CACHE_CALIBRATION", receipt_body)
        if declared and declared != computed:
            raise Lane5SandboxCacheError(
                "LANE5_CACHE_CALIBRATION_EVIDENCE_DIGEST_DRIFT"
            )
        return Lane5CacheCalibration(
            schema=CALIBRATION_SCHEMA,
            evidence_sha256=computed,
            **receipt_body,
        )


def load_calibration(path: str | Path | None = None) -> Lane5CacheCalibration:
    selected = path or os.getenv(DEFAULT_CALIBRATION_ENV)
    if not selected:
        return Lane5CacheCalibration.verified_floor()
    source = Path(selected).expanduser().resolve()
    if not source.is_file():
        raise Lane5SandboxCacheError(
            f"LANE5_CACHE_CALIBRATION_FILE_REQUIRED:{source}"
        )
    data = json.loads(source.read_text(encoding="utf-8"))
    return Lane5CacheCalibration.from_evidence(data)


@dataclass(frozen=True)
class _QueueItem:
    sequence: int
    ticket: str
    traffic_class: str
    operation: str
    read_only: bool
    state_affecting: bool
    dependency_root: str
    request_digest: str
    cache_key: str
    cache_hit: bool
    reusable_hint: bool
    frame_present: bool
    payload: dict[str, Any]


@dataclass
class _CacheEntry:
    key: str
    frame_le: bytes
    candidate_result: dict[str, Any]
    source_ticket: str
    hit_count: int = 0


class Lane5InterceptorSandboxCache:
    """Thread-safe candidate queue/cache owned by the Lane 5 interceptor."""

    def __init__(
        self,
        *,
        calibration: Lane5CacheCalibration | None = None,
    ) -> None:
        self.calibration = calibration or load_calibration()
        self._queue: list[_QueueItem] = []
        self._cache: "OrderedDict[str, _CacheEntry]" = OrderedDict()
        self._processed: dict[str, dict[str, Any]] = {}
        self._sequence = 0
        self._resident_payload_bytes = 0
        self._lock = RLock()

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "schema": SCHEMA,
                "calibration": self.calibration.to_dict(),
                "queued": len(self._queue),
                "processed_receipts": len(self._processed),
                "cache_entries": len(self._cache),
                "resident_payload_bytes": self._resident_payload_bytes,
                "capacity_records": self.calibration.max_records,
                "capacity_bytes": self.calibration.max_bytes,
                "production_calibrated": self.calibration.production_accepted,
                "candidate_only": True,
                "canonical_vm81_mutation_authority": False,
                "canonical_hash72_authority": False,
                "canonical_hash216_authority": False,
                "canonical_persistence_authority": False,
                "pqc_key_authority": False,
                "floating_point_canonical_authority": False,
            }

    @staticmethod
    def _frame_from_payload(payload: Mapping[str, Any]) -> bytes | None:
        for key in ("raw_frame_le", "frame_le", "output_snapshot"):
            value = payload.get(key)
            if isinstance(value, (bytes, bytearray, memoryview)):
                raw = bytes(value)
                if len(raw) != RECORD_BYTES:
                    raise Lane5SandboxCacheError(
                        f"LANE5_CACHE_FRAME_MUST_BE_{RECORD_BYTES}_BYTES:{key}"
                    )
                return raw
        return None

    @staticmethod
    def _dependency_root(
        *,
        payload: Mapping[str, Any],
        read_only: bool,
        ticket_seed: str,
    ) -> str:
        if read_only:
            return "READ_ONLY:" + ticket_seed
        for key in (
            "dependency_root",
            "expected_input_hash72",
            "parent_hash216",
            "previous_hash216",
            "state_hash72",
        ):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return f"{key}:{value}"
        # Unknown stateful traffic is serialized as one dependency chain rather
        # than reordered speculatively.
        return "GLOBAL_STATE_AFFECTING_CHAIN"

    def enqueue(
        self,
        *,
        traffic_class: str,
        operation: str,
        payload: Mapping[str, Any] | None,
        read_only: bool,
    ) -> dict[str, Any]:
        payload_dict = dict(payload or {})
        request_body = {
            "traffic_class": traffic_class,
            "operation": operation,
            "payload": payload_dict,
            "read_only": bool(read_only),
        }
        request_digest = _digest("LANE5_QUEUE_REQUEST", request_body)
        frame = self._frame_from_payload(payload_dict)
        cache_key = (
            sha256(frame).hexdigest()
            if frame is not None
            else _digest("LANE5_QUEUE_CACHE_KEY", request_body)
        )
        reusable_hint = bool(
            payload_dict.get("replay_compatible")
            or payload_dict.get("cache_reusable")
            or payload_dict.get("composition_reusable")
            or payload_dict.get("hash216_cache_hit")
        )
        with self._lock:
            self._sequence += 1
            sequence = self._sequence
            ticket = _digest(
                "LANE5_QUEUE_TICKET",
                {
                    "sequence": sequence,
                    "request_digest": request_digest,
                    "traffic_class": traffic_class,
                    "operation": operation,
                },
            )
            dependency_root = self._dependency_root(
                payload=payload_dict,
                read_only=bool(read_only),
                ticket_seed=ticket,
            )
            cache_hit = cache_key in self._cache
            item = _QueueItem(
                sequence=sequence,
                ticket=ticket,
                traffic_class=traffic_class,
                operation=operation,
                read_only=bool(read_only),
                state_affecting=not bool(read_only),
                dependency_root=dependency_root,
                request_digest=request_digest,
                cache_key=cache_key,
                cache_hit=cache_hit,
                reusable_hint=reusable_hint,
                frame_present=frame is not None,
                payload=_normalize(payload_dict),
            )
            self._queue.append(item)
            return {
                "schema": QUEUE_RECEIPT_SCHEMA,
                "ticket": ticket,
                "sequence": sequence,
                "queued": True,
                "dependency_root": dependency_root,
                "cache_hit_at_enqueue": cache_hit,
                "reusable_hint": reusable_hint,
                "serial_bits": SERIAL_BITS,
                "record_bytes": RECORD_BYTES,
                "byte_order": BYTE_ORDER,
                "calibration_classification": self.calibration.classification,
                "capacity_records": self.calibration.max_records,
                "capacity_bytes": self.calibration.max_bytes,
                "production_calibrated": self.calibration.production_accepted,
            }

    def _eligible_heads(self) -> list[_QueueItem]:
        heads: dict[str, _QueueItem] = {}
        for item in sorted(self._queue, key=lambda row: row.sequence):
            heads.setdefault(item.dependency_root, item)
        return list(heads.values())

    @staticmethod
    def _priority(item: _QueueItem) -> tuple[int, int, int, int]:
        # Lower tuple wins.  Reuse/cached candidates are the first optimization
        # objective across independent chains.  Read-only observation may run
        # ahead of independent stateful work but never ahead inside one chain.
        return (
            0 if item.cache_hit else 1,
            0 if item.reusable_hint else 1,
            0 if item.read_only else 1,
            item.sequence,
        )

    def optimize_next(self) -> dict[str, Any]:
        with self._lock:
            if not self._queue:
                raise Lane5SandboxCacheError("LANE5_QUEUE_EMPTY")
            eligible = self._eligible_heads()
            selected = min(eligible, key=self._priority)
            oldest_sequence = min(item.sequence for item in self._queue)
            reordered = selected.sequence != oldest_sequence
            self._queue = [
                item for item in self._queue if item.ticket != selected.ticket
            ]
            cache_entry = self._cache.get(selected.cache_key)
            if cache_entry is not None:
                cache_entry.hit_count += 1
                self._cache.move_to_end(selected.cache_key)
            receipt_body = {
                "schema": QUEUE_RECEIPT_SCHEMA,
                "ticket": selected.ticket,
                "sequence": selected.sequence,
                "traffic_class": selected.traffic_class,
                "operation": selected.operation,
                "dependency_root": selected.dependency_root,
                "lane5_queue_optimized": True,
                "lane5_reordered": reordered,
                "cache_hit": cache_entry is not None,
                "reusable_hint": selected.reusable_hint,
                "priority_vector": list(self._priority(selected)),
                "request_digest": selected.request_digest,
                "cache_key": selected.cache_key,
                "frame_present": selected.frame_present,
                "candidate_only": True,
                "requires_rna_cpp_cell_wall": selected.state_affecting,
                "requires_signed_pqc_admission": selected.state_affecting,
                "canonical_mutation_authority": False,
                "direct_fallback_allowed": False,
            }
            receipt_body["queue_receipt_sha256"] = _digest(
                "LANE5_QUEUE_OPTIMIZATION_RECEIPT", receipt_body
            )
            self._processed[selected.ticket] = receipt_body
            return dict(receipt_body)

    def optimize_until(self, ticket: str) -> dict[str, Any]:
        while True:
            with self._lock:
                existing = self._processed.get(ticket)
                if existing is not None:
                    return dict(existing)
                if not any(item.ticket == ticket for item in self._queue):
                    raise Lane5SandboxCacheError(
                        "LANE5_QUEUE_TICKET_NOT_FOUND:" + ticket
                    )
            self.optimize_next()

    def get_cached_candidate(self, cache_key: str) -> dict[str, Any] | None:
        with self._lock:
            entry = self._cache.get(cache_key)
            if entry is None:
                return None
            entry.hit_count += 1
            self._cache.move_to_end(cache_key)
            return {
                "schema": CACHE_RECEIPT_SCHEMA,
                "cache_key": cache_key,
                "frame_le": bytes(entry.frame_le),
                "candidate_result": dict(entry.candidate_result),
                "source_ticket": entry.source_ticket,
                "hit_count": entry.hit_count,
                "candidate_only": True,
                "canonical_mutation_authority": False,
            }

    def store_candidate(
        self,
        *,
        cache_key: str,
        frame_le: bytes | bytearray | memoryview,
        candidate_result: Mapping[str, Any],
        source_ticket: str,
    ) -> dict[str, Any]:
        raw = bytes(frame_le)
        if len(raw) != RECORD_BYTES:
            raise Lane5SandboxCacheError(
                f"LANE5_CACHE_FRAME_MUST_BE_{RECORD_BYTES}_BYTES"
            )
        result = dict(candidate_result)
        if result.get("candidate_only") is not True:
            raise Lane5SandboxCacheError("LANE5_CACHE_CANDIDATE_ONLY_REQUIRED")
        for key in (
            "canonical_mutation_authority",
            "canonical_vm81_mutation_authority",
            "canonical_hash72_authority",
            "canonical_hash216_authority",
            "canonical_persistence_authority",
        ):
            if result.get(key, False) is not False:
                raise Lane5SandboxCacheError(
                    f"LANE5_CACHE_AUTHORITY_ESCALATION:{key}"
                )
        with self._lock:
            prior = self._cache.pop(cache_key, None)
            if prior is not None:
                self._resident_payload_bytes -= RECORD_BYTES
            while (
                self._cache
                and (
                    len(self._cache) >= self.calibration.max_records
                    or self._resident_payload_bytes + RECORD_BYTES
                    > self.calibration.max_bytes
                )
            ):
                _, evicted = self._cache.popitem(last=False)
                self._resident_payload_bytes -= len(evicted.frame_le)
            if self.calibration.max_records < 1 or self.calibration.max_bytes < RECORD_BYTES:
                raise Lane5SandboxCacheError("LANE5_CACHE_CALIBRATION_TOO_SMALL")
            self._cache[cache_key] = _CacheEntry(
                key=cache_key,
                frame_le=raw,
                candidate_result=_normalize(result),
                source_ticket=source_ticket,
            )
            self._resident_payload_bytes += RECORD_BYTES
            return {
                "schema": CACHE_RECEIPT_SCHEMA,
                "cache_key": cache_key,
                "stored": True,
                "entry_count": len(self._cache),
                "resident_payload_bytes": self._resident_payload_bytes,
                "capacity_records": self.calibration.max_records,
                "capacity_bytes": self.calibration.max_bytes,
                "candidate_only": True,
                "canonical_mutation_authority": False,
            }


_DEFAULT_SANDBOX: Lane5InterceptorSandboxCache | None = None
_DEFAULT_LOCK = RLock()


def default_sandbox_cache() -> Lane5InterceptorSandboxCache:
    global _DEFAULT_SANDBOX
    with _DEFAULT_LOCK:
        if _DEFAULT_SANDBOX is None:
            _DEFAULT_SANDBOX = Lane5InterceptorSandboxCache()
        return _DEFAULT_SANDBOX


def reset_default_sandbox_for_tests(
    calibration: Lane5CacheCalibration | None = None,
) -> Lane5InterceptorSandboxCache:
    global _DEFAULT_SANDBOX
    with _DEFAULT_LOCK:
        _DEFAULT_SANDBOX = Lane5InterceptorSandboxCache(
            calibration=calibration or Lane5CacheCalibration.verified_floor()
        )
        return _DEFAULT_SANDBOX


__all__ = [
    "BIT_ORDER",
    "BYTE_ORDER",
    "CALIBRATION_SCHEMA",
    "DEFAULT_CALIBRATION_ENV",
    "Lane5CacheCalibration",
    "Lane5InterceptorSandboxCache",
    "Lane5SandboxCacheError",
    "MEASURED_MAXIMUM",
    "RECORD_BYTES",
    "SCHEMA",
    "SERIAL_BITS",
    "VERIFIED_FLOOR_BYTES",
    "VERIFIED_FLOOR_RECORDS",
    "VERIFIED_WORKSET_FLOOR",
    "default_sandbox_cache",
    "load_calibration",
    "reset_default_sandbox_for_tests",
]
