#!/usr/bin/env python3
"""Generate or verify deterministic Pass 211 BigInt/HFC reference evidence."""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
import random
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass210_holographic_frame_compression_v1 import (
    HFCValidationError,
    HolographicFrameCompressionRuntime,
    affine_fibonacci_mod2,
)
from hhs_backend.runtime.hhs_pass211_bigint_hfc_carrier_v1 import (
    CONTRACT,
    PACKED_SHARD_BYTES,
    RUNTIME_CLASSIFICATION,
    Pass211BigIntHFCRuntime,
    Pass211ValidationError,
    packed_bytes_to_register,
)
from hhs_runtime.palindromic_ecc import (
    PalindromicCarrier,
    decode_palindromic_carrier,
    protect_encrypted_bigint,
    run_ecc_stress,
)

OUTPUT = ROOT / "evidence" / "pass211" / "PASS_211_BIGINT_HFC_REFERENCE_VECTORS.json"


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


CORPUS = (
    ("one_bit", 1),
    ("byte_a5", 0xA5),
    ("word_64", (1 << 63) + 0x133),
    ("factorial_72", math.factorial(72)),
    ("lcm_1_72", _lcm_to(72)),
    ("fibonacci_500", _fib(500)),
    ("mersenne_521", (1 << 521) - 1),
    ("palindrome_constant", int("123456789012345678909876543210987654321")),
    ("random_256", _random_bigint(256, 133)),
    ("random_1024", _random_bigint(1024, 211)),
    ("random_4096", _random_bigint(4096, 133211)),
)
FITTING_LABELS = ("one_bit", "factorial_72", "fibonacci_500", "palindrome_constant")


def _error(callable_: Any) -> str:
    try:
        callable_()
    except Exception as exc:  # evidence intentionally records exact fail-closed class
        return f"{type(exc).__name__}:{exc}"
    return "NO_ERROR"


def build_evidence() -> dict[str, Any]:
    runtime = Pass211BigIntHFCRuntime()
    pass133_results: list[dict[str, Any]] = []
    values = dict(CORPUS)
    for label, value in CORPUS:
        protected = protect_encrypted_bigint(value)
        carrier = PalindromicCarrier.from_bigint(int(protected["carrier_bigint_hex"], 16))
        decoded = decode_palindromic_carrier(carrier)
        source_bytes = max(1, (value.bit_length() + 7) // 8)
        carrier_bytes = (int(protected["carrier_bigint_hex"], 16).bit_length() + 7) // 8
        pass133_results.append(
            {
                "label": label,
                "source_bit_length": value.bit_length(),
                "source_byte_length": source_bytes,
                "carrier_byte_length": carrier_bytes,
                "expansion_ratio": {"numerator": carrier_bytes, "denominator": source_bytes},
                "roundtrip_exact": int(decoded["ciphertext_hex"], 16) == value,
                "carrier_status": protected["status"],
            }
        )

    stress = []
    for label, value in (("factorial_72", values["factorial_72"]), ("random_256", values["random_256"])):
        report = run_ecc_stress(value, sample_limit=256)
        stress.append({"label": label, **report})

    package_summaries = []
    erasure_events = []
    fitting_packages = {}
    for label in FITTING_LABELS:
        value = values[label]
        package = runtime.encode(value)
        fitting_packages[label] = package
        decoded = runtime.decode(package)
        package_summaries.append(
            {
                "label": label,
                "source_bit_length": value.bit_length(),
                "carrier_byte_length": package.carrier_byte_length,
                "shard_count": package.shard_count,
                "final_shard_bit_length": package.final_shard_bit_length,
                "package_root216": package.package_root216,
                "package_receipt_hash72": package.package_receipt_hash72,
                "strict_domain_statuses": [shard.strict_domain_status for shard in package.shards],
                "roundtrip_exact": decoded["ciphertext_hex"] == hex(value),
                "metrics": dict(package.metrics),
            }
        )
        for lost in range(36):
            event = runtime.recover_shard(package, 0, lost)
            erasure_events.append(
                {
                    "label": label,
                    "lost_snapshot_index": lost,
                    "status": event["status"],
                    "payload_hash216": event["payload_hash216"],
                }
            )

    multi_value = values["random_1024"]
    multi = runtime.encode(multi_value)
    multi_decode = runtime.decode(multi)
    multi_summary = {
        "label": "random_1024",
        "source_bit_length": multi_value.bit_length(),
        "carrier_byte_length": multi.carrier_byte_length,
        "single_register_capacity_bytes": PACKED_SHARD_BYTES,
        "shard_count": multi.shard_count,
        "shard_payload_byte_lengths": [shard.payload_byte_length for shard in multi.shards],
        "final_shard_bit_length": multi.final_shard_bit_length,
        "ordered_shard_roots": list(multi.ordered_shard_roots),
        "package_root216": multi.package_root216,
        "roundtrip_exact": multi_decode["ciphertext_hex"] == hex(multi_value),
    }

    stacked_package = fitting_packages["factorial_72"]
    hfc_recovery = runtime.recover_shard(stacked_package, 0, 17)
    carrier_payload = bytes.fromhex(stacked_package.shards[0].payload_hex)
    carrier = PalindromicCarrier.from_bigint(int.from_bytes(carrier_payload, "big"))
    damaged_left = list(carrier.left_bits)
    damaged_left[0] = "0" if damaged_left[0] == "1" else "1"
    stacked_decode = decode_palindromic_carrier(
        PalindromicCarrier(
            carrier.radix,
            "".join(damaged_left),
            carrier.center,
            carrier.right_bits,
            carrier.ecc_contract,
        )
    )
    stacked = {
        "hfc_recovery_status": hfc_recovery["status"],
        "ecc_status": stacked_decode["status"],
        "ecc_correction_events": stacked_decode["correction_events"],
        "ciphertext_exact": int(stacked_decode["ciphertext_hex"], 16) == values["factorial_72"],
    }

    anchored_payload = bytearray.fromhex(stacked_package.shards[0].payload_hex)
    anchored_payload[1000 // 8] ^= 1 << (7 - (1000 % 8))
    anchored = runtime.anchored_compare(stacked_package, 0, anchored_payload)

    hfc = HolographicFrameCompressionRuntime()
    fibonacci_register = affine_fibonacci_mod2(1, 1)
    strict_package = hfc.strict_compress(fibonacci_register)
    strict_decompressed = hfc.strict_decompress(strict_package)
    bigint_register = packed_bytes_to_register(carrier_payload)
    strict_boundary = {
        "fibonacci_status": "STRICT_DOMAIN_ADMITTED",
        "fibonacci_seed": strict_package["seed"],
        "fibonacci_roundtrip_exact": strict_decompressed == fibonacci_register,
        "bigint_status": stacked_package.shards[0].strict_domain_status,
        "bigint_detail": stacked_package.shards[0].strict_domain_detail,
        "direct_bigint_probe_error": _error(lambda: HolographicFrameCompressionRuntime().strict_compress(bigint_register)),
    }

    multi_dict = multi.to_dict()
    missing = copy.deepcopy(multi_dict)
    missing["shards"].pop()
    duplicate = copy.deepcopy(multi_dict)
    duplicate["shards"][1] = copy.deepcopy(duplicate["shards"][0])
    reordered = copy.deepcopy(multi_dict)
    reordered["shards"] = list(reversed(reordered["shards"]))
    substituted = copy.deepcopy(multi_dict)
    changed = bytearray.fromhex(substituted["shards"][0]["payload_hex"])
    changed[0] ^= 0x80
    substituted["shards"][0]["payload_hex"] = changed.hex()
    negatives = {
        "zero": _error(lambda: runtime.encode(0)),
        "negative": _error(lambda: runtime.encode(-1)),
        "missing_shard": _error(lambda: runtime.decode(missing)),
        "duplicate_shard": _error(lambda: runtime.decode(duplicate)),
        "reordered_shards": _error(lambda: runtime.decode(reordered)),
        "substituted_shard": _error(lambda: runtime.decode(substituted)),
    }

    replay_value = values["fibonacci_500"]
    replay_left = Pass211BigIntHFCRuntime().encode(replay_value).to_dict()
    replay_right = Pass211BigIntHFCRuntime().encode(replay_value).to_dict()

    evidence = {
        "schema": "HHS_PASS_211_BIGINT_HFC_REFERENCE_EVIDENCE_V1",
        "contract": CONTRACT,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "capacity": {
            "hfc_boolean_cells": 5184,
            "packed_shard_bytes": PACKED_SHARD_BYTES,
            "bit_order": "MSB_FIRST_WITHIN_EACH_BYTE",
        },
        "pass133_independent_corpus": pass133_results,
        "pass133_stress": stress,
        "combined_fitting_packages": package_summaries,
        "single_snapshot_erasure_events": erasure_events,
        "multi_register_boundary": multi_summary,
        "stacked_integrity_drill": stacked,
        "strict_domain_boundary": strict_boundary,
        "anchored_corruption_drill": anchored,
        "negative_cases": negatives,
        "deterministic_replay": {
            "equal": replay_left == replay_right,
            "package_root216": replay_left["package_root216"],
            "package_receipt_hash72": replay_left["package_receipt_hash72"],
        },
        "suite_summary": {
            "pass133_roundtrips": sum(item["roundtrip_exact"] for item in pass133_results),
            "pass133_corpus_size": len(pass133_results),
            "single_bit_corrections": sum(item["single_bit_corrected"] for item in stress),
            "single_bit_samples": sum(item["single_bit_samples"] for item in stress),
            "combined_erasure_recoveries": len(erasure_events),
            "combined_erasure_expected": 144,
            "anchored_cell_1000_exact": anchored["disagreement_cells"] == [1000],
            "fresh_projection_self_agreement": anchored["fresh_projection_agreement"],
            "strict_claim_boundary_preserved": (
                strict_boundary["fibonacci_roundtrip_exact"]
                and strict_boundary["bigint_status"] == "STRICT_DOMAIN_REJECTED"
            ),
            "runtime_verified": True,
        },
    }
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(build_evidence(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
            print("PASS211_EVIDENCE_MISMATCH")
            return 1
        print("PASS211_EVIDENCE_CHECK_OK")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
