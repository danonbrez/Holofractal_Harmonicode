"""Pass 220 I011: exact Möbius quarter-phase and harmonic coherence witness.

Projection/witness infrastructure only.  This module does not widen canonical
VM81, Hash72, Hash216, persistence, receipt, or mutation authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

SCHEMA = "HHS_PASS_220_MOBIUS_QUARTER_PHASE_HARMONIC_V1"
LEMMA = "HHS-L146-013"
VERSION = "1.0.0"
PHASE_MODULUS = 72
QUARTER_PHASE = 18
PHASE_POSITIONS = (0, 18, 36, 54, 72)
VM81_NUCLEI = 9


class Pass220MobiusError(ValueError):
    pass


def _q(value: Any, *, name: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise Pass220MobiusError(f"{name} must be exact; float authority is forbidden")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise Pass220MobiusError(f"{name} is not an exact rational") from exc


def _fraction_record(value: Fraction) -> Dict[str, int]:
    q = Fraction(value)
    return {"numerator": q.numerator, "denominator": q.denominator}


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Fraction):
        return _fraction_record(value)
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _canonicalize(item) for key, item in value.items()}
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return _canonicalize(record)


def mobius_rho(m: Any) -> Fraction:
    """rho(m)=(m-1)/(m+1), exact on the finite nonsingular branch."""
    x = _q(m, name="m")
    if x == -1:
        raise Pass220MobiusError("m=-1 is the Möbius pole")
    return (x - 1) / (x + 1)


def mobius_rho_inverse(rho: Any) -> Fraction:
    """Exact inverse m=(1+rho)/(1-rho)."""
    r = _q(rho, name="rho")
    if r == 1:
        raise Pass220MobiusError("rho=1 is the inverse Möbius pole")
    return (1 + r) / (1 - r)


def mobius_orbit4(m: Any) -> Tuple[Fraction, Fraction, Fraction, Fraction, Fraction]:
    """Return the finite C4 orbit m,Cm,C²m,C³m,C⁴m.

    The finite chart excludes {-1,0,1}; the projective transformation itself
    remains represented separately by mobius_matrix_power4().
    """
    x0 = _q(m, name="m")
    if x0 in (Fraction(-1), Fraction(0), Fraction(1)):
        raise Pass220MobiusError("finite four-step orbit crosses a projective pole")
    x1 = mobius_rho(x0)
    x2 = mobius_rho(x1)
    x3 = mobius_rho(x2)
    x4 = mobius_rho(x3)
    if x2 != -1 / x0:
        raise Pass220MobiusError("half-cycle reciprocal inversion failed")
    if x4 != x0:
        raise Pass220MobiusError("four-cycle closure failed")
    return x0, x1, x2, x3, x4


def _matmul2(
    left: Tuple[Tuple[int, int], Tuple[int, int]],
    right: Tuple[Tuple[int, int], Tuple[int, int]],
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    return (
        (
            left[0][0] * right[0][0] + left[0][1] * right[1][0],
            left[0][0] * right[0][1] + left[0][1] * right[1][1],
        ),
        (
            left[1][0] * right[0][0] + left[1][1] * right[1][0],
            left[1][0] * right[0][1] + left[1][1] * right[1][1],
        ),
    )


def mobius_matrix_power4() -> Dict[str, Any]:
    """Witness the projective order-four matrix relation M^4=-4I ~ I."""
    matrix = ((1, -1), (1, 1))
    square = _matmul2(matrix, matrix)
    fourth = _matmul2(square, square)
    expected_square = ((0, -2), (2, 0))
    expected_fourth = ((-4, 0), (0, -4))
    if square != expected_square or fourth != expected_fourth:
        raise Pass220MobiusError("projective matrix cycle mismatch")
    return _receipt(
        {
            "schema": f"{SCHEMA}_MATRIX_C4_WITNESS",
            "matrix": matrix,
            "matrix_squared": square,
            "matrix_fourth": fourth,
            "projective_identity": True,
            "quarter_phase_positions": PHASE_POSITIONS,
            "floating_point_authority": False,
            "projection_only": True,
            "canonical_admission_authority": False,
        }
    )


def phase_cycle_witness(m: Any) -> Dict[str, Any]:
    orbit = mobius_orbit4(m)
    phase_values = {
        str(position): orbit[index]
        for index, position in enumerate(PHASE_POSITIONS)
    }
    return _receipt(
        {
            "schema": f"{SCHEMA}_PHASE_CYCLE_WITNESS",
            "lemma": LEMMA,
            "phase_modulus": PHASE_MODULUS,
            "quarter_phase": QUARTER_PHASE,
            "phase_values": phase_values,
            "half_cycle_is_negative_reciprocal": orbit[2] == -1 / orbit[0],
            "full_cycle_closed": orbit[4] == orbit[0],
            "floating_point_authority": False,
            "projection_only": True,
            "canonical_admission_authority": False,
        }
    )


def harmonic_partner(channel: Any) -> Fraction:
    """T(r)=r/(r-1), the self-inverse harmonic partner map."""
    r = _q(channel, name="channel")
    if r in (0, 1):
        raise Pass220MobiusError("harmonic partner is singular/non-admissible")
    return r / (r - 1)


def harmonic_closure(left: Any, right: Any) -> bool:
    """Exact self-normalizing phase-channel admission predicate."""
    r = _q(left, name="left")
    s = _q(right, name="right")
    if r == 0 or s == 0 or r + s == 0:
        return False
    return (
        r * s == r + s
        and (1 / r) + (1 / s) == 1
        and (r - 1) * (s - 1) == 1
    )


def harmonic_pair_from_lambda(lam: Any) -> Tuple[Fraction, Fraction]:
    """Parameterize every finite translated reciprocal branch.

    xy=1+lambda, zw=1+lambda^-1.
    """
    value = _q(lam, name="lambda")
    if value == 0:
        raise Pass220MobiusError("lambda=0 has no reciprocal")
    pair = (1 + value, 1 + 1 / value)
    if not harmonic_closure(*pair):
        raise Pass220MobiusError("lambda produced a non-admissible harmonic branch")
    return pair


def harmonic_involution_witness(channel: Any) -> Dict[str, Any]:
    r = _q(channel, name="channel")
    partner = harmonic_partner(r)
    returned = harmonic_partner(partner)
    if returned != r or not harmonic_closure(r, partner):
        raise Pass220MobiusError("harmonic involution failed")
    return _receipt(
        {
            "schema": f"{SCHEMA}_HARMONIC_INVOLUTION_WITNESS",
            "channel": r,
            "partner": partner,
            "returned": returned,
            "involution": True,
            "fixed_point_if_symmetric": r == partner,
            "floating_point_authority": False,
            "projection_only": True,
        }
    )


def vm81_harmonic_coherence(
    nucleus_pairs: Sequence[Tuple[Any, Any]],
) -> Dict[str, Any]:
    """AND-fold nine locally self-normalizing nuclei."""
    if len(nucleus_pairs) != VM81_NUCLEI:
        raise Pass220MobiusError("VM81 harmonic fold requires exactly nine nucleus pairs")
    local = []
    for index, pair in enumerate(nucleus_pairs):
        if len(pair) != 2:
            raise Pass220MobiusError(f"nucleus[{index}] must contain exactly two channels")
        admitted = harmonic_closure(pair[0], pair[1])
        local.append(
            {
                "nucleus": index,
                "left": _q(pair[0], name=f"nucleus[{index}].left"),
                "right": _q(pair[1], name=f"nucleus[{index}].right"),
                "harmonic_closed": admitted,
            }
        )
    admitted = all(item["harmonic_closed"] for item in local)
    return _receipt(
        {
            "schema": f"{SCHEMA}_VM81_COHERENCE_WITNESS",
            "vm81_cells": 81,
            "nucleus_count": VM81_NUCLEI,
            "nuclei": local,
            "admitted": admitted,
            "reason_code": "ADMIT_LOCAL_HARMONIC_AND_FOLD" if admitted else "REJECT_HARMONIC_INCOHERENCE",
            "floating_point_authority": False,
            "projection_only": True,
            "canonical_admission_authority": False,
        }
    )


@dataclass(frozen=True)
class Qsqrt5:
    """Exact a+b*sqrt(5) element."""

    a: Fraction
    b: Fraction

    def __init__(self, a: Any = 0, b: Any = 0):
        object.__setattr__(self, "a", _q(a, name="a"))
        object.__setattr__(self, "b", _q(b, name="b"))

    def __add__(self, other: "Qsqrt5") -> "Qsqrt5":
        return Qsqrt5(self.a + other.a, self.b + other.b)

    def __sub__(self, other: "Qsqrt5") -> "Qsqrt5":
        return Qsqrt5(self.a - other.a, self.b - other.b)

    def __mul__(self, other: "Qsqrt5") -> "Qsqrt5":
        return Qsqrt5(
            self.a * other.a + 5 * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    def conjugate(self) -> "Qsqrt5":
        return Qsqrt5(self.a, -self.b)

    def norm(self) -> Fraction:
        return self.a * self.a - 5 * self.b * self.b

    def as_record(self) -> Dict[str, Any]:
        return {"a": _fraction_record(self.a), "b": _fraction_record(self.b), "radicand": 5}


def golden_unit_witness() -> Dict[str, Any]:
    one = Qsqrt5(1, 0)
    phi = Qsqrt5(Fraction(1, 2), Fraction(1, 2))
    phi2 = phi * phi
    if phi2 != phi + one:
        raise Pass220MobiusError("golden unit identity failed")
    return _receipt(
        {
            "schema": f"{SCHEMA}_GOLDEN_UNIT_WITNESS",
            "phi": phi.as_record(),
            "phi_squared": phi2.as_record(),
            "phi_squared_equals_phi_plus_one": True,
            "floating_point_authority": False,
            "projection_only": True,
        }
    )


def norm_polynomial_m(m: Any) -> Fraction:
    x = _q(m, name="m")
    return x**4 - 3 * x**3 - x - 1


def norm_polynomial_rho(rho: Any) -> Fraction:
    r = _q(rho, name="rho")
    return r**4 + 3 * r**3 + r - 1


def norm_transform_identity(rho: Any) -> Dict[str, Any]:
    """Verify (1-rho)^4 F((1+rho)/(1-rho)) = 4 G(rho)."""
    r = _q(rho, name="rho")
    if r == 1:
        raise Pass220MobiusError("rho=1 is singular in the norm transform")
    m = mobius_rho_inverse(r)
    left = (1 - r) ** 4 * norm_polynomial_m(m)
    right = 4 * norm_polynomial_rho(r)
    if left != right:
        raise Pass220MobiusError("Möbius norm-polynomial transform failed")
    return _receipt(
        {
            "schema": f"{SCHEMA}_NORM_TRANSFORM_WITNESS",
            "rho": r,
            "m": m,
            "left": left,
            "right": right,
            "identity_holds": True,
            "floating_point_authority": False,
            "projection_only": True,
        }
    )


def composed_i011_witness(
    m: Any,
    nucleus_pairs: Sequence[Tuple[Any, Any]],
) -> Dict[str, Any]:
    phase = phase_cycle_witness(m)
    matrix = mobius_matrix_power4()
    golden = golden_unit_witness()
    coherence = vm81_harmonic_coherence(nucleus_pairs)
    return _receipt(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "lemma": LEMMA,
            "phase_cycle_receipt": phase["receipt_sha256"],
            "matrix_cycle_receipt": matrix["receipt_sha256"],
            "golden_unit_receipt": golden["receipt_sha256"],
            "vm81_coherence_receipt": coherence["receipt_sha256"],
            "admitted_projection": coherence["admitted"],
            "floating_point_authority": False,
            "projection_only": True,
            "canonical_admission_authority": False,
        }
    )
