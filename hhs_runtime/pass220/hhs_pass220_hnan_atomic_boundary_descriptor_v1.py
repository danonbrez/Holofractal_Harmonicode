"""Pass 220: fail-closed eight-sector quantum boundary admission descriptor.

Candidate-only. This module cannot mutate particle physics, create HNAN gates,
prove hydrogen, or mint VM81/Hash72/Hash216 receipts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

HNAN_OUTER_ADDRESSES = ("000", "001", "010", "011", "100", "101", "110", "111")
HNAN_OUTER_TERMS = ("xy", "x+y", "yx", "xy-zw", "wz-yx", "wz", "z+w", "zw")
CALIBRATION = ("-180/72", "108/72", "180/72")
ROOT_MODULUS = 72
SERIALIZATION_HZ = 81


@dataclass(frozen=True)
class Boundary:
    address: str
    ordered_term: str
    equation_id: str
    equation_digest: str
    witness_id: str


@dataclass(frozen=True)
class BoundaryInspection:
    candidate: bool
    reasons: Tuple[str, ...]
    addresses: Tuple[str, ...]
    carrier_modulus: int = ROOT_MODULUS
    serialization_hz: int = SERIALIZATION_HZ
    calibration: Tuple[str, ...] = CALIBRATION
    native_admitted: bool = False
    hydrogen_verified: bool = False


def inspect_boundaries(boundaries: Tuple[Boundary, ...]) -> BoundaryInspection:
    """Validate descriptor completeness only; never assert formal proof.

    A witness ID denotes a requested proof reference, not proof validity.
    Sector order and terms follow the fixed outer HNAN positions; no
    commutation or inferred phase permutation is allowed.
    """
    reasons = []
    if len(boundaries) != 8:
        reasons.append("exactly_eight_boundaries_required")
    for i, entry in enumerate(boundaries):
        if not isinstance(entry, Boundary):
            reasons.append("invalid_boundary_type")
            continue
        if i >= 8 or entry.address != HNAN_OUTER_ADDRESSES[i]:
            reasons.append("ordered_hnan_address_mismatch")
        if i >= 8 or entry.ordered_term != HNAN_OUTER_TERMS[i]:
            reasons.append("ordered_hnan_term_mismatch")
        if not all(isinstance(x, str) and x.strip()
                   for x in (entry.equation_id, entry.equation_digest, entry.witness_id)):
            reasons.append("missing_equation_or_witness_reference")
    eq_ids = [x.equation_id for x in boundaries if isinstance(x, Boundary)]
    digests = [x.equation_digest for x in boundaries if isinstance(x, Boundary)]
    if len(set(eq_ids)) != len(eq_ids):
        reasons.append("duplicate_equation_identity")
    if len(set(digests)) != len(digests):
        reasons.append("duplicate_equation_digest")
    return BoundaryInspection(not reasons, tuple(dict.fromkeys(reasons)),
                              tuple(x.address for x in boundaries if isinstance(x, Boundary)))
