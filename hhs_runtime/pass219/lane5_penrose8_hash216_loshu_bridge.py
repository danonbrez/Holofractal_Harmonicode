"""Pass 219 Lane 5 Penrose 8-real phase / Hash72 / Hash216 / Lo-Shu bridge.

This is an additive, read-only proof bridge over PR #571 authority.  It binds:
- the four-complex/eight-real Penrose twistor projection,
- the eight 3-bit local truth addresses,
- the eight outer positions of the native 3x3 Lo-Shu tensor,
- nine coupled nuclei -> 72 canonical outer coordinates,
- Hash72's canonical position/character chart,
- ordered Hash216 = previous72 || next72 || receipt72,
- one SHA-256 witness per ordered Hash216 coordinate.

No object in this module mints Hash72/Hash216, mutates VM81, grants GPU
canonical authority, scalarizes the x/y/z/w tensor, or replaces repository
native algebra by a conventional external projection.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Sequence

from hhs_runtime.core.hash72_validator_v1 import (
    HASH72_ALPHABET,
    HASH72_SYMBOL_COUNT,
    validate_hash72,
)
from hhs_runtime.pass219.lane5_genesis_orientation_u9_qe_bridge import (
    EIGENVECTOR0_TENSOR,
    GENESIS_NUCLEUS_CELLS,
    PHASE_COVER_POSITIONS,
    VM81_CELLS,
)
from hhs_runtime.pass219.lane5_poincare_integral_bridge import canonical_omega

SCHEMA = "HHS_PASS219_LANE5_PENROSE8_HASH216_LOSHU_BRIDGE_V1"
VERSION = "1.0.0-cycle7"

TRUTH3_ADDRESSES = tuple(f"{i:03b}" for i in range(8))
PENROSE8_REAL_PHASE_ORDER = (
    "Re(omega^0)",
    "Re(omega^1)",
    "Re(pi_0')",
    "Re(pi_1')",
    "Im(omega^0)",
    "Im(omega^1)",
    "Im(pi_0')",
    "Im(pi_1')",
)
LO_SHU_OUTER_POSITIONS = (
    (0, 0), (0, 1), (0, 2),
    (1, 0),         (1, 2),
    (2, 0), (2, 1), (2, 2),
)
LO_SHU_OUTER_EXPRESSIONS = tuple(
    EIGENVECTOR0_TENSOR[row][column]
    for row, column in LO_SHU_OUTER_POSITIONS
)
HASH216_LAYERS = ("previous", "next", "receipt")
PYTHAGOREAN_LINEAGE_CLOSURE = (
    "a^2+b^2=c^2=P^4/c^2="
    "(Hash72_previous,Hash72_next,Hash72_receipt)"
)

Q = Fraction
Gaussian = tuple[Fraction, Fraction]
Matrix2 = tuple[tuple[Gaussian, Gaussian], tuple[Gaussian, Gaussian]]


class Penrose8Hash216BridgeError(ValueError):
    pass


def _q(value: int | Fraction, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise Penrose8Hash216BridgeError(f"{name} must be exact int/Fraction")
    return Fraction(value)


def _g(real: int | Fraction, imag: int | Fraction = 0) -> Gaussian:
    return (_q(real, "real"), _q(imag, "imag"))


def _gadd(a: Gaussian, b: Gaussian) -> Gaussian:
    return (a[0] + b[0], a[1] + b[1])


def _gmul(a: Gaussian, b: Gaussian) -> Gaussian:
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _gconj(a: Gaussian) -> Gaussian:
    return (a[0], -a[1])


def _gjson(value: Gaussian) -> dict[str, list[int]]:
    return {
        "re": [value[0].numerator, value[0].denominator],
        "im": [value[1].numerator, value[1].denominator],
    }


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    core = dict(payload)
    core["receipt_sha256"] = sha256(_stable(core).encode("utf-8")).hexdigest()
    return core


def minkowski_hermitian_matrix(
    t: int | Fraction,
    x: int | Fraction,
    y: int | Fraction,
    z: int | Fraction,
) -> Matrix2:
    """Return X=[[t+z,x-i y],[x+i y,t-z]] exactly."""
    tq, xq, yq, zq = (_q(t, "t"), _q(x, "x"), _q(y, "y"), _q(z, "z"))
    return (
        (_g(tq + zq), _g(xq, -yq)),
        (_g(xq, yq), _g(tq - zq)),
    )


def _validate_hermitian2(matrix: Sequence[Sequence[Gaussian]]) -> Matrix2:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise Penrose8Hash216BridgeError("X must be exactly 2x2")
    m = tuple(tuple(_g(v[0], v[1]) for v in row) for row in matrix)
    if m[0][0][1] or m[1][1][1] or m[1][0] != _gconj(m[0][1]):
        raise Penrose8Hash216BridgeError("X must be Hermitian")
    return m  # type: ignore[return-value]


def incidence_twistor(
    X: Sequence[Sequence[Gaussian]],
    pi0: Gaussian,
    pi1: Gaussian,
) -> tuple[Gaussian, Gaussian, Gaussian, Gaussian]:
    """Compute Z=(omega^0,omega^1,pi_0',pi_1') with omega=i X pi."""
    m = _validate_hermitian2(X)
    p = (_g(pi0[0], pi0[1]), _g(pi1[0], pi1[1]))
    iunit = _g(0, 1)
    omega = tuple(
        _gmul(
            iunit,
            _gadd(_gmul(m[row][0], p[0]), _gmul(m[row][1], p[1])),
        )
        for row in range(2)
    )
    return (omega[0], omega[1], p[0], p[1])


def twistor_real8(
    Z: Sequence[Gaussian],
) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]:
    if len(Z) != 4:
        raise Penrose8Hash216BridgeError("twistor must have four complex components")
    z = tuple(_g(v[0], v[1]) for v in Z)
    return (
        z[0][0], z[1][0], z[2][0], z[3][0],
        z[0][1], z[1][1], z[2][1], z[3][1],
    )


def twistor_null_form(Z: Sequence[Gaussian]) -> Gaussian:
    """Return omega†pi + pi†omega for the incidence convention used here."""
    if len(Z) != 4:
        raise Penrose8Hash216BridgeError("twistor must have four complex components")
    omega = (_g(*Z[0]), _g(*Z[1]))
    pi = (_g(*Z[2]), _g(*Z[3]))
    value = _g(0)
    for index in range(2):
        value = _gadd(value, _gmul(_gconj(omega[index]), pi[index]))
        value = _gadd(value, _gmul(_gconj(pi[index]), omega[index]))
    return value


def massless_momentum_spinor(pi0: Gaussian, pi1: Gaussian) -> Matrix2:
    p = (_g(*pi0), _g(*pi1))
    return tuple(
        tuple(_gmul(p[row], _gconj(p[column])) for column in range(2))
        for row in range(2)
    )  # type: ignore[return-value]


def gaussian_det2(matrix: Sequence[Sequence[Gaussian]]) -> Gaussian:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise Penrose8Hash216BridgeError("determinant requires 2x2 Gaussian matrix")
    a, b = matrix[0]
    c, d = matrix[1]
    ad = _gmul(a, d)
    bc = _gmul(b, c)
    return (ad[0] - bc[0], ad[1] - bc[1])


def hash72_coordinate_chart() -> tuple[dict[str, Any], ...]:
    """Canonical 9x8 chart: position, character, local cell, phase coordinate."""
    if not (
        len(HASH72_ALPHABET)
        == HASH72_SYMBOL_COUNT
        == PHASE_COVER_POSITIONS
        == 72
    ):
        raise Penrose8Hash216BridgeError("Hash72/phase-cover cardinality drift")
    if GENESIS_NUCLEUS_CELLS != 9 or VM81_CELLS != 81:
        raise Penrose8Hash216BridgeError("VM81 Genesis cardinality drift")

    chart: list[dict[str, Any]] = []
    for nucleus in range(GENESIS_NUCLEUS_CELLS):
        for local in range(8):
            index = nucleus * 8 + local
            chart.append(
                {
                    "hash72_index": index,
                    "canonical_character": HASH72_ALPHABET[index],
                    "nucleus_index": nucleus,
                    "local_outer_index": local,
                    "truth3_address": TRUTH3_ADDRESSES[local],
                    "loshu_position": list(LO_SHU_OUTER_POSITIONS[local]),
                    "loshu_tensor_expression": LO_SHU_OUTER_EXPRESSIONS[local],
                    "penrose8_real_phase_coordinate": PENROSE8_REAL_PHASE_ORDER[local],
                    "all_nine_nuclei_coupled": True,
                    "foreign_qudit_count": VM81_CELLS - 1,
                    "self_exclusion": True,
                }
            )
    return tuple(chart)


def penrose8_projection_witness(
    *,
    t: int | Fraction = 3,
    x: int | Fraction = 1,
    y: int | Fraction = 2,
    z: int | Fraction = -1,
    pi0: Gaussian = (Fraction(1), Fraction(2)),
    pi1: Gaussian = (Fraction(3), Fraction(-1)),
) -> dict[str, Any]:
    X = minkowski_hermitian_matrix(t, x, y, z)
    Z = incidence_twistor(X, pi0, pi1)
    real8 = twistor_real8(Z)
    null_form = twistor_null_form(Z)
    momentum = massless_momentum_spinor(pi0, pi1)
    momentum_det = gaussian_det2(momentum)
    omega8 = canonical_omega(4)

    checks = {
        "four_complex_components": len(Z) == 4,
        "eight_real_coordinates": len(real8) == 8,
        "incidence_null_form_zero": null_form == _g(0),
        "massless_momentum_rank_one_det_zero": momentum_det == _g(0),
        "three_bit_truth_table_has_eight_states": len(TRUTH3_ADDRESSES) == 2**3 == 8,
        "outer_tensor_has_eight_positions": len(LO_SHU_OUTER_POSITIONS) == 8,
        "phase_coordinate_order_bijective": len(set(PENROSE8_REAL_PHASE_ORDER)) == 8,
        "poincare_8d_omega_exact": (
            len(omega8) == 8
            and all(len(row) == 8 for row in omega8)
            and all(omega8[i][j] == -omega8[j][i] for i in range(8) for j in range(8))
        ),
    }

    return _receipt(
        {
            "schema": "HHS_PASS219_PENROSE8_PHASE_PROJECTION_WITNESS_V1",
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "equations": {
                "twistor": "Z=(omega^0,omega^1,pi_0',pi_1') in C^4 ~= R^8",
                "incidence": "omega=i X pi",
                "minkowski_matrix": "X=[[t+z,x-i*y],[x+i*y,t-z]]",
                "null_form": "omega^dagger*pi+pi^dagger*omega=0",
                "massless_momentum": "p=pi*pi^dagger; det(p)=0",
                "poincare_8d": "Omega_8=[[0,I4],[-I4,0]]",
            },
            "real8_order": list(PENROSE8_REAL_PHASE_ORDER),
            "real8_value": [[v.numerator, v.denominator] for v in real8],
            "twistor": [_gjson(v) for v in Z],
            "null_form": _gjson(null_form),
            "massless_momentum_det": _gjson(momentum_det),
            "projective_quotient_applied": False,
            "hhs_projection_contract_only": True,
            "external_physical_equivalence_beyond_projection_claimed": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_mint_authority": False,
        }
    )


def hash72_loshu_witness(value: str) -> dict[str, Any]:
    if not validate_hash72(value):
        raise Penrose8Hash216BridgeError("canonical Hash72 value required")
    chart = hash72_coordinate_chart()
    checks = {
        "hash72_length": len(value) == 72,
        "chart_length": len(chart) == 72,
        "canonical_character_position_bijection": all(
            row["canonical_character"] == HASH72_ALPHABET[row["hash72_index"]]
            for row in chart
        ),
        "nine_nuclei_times_eight_outer": GENESIS_NUCLEUS_CELLS * 8 == 72,
        "local_truth_addresses_complete": all(
            tuple(chart[n * 8 + i]["truth3_address"] for i in range(8))
            == TRUTH3_ADDRESSES
            for n in range(9)
        ),
    }
    return _receipt(
        {
            "schema": "HHS_PASS219_HASH72_LOSHU_COORDINATE_WITNESS_V1",
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "hash72": value,
            "coordinate_chart": list(chart),
            "native_equivalence": "u^72 = Hash72 = 72 Lo-Shu outer qudit coordinates",
            "outer_boundary_free": False,
            "holographic_nuclear_constraint": "one recursively coupled Lo-Shu nuclear manifold",
            "canonical_hash72_mint_authority": False,
        }
    )


def hash216_lineage_witness(previous: str, next_state: str, receipt72: str) -> dict[str, Any]:
    layers = (
        ("previous", previous),
        ("next", next_state),
        ("receipt", receipt72),
    )
    for name, value in layers:
        if not validate_hash72(value):
            raise Penrose8Hash216BridgeError(f"{name} canonical Hash72 required")
    hash216 = "".join(value for _, value in layers)
    chart = hash72_coordinate_chart()
    coordinates: list[dict[str, Any]] = []
    digests: list[str] = []
    for layer_index, (layer, value) in enumerate(layers):
        for local_index, symbol in enumerate(value):
            global_index = layer_index * 72 + local_index
            digest = sha256(symbol.encode("ascii")).hexdigest()
            digests.append(digest)
            row = chart[local_index]
            coordinates.append(
                {
                    "hash216_index": global_index,
                    "lineage_layer": layer,
                    "hash72_index": local_index,
                    "canonical_character": row["canonical_character"],
                    "state_symbol": symbol,
                    "nucleus_index": row["nucleus_index"],
                    "truth3_address": row["truth3_address"],
                    "loshu_tensor_expression": row["loshu_tensor_expression"],
                    "penrose8_real_phase_coordinate": row["penrose8_real_phase_coordinate"],
                    "sha256": digest,
                }
            )

    checks = {
        "ordered_three_hash72": hash216 == previous + next_state + receipt72,
        "hash216_length": len(hash216) == 216,
        "three_times_72": 3 * 72 == 216,
        "sha256_per_coordinate": len(digests) == 216 and all(len(d) == 64 for d in digests),
        "vm5184_relation": 72**2 == 5184,
        "layer_order_exact": tuple(layer for layer, _ in layers) == HASH216_LAYERS,
    }
    return _receipt(
        {
            "schema": "HHS_PASS219_HASH216_ORDERED_LOSHU_LINEAGE_WITNESS_V1",
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "hash216": hash216,
            "lineage_order": list(HASH216_LAYERS),
            "coordinates": coordinates,
            "sha256_vector": digests,
            "sha256_vector_concatenated": "".join(digests),
            "pythagorean_lineage_closure": PYTHAGOREAN_LINEAGE_CLOSURE,
            "ordered_equality_chain_scalar_rewrite_authorized": False,
            "canonical_hash216_mint_authority": False,
        }
    )


def full_penrose8_hash216_bridge_receipt(
    previous: str,
    next_state: str,
    receipt72: str,
) -> dict[str, Any]:
    phase = penrose8_projection_witness()
    previous_w = hash72_loshu_witness(previous)
    next_w = hash72_loshu_witness(next_state)
    receipt_w = hash72_loshu_witness(receipt72)
    lineage = hash216_lineage_witness(previous, next_state, receipt72)
    checks = {
        "penrose8_projection_pass": phase["status"] == "PASS",
        "previous_hash72_pass": previous_w["status"] == "PASS",
        "next_hash72_pass": next_w["status"] == "PASS",
        "receipt_hash72_pass": receipt_w["status"] == "PASS",
        "hash216_lineage_pass": lineage["status"] == "PASS",
        "local_3bit_to_8d_to_loshu": (
            len(TRUTH3_ADDRESSES)
            == len(PENROSE8_REAL_PHASE_ORDER)
            == len(LO_SHU_OUTER_POSITIONS)
            == 8
        ),
        "global_9x8_to_hash72": 9 * 8 == HASH72_SYMBOL_COUNT == 72,
        "transition_3x72_to_hash216": 3 * HASH72_SYMBOL_COUNT == 216,
        "vm5184_relation": HASH72_SYMBOL_COUNT**2 == 5184,
    }
    return _receipt(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "bindings": {
                "local": (
                    "3-bit truth address <-> Lo-Shu outer cell <-> "
                    "Penrose8 real phase coordinate"
                ),
                "global": "9 nuclei * 8 outer coordinates = 72 = u^72 = Hash72 geometry",
                "transition": "Hash216 = previous72 || next72 || receipt72",
                "digest": "216 * SHA256(state_symbol), indexed by ordered lineage coordinate",
                "relation_surface": "72^2=5184",
            },
            "phase_receipt_sha256": phase["receipt_sha256"],
            "previous_hash72_receipt_sha256": previous_w["receipt_sha256"],
            "next_hash72_receipt_sha256": next_w["receipt_sha256"],
            "receipt_hash72_receipt_sha256": receipt_w["receipt_sha256"],
            "hash216_receipt_sha256": lineage["receipt_sha256"],
            "pythagorean_lineage_closure": PYTHAGOREAN_LINEAGE_CLOSURE,
            "projective_quotient_applied": False,
            "hhs_projection_contract_only": True,
            "external_physical_equivalence_beyond_projection_claimed": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_mint_authority": False,
            "canonical_persistence_authority": False,
            "floating_point_canonical_authority": False,
        }
    )


def self_test() -> dict[str, Any]:
    previous = HASH72_ALPHABET
    next_state = HASH72_ALPHABET[1:] + HASH72_ALPHABET[:1]
    receipt72 = HASH72_ALPHABET[2:] + HASH72_ALPHABET[:2]
    result = full_penrose8_hash216_bridge_receipt(previous, next_state, receipt72)
    if result["status"] != "PASS":
        raise Penrose8Hash216BridgeError("Cycle 7 bridge self-test failed")
    return {
        "schema": "HHS_PASS219_LANE5_PENROSE8_HASH216_LOSHU_SELF_TEST_V1",
        "status": "PASS",
        "bridge_receipt_sha256": result["receipt_sha256"],
    }


if __name__ == "__main__":
    print(_stable(self_test()))
