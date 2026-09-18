"""Exact Lane 5 Fibonacci-trinity transformation preservation witness.

This surface treats a valid additive trinity (A,B,C) with C=A+B as a typed
square-state / BigInt-reference branch.  The constructor geometry

    (C-B, C-A, A+B) == (A,B,C)

is independent of the prime factorization of A, B, and C.  A transformation
between branches preserves the checked geometry when both branches execute the
same constructor and independently close to the normalized Genesis residual.

The Genesis residual here is a proof residual over the already initialized
Genesis geometry.  It is not a replacement serialization of the Genesis ROM.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isqrt
from typing import Any, Dict, Mapping, Sequence, Tuple


SCHEMA = "HHS_PASS219_LANE5_FIBONACCI_GENESIS_PRESERVATION_V1"
PROFILE = "PASS219-LANE5-FIBONACCI-GENESIS-PRESERVATION-v1"
CONSTRUCTOR_SURFACE = "(C-B,C-A,A+B)==(A,B,C)"
RECURRENCE_SURFACE = "C=A+B"
GENESIS_RESIDUAL = (0, 0, 0)
GENESIS_ADDRESS_COUNT = 81 * 64
HASH72_ADDRESS_COUNT = 72 * 72
INCIDENCE = ((0, 1), (1, 2), (2, 0))
PRODUCT_DEPENDENCIES = ((0, 1), (1, 2), (2, 0))


class Lane5FibonacciGenesisPreservationError(ValueError):
    pass


def _exact_positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Lane5FibonacciGenesisPreservationError(
            f"{name}_MUST_BE_EXACT_INTEGER"
        )
    if value <= 0:
        raise Lane5FibonacciGenesisPreservationError(
            f"{name}_MUST_BE_POSITIVE"
        )
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _seal(receipt: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(receipt)
    payload["receipt_sha256"] = sha256(
        _stable_json(payload).encode("utf-8")
    ).hexdigest()
    return payload


def prime_factorization(value: int) -> Tuple[Tuple[int, int], ...]:
    """Return the exact prime-exponent fingerprint of a positive integer."""
    n = _exact_positive_int(value, "FACTOR_VALUE")
    if n == 1:
        return ()
    out = []
    exponent = 0
    while n % 2 == 0:
        exponent += 1
        n //= 2
    if exponent:
        out.append((2, exponent))
    p = 3
    while p <= isqrt(n):
        exponent = 0
        while n % p == 0:
            exponent += 1
            n //= p
        if exponent:
            out.append((p, exponent))
        p += 2
    if n > 1:
        out.append((n, 1))
    return tuple(out)


def admit_fibonacci_trinity(a2: Any, b2: Any, c2: Any) -> Tuple[int, int, int]:
    """Admit a generalized Fibonacci trinity of square-state references."""
    a = _exact_positive_int(a2, "A2")
    b = _exact_positive_int(b2, "B2")
    c = _exact_positive_int(c2, "C2")
    if a + b != c:
        raise Lane5FibonacciGenesisPreservationError(
            "FIBONACCI_TRINITY_RECURRENCE_MISMATCH"
        )
    return (a, b, c)


def branch_geometry(a2: Any, b2: Any, c2: Any) -> Dict[str, Any]:
    """Build one exact branch and prove self-reconstruction + Genesis closure."""
    trinity = admit_fibonacci_trinity(a2, b2, c2)
    a, b, c = trinity

    reconstruction = (c - b, c - a, a + b)
    residual = tuple(
        reconstruction[index] - trinity[index] for index in range(3)
    )
    if reconstruction != trinity or residual != GENESIS_RESIDUAL:
        raise Lane5FibonacciGenesisPreservationError(
            "CONSTRUCTOR_GENESIS_CLOSURE_MISMATCH"
        )

    edge_values = (
        (a, b),
        (b, c),
        (c, a),
    )
    product_values = (
        a * b,
        b * c,
        c * a,
    )
    factorization = tuple(prime_factorization(value) for value in trinity)

    return {
        "trinity": trinity,
        "recurrence_surface": RECURRENCE_SURFACE,
        "constructor_surface": CONSTRUCTOR_SURFACE,
        "constructor_reconstruction": reconstruction,
        "genesis_normalization_residual": residual,
        "genesis_normalized": residual == GENESIS_RESIDUAL,
        "incidence": INCIDENCE,
        "directed_edges": edge_values,
        "product_dependency_edges": PRODUCT_DEPENDENCIES,
        "recursive_squared_product_values": product_values,
        "prime_quantization_fingerprint": factorization,
        "prime_factorization_used_for_admission": False,
    }


def transformation_preservation_witness(
    source: Sequence[Any],
    target: Sequence[Any],
    *,
    require_fingerprint_change: bool = True,
) -> Dict[str, Any]:
    """Prove geometry-preserving branch transformation with Genesis closure."""
    if len(source) != 3 or len(target) != 3:
        raise Lane5FibonacciGenesisPreservationError(
            "TRINITY_ARITY_MISMATCH"
        )

    source_branch = branch_geometry(source[0], source[1], source[2])
    target_branch = branch_geometry(target[0], target[1], target[2])

    source_fp = source_branch["prime_quantization_fingerprint"]
    target_fp = target_branch["prime_quantization_fingerprint"]
    fingerprint_changed = source_fp != target_fp
    if require_fingerprint_change and not fingerprint_changed:
        raise Lane5FibonacciGenesisPreservationError(
            "PRIME_FINGERPRINT_DID_NOT_CHANGE"
        )

    geometry_preserved = (
        source_branch["incidence"] == target_branch["incidence"] == INCIDENCE
        and source_branch["product_dependency_edges"]
        == target_branch["product_dependency_edges"]
        == PRODUCT_DEPENDENCIES
        and source_branch["constructor_surface"]
        == target_branch["constructor_surface"]
        == CONSTRUCTOR_SURFACE
        and source_branch["genesis_normalized"]
        and target_branch["genesis_normalized"]
    )
    genesis_closure_equal = (
        source_branch["genesis_normalization_residual"]
        == target_branch["genesis_normalization_residual"]
        == GENESIS_RESIDUAL
    )
    information_preserved = geometry_preserved and genesis_closure_equal

    if not information_preserved:
        raise Lane5FibonacciGenesisPreservationError(
            "TRANSFORMATION_INFORMATION_PRESERVATION_FAILED"
        )

    receipt: Dict[str, Any] = {
        "schema": SCHEMA,
        "profile": PROFILE,
        "source": source_branch,
        "target": target_branch,
        "prime_quantization_fingerprint_changed": fingerprint_changed,
        "prime_factorization_is_geometry_independent": True,
        "geometry_preserved": geometry_preserved,
        "genesis_closure_equal": genesis_closure_equal,
        "normalized_genesis_residual": GENESIS_RESIDUAL,
        "transformation_information_preserved": information_preserved,
        "genesis_geometry_initialized": True,
        "genesis_address_count": GENESIS_ADDRESS_COUNT,
        "hash72_address_count": HASH72_ADDRESS_COUNT,
        "address_geometry_identity": GENESIS_ADDRESS_COUNT == HASH72_ADDRESS_COUNT == 5184,
        "projection_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)
