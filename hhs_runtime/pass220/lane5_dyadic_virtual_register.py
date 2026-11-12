"""Exact read-only Lane 5 dyadic virtual-register candidates.

No VM81 admission, Hash72 mint, Hash216 persistence or canonical mutation.
Exact Fraction identities are projections, never OP_11 constitutive receipts.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt

RADIX = 72
WIDTH = 72
VM5184 = 5184

def _integer(value: int, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} requires an exact integer")
    return value

def dyadic(exponent: int) -> Fraction:
    n = _integer(exponent, "exponent")
    return Fraction(1 << n, 1) if n >= 0 else Fraction(1, 1 << -n)

def shell(depth: int) -> tuple[tuple[int, Fraction], ...]:
    n = _integer(depth, "depth")
    if n < 0:
        raise ValueError("negative shell depth")
    return tuple((k, dyadic(k)) for k in range(-n, n + 1))

def reciprocal_witness(exponent: int) -> bool:
    return dyadic(exponent) * dyadic(-exponent) == Fraction(1)

def encode_address(digits: tuple[int, ...]) -> int:
    if not isinstance(digits, tuple) or len(digits) != WIDTH:
        raise ValueError("expected 72 ordered radix-72 digits")
    result = 0
    for digit in reversed(digits):
        v = _integer(digit, "address digit")
        if not 0 <= v < RADIX:
            raise ValueError("radix-72 digit outside 0..71")
        result = result * RADIX + v
    return result

def decode_address(index: int) -> tuple[int, ...]:
    value = _integer(index, "address")
    if not 0 <= value < RADIX ** WIDTH:
        raise ValueError("address outside 72**72")
    result = []
    for _ in range(WIDTH):
        value, digit = divmod(value, RADIX)
        result.append(digit)
    return tuple(result)

def hydration_address(row: int, column: int) -> int:
    i = _integer(row, "row")
    j = _integer(column, "column")
    if not 0 <= i < RADIX or not 0 <= j < RADIX:
        raise ValueError("hydration coordinate outside 72x72")
    return RADIX * i + j

@dataclass(frozen=True)
class VirtualRegister:
    address: tuple[int, ...]
    exponent: int
    phase: str
    cell_type: str
    constructor: str
    provenance: str

    def __post_init__(self) -> None:
        encode_address(self.address)
        _integer(self.exponent, "exponent")
        for key in ("phase", "cell_type", "constructor", "provenance"):
            if not isinstance(getattr(self, key), str) or not getattr(self, key):
                raise ValueError(f"{key} must be a nonempty provenance-bearing string")

    @property
    def index(self) -> int:
        return encode_address(self.address)

    @property
    def quantization(self) -> Fraction:
        return dyadic(self.exponent)

def symmetric_witness(center: Fraction, exponent: int) -> dict[str, object]:
    """Rational projection where sqrt(2**n) is rational, else symbolic."""
    if type(center) is not Fraction:
        raise TypeError("center must be an exact Fraction")
    n = _integer(exponent, "exponent")
    delta = dyadic(n)
    if n % 2:
        return {"center": center, "delta": delta,
                "displacement": ("sqrt", delta),
                "p": None, "q": None,
                "pq": center * center - delta,
                "sum": 2 * center, "status": "SYMBOLIC_UNADMITTED"}
    d = dyadic(n // 2)
    p, q = center - d, center + d
    assert p + q == 2 * center and center * center - p * q == delta
    return {"center": center, "delta": delta, "displacement": d,
            "p": p, "q": q, "pq": p * q,
            "sum": p + q, "status": "EXACT_PROJECTION_UNADMITTED"}

def prime_center_witness(prime: int) -> dict[str, int]:
    """Candidate unit-defect witness with exact primality guard."""
    p = _integer(prime, "prime")
    if p < 3 or p % 2 == 0:
        raise ValueError("odd prime center required")
    for d in range(3, isqrt(p) + 1, 2):
        if p % d == 0:
            raise ValueError("center is composite")
    left, right = p - 1, p + 1
    assert p * p - left * right == 1
    return {"P": p, "p": left, "q": right, "modulus": left * right,
            "square": p * p, "defect": 1}


def symbolic_reciprocal_pair(exponent: int) -> dict[str, object]:
    """Typed exact two-radical candidate; never numerically collapses branches.

    For delta=2**n choose P=sqrt(1+delta), d=sqrt(delta).
    The conjugate product is one by polynomial identity, with distinct
    ordered operands. This is a symbolic projection, not OP_11 admission.
    """
    n = _integer(exponent, "exponent")
    delta = dyadic(n)
    center_squared = Fraction(1) + delta
    return {
        "schema": "HHS_LANE5_DYADIC_RECIPROCAL_PAIR_CANDIDATE_V1",
        "exponent": n,
        "delta": delta,
        "P": ("POSITIVE_SQRT", center_squared),
        "d": ("POSITIVE_SQRT", delta),
        "p": ("ORDERED_SUBTRACT", "P", "d"),
        "q": ("ORDERED_ADD", "P", "d"),
        "p_plus_q": ("TWICE", "P"),
        "p_times_q": Fraction(1),
        "difference_of_squares": center_squared - delta,
        "identities": ("P2_MINUS_PQ_EQUALS_DELTA", "P_PLUS_PQ_SYMMETRY", "PQ_EQUALS_ONE"),
        "operator_semantics": "TYPED_CONSTITUTIVE_UNRESOLVED",
        "admission": "CANDIDATE_ONLY",
    }


def prepare_lane5_hydration_candidate(
    register: VirtualRegister, *, witness: dict[str, object] | None = None
) -> dict[str, object]:
    """Build a read-only Lane 5 proposal, without side effects or receipts.

    Gate operator semantics are inherited from Pass148; they are not
    implemented here. The resulting proposal must be submitted through
    the existing VM81 admission and Hash72-before-Hash216 authority path.
    """
    if not isinstance(register, VirtualRegister):
        raise TypeError("exact VirtualRegister required")
    from hhs_runtime.pass148.registry import OPERATORS
    gate = OPERATORS["HHS_GATE_EQ"]
    if gate["commutative"] or gate["operator_id"] != "HHS_GATE_EQ":
        raise RuntimeError("inherited gate definition drift")
    if witness is None:
        witness = symbolic_reciprocal_pair(register.exponent)
    if not isinstance(witness, dict) or witness.get("exponent") != register.exponent:
        raise ValueError("symbolic witness exponent/address mismatch")
    if witness.get("admission") != "CANDIDATE_ONLY":
        raise ValueError("unverified witness cannot claim admission")
    # Reject edited, substituted, or incomplete proof terms. A candidate's
    # own assertion of exactness never supplies a native receipt.
    expected = symbolic_reciprocal_pair(register.exponent)
    if set(witness) != set(expected) or any(
        type(witness[key]) is not type(value) or witness[key] != value
        for key, value in expected.items()
    ):
        raise ValueError("symbolic reciprocal witness drift")
    return {
        "schema": "HHS_LANE5_DYADIC_VIRTUAL_HYDRATION_PROPOSAL_V1",
        "virtual_address": register.index,
        "radix72_address": register.address,
        "signed_exponent": register.exponent,
        "quantization": register.quantization,
        "phase": register.phase,
        "cell_type": register.cell_type,
        "constructor": register.constructor,
        "provenance": register.provenance,
        "inherited_gate_id": gate["operator_id"],
        "inherited_gate_semantics": gate["semantics"],
        "witness": dict(witness),
        "candidate_only": True,
        "requires": ("NATIVE_CPLUSPLUS_CELL_WALL", "SINGLETON_VM81_ADMISSION",
                     "HASH72_RECEIPT", "HASH216_LINEAGE", "REPLAY"),
        "canonical_hash_mutation": None,
    }


def bind_existing_pass159_provenance(
    register: VirtualRegister,
    provenance: dict[str, object],
    *,
    root: str | None = None,
) -> dict[str, object]:
    """Read-only handoff to the inherited Pass219 I157 source/VMIR contract.

    The returned fields describe independently supplied provenance metadata.
    They never claim that this module executed a frontend or VM81 admission.
    """
    if not isinstance(register, VirtualRegister):
        raise TypeError("exact VirtualRegister required")
    if not isinstance(provenance, dict):
        raise TypeError("Pass159 provenance mapping required")
    from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
        normalize_pass159_provenance,
        verify_frozen_source_identity,
    )
    # Verify the actual frozen source bytes in the checked-out repository.
    source_receipt = verify_frozen_source_identity(root)
    normalized = normalize_pass159_provenance(provenance)
    binding = normalized["provenance_binding_sha256"]
    if register.provenance != binding:
        raise ValueError("register provenance differs from Pass159 source/VMIR binding")
    proposal = prepare_lane5_hydration_candidate(register)
    return {
        "schema": "HHS_LANE5_DYADIC_PASS159_CANDIDATE_BINDING_V1",
        "proposal": proposal,
        "pass159_source_identity": source_receipt,
        "pass159_provenance": normalized,
        "provenance_binding_sha256": binding,
        "pass159_metadata_validated": True,
        "frontend_executed_here": False,
        "vm81_admitted": False,
        "hash72_minted": False,
        "hash216_persisted": False,
        "canonical_hash_mutation": None,
    }
