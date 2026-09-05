"""Pass 219 constitutional serialization transport adapter.

This adapter makes the first consequential transport surface intrinsic rather
than caller-optional. It preserves payload bytes exactly, binds mandatory
constitutional invariant identifiers and provenance into a deterministic
transport envelope, and emits a serialization_bytecode modality trace.

It is transport-only. It cannot mint authority or mutate VM81 state.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Dict, Iterable, Mapping, Tuple

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import (
    EthicsState,
    ModalityInvariantTrace,
)
from hhs_runtime.hhs_pass219_constitutional_modality_registry_v1 import (
    BASE_INVARIANTS,
    build_modality_trace,
)

VERSION = "HHS_PASS219_CONSTITUTIONAL_SERIALIZATION_ADAPTER_V1"
SCHEMA = "HHS_PASS219_CONSTITUTIONAL_SERIALIZATION_ENVELOPE_V1"
AUTHORITY = "TRANSPORT_ONLY_NO_VM81_MUTATION_AUTHORITY"
MODALITY_ID = "serialization_bytecode"


class ConstitutionalSerializationError(ValueError):
    """Raised when a constitutional transport envelope fails exact validation."""


def _ordered_unique(values: Iterable[str]) -> Tuple[str, ...]:
    seen = set()
    out = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return tuple(out)


def _payload_hash72(payload: bytes) -> str:
    return hash72_digest((VERSION, "payload", payload.hex()), width=24)


def _envelope_hash72(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hash72_digest((VERSION, "envelope", canonical), width=24)


@dataclass(frozen=True)
class ConstitutionalSerializationEnvelope:
    payload: bytes
    provenance_ids: Tuple[str, ...]
    invariant_ids: Tuple[str, ...] = BASE_INVARIANTS

    def __post_init__(self) -> None:
        if not isinstance(self.payload, bytes):
            raise TypeError("payload must be exact bytes")
        if not self.provenance_ids:
            raise ConstitutionalSerializationError("at least one provenance id is required")
        required = set(BASE_INVARIANTS)
        supplied = set(self.invariant_ids)
        if not required.issubset(supplied):
            missing = sorted(required - supplied)
            raise ConstitutionalSerializationError(
                "mandatory constitutional invariants missing: " + ",".join(missing)
            )

    @property
    def payload_hash72(self) -> str:
        return _payload_hash72(self.payload)

    def body_without_receipt(self) -> Dict[str, object]:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": AUTHORITY,
            "modality_id": MODALITY_ID,
            "payload_hex": self.payload.hex(),
            "payload_length": len(self.payload),
            "payload_hash72": self.payload_hash72,
            "provenance_ids": list(_ordered_unique(self.provenance_ids)),
            "invariant_ids": list(_ordered_unique(self.invariant_ids)),
            "canonical_vm81_mutation_performed": False,
            "action_authority_minted": False,
        }

    @property
    def envelope_hash72(self) -> str:
        return _envelope_hash72(self.body_without_receipt())

    @property
    def modality_trace(self) -> ModalityInvariantTrace:
        return build_modality_trace(
            MODALITY_ID,
            local_state=EthicsState.PASS,
            preserved_invariants=self.invariant_ids,
            ingress_preserves_constraints=True,
            egress_preserves_constraints=True,
            provenance_preserved=bool(self.provenance_ids),
        )

    def to_dict(self) -> Dict[str, object]:
        out = self.body_without_receipt()
        out["envelope_hash72"] = self.envelope_hash72
        out["modality_trace"] = self.modality_trace.to_dict()
        return out

    def serialize(self) -> bytes:
        """Return deterministic UTF-8 JSON bytes for transport/storage."""
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")


def decode_constitutional_serialization_envelope(raw: bytes) -> ConstitutionalSerializationEnvelope:
    """Decode and revalidate exact payload, provenance, invariants, and receipts."""
    if not isinstance(raw, bytes):
        raise TypeError("serialized envelope must be bytes")
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConstitutionalSerializationError("malformed serialization envelope") from exc
    if not isinstance(obj, dict):
        raise ConstitutionalSerializationError("serialization envelope must be an object")
    if obj.get("schema") != SCHEMA or obj.get("version") != VERSION:
        raise ConstitutionalSerializationError("serialization envelope schema/version mismatch")
    if obj.get("authority") != AUTHORITY or obj.get("modality_id") != MODALITY_ID:
        raise ConstitutionalSerializationError("serialization authority/modality mismatch")
    if obj.get("canonical_vm81_mutation_performed") is not False:
        raise ConstitutionalSerializationError("transport envelope cannot claim VM81 mutation")
    if obj.get("action_authority_minted") is not False:
        raise ConstitutionalSerializationError("transport envelope cannot mint authority")

    payload_hex = obj.get("payload_hex")
    if not isinstance(payload_hex, str):
        raise ConstitutionalSerializationError("payload_hex missing")
    try:
        payload = bytes.fromhex(payload_hex)
    except ValueError as exc:
        raise ConstitutionalSerializationError("payload_hex malformed") from exc
    if obj.get("payload_length") != len(payload):
        raise ConstitutionalSerializationError("payload length mismatch")
    if obj.get("payload_hash72") != _payload_hash72(payload):
        raise ConstitutionalSerializationError("payload Hash72 mismatch")

    provenance_raw = obj.get("provenance_ids")
    invariants_raw = obj.get("invariant_ids")
    if not isinstance(provenance_raw, list) or not all(isinstance(x, str) for x in provenance_raw):
        raise ConstitutionalSerializationError("provenance_ids malformed")
    if not isinstance(invariants_raw, list) or not all(isinstance(x, str) for x in invariants_raw):
        raise ConstitutionalSerializationError("invariant_ids malformed")

    envelope = ConstitutionalSerializationEnvelope(
        payload=payload,
        provenance_ids=tuple(provenance_raw),
        invariant_ids=tuple(invariants_raw),
    )
    if obj.get("envelope_hash72") != envelope.envelope_hash72:
        raise ConstitutionalSerializationError("envelope Hash72 mismatch")

    trace = obj.get("modality_trace")
    if not isinstance(trace, dict):
        raise ConstitutionalSerializationError("modality trace missing")
    expected_trace = envelope.modality_trace.to_dict()
    if trace != expected_trace:
        raise ConstitutionalSerializationError("modality trace mismatch")
    if not envelope.modality_trace.preservation_complete:
        raise ConstitutionalSerializationError("constitutional invariant preservation incomplete")
    return envelope


__all__ = [
    "VERSION",
    "SCHEMA",
    "AUTHORITY",
    "MODALITY_ID",
    "ConstitutionalSerializationError",
    "ConstitutionalSerializationEnvelope",
    "decode_constitutional_serialization_envelope",
]
