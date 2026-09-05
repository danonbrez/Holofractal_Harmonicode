"""Pass 219 constitutional hydration/vector-cache trace membrane.

This adapter binds the inherited exact raw5184 hydration surface and a derived
vector/cache reuse envelope to the Pass 219 constitutional modality registry.
It is deliberately non-authoritative: it cannot mutate VM81, commit Hash72,
commit Hash216, or persist canonical state.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Dict, Iterable, Mapping, Tuple

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import EthicsState, ModalityInvariantTrace
from hhs_runtime.hhs_pass219_constitutional_modality_registry_v1 import (
    BASE_INVARIANTS,
    build_modality_trace,
    get_modality_contract,
)
from hhs_runtime.hhs_pass219_global_raw5184_serialization_hydration_v1 import (
    RAW_BYTES,
    hydrate_raw5184_bytes,
    serialize_raw5184_bytes,
)

VERSION = "HHS_PASS219_CONSTITUTIONAL_HYDRATION_VECTOR_CACHE_V1"
SCHEMA = "HHS_PASS219_CONSTITUTIONAL_HYDRATION_VECTOR_CACHE_ENVELOPE_V1"
AUTHORITY = "DERIVED_REUSE_ONLY_NO_VM81_MUTATION_AUTHORITY"
HASH72_LENGTH = 72


class ConstitutionalHydrationCacheError(ValueError):
    pass


def _ordered_unique(values: Iterable[str]) -> Tuple[str, ...]:
    seen = set()
    out = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return tuple(out)


def _is_hash72(value: object) -> bool:
    return isinstance(value, str) and len(value) == HASH72_LENGTH


def _reference_hash72(label: str, payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hash72_digest((VERSION, label, canonical), width=24)


@dataclass(frozen=True)
class HydrationVectorCacheEnvelope:
    vector_key: str
    source_trace_hash72: str
    provenance: str
    payload_sha256: str
    raw_bytes: bytes
    required_invariants: Tuple[str, ...]
    preserved_invariants: Tuple[str, ...]
    modality_traces: Tuple[ModalityInvariantTrace, ...]
    envelope_hash72: str

    @property
    def preservation_complete(self) -> bool:
        required = set(self.required_invariants)
        preserved = set(self.preserved_invariants)
        return required.issubset(preserved) and all(trace.preservation_complete for trace in self.modality_traces)

    def to_dict(self, *, include_bytes: bool = False) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": AUTHORITY,
            "vector_key": self.vector_key,
            "source_trace_hash72": self.source_trace_hash72,
            "provenance": self.provenance,
            "payload_sha256": self.payload_sha256,
            "raw_byte_count": len(self.raw_bytes),
            "required_invariants": list(self.required_invariants),
            "preserved_invariants": list(self.preserved_invariants),
            "preservation_complete": self.preservation_complete,
            "modality_traces": [trace.to_dict() for trace in self.modality_traces],
            "vm81_mutation_authority": False,
            "hash72_commit_authority": False,
            "hash216_commit_authority": False,
            "canonical_persistence_authority": False,
            "envelope_hash72": self.envelope_hash72,
        }
        if include_bytes:
            payload["raw_bytes_hex"] = self.raw_bytes.hex()
        return payload


def _envelope_receipt_payload(
    *,
    vector_key: str,
    source_trace_hash72: str,
    provenance: str,
    payload_sha256: str,
    required_invariants: Tuple[str, ...],
    preserved_invariants: Tuple[str, ...],
    modality_traces: Tuple[ModalityInvariantTrace, ...],
) -> Dict[str, object]:
    return {
        "vector_key": vector_key,
        "source_trace_hash72": source_trace_hash72,
        "provenance": provenance,
        "payload_sha256": payload_sha256,
        "required_invariants": list(required_invariants),
        "preserved_invariants": list(preserved_invariants),
        "modality_traces": [trace.to_dict() for trace in modality_traces],
    }


def hydrate_and_bind_raw5184(
    payload: bytes | bytearray | memoryview,
    *,
    source_trace_hash72: str,
    provenance: str,
    preserved_invariants: Iterable[str] = BASE_INVARIANTS,
    vector_key: str | None = None,
) -> HydrationVectorCacheEnvelope:
    """Hydrate exact 5184-bit bytes and bind hydration/cache provenance."""

    raw = bytes(payload)
    if len(raw) != RAW_BYTES:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_RAW5184_BYTE_COUNT")
    if not _is_hash72(source_trace_hash72):
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_SOURCE_TRACE_HASH72")
    provenance = str(provenance).strip()
    if not provenance:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_PROVENANCE_REQUIRED")

    preserved = _ordered_unique(preserved_invariants)
    required = tuple(BASE_INVARIANTS)
    missing = tuple(item for item in required if item not in set(preserved))
    if missing:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_INVARIANT_LOSS:" + ",".join(missing))

    # Invoke inherited authoritative-format hydration logic. This adapter only
    # validates and mirrors bytes; hydration remains derived/non-mutating.
    hydrate_raw5184_bytes(raw)
    replay = serialize_raw5184_bytes(raw)
    if replay != raw:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_HYDRATION_BIT_IDENTITY")

    traces = tuple(
        build_modality_trace(
            modality_id,
            local_state=EthicsState.PASS,
            preserved_invariants=preserved,
            ingress_preserves_constraints=True,
            egress_preserves_constraints=True,
            provenance_preserved=True,
        )
        for modality_id in ("serialization_bytecode", "hydration_rom", "vector_cache")
    )
    if any(get_modality_contract(trace.modality_id).mutation_authority for trace in traces):
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_NONAUTHORITATIVE_TOPOLOGY")

    payload_sha256 = sha256(raw).hexdigest()
    if vector_key is None:
        vector_key = sha256(
            b"HHS-P219-CONSTITUTIONAL-VECTOR-CACHE-V1\0"
            + source_trace_hash72.encode("ascii")
            + payload_sha256.encode("ascii")
            + provenance.encode("utf-8")
        ).hexdigest()
    vector_key = str(vector_key).strip()
    if not vector_key:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_VECTOR_KEY_REQUIRED")

    receipt_payload = _envelope_receipt_payload(
        vector_key=vector_key,
        source_trace_hash72=source_trace_hash72,
        provenance=provenance,
        payload_sha256=payload_sha256,
        required_invariants=required,
        preserved_invariants=preserved,
        modality_traces=traces,
    )
    return HydrationVectorCacheEnvelope(
        vector_key=vector_key,
        source_trace_hash72=source_trace_hash72,
        provenance=provenance,
        payload_sha256=payload_sha256,
        raw_bytes=raw,
        required_invariants=required,
        preserved_invariants=preserved,
        modality_traces=traces,
        envelope_hash72=_reference_hash72(SCHEMA, receipt_payload),
    )


def validate_envelope(envelope: HydrationVectorCacheEnvelope) -> None:
    if not _is_hash72(envelope.source_trace_hash72) or not _is_hash72(envelope.envelope_hash72):
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_HASH72_BINDING")
    if len(envelope.raw_bytes) != RAW_BYTES:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_RAW5184_BYTE_COUNT")
    if sha256(envelope.raw_bytes).hexdigest() != envelope.payload_sha256:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_CACHE_PAYLOAD_TAMPER")
    if not envelope.preservation_complete:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_CACHE_INVARIANT_LOSS")
    if tuple(trace.modality_id for trace in envelope.modality_traces) != (
        "serialization_bytecode",
        "hydration_rom",
        "vector_cache",
    ):
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_CACHE_MODALITY_CHAIN")

    expected = _reference_hash72(
        SCHEMA,
        _envelope_receipt_payload(
            vector_key=envelope.vector_key,
            source_trace_hash72=envelope.source_trace_hash72,
            provenance=envelope.provenance,
            payload_sha256=envelope.payload_sha256,
            required_invariants=envelope.required_invariants,
            preserved_invariants=envelope.preserved_invariants,
            modality_traces=envelope.modality_traces,
        ),
    )
    if expected != envelope.envelope_hash72:
        raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_CACHE_RECEIPT_MISMATCH")


class ConstitutionalVectorCache:
    """Derived in-memory reuse cache; never canonical state or authority."""

    def __init__(self) -> None:
        self._entries: Dict[str, HydrationVectorCacheEnvelope] = {}

    def insert(self, envelope: HydrationVectorCacheEnvelope) -> HydrationVectorCacheEnvelope:
        validate_envelope(envelope)
        existing = self._entries.get(envelope.vector_key)
        if existing is not None:
            if existing != envelope:
                raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_VECTOR_KEY_COLLISION")
            return existing
        self._entries[envelope.vector_key] = envelope
        return envelope

    def lookup(self, vector_key: str) -> HydrationVectorCacheEnvelope:
        try:
            envelope = self._entries[vector_key]
        except KeyError as exc:
            raise ConstitutionalHydrationCacheError("CONSTITUTIONAL_VECTOR_CACHE_MISS") from exc
        validate_envelope(envelope)
        return envelope

    def invalidate(self, vector_key: str) -> None:
        self._entries.pop(vector_key, None)

    def __len__(self) -> int:
        return len(self._entries)


__all__ = [
    "VERSION",
    "SCHEMA",
    "AUTHORITY",
    "ConstitutionalHydrationCacheError",
    "HydrationVectorCacheEnvelope",
    "hydrate_and_bind_raw5184",
    "validate_envelope",
    "ConstitutionalVectorCache",
]
