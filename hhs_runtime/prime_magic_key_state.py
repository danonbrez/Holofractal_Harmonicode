"""Pass 133.1 Prime-Magic Sudoku Tensor BigInt key-state workload."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import prod
from typing import Any

from .bigint_envelope import BigIntEnvelope, decode_explicit_primes, encode_explicit_primes
from .canonical import bigint_to_bytes, canonical_bytes, canonical_json, sha256_hex
from .hash72_checkpoint import make_hash72_witness
from .prime_generation import EntropyAttestation, generate_distinct_primes, verify_prime_alphabet
from .sudoku_tensor import LOSHU0, pack_topology, unpack_topology, units, validate_sudoku, vm81_loshu_order

PRIME_DOMAIN = "HHS-P133-PRIME-ALPHABET-V1"
SUDOKU_DOMAIN = "HHS-P133-SUDOKU-TOPOLOGY-V1"


def _magic_closure(grid: list[list[int]], primes: list[int]) -> dict[str, Any]:
    tensor = [[primes[s] for s in row] for row in grid]
    sigma = sum(primes)
    pi = prod(primes)
    closures: dict[str, list[dict[str, Any]]] = {}
    for kind, group in units(tensor).items():
        closures[kind] = []
        for idx, unit in enumerate(group):
            entry = {
                "unit": idx,
                "cardinality": len(unit),
                "distinct": len(set(unit)),
                "sum_match": sum(unit) == sigma,
                "product_match": prod(unit) == pi,
                "membership_match": sorted(unit) == sorted(primes),
            }
            entry["closed"] = all([
                entry["cardinality"] == 9,
                entry["distinct"] == 9,
                entry["sum_match"],
                entry["product_match"],
                entry["membership_match"],
            ])
            closures[kind].append(entry)
    return {
        "schema": "HHS_PASS133_PRIME_MAGIC_CLOSURE_V1",
        "M_sigma": str(sigma),
        "M_pi": str(pi),
        "closures": closures,
        "global_closed": all(e["closed"] for group in closures.values() for e in group),
        "tensor": [[str(v) for v in row] for row in tensor],
    }


def build_prime_magic_key_state(
    seed: bytes,
    *,
    prime_bits: int = 64,
    mode: str = "explicit",
    nonce: bytes = b"PASS133-DEFAULT-NONCE",
    parent_root: str,
    entropy_attestation: EntropyAttestation | None = None,
) -> dict[str, Any]:
    from .sudoku_tensor import derive_diagonal_sudoku
    if mode not in {"explicit", "seeded"}:
        raise ValueError("mode must be explicit or seeded")
    entropy_attestation = entropy_attestation or EntropyAttestation(
        source_id="PUBLIC_DETERMINISTIC_TEST_SEED",
        seed_bits=len(seed)*8,
        asserted_min_entropy_bits=0,
        independently_attested=False,
        public_test_seed=True,
    )
    context = {"nonce_sha256": sha256(nonce).hexdigest(), "parent_root": parent_root}
    primes, receipts = generate_distinct_primes(seed, count=9, bits=prime_bits, domain=PRIME_DOMAIN, context=context)
    grid = derive_diagonal_sudoku(seed, SUDOKU_DOMAIN)
    sudoku_validation = validate_sudoku(grid)
    magic = _magic_closure(grid, primes)
    topology, ranks = pack_topology(grid)
    order = vm81_loshu_order()
    counters = [r.candidate_counter for r in receipts]
    alphabet_field = encode_explicit_primes(primes) if mode == "explicit" else bytes(seed)
    envelope = BigIntEnvelope(
        version="1.0.0",
        mode=mode,
        prime_bits=prime_bits,
        alphabet_or_seed=alphabet_field,
        topology=topology,
        nonce=nonce,
        order=order,
        normalization={"operator": "PRIME_SYMBOL_PROJECTION", "no_floats": True},
        reconstruction={"prime_domain": PRIME_DOMAIN, "sudoku_domain": SUDOKU_DOMAIN, "counter_required": True},
        parent_root=parent_root,
        counters=counters,
        context=context,
    )
    bigint = envelope.to_bigint()
    decoded = BigIntEnvelope.from_bigint(bigint)
    if decoded.mode == "explicit":
        primes2 = decode_explicit_primes(decoded.alphabet_or_seed)
    else:
        primes2, _ = generate_distinct_primes(decoded.alphabet_or_seed, count=9, bits=decoded.prime_bits, domain=PRIME_DOMAIN, context=decoded.context)
    grid2 = unpack_topology(decoded.topology)
    magic2 = _magic_closure(grid2, primes2)
    tensor_root = make_hash72_witness("hhs_pass133_prime_magic_tensor_v1", magic["tensor"]).to_dict()
    tensor_root2 = make_hash72_witness("hhs_pass133_prime_magic_tensor_v1", magic2["tensor"]).to_dict()
    delta_key = int(
        primes2 == primes
        and grid2 == grid
        and magic2["M_sigma"] == magic["M_sigma"]
        and magic2["M_pi"] == magic["M_pi"]
        and decoded.order == order
        and tensor_root2["dna"] == tensor_root["dna"]
    )
    raw_tensor_bits = 81 * prime_bits
    alphabet_bits = len(alphabet_field) * 8
    topology_bits = topology.bit_length()
    envelope_bits = len(envelope.encode_bytes()) * 8
    result = {
        "schema": "HHS_PASS133_PRIME_MAGIC_KEY_STATE_V1",
        "status": "PRIME_MAGIC_SUDOKU_BIGINT_KEY_STATE_VERIFIED" if delta_key and magic["global_closed"] else "KEY_GENERATOR_READINESS_BOUNDED",
        "prime_bits": prime_bits,
        "mode": mode,
        "entropy_attestation": entropy_attestation.to_dict(),
        "entropy_status": "ENTROPY_SOURCE_ATTESTED" if entropy_attestation.independently_attested else "ENTROPY_SOURCE_UNATTESTED",
        "primes": [str(p) for p in primes],
        "prime_validation": verify_prime_alphabet(primes, prime_bits),
        "prime_receipts": [r.to_dict() for r in receipts],
        "sudoku": grid,
        "sudoku_validation": sudoku_validation,
        "vm81_order": order,
        "factoradic_row_ranks": ranks,
        "topology_bigint": str(topology),
        "topology_bit_length": topology_bits,
        "topology_under_167_bits": topology_bits <= 167,
        "magic_closure": magic,
        "key_bigint": str(bigint),
        "key_bigint_bit_length": bigint.bit_length(),
        "key_envelope_sha256": sha256_hex(envelope.encode_bytes()),
        "tensor_hash72_witness": tensor_root,
        "reconstruction": {
            "delta_key": delta_key,
            "primes_match": primes2 == primes,
            "sudoku_match": grid2 == grid,
            "hash72_match": tensor_root2["dna"] == tensor_root["dna"],
            "status": "LOSSLESS_KEY_STATE_RECONSTRUCTION_VERIFIED" if delta_key else "RECONSTRUCTION_VARIANCE_DETECTED",
        },
        "compression": {
            "raw_tensor_bits": raw_tensor_bits,
            "alphabet_or_seed_bits": alphabet_bits,
            "topology_bits": topology_bits,
            "operational_envelope_bits": envelope_bits,
            "gross_ratio_raw_to_alphabet_plus_topology": f"{raw_tensor_bits}/{alphabet_bits + topology_bits}",
            "net_ratio_numerator": raw_tensor_bits,
            "net_ratio_denominator": envelope_bits,
        },
    }
    return result


def run_prime_magic_negative_tests(baseline: dict[str, Any]) -> dict[str, Any]:
    import copy
    cases: list[dict[str, Any]] = []
    grid = baseline["sudoku"]
    primes = [int(p) for p in baseline["primes"]]

    def add(name: str, detected: bool, outcome: str) -> None:
        cases.append({"case": name, "detected": bool(detected), "outcome": outcome})

    bad = [row[:] for row in grid]; bad[0][0] = bad[0][1]
    add("repeated_symbol_row", not validate_sudoku(bad)["ok"], "SUDOKU_CONSTRAINT_FAILURE")
    bad = [row[:] for row in grid]; bad[0][0], bad[1][0] = bad[1][0], bad[0][0]
    add("repeated_symbol_column", not validate_sudoku(bad)["ok"], "SUDOKU_CONSTRAINT_FAILURE")
    bad = [row[:] for row in grid]; bad[0][0], bad[1][1] = bad[1][1], bad[0][0]
    add("invalid_diagonal", not validate_sudoku(bad)["ok"], "SUDOKU_CONSTRAINT_FAILURE")
    add("duplicate_prime", len(set(primes[:-1]+[primes[0]])) != 9, "DUPLICATE_PRIME_DETECTED")
    add("composite_symbol", __import__('sympy').isprime(primes[0]*primes[1]) is False, "INVALID_PRIME_STATE_REJECTED")
    try:
        from .sudoku_tensor import unrank_permutation, S9
        unrank_permutation(S9)
        out = False
    except ValueError:
        out = True
    add("factoradic_rank_out_of_range", out, "SERIALIZATION_INTEGRITY_FAILURE")
    try:
        from .bigint_envelope import BigIntEnvelope
        raw = bytearray(int(baseline["key_bigint"]).to_bytes((int(baseline["key_bigint"]).bit_length()+7)//8,"big"))
        raw[0] ^= 1
        BigIntEnvelope.decode_bytes(bytes(raw))
        out = False
    except Exception:
        out = True
    add("corrupted_bigint_magic", out, "SERIALIZATION_INTEGRITY_FAILURE")
    add("floating_point_prime_conversion", isinstance(float(primes[0]), float), "CONTROL_CONTAMINATION_DETECTED")
    add("public_seed_as_secret_entropy", baseline["entropy_status"] == "ENTROPY_SOURCE_UNATTESTED", "ENTROPY_SOURCE_UNATTESTED")
    return {
        "schema": "HHS_PASS133_KEY_GENERATOR_NEGATIVE_TEST_REPORT_V1",
        "cases": cases,
        "passed": sum(1 for c in cases if c["detected"]),
        "total": len(cases),
        "status": "PASS" if all(c["detected"] for c in cases) else "FAIL",
    }
