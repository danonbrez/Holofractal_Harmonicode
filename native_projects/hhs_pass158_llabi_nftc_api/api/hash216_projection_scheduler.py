from __future__ import annotations

from collections import OrderedDict, deque
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from threading import RLock
from typing import Any, Callable, Mapping, Sequence

ZERO_ROOT = "0" * 64
SCHEMA = "HHS_HASH216_GUI_PROJECTION_PACKAGE_V1"
HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
SNAPSHOT_SCHEMA = "HHS_HASH216_GUI_PROJECTION_SCHEDULER_SNAPSHOT_V1"
ReceiptVerifier = Callable[[str, str], bool]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


class Hash216Authority:
    """Thin adapter over the inherited Pass 150 Hash216 authority."""

    def __init__(self) -> None:
        try:
            from hhs_runtime.pass150.genome import Hash216Genome
        except ImportError as exc:  # pragma: no cover - repository integration path
            raise RuntimeError("HASH216_AUTHORITY_UNAVAILABLE") from exc
        self._genome = Hash216Genome

    def positions(self, payload: bytes, *, previous_root: str, sequence: int) -> tuple[str, ...]:
        return tuple(
            self._genome.positions(
                payload,
                previous_root=previous_root,
                sequence=sequence,
            )
        )

    def root(self, positions: Sequence[str]) -> str:
        return str(self._genome.root(tuple(positions)))


@dataclass(frozen=True)
class FrameTelemetry:
    frame_sequence: int
    target_frame_ns: int
    physics_ns: int = 0
    projection_ns: int = 0
    buffer_upload_ns: int = 0
    render_ns: int = 0
    runtime_ingress_ns: int = 0
    receipt_ns: int = 0
    backlog_count: int = 0

    def __post_init__(self) -> None:
        for key, value in asdict(self).items():
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"INVALID_FRAME_TELEMETRY:{key}")
        if self.target_frame_ns == 0:
            raise ValueError("INVALID_FRAME_TELEMETRY:target_frame_ns")

    @property
    def workload_ns(self) -> int:
        return (
            self.physics_ns
            + self.projection_ns
            + self.buffer_upload_ns
            + self.render_ns
            + self.runtime_ingress_ns
            + self.receipt_ns
        )


@dataclass(frozen=True)
class FrameBudgetDecision:
    classification: str
    target_frame_ns: int
    workload_ns: int
    remaining_ns: int
    pressure_basis_points: int
    max_events_per_package: int
    max_chunks_per_package: int
    render_divisor: int
    physics_catchup_limit: int
    hold_classes: tuple[str, ...]


@dataclass(frozen=True)
class ChunkRecord:
    object_id: str
    object_class: str
    version: int
    previous_root: str
    content_sha256: str
    payload: Any
    dependency_roots: tuple[tuple[str, str], ...]
    positions: tuple[str, ...]
    genome_root: str
    static: bool

    def summary(self, *, include_payload: bool = True) -> dict[str, Any]:
        result = {
            "object_id": self.object_id,
            "object_class": self.object_class,
            "version": self.version,
            "previous_root_hash216": self.previous_root,
            "content_sha256": self.content_sha256,
            "dependency_roots": [list(item) for item in self.dependency_roots],
            "hash216_positions": list(self.positions),
            "hash216_root": self.genome_root,
            "static": self.static,
        }
        if include_payload:
            result["payload"] = self.payload
        return result


@dataclass(frozen=True)
class ProjectionEvent:
    event_sequence: int
    object_id: str
    chunk_root: str
    authoritative: bool
    delta_offset_vector: Any


@dataclass(frozen=True)
class _ChunkCandidate:
    object_id: str
    object_class: str
    version: int
    previous_root: str
    content_sha256: str
    payload: Any
    dependency_roots: tuple[tuple[str, str], ...]
    canonical_payload: bytes
    static: bool
    existing: ChunkRecord | None
    changed: bool


class Hash216ProjectionScheduler:
    """Automatic Hash216 state-delta and GUI frame-budget projection scheduler.

    This component has no mutation authority. It identifies changed chunks,
    preserves authoritative events losslessly, coalesces replaceable projection
    events, and emits packages that require VM81 admission and Hash72 closure.
    """

    def __init__(
        self,
        *,
        authority: Any | None = None,
        receipt_verifier: ReceiptVerifier | None = None,
        max_authoritative_events: int = 4096,
        max_transient_events: int = 2048,
        normal_events_per_package: int = 64,
        normal_chunks_per_package: int = 64,
    ) -> None:
        if min(
            max_authoritative_events,
            max_transient_events,
            normal_events_per_package,
            normal_chunks_per_package,
        ) < 1:
            raise ValueError("INVALID_SCHEDULER_BOUND")
        self._authority = authority or Hash216Authority()
        self._receipt_verifier = receipt_verifier
        self._max_authoritative_events = max_authoritative_events
        self._max_transient_events = max_transient_events
        self._normal_events = normal_events_per_package
        self._normal_chunks = normal_chunks_per_package
        self._objects: dict[str, ChunkRecord] = {}
        self._chunks_by_root: dict[str, ChunkRecord] = {}
        self._continuations: dict[tuple[str, str, int], ChunkRecord] = {}
        self._authoritative: deque[ProjectionEvent] = deque()
        self._transient: OrderedDict[str, ProjectionEvent] = OrderedDict()
        self._packages: dict[str, dict[str, Any]] = {}
        self._last_package_root = ZERO_ROOT
        self._event_sequence = 0
        self._package_sequence = 0
        self._coalesced_events = 0
        self._reused_chunks = 0
        self._latest_telemetry: FrameTelemetry | None = None
        self._latest_budget = self._default_budget()
        self._lock = RLock()

    def set_receipt_verifier(self, verifier: ReceiptVerifier | None) -> None:
        with self._lock:
            self._receipt_verifier = verifier

    def _default_budget(self) -> FrameBudgetDecision:
        return FrameBudgetDecision(
            classification="FRAME_BUDGET_UNOBSERVED",
            target_frame_ns=16_666_667,
            workload_ns=0,
            remaining_ns=16_666_667,
            pressure_basis_points=0,
            max_events_per_package=self._normal_events,
            max_chunks_per_package=self._normal_chunks,
            render_divisor=1,
            physics_catchup_limit=8,
            hold_classes=(),
        )

    def _dependency_roots(self, dependencies: Sequence[str]) -> tuple[tuple[str, str], ...]:
        roots: list[tuple[str, str]] = []
        for dependency in dependencies:
            record = self._objects.get(dependency)
            if record is None:
                raise KeyError(f"DEPENDENCY_NOT_REGISTERED:{dependency}")
            roots.append((dependency, record.genome_root))
        return tuple(sorted(roots))

    def _prepare_chunk(
        self,
        *,
        object_id: str,
        object_class: str,
        value: Any,
        static: bool,
        dependencies: Sequence[str],
    ) -> _ChunkCandidate:
        payload = json.loads(canonical_bytes(value))
        dependency_roots = self._dependency_roots(dependencies)
        fingerprint_payload = {
            "object_id": object_id,
            "object_class": object_class,
            "payload": payload,
            "dependency_roots": dependency_roots,
            "static": static,
        }
        raw = canonical_bytes(fingerprint_payload)
        content_hash = sha256(raw).hexdigest()
        existing = self._objects.get(object_id)
        if existing is not None and existing.content_sha256 == content_hash:
            return _ChunkCandidate(
                object_id=object_id,
                object_class=object_class,
                version=existing.version,
                previous_root=existing.previous_root,
                content_sha256=content_hash,
                payload=payload,
                dependency_roots=dependency_roots,
                canonical_payload=raw,
                static=static,
                existing=existing,
                changed=False,
            )
        if existing is not None and existing.static:
            raise ValueError("STATIC_OBJECT_MUTATION_REJECTED")
        return _ChunkCandidate(
            object_id=object_id,
            object_class=object_class,
            version=1 if existing is None else existing.version + 1,
            previous_root=existing.genome_root if existing else ZERO_ROOT,
            content_sha256=content_hash,
            payload=payload,
            dependency_roots=dependency_roots,
            canonical_payload=raw,
            static=static,
            existing=existing,
            changed=True,
        )

    def _commit_chunk(self, candidate: _ChunkCandidate) -> ChunkRecord:
        if not candidate.changed and candidate.existing is not None:
            return candidate.existing
        cache_key = (
            candidate.content_sha256,
            candidate.previous_root,
            candidate.version,
        )
        cached = self._continuations.get(cache_key)
        if cached is not None:
            self._reused_chunks += 1
            record = cached
        else:
            positions = tuple(
                self._authority.positions(
                    candidate.canonical_payload,
                    previous_root=candidate.previous_root,
                    sequence=candidate.version,
                )
            )
            if len(positions) != 216:
                raise ValueError("HASH216_POSITION_COUNT_MISMATCH")
            root = self._authority.root(positions)
            record = ChunkRecord(
                object_id=candidate.object_id,
                object_class=candidate.object_class,
                version=candidate.version,
                previous_root=candidate.previous_root,
                content_sha256=candidate.content_sha256,
                payload=candidate.payload,
                dependency_roots=candidate.dependency_roots,
                positions=positions,
                genome_root=root,
                static=candidate.static,
            )
            self._continuations[cache_key] = record
        self._objects[candidate.object_id] = record
        self._chunks_by_root[record.genome_root] = record
        return record

    def register_static_object(
        self,
        object_id: str,
        object_class: str,
        value: Any,
        *,
        dependencies: Sequence[str] = (),
    ) -> dict[str, Any]:
        return self.observe_runtime_state(
            object_id,
            object_class,
            value,
            authoritative=False,
            static=True,
            dependencies=dependencies,
        )

    def observe_runtime_state(
        self,
        object_id: str,
        object_class: str,
        value: Any,
        *,
        authoritative: bool = False,
        static: bool = False,
        dependencies: Sequence[str] = (),
        delta_offset_vector: Any = None,
    ) -> dict[str, Any]:
        if not object_id or not object_class:
            raise ValueError("OBJECT_ID_AND_CLASS_REQUIRED")
        with self._lock:
            candidate = self._prepare_chunk(
                object_id=object_id,
                object_class=object_class,
                value=value,
                static=static,
                dependencies=dependencies,
            )
            if not candidate.changed and candidate.existing is not None:
                return {
                    "classification": "HASH216_CONTINUATION_REUSED",
                    "changed": False,
                    "chunk": candidate.existing.summary(include_payload=False),
                }
            if authoritative and len(self._authoritative) >= self._max_authoritative_events:
                raise BufferError("AUTHORITATIVE_PROJECTION_QUEUE_BOUND")

            record = self._commit_chunk(candidate)
            next_event_sequence = self._event_sequence + 1
            event = ProjectionEvent(
                event_sequence=next_event_sequence,
                object_id=object_id,
                chunk_root=record.genome_root,
                authoritative=authoritative,
                delta_offset_vector=json.loads(canonical_bytes(delta_offset_vector))
                if delta_offset_vector is not None
                else None,
            )
            if authoritative:
                self._authoritative.append(event)
            else:
                if object_id in self._transient:
                    self._coalesced_events += 1
                    self._transient.pop(object_id)
                elif len(self._transient) >= self._max_transient_events:
                    self._transient.popitem(last=False)
                    self._coalesced_events += 1
                self._transient[object_id] = event
            self._event_sequence = next_event_sequence
            return {
                "classification": "HASH216_STATE_CHANGE_INDEXED",
                "changed": True,
                "authoritative": authoritative,
                "chunk": record.summary(include_payload=False),
            }

    def observe_frame_telemetry(self, telemetry: FrameTelemetry | Mapping[str, int]) -> dict[str, Any]:
        observed = telemetry if isinstance(telemetry, FrameTelemetry) else FrameTelemetry(**telemetry)
        workload = observed.workload_ns
        target = observed.target_frame_ns
        remaining = target - workload
        pressure = (workload * 10_000) // target
        if workload <= target:
            decision = FrameBudgetDecision(
                classification="FRAME_BUDGET_NORMAL",
                target_frame_ns=target,
                workload_ns=workload,
                remaining_ns=remaining,
                pressure_basis_points=pressure,
                max_events_per_package=self._normal_events,
                max_chunks_per_package=self._normal_chunks,
                render_divisor=1,
                physics_catchup_limit=8,
                hold_classes=(),
            )
        elif workload <= (target * 3) // 2:
            decision = FrameBudgetDecision(
                classification="FRAME_BUDGET_PRESSURE",
                target_frame_ns=target,
                workload_ns=workload,
                remaining_ns=remaining,
                pressure_basis_points=pressure,
                max_events_per_package=max(8, self._normal_events // 2),
                max_chunks_per_package=max(8, self._normal_chunks // 2),
                render_divisor=2,
                physics_catchup_limit=4,
                hold_classes=("DIAGNOSTICS", "COLOR_PROJECTION"),
            )
        else:
            decision = FrameBudgetDecision(
                classification="FRAME_BUDGET_CRITICAL",
                target_frame_ns=target,
                workload_ns=workload,
                remaining_ns=remaining,
                pressure_basis_points=pressure,
                max_events_per_package=max(1, self._normal_events // 8),
                max_chunks_per_package=max(1, self._normal_chunks // 4),
                render_divisor=4,
                physics_catchup_limit=1,
                hold_classes=(
                    "DIAGNOSTICS",
                    "COLOR_PROJECTION",
                    "TRANSIENT_GRAPH",
                    "TRANSIENT_STATUS",
                    "PHYSICS_CATCHUP",
                ),
            )
        with self._lock:
            self._latest_telemetry = observed
            self._latest_budget = decision
        return asdict(decision)

    def _collect_events(self, max_events: int, max_chunks: int) -> list[ProjectionEvent]:
        selected: list[ProjectionEvent] = []
        roots: set[str] = set()

        while self._authoritative and len(selected) < max_events:
            event = self._authoritative[0]
            introduces_root = event.chunk_root not in roots
            if introduces_root and len(roots) >= max_chunks:
                break
            selected.append(self._authoritative.popleft())
            roots.add(event.chunk_root)

        while self._transient and len(selected) < max_events:
            object_id, event = next(iter(self._transient.items()))
            introduces_root = event.chunk_root not in roots
            if introduces_root and len(roots) >= max_chunks:
                break
            self._transient.pop(object_id)
            selected.append(event)
            roots.add(event.chunk_root)
        return selected

    def build_projection_package(
        self,
        frame_sequence: int,
        *,
        projection_profile: str = "BALANCED",
    ) -> dict[str, Any]:
        if not isinstance(frame_sequence, int) or frame_sequence < 0:
            raise ValueError("INVALID_FRAME_SEQUENCE")
        with self._lock:
            budget = self._latest_budget
            events = self._collect_events(
                budget.max_events_per_package,
                budget.max_chunks_per_package,
            )
            chunk_roots: set[str] = set()
            chunks: list[ChunkRecord] = []
            delta_vectors: list[dict[str, Any]] = []
            authoritative_events = 0
            for event in events:
                try:
                    record = self._chunks_by_root[event.chunk_root]
                except KeyError as exc:
                    raise ValueError("HASH216_EVENT_CHUNK_MISSING") from exc
                if record.genome_root not in chunk_roots:
                    chunks.append(record)
                    chunk_roots.add(record.genome_root)
                if event.delta_offset_vector is not None:
                    delta_vectors.append({
                        "object_id": event.object_id,
                        "chunk_root_hash216": event.chunk_root,
                        "value": event.delta_offset_vector,
                    })
                authoritative_events += int(event.authoritative)
            self._package_sequence += 1
            body = {
                "schema": SCHEMA,
                "package_sequence": self._package_sequence,
                "frame_sequence": frame_sequence,
                "projection_profile": projection_profile,
                "source_state_roots_hash216": {
                    key: record.genome_root for key, record in sorted(self._objects.items())
                },
                "previous_projection_root_hash216": self._last_package_root,
                "changed_chunks": [item.summary() for item in chunks],
                "changed_chunk_count": len(chunks),
                "event_count": len(events),
                "authoritative_event_count": authoritative_events,
                "dirty_attribute_mask": sorted({item.object_class for item in chunks}),
                "delta_offset_vectors": delta_vectors,
                "frame_budget": asdict(budget),
                "queue_after": {
                    "authoritative": len(self._authoritative),
                    "transient": len(self._transient),
                },
                "requires_vm81_validation": True,
                "mutation_authority": False,
                "vm81_admission": "PENDING",
                "receipt_hash72": None,
            }
            raw = canonical_bytes(body)
            positions = tuple(
                self._authority.positions(
                    raw,
                    previous_root=self._last_package_root,
                    sequence=self._package_sequence,
                )
            )
            if len(positions) != 216:
                raise ValueError("HASH216_POSITION_COUNT_MISMATCH")
            root = self._authority.root(positions)
            package = {
                **body,
                "projection_hash216_positions": list(positions),
                "projection_root_hash216": root,
                "classification": "HHS_PASS_158_HASH216_GUI_PROJECTION_PACKAGE_BUILT",
            }
            self._packages[root] = package
            self._last_package_root = root
            return json.loads(canonical_bytes(package))

    def acknowledge_vm81(
        self,
        projection_root_hash216: str,
        *,
        admitted: bool,
        receipt_hash72: str | None = None,
        classification: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            if projection_root_hash216 not in self._packages:
                raise KeyError("PROJECTION_PACKAGE_NOT_FOUND")
            if admitted and not receipt_hash72:
                raise ValueError("HASH72_RECEIPT_REQUIRED_FOR_ADMISSION")
            if admitted and (
                len(receipt_hash72 or "") != 72
                or any(symbol not in HASH72_ALPHABET for symbol in receipt_hash72 or "")
            ):
                raise ValueError("HASH72_RECEIPT_INVALID")
            if admitted:
                if self._receipt_verifier is None:
                    raise ValueError("HASH72_RECEIPT_VERIFIER_REQUIRED")
                if not self._receipt_verifier(str(receipt_hash72), projection_root_hash216):
                    raise ValueError("HASH72_RECEIPT_MISMATCH")
            package = dict(self._packages[projection_root_hash216])
            package["vm81_admission"] = "ADMITTED" if admitted else "REJECTED"
            package["receipt_hash72"] = receipt_hash72
            package["classification"] = classification or (
                "HHS_PASS_158_HASH216_GUI_PROJECTION_ADMITTED"
                if admitted
                else "HHS_PASS_158_HASH216_GUI_PROJECTION_REJECTED"
            )
            self._packages[projection_root_hash216] = package
            return json.loads(canonical_bytes(package))

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "schema": SNAPSHOT_SCHEMA,
                "objects": {
                    key: value.summary() for key, value in sorted(self._objects.items())
                },
                "chunk_history": {
                    key: value.summary() for key, value in sorted(self._chunks_by_root.items())
                },
                "authoritative_queue": [asdict(item) for item in self._authoritative],
                "transient_queue": [asdict(item) for item in self._transient.values()],
                "last_package_root": self._last_package_root,
                "event_sequence": self._event_sequence,
                "package_sequence": self._package_sequence,
                "coalesced_events": self._coalesced_events,
                "reused_chunks": self._reused_chunks,
                "latest_telemetry": asdict(self._latest_telemetry) if self._latest_telemetry else None,
                "latest_budget": asdict(self._latest_budget),
                "mutation_authority": False,
            }

    def _record_from_snapshot(self, object_id: str, raw: Mapping[str, Any]) -> ChunkRecord:
        object_class = str(raw["object_class"])
        version = int(raw["version"])
        previous_root = str(raw.get("previous_root_hash216", ZERO_ROOT))
        payload = json.loads(canonical_bytes(raw.get("payload")))
        dependency_roots = tuple(
            sorted((str(a), str(b)) for a, b in raw.get("dependency_roots", []))
        )
        static = bool(raw["static"])
        fingerprint_payload = {
            "object_id": object_id,
            "object_class": object_class,
            "payload": payload,
            "dependency_roots": dependency_roots,
            "static": static,
        }
        canonical_payload = canonical_bytes(fingerprint_payload)
        expected_content_hash = sha256(canonical_payload).hexdigest()
        expected_positions = tuple(
            self._authority.positions(
                canonical_payload,
                previous_root=previous_root,
                sequence=version,
            )
        )
        if len(expected_positions) != 216:
            raise ValueError("HASH216_POSITION_COUNT_MISMATCH")
        expected_root = self._authority.root(expected_positions)
        supplied_positions = tuple(str(item) for item in raw["hash216_positions"])
        supplied_root = str(raw["hash216_root"])
        supplied_content_hash = str(raw["content_sha256"])
        if (
            supplied_content_hash != expected_content_hash
            or supplied_positions != expected_positions
            or supplied_root != expected_root
        ):
            raise ValueError("HASH216_SNAPSHOT_IDENTITY_MISMATCH")
        return ChunkRecord(
            object_id=object_id,
            object_class=object_class,
            version=version,
            previous_root=previous_root,
            content_sha256=expected_content_hash,
            payload=payload,
            dependency_roots=dependency_roots,
            positions=expected_positions,
            genome_root=expected_root,
            static=static,
        )

    def recover(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        if snapshot.get("schema") != SNAPSHOT_SCHEMA:
            raise ValueError("INVALID_SCHEDULER_SNAPSHOT")
        with self._lock:
            new_chunks: dict[str, ChunkRecord] = {}
            history = snapshot.get("chunk_history") or {
                raw["hash216_root"]: raw for raw in snapshot.get("objects", {}).values()
            }
            for root, raw in history.items():
                record = self._record_from_snapshot(str(raw["object_id"]), raw)
                if root != record.genome_root:
                    raise ValueError("HASH216_SNAPSHOT_IDENTITY_MISMATCH")
                new_chunks[root] = record

            new_objects: dict[str, ChunkRecord] = {}
            for object_id, raw in snapshot.get("objects", {}).items():
                root = str(raw["hash216_root"])
                try:
                    record = new_chunks[root]
                except KeyError as exc:
                    raise ValueError("HASH216_SNAPSHOT_LATEST_CHUNK_MISSING") from exc
                if record.object_id != object_id:
                    raise ValueError("HASH216_SNAPSHOT_OBJECT_ID_MISMATCH")
                new_objects[object_id] = record

            authoritative = deque(
                ProjectionEvent(**item) for item in snapshot.get("authoritative_queue", [])
            )
            transient = OrderedDict(
                (item["object_id"], ProjectionEvent(**item))
                for item in snapshot.get("transient_queue", [])
            )
            for event in [*authoritative, *transient.values()]:
                if event.chunk_root not in new_chunks:
                    raise ValueError("HASH216_EVENT_CHUNK_MISSING")

            self._objects = new_objects
            self._chunks_by_root = new_chunks
            self._continuations = {
                (record.content_sha256, record.previous_root, record.version): record
                for record in new_chunks.values()
            }
            self._authoritative = authoritative
            self._transient = transient
            self._last_package_root = str(snapshot.get("last_package_root", ZERO_ROOT))
            self._event_sequence = int(snapshot.get("event_sequence", 0))
            self._package_sequence = int(snapshot.get("package_sequence", 0))
            self._coalesced_events = int(snapshot.get("coalesced_events", 0))
            self._reused_chunks = int(snapshot.get("reused_chunks", 0))
            telemetry = snapshot.get("latest_telemetry")
            self._latest_telemetry = FrameTelemetry(**telemetry) if telemetry else None
            self._latest_budget = FrameBudgetDecision(
                **snapshot.get("latest_budget", asdict(self._default_budget()))
            )
            return self.status()

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "schema": "HHS_HASH216_GUI_PROJECTION_SCHEDULER_STATUS_V1",
                "classification": "HHS_PASS_158_HASH216_GUI_PROJECTION_SCHEDULER_READY",
                "objects": len(self._objects),
                "versioned_chunks": len(self._chunks_by_root),
                "continuations": len(self._continuations),
                "authoritative_queue": len(self._authoritative),
                "transient_queue": len(self._transient),
                "coalesced_events": self._coalesced_events,
                "reused_chunks": self._reused_chunks,
                "last_projection_root_hash216": self._last_package_root,
                "frame_budget": asdict(self._latest_budget),
                "receipt_verifier_configured": self._receipt_verifier is not None,
                "requires_vm81_validation": True,
                "mutation_authority": False,
            }
