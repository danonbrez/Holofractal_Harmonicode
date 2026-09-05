from __future__ import annotations

import json

import pytest

from hhs_runtime.hhs_pass219_constitutional_modality_registry_v1 import BASE_INVARIANTS
from hhs_runtime.hhs_pass219_constitutional_serialization_adapter_v1 import (
    AUTHORITY,
    MODALITY_ID,
    ConstitutionalSerializationEnvelope,
    ConstitutionalSerializationError,
    decode_constitutional_serialization_envelope,
)


def _envelope(payload: bytes = b"\x00\x01VM81\xff") -> ConstitutionalSerializationEnvelope:
    return ConstitutionalSerializationEnvelope(
        payload=payload,
        provenance_ids=("source:fixture", "previous:hash72"),
    )


def test_round_trip_preserves_exact_payload_invariants_and_provenance():
    original = _envelope()
    restored = decode_constitutional_serialization_envelope(original.serialize())
    assert restored.payload == original.payload
    assert restored.provenance_ids == original.provenance_ids
    assert set(BASE_INVARIANTS).issubset(set(restored.invariant_ids))
    assert restored.modality_trace.preservation_complete is True


def test_transport_is_non_authoritative():
    payload = _envelope().to_dict()
    assert payload["authority"] == AUTHORITY
    assert payload["modality_id"] == MODALITY_ID
    assert payload["canonical_vm81_mutation_performed"] is False
    assert payload["action_authority_minted"] is False


def test_missing_mandatory_invariant_fails_closed():
    with pytest.raises(ConstitutionalSerializationError, match="mandatory constitutional invariants missing"):
        ConstitutionalSerializationEnvelope(
            payload=b"x",
            provenance_ids=("source:x",),
            invariant_ids=BASE_INVARIANTS[:-1],
        )


def test_missing_provenance_fails_closed():
    with pytest.raises(ConstitutionalSerializationError, match="provenance"):
        ConstitutionalSerializationEnvelope(payload=b"x", provenance_ids=())


def _mutate(raw: bytes, field: str, value):
    obj = json.loads(raw.decode("utf-8"))
    obj[field] = value
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def test_payload_tamper_detected():
    raw = _envelope(b"abc").serialize()
    obj = json.loads(raw.decode("utf-8"))
    obj["payload_hex"] = b"abd".hex()
    tampered = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(ConstitutionalSerializationError, match="payload Hash72 mismatch"):
        decode_constitutional_serialization_envelope(tampered)


def test_transport_cannot_claim_vm81_mutation():
    with pytest.raises(ConstitutionalSerializationError, match="cannot claim VM81 mutation"):
        decode_constitutional_serialization_envelope(
            _mutate(_envelope().serialize(), "canonical_vm81_mutation_performed", True)
        )


def test_transport_cannot_claim_authority_minting():
    with pytest.raises(ConstitutionalSerializationError, match="cannot mint authority"):
        decode_constitutional_serialization_envelope(
            _mutate(_envelope().serialize(), "action_authority_minted", True)
        )


def test_provenance_tamper_detected_by_envelope_receipt():
    raw = _envelope().serialize()
    obj = json.loads(raw.decode("utf-8"))
    obj["provenance_ids"] = ["source:laundered"]
    tampered = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(ConstitutionalSerializationError, match="envelope Hash72 mismatch"):
        decode_constitutional_serialization_envelope(tampered)


def test_modality_trace_tamper_detected():
    raw = _envelope().serialize()
    obj = json.loads(raw.decode("utf-8"))
    obj["modality_trace"]["provenance_preserved"] = False
    tampered = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(ConstitutionalSerializationError, match="modality trace mismatch"):
        decode_constitutional_serialization_envelope(tampered)
