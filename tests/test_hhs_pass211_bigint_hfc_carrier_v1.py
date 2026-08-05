from __future__ import annotations

import copy
import math
import random

import pytest

from hhs_backend.runtime.hhs_pass210_holographic_frame_compression_v1 import (
    HFCValidationError,
    HolographicFrameCompressionRuntime,
    affine_fibonacci_mod2,
)
from hhs_backend.runtime.hhs_pass211_bigint_hfc_carrier_v1 import (
    PACKED_SHARD_BYTES,
    Pass211BigIntHFCRuntime,
    Pass211ValidationError,
    packed_bytes_to_register,
    register_to_packed_bytes,
)
from hhs_runtime.palindromic_ecc import (
    PalindromicCarrier,
    decode_palindromic_carrier,
    protect_encrypted_bigint,
    run_ecc_stress,
)


def _fib(index: int) -> int:
    left, right = 0, 1
    for _ in range(index):
        left, right = right, left + right
    return left


def _lcm_to(limit: int) -> int:
    value = 1
    for item in range(1, limit + 1):
        value = math.lcm(value, item)
    return value


def _random_bigint(bits: int, seed: int) -> int:
    generator = random.Random(seed)
    return generator.getrandbits(bits) | (1 << (bits - 1)) | 1


PALINDROME_CONSTANT = int("123456789012345678909876543210987654321")
PASS133_CORPUS = (
    1,
    0xA5,
    (1 << 63) + 0x133,
    math.factorial(72),
    _lcm_to(72),
    _fib(500),
    (1 << 521) - 1,
    PALINDROME_CONSTANT,
    _random_bigint(256, 133),
    _random_bigint(1024, 211),
    _random_bigint(4096, 133211),
)
FITTING_CORPUS = (
    1,
    math.factorial(72),
    _fib(500),
    PALINDROME_CONSTANT,
)


def test_pass133_independent_corpus_roundtrips_11_of_11() -> None:
    for value in PASS133_CORPUS:
        protected = protect_encrypted_bigint(value)
        assert protected["status"] == "PALINDROMIC_ECC_BIGINT_RECONSTRUCTION_VERIFIED"
        carrier = PalindromicCarrier.from_bigint(int(protected["carrier_bigint_hex"], 16))
        decoded = decode_palindromic_carrier(carrier)
        assert int(decoded["ciphertext_hex"], 16) == value


def test_pass133_single_bit_stress_512_and_double_error_fail_closed() -> None:
    for value in (math.factorial(72), _random_bigint(256, 133)):
        report = run_ecc_stress(value, sample_limit=256)
        assert report["single_bit_samples"] == 256
        assert report["single_bit_corrected"] == 256
        assert report["double_error_fail_closed"] is True
        assert report["status"] == "PASS"


def test_bit_packing_is_exact_648_byte_capacity() -> None:
    payload = bytes((index * 73 + 19) % 256 for index in range(PACKED_SHARD_BYTES))
    register = packed_bytes_to_register(payload)
    assert len(register) == 5184
    assert set(register) <= {0, 1}
    assert register_to_packed_bytes(register, 5184) == payload


def test_combined_four_fitting_packages_survive_all_36_erasures() -> None:
    runtime = Pass211BigIntHFCRuntime()
    recovery_count = 0
    for value in FITTING_CORPUS:
        package = runtime.encode(value)
        assert package.shard_count == 1
        assert package.carrier_byte_length <= PACKED_SHARD_BYTES
        assert runtime.decode(package)["ciphertext_hex"] == hex(value)
        for lost_index in range(36):
            recovery = runtime.recover_shard(package, 0, lost_index)
            assert recovery["status"] == "PASS211_SHARD_ERASURE_RECOVERY_VERIFIED"
            recovery_count += 1
    assert recovery_count == 144


def test_multiregister_1024_bit_payload_roundtrips() -> None:
    value = _random_bigint(1024, 211)
    runtime = Pass211BigIntHFCRuntime()
    package = runtime.encode(value)
    assert package.carrier_byte_length > PACKED_SHARD_BYTES
    assert package.shard_count >= 2
    assert package.metrics["multi_register_required"] is True
    assert runtime.decode(package)["ciphertext_hex"] == hex(value)


def test_stacked_hfc_erasure_then_pass133_ecc_correction() -> None:
    value = math.factorial(72)
    runtime = Pass211BigIntHFCRuntime()
    package = runtime.encode(value)
    assert runtime.recover_shard(package, 0, 17)["status"] == "PASS211_SHARD_ERASURE_RECOVERY_VERIFIED"
    payload = bytes.fromhex(package.shards[0].payload_hex)
    carrier = PalindromicCarrier.from_bigint(int.from_bytes(payload, "big"))
    damaged_left = list(carrier.left_bits)
    damaged_left[0] = "0" if damaged_left[0] == "1" else "1"
    damaged = PalindromicCarrier(
        radix=carrier.radix,
        left_bits="".join(damaged_left),
        center=carrier.center,
        right_bits=carrier.right_bits,
        ecc_contract=carrier.ecc_contract,
    )
    decoded = decode_palindromic_carrier(damaged)
    assert int(decoded["ciphertext_hex"], 16) == value
    assert decoded["correction_events"] == 1
    assert decoded["status"] == "ECC_ERROR_CORRECTED"


def test_strict_domain_boundary_is_preserved() -> None:
    hfc = HolographicFrameCompressionRuntime()
    fibonacci_register = affine_fibonacci_mod2(1, 1)
    strict_package = hfc.strict_compress(fibonacci_register)
    assert hfc.strict_decompress(strict_package) == fibonacci_register

    package = Pass211BigIntHFCRuntime().encode(math.factorial(72))
    assert package.shards[0].strict_domain_status == "STRICT_DOMAIN_REJECTED"
    assert package.shards[0].strict_domain_detail == "HFC_STRICT_COMPRESSION_DOMAIN_WITNESS_REQUIRED"
    with pytest.raises(HFCValidationError, match="DOMAIN_WITNESS_REQUIRED"):
        HolographicFrameCompressionRuntime().strict_compress(
            packed_bytes_to_register(bytes.fromhex(package.shards[0].payload_hex))
        )


def test_anchored_comparison_localizes_cell_1000_and_fresh_self_agrees() -> None:
    runtime = Pass211BigIntHFCRuntime()
    package = runtime.encode(math.factorial(72))
    payload = bytearray.fromhex(package.shards[0].payload_hex)
    payload[1000 // 8] ^= 1 << (7 - (1000 % 8))
    verdict = runtime.anchored_compare(package, 0, payload)
    assert verdict["status"] == "ANCHORED_DISAGREEMENT_LOCATED"
    assert verdict["disagreement_cells"] == [1000]
    assert verdict["fresh_projection_agreement"] is True
    assert verdict["fresh_projection_self_consistency_is_not_historical_integrity"] is True
    assert sorted(verdict["surviving_witnesses"]) == [
        "stored_frame",
        "stored_hash216",
        "stored_hash72",
        "stored_phase",
    ]
    assert not any(verdict["fresh_anchor_matches"].values())


def test_exact_fresh_read_verifies_all_anchors() -> None:
    runtime = Pass211BigIntHFCRuntime()
    package = runtime.encode(PALINDROME_CONSTANT)
    payload = bytes.fromhex(package.shards[0].payload_hex)
    verdict = runtime.anchored_compare(package, 0, payload)
    assert verdict["status"] == "ANCHORED_WITNESSES_VERIFIED"
    assert verdict["disagreement_cells"] == []
    assert all(verdict["fresh_anchor_matches"].values())


def test_package_is_deterministic_across_clean_runtimes() -> None:
    value = _fib(500)
    left = Pass211BigIntHFCRuntime().encode(value).to_dict()
    right = Pass211BigIntHFCRuntime().encode(value).to_dict()
    assert left == right


def test_missing_duplicate_reordered_and_substituted_shards_fail_closed() -> None:
    runtime = Pass211BigIntHFCRuntime()
    package = runtime.encode(_random_bigint(1024, 211)).to_dict()
    assert len(package["shards"]) >= 2

    missing = copy.deepcopy(package)
    missing["shards"].pop()
    with pytest.raises(Pass211ValidationError, match="MISSING_SHARD"):
        runtime.decode(missing)

    duplicate = copy.deepcopy(package)
    duplicate["shards"][1] = copy.deepcopy(duplicate["shards"][0])
    with pytest.raises(Pass211ValidationError, match="DUPLICATE_SHARD"):
        runtime.decode(duplicate)

    reordered = copy.deepcopy(package)
    reordered["shards"] = list(reversed(reordered["shards"]))
    with pytest.raises(Pass211ValidationError, match="SHARD_ORDER_VIOLATION"):
        runtime.decode(reordered)

    substituted = copy.deepcopy(package)
    payload = bytearray.fromhex(substituted["shards"][0]["payload_hex"])
    payload[0] ^= 0x80
    substituted["shards"][0]["payload_hex"] = payload.hex()
    with pytest.raises(Pass211ValidationError, match="SHARD_SUBSTITUTION_DETECTED"):
        runtime.decode(substituted)


def test_receipt_root_metrics_and_pass133_witness_tampering_fail_closed() -> None:
    runtime = Pass211BigIntHFCRuntime()
    package = runtime.encode(math.factorial(72)).to_dict()

    receipt = copy.deepcopy(package)
    receipt["package_receipt_hash72"] = "0" * 72
    with pytest.raises(Pass211ValidationError, match="PACKAGE_RECEIPT_MISMATCH"):
        runtime.decode(receipt)

    metrics = copy.deepcopy(package)
    metrics["metrics"]["native_packed_capacity_bytes"] += 1
    with pytest.raises(Pass211ValidationError, match="METRICS_MISMATCH"):
        runtime.decode(metrics)

    witness = copy.deepcopy(package)
    witness["pass133_hash72_digest"] = "0" * len(witness["pass133_hash72_digest"])
    with pytest.raises(Pass211ValidationError, match="PASS133_HASH72_WITNESS_MISMATCH"):
        runtime.decode(witness)


def test_zero_and_negative_values_are_rejected_by_pass133_envelope() -> None:
    runtime = Pass211BigIntHFCRuntime()
    for value in (0, -1, -133):
        with pytest.raises(Pass211ValidationError, match="PASS133_ENVELOPE_REJECTED"):
            runtime.encode(value)
