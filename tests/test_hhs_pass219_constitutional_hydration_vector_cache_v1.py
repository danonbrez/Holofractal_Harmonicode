from __future__ import annotations

from dataclasses import replace

import pytest

from hhs_runtime.hhs_pass219_constitutional_hydration_vector_cache_v1 import (
    ConstitutionalHydrationCacheError,
    ConstitutionalVectorCache,
    hydrate_and_bind_raw5184,
    validate_envelope,
)
from hhs_runtime.hhs_pass219_constitutional_modality_registry_v1 import BASE_INVARIANTS
from hhs_runtime.hhs_pass219_global_raw5184_serialization_hydration_v1 import RAW_BYTES


TRACE72 = "T" * 72
RAW = bytes((index * 17) & 0xFF for index in range(RAW_BYTES))


def _envelope(**kwargs):
    values = {
        "source_trace_hash72": TRACE72,
        "provenance": "fixture:pass219-hydration-vector-cache",
    }
    values.update(kwargs)
    return hydrate_and_bind_raw5184(RAW, **values)


def test_hydration_vector_cache_preserves_exact_raw5184_bytes_and_topology():
    envelope = _envelope()
    assert envelope.raw_bytes == RAW
    assert envelope.preservation_complete is True
    assert tuple(trace.modality_id for trace in envelope.modality_traces) == (
        "serialization_bytecode",
        "hydration_rom",
        "vector_cache",
    )
    assert all(trace.preservation_complete for trace in envelope.modality_traces)
    payload = envelope.to_dict()
    assert payload["vm81_mutation_authority"] is False
    assert payload["hash72_commit_authority"] is False
    assert payload["hash216_commit_authority"] is False
    assert payload["canonical_persistence_authority"] is False
    assert len(payload["envelope_hash72"]) == 72


def test_hydration_binding_rejects_malformed_source_hash72():
    with pytest.raises(ConstitutionalHydrationCacheError, match="SOURCE_TRACE_HASH72"):
        hydrate_and_bind_raw5184(
            RAW,
            source_trace_hash72="short",
            provenance="fixture",
        )


def test_hydration_binding_rejects_missing_mandatory_invariant():
    preserved = tuple(x for x in BASE_INVARIANTS if x != "RESPONSIBILITY_PRESERVATION")
    with pytest.raises(ConstitutionalHydrationCacheError, match="INVARIANT_LOSS"):
        hydrate_and_bind_raw5184(
            RAW,
            source_trace_hash72=TRACE72,
            provenance="fixture",
            preserved_invariants=preserved,
        )


def test_hydration_binding_rejects_non_5184_payload():
    with pytest.raises(ConstitutionalHydrationCacheError, match="RAW5184_BYTE_COUNT"):
        hydrate_and_bind_raw5184(
            RAW[:-1],
            source_trace_hash72=TRACE72,
            provenance="fixture",
        )


def test_vector_cache_is_idempotent_for_identical_receipted_entry():
    cache = ConstitutionalVectorCache()
    envelope = _envelope()
    first = cache.insert(envelope)
    second = cache.insert(envelope)
    assert first is second
    assert len(cache) == 1
    assert cache.lookup(envelope.vector_key) == envelope


def test_vector_cache_rejects_payload_tamper_even_if_key_is_unchanged():
    envelope = _envelope()
    tampered = replace(envelope, raw_bytes=bytes([RAW[0] ^ 1]) + RAW[1:])
    with pytest.raises(ConstitutionalHydrationCacheError, match="PAYLOAD_TAMPER"):
        validate_envelope(tampered)


def test_vector_cache_rejects_receipt_tamper():
    envelope = _envelope()
    tampered = replace(envelope, envelope_hash72="X" * 72)
    with pytest.raises(ConstitutionalHydrationCacheError, match="RECEIPT_MISMATCH"):
        validate_envelope(tampered)


def test_vector_cache_rejects_same_key_for_different_receipted_identity():
    cache = ConstitutionalVectorCache()
    first = _envelope(vector_key="fixed-key")
    second = hydrate_and_bind_raw5184(
        RAW,
        source_trace_hash72=TRACE72,
        provenance="different-provenance",
        vector_key="fixed-key",
    )
    cache.insert(first)
    with pytest.raises(ConstitutionalHydrationCacheError, match="VECTOR_KEY_COLLISION"):
        cache.insert(second)


def test_vector_cache_miss_fails_closed():
    with pytest.raises(ConstitutionalHydrationCacheError, match="CACHE_MISS"):
        ConstitutionalVectorCache().lookup("missing")
