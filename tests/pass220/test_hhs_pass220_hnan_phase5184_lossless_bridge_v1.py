"""Dependency-scoped HNAN / I148 / I065 read-only integration regression."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

import hhs_runtime.hhs_pass220_hnan_phase5184_lossless_bridge_v1 as bridge
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    HASH72_ALPHABET,
    I065HydrationError,
)


def frame(seed: bytes) -> str:
    data = bytearray()
    n = 0
    while len(data) < 648:
        data.extend(sha256(seed + n.to_bytes(4, "big")).digest())
        n += 1
    return "".join(f"{b:08b}" for b in data[:648])


@pytest.mark.parametrize("seed", [b"hnan-1", b"hnan-2", b"hnan-3", b"hnan-4"])
def test_arbitrary_raw_5184_recovery_without_digest_loss(seed: bytes) -> None:
    raw = frame(seed)
    witness = bridge.candidate_bridge(raw, HASH72_ALPHABET)
    assert witness["raw_width"] == 5184
    assert witness["vm81_cells"] == 81
    assert witness["quad_count"] == 20
    assert bridge.recover_raw(witness) == raw
    assert witness["hnan_invariants_pass"] is True
    assert witness["phase_difference_exact"] is True
    assert witness["radix_binary3_groups"] == 1728
    assert witness["radix_balanced_trits"] == 3456
    assert witness["radix_base64_sextets"] == 864
    assert witness["base64_trinary_roundtrip_exact"] is True
    assert len(witness["phase_difference_witnesses"]) == 20
    assert all(len(row) == 3 for row in witness["phase_difference_witnesses"])
    assert all((right + delta) % 72 == left
               for row in witness["phase_difference_witnesses"]
               for left, right, delta in row)
    assert witness["hnan_tensor"] == bridge.EXPECTED_TENSOR
    assert witness["hnan_center_source"] == bridge.EXPECTED_TENSOR[1][1]
    assert witness["hnan_terminal_source"] == "xy+epsilon"
    assert witness["hash72_hydrated_vertex_count"] == 0
    assert witness["hash72_admitted_generator_roundtrip"] is None
    assert witness["generic_5184_to_72_compression_claim"] is False


def test_full_admitted_generator_hydrates_and_recompresses() -> None:
    half = frame(b"admitted")[:2592]
    raw = half + half[::-1]
    generator = HASH72_ALPHABET[::-1]
    witness = bridge.candidate_bridge(
        raw, generator, require_i065_palindrome=True, expand_generator=True,
    )
    assert bridge.recover_raw(witness) == raw
    assert witness["hash72_hydrated_vertex_count"] == 5184
    assert witness["hash72_admitted_generator_roundtrip"] is True
    assert witness["hash72_generator"] == generator
    assert witness["i065_palindrome_enforced"] is True
    assert witness["candidate_only"] is True
    assert witness["new_vm81_mutation_authority"] is False
    assert witness["new_hash72_commit_authority"] is False


def test_candidate_does_not_materialize_unneeded_vertices(monkeypatch) -> None:
    def forbidden(_word):
        raise AssertionError("unnecessary eager full Hash72 hydration")
    monkeypatch.setattr(bridge, "hash72_vertex_geometry", forbidden)
    witness = bridge.candidate_bridge(frame(b"fast"), HASH72_ALPHABET)
    assert witness["hash72_hydrated_vertex_count"] == 0


def test_i065_palindrome_is_explicit_admission_not_raw_transport() -> None:
    raw = "1" + "0" * 5183
    assert bridge.recover_raw(bridge.candidate_bridge(raw, HASH72_ALPHABET)) == raw
    with pytest.raises(I065HydrationError):
        bridge.candidate_bridge(
            raw, HASH72_ALPHABET, require_i065_palindrome=True
        )


@pytest.mark.parametrize("bad", ["0"*5183, "0"*5183+"X"])
def test_bad_raw_fail_closed(bad: str) -> None:
    with pytest.raises((ValueError, AssertionError)):
        bridge.candidate_bridge(bad, HASH72_ALPHABET)


@pytest.mark.parametrize("bad", ["0"*71, "?"*71 + "~"])
def test_bad_hash72_generator_rejected(bad: str) -> None:
    with pytest.raises(bridge.Phase5184BridgeError):
        bridge.candidate_bridge("0"*5184, bad)


def test_corrupted_source_witness_fails_closed() -> None:
    witness = bridge.candidate_bridge(frame(b"tamper"), HASH72_ALPHABET)
    witness["raw_bits"] = "0" * 5184
    with pytest.raises(bridge.Phase5184BridgeError):
        bridge.recover_raw(witness)


def test_lean_and_wolfram_proof_surfaces_present() -> None:
    root = Path(__file__).resolve().parents[2]
    lean = (root / "formal/lean/HHS/Pass220/HNANPhase5184.lean").read_text()
    wolfram = (
        root / "formal/wolfram/pass220_hnan_phase5184_lossless_bridge_v1.wl"
    ).read_text()
    for token in (
        "orderedTensorExact", "generatorExactRoundTrip",
        "rawExactRoundTrip", "rawInjectionForFixedGenerator",
        "arbitrary5184CompressionClaimed",
    ):
        assert token in lean
    for token in (
        "TestReport", "hnan-tensor-shape", "generator-inverse",
        "ordered-product-not-swappable", "palindrome-admission",
        "GenericUnconstrainedPayloadCompressionClaimed",
    ):
        assert token in wolfram


def test_corrupt_relative_phase_is_detected() -> None:
    witness = bridge.candidate_bridge(frame(b"phase-diff-tamper"), HASH72_ALPHABET)
    values = list(witness["phase_difference_witnesses"])
    first = list(values[0])
    left, right, delta = first[0]
    first[0] = (left, right, (delta + 1) % 72)
    values[0] = tuple(first)
    witness["phase_difference_witnesses"] = tuple(values)
    with pytest.raises(bridge.Phase5184BridgeError, match="PHASE_DIFFERENCE"):
        bridge.recover_raw(witness)
