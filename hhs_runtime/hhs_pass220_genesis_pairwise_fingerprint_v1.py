"""Genesis-relative 5184 pair fingerprint candidate using inherited I002 service.

This adapter does not claim native gyroscopic closure or mint Hash216 receipts.
"""
from __future__ import annotations
from hashlib import sha256
import json
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    coordinate_5184, prime_modular_fingerprint, DEFAULT_PRIMES,
)

SCHEMA = "HHS_PASS220_GENESIS_PAIRWISE_FINGERPRINT_CANDIDATE_V1"


def _fingerprint(value, primes):
    if type(value) is not int or value < 0:
        raise ValueError("NONNEGATIVE_EXACT_BIGINT_REQUIRED")
    return prime_modular_fingerprint(value, primes)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def derive_genesis_pair(*, index_a: int, index_b: int,
                        value_a: int, value_b: int,
                        genesis_identity: str, genesis_value: int = 0,
                        primes=DEFAULT_PRIMES) -> dict:
    """Ordered pair, with independently fingerprinted genesis-relative residues."""
    if not isinstance(genesis_identity, str) or not genesis_identity:
        raise ValueError("GENESIS_IDENTITY_REQUIRED")
    a = coordinate_5184(index_a)
    b = coordinate_5184(index_b)
    g = _fingerprint(genesis_value, primes)
    f_a = _fingerprint(value_a, primes)
    f_b = _fingerprint(value_b, primes)
    residues = tuple((r_a-r_b) % prime for r_a,r_b,prime in
                     zip(f_a["residues"],f_b["residues"],f_a["primes"]))
    # Shared exact 5184/u72 phase constraints from inherited Platonic contract.
    # This is a candidate projection, not the native gyroscopic verifier.
    factorizations = ((72, 72), (64, 81), (36, 144), (48, 108))
    if any(a * b != 5184 for a, b in factorizations):
        raise ValueError("INHERITED_QUANTIZATION_FAILURE")
    source_phase, target_phase = index_a % 72, index_b % 72
    geometry = {
        "factorizations": factorizations,
        "u72_phase_source": source_phase,
        "u72_phase_target": target_phase,
        "forward_step": (target_phase - source_phase) % 72,
        "reverse_step": (source_phase - target_phase) % 72,
        "phase_ladder": (0, 9, 18, 36, 72),
        "pentagon_closure": 5 * 72 == 360,
        "dodecahedron_incidence": 5 * 12 == 2 * 30
            and 3 * 20 == 2 * 30 and 20 - 30 + 12 == 2,
    }
    if not geometry["pentagon_closure"] or not geometry["dodecahedron_incidence"]:
        raise ValueError("PLATONIC_CLOSURE_FAILURE")
    payload = {"schema": SCHEMA, "genesis_identity": genesis_identity,
               "genesis_fingerprint": g,
               "source": {"coordinate": a, "fingerprint": f_a},
               "target": {"coordinate": b, "fingerprint": f_b},
               "ordered_pair_residues": residues,
               "inherited_platonic_phase_projection": geometry,
               "genesis_relative_source": tuple(
                   (x-y)%p for x,y,p in zip(f_a["residues"],g["residues"],f_a["primes"])),
               "genesis_relative_target": tuple(
                   (x-y)%p for x,y,p in zip(f_b["residues"],g["residues"],f_b["primes"])),
               "gyroscopic_orientation_native_verified": False,
               "signed_hash216_closure_verified": False,
               "candidate_only": True}
    return {**payload, "candidate_proof_sha256": sha256(_canonical(payload).encode()).hexdigest()}


def replay_genesis_pair(record, **inputs):
    expected = derive_genesis_pair(**inputs)
    if record != expected:
        raise ValueError("GENESIS_PAIR_REPLAY_MISMATCH")
    return expected


def native_ordered_phase_pair(*, index_a: int, index_b: int,
                              value_a: int, value_b: int,
                              genesis_identity: str, genesis_value: int = 0,
                              primes=DEFAULT_PRIMES) -> dict:
    """Bind candidate pair to inherited compiled C ABI phase products.

    Fail closed when native runtime is unavailable. This does not itself
    attest Genesis ancestry or mint a Hash216 closure.
    """
    from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactRuntimeBridge

    witness = derive_genesis_pair(
        index_a=index_a, index_b=index_b, value_a=value_a,
        value_b=value_b, genesis_identity=genesis_identity,
        genesis_value=genesis_value, primes=primes,
    )
    if not HHSExactRuntimeBridge.validate():
        raise ValueError("NATIVE_EXACT_ABI_NOT_VALIDATED")
    left_a = HHSExactRuntimeBridge.address_decode(index_a)
    left_b = HHSExactRuntimeBridge.address_decode(index_b)
    if left_a[0] != index_a // 64 or left_b[0] != index_b // 64:
        raise ValueError("NATIVE_ADDRESS_MISMATCH")
    forward = HHSExactRuntimeBridge.phase_product(left_a[1], left_b[2])
    reverse = HHSExactRuntimeBridge.phase_product(left_b[1], left_a[2])
    if forward["left_basis"] != left_a[1] or forward["right_basis"] != left_b[2]:
        raise ValueError("NATIVE_ORDERED_PHASE_MISMATCH")
    if reverse["left_basis"] != left_b[1] or reverse["right_basis"] != left_a[2]:
        raise ValueError("NATIVE_REVERSE_PHASE_MISMATCH")
    extension = {
        "native_5184_source_address": list(left_a),
        "native_5184_target_address": list(left_b),
        "native_forward_phase_product": forward,
        "native_reverse_phase_product": reverse,
        "native_exact_phase_abi_verified": True,
        "native_genesis_ancestry_verified": False,
        "native_gyroscopic_global_closure_verified": False,
    }
    payload = dict(witness)
    payload["native_phase_evidence"] = extension
    payload["candidate_proof_sha256"] = sha256(
        _canonical({k: v for k, v in payload.items()
                    if k != "candidate_proof_sha256"}).encode()
    ).hexdigest()
    return payload


def replay_native_ordered_phase_pair(record, **inputs):
    expected = native_ordered_phase_pair(**inputs)
    if record != expected:
        raise ValueError("NATIVE_PHASE_PAIR_REPLAY_MISMATCH")
    return expected
