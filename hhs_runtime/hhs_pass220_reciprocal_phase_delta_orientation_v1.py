"""Pass 220 exact reciprocal phase-72 diagnostic and ordered HNAN obligation.

The scalar shadow is a diagnostic only. Native ordered reciprocal channels,
typed Delta, and HNAN center cannot be replaced by its scalar evaluation.
"""
from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
import json
from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import Phase72
from hhs_runtime.hhs_pass220_ordered_antipodal_phase72_v1 import (
    phase72_transport_witness,
)

SCHEMA = "HHS_PASS220_RECIPROCAL_PHASE_DELTA_ORIENTATION_V1"
EXPRESSION = "(((q-p)/(p-q))/u^72)*(((p-q)/(q-p))/u^36)/u^72=Delta"
TERMINAL = "AB/-P^4==P^4/-BA==u^(-36)/yx==u^72/xy=Delta"
ORDERED_CHANNELS = (("q-p", "p-q"), ("AB", "BA"), ("yx", "xy"))


class ReciprocalPhaseBoundaryError(ValueError):
    pass


def scalar_shadow(p: Fraction, q: Fraction) -> Fraction:
    """Exactly evaluate a conventional scalar comparison, not native closure."""
    if isinstance(p, (bool, float)) or isinstance(q, (bool, float)):
        raise ReciprocalPhaseBoundaryError("EXACT_RATIONAL_REQUIRED")
    p, q = Fraction(p), Fraction(q)
    if p == q:
        raise ReciprocalPhaseBoundaryError("TYPED_P_EQ_Q_BOUNDARY")
    # Root-of-unity powers are exact signs at 36 and 72.
    u72 = Fraction(1 if Phase72(72) == Phase72(0) else 0)
    u36 = Fraction(-1 if Phase72(36) == Phase72(-36) else 0)
    return ((q-p)/(p-q)/u72) * (((p-q)/(q-p))/u36)/u72


def reciprocal_phase_witness(p: Fraction, q: Fraction) -> dict:
    comparison = scalar_shadow(p, q)
    prior = phase72_transport_witness()
    if not prior["phase_full_is_identity"] or not prior["phase_half_square_is_identity"]:
        raise ReciprocalPhaseBoundaryError("PHASE72_INHERITED_INVARIANT_DRIFT")
    payload = {
        "schema": SCHEMA,
        "source_expression": EXPRESSION,
        "terminal_ordered_source": TERMINAL,
        "ordered_channel_pairs": ORDERED_CHANNELS,
        "scalar_shadow": [comparison.numerator, comparison.denominator],
        "scalar_shadow_equals_delta_one": comparison == 1,
        "typed_delta_target": "Delta=1",
        "phase72_parent_receipt_sha256": prior["candidate_receipt_sha256"],
        "phase36_antipodal": True,
        "phase72_identity": True,
        "native_hnan_orientation_closure_proven": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    payload["receipt_sha256"] = sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return payload
