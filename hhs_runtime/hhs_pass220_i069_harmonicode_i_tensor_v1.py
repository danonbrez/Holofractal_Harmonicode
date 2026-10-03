"""Pass 220 I069 — HARMONICODE I Tensor exact generator/projection.

This module preserves the user-supplied HARMONICODE source verbatim and exposes
an exact integer generator for its three 3x3 matrix channels.  It does not
evaluate the native E membrane as host-language Boolean division and does not
commute or cancel the ordered x*y channel.
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from python.hhs_gfcc.core import HASH72_POSITIONS, inherited_hash72

SCHEMA = "HHS_PASS_220_I069_HARMONICODE_I_TENSOR_V1"
PROFILE = "PASS220-I069-HARMONICODE-I-TENSOR-v1"

VERBATIM_SOURCE = (
    "u^((MatrixTimes(x,((-List(List(64,8,24),List(8,24,40),"
    "List(24,40,56)))/(E==List(8,24,40,56,72,16,32,48,64))))"
    "-MatrixTimes(y,((-List(List(8,64,48),List(64,48,32),"
    "List(48,32,16)))/(E==List(8,24,40,56,72,16,32,48,64))))"
    "==Mod(MatrixTimes(x*y,(List(List(56,64,24),List(40,72,32),"
    "List(48,8,16))/(E==List(8,24,40,56,72,16,32,48,64)))),72))"
    "/u==u^72)"
)

E_VECTOR = (8, 24, 40, 56, 72, 16, 32, 48, 64)
LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
EXPECTED_A = ((64, 8, 24), (8, 24, 40), (24, 40, 56))
EXPECTED_B = ((8, 64, 48), (64, 48, 32), (48, 32, 16))
EXPECTED_C = ((56, 64, 24), (40, 72, 32), (48, 8, 16))

AUTHORITY_BOUNDARY = {
    "formal_projection_only": True,
    "verbatim_source_authoritative": True,
    "ordered_matrix_times_preserved": True,
    "ordered_xy_preserved": True,
    "e_membrane_not_host_boolean_division": True,
    "exact_integer_generator": True,
    "floating_point_authority": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_persistence_authority": False,
}


class Pass220I069TensorError(ValueError):
    """Raised when an I069 projection violates its exact construction."""


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I069TensorError(f"floating-point value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def hash72(value: Any) -> str:
    return inherited_hash72(canonical_bytes(value))


def phase_kernel() -> tuple[tuple[int, int, int], ...]:
    """Generate the normalized A channel without storing its nine entries."""
    return tuple(
        tuple((2 * (row + col) - 1) % 9 for col in range(3))
        for row in range(3)
    )


def matrix_a() -> tuple[tuple[int, int, int], ...]:
    return tuple(tuple(8 * value for value in row) for row in phase_kernel())


def matrix_b() -> tuple[tuple[int, int, int], ...]:
    # Every kernel value is in 1..8, so 9-k is its nonzero mod-9 complement.
    return tuple(
        tuple(8 * (9 - value) for value in row)
        for row in phase_kernel()
    )


def lo_shu_route() -> tuple[int, ...]:
    return tuple(value for row in LO_SHU for value in row)


def matrix_c(
    e_vector: Sequence[int] = E_VECTOR,
    route: Sequence[int] | None = None,
) -> tuple[tuple[int, int, int], ...]:
    """Route E through the one-based flattened Lo Shu permutation."""
    if route is None:
        route = lo_shu_route()
    if len(e_vector) != 9 or len(route) != 9:
        raise Pass220I069TensorError("E vector and Lo Shu route must have width 9")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in e_vector):
        raise Pass220I069TensorError("E vector must contain exact integers")
    if sorted(route) != list(range(1, 10)):
        raise Pass220I069TensorError("Lo Shu route must be a permutation of 1..9")
    routed = tuple(e_vector[index - 1] for index in route)
    return tuple(
        tuple(routed[offset : offset + 3])
        for offset in range(0, 9, 3)
    )


def _det3(matrix: Sequence[Sequence[int]]) -> int:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise Pass220I069TensorError("determinant requires a 3x3 matrix")
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    )


def _mod_matrix(
    matrix: Sequence[Sequence[int]],
    modulus: int,
) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        tuple(value % modulus for value in row)
        for row in matrix
    )


def _negate(
    matrix: Sequence[Sequence[int]],
) -> tuple[tuple[int, int, int], ...]:
    return tuple(tuple(-value for value in row) for row in matrix)


def generator_descriptor() -> dict[str, Any]:
    """Compact authoritative construction rather than three unrelated matrices."""
    return {
        "scale": 8,
        "phase_modulus": 9,
        "residue_modulus": 72,
        "phase_kernel_rule": "Mod[2*(row0+col0)-1,9]",
        "complement_rule": "9-phase_kernel",
        "e_vector": list(E_VECTOR),
        "lo_shu_route": list(lo_shu_route()),
        "product_rule": "Partition[E[[Flatten[LoShu]]],3]",
    }


def materialize_projection() -> dict[str, Any]:
    a = matrix_a()
    b = matrix_b()
    c = matrix_c()
    checks = {
        "verbatim_matrix_times_preserved": "MatrixTimes" in VERBATIM_SOURCE,
        "verbatim_e_membrane_preserved": (
            "E==List(8,24,40,56,72,16,32,48,64)" in VERBATIM_SOURCE
        ),
        "verbatim_ordered_xy_preserved": "MatrixTimes(x*y" in VERBATIM_SOURCE,
        "verbatim_u72_preserved": "u^72" in VERBATIM_SOURCE,
        "e_vector_eight_scaled_permutation": sorted(value // 8 for value in E_VECTOR)
        == list(range(1, 10)),
        "lo_shu_is_permutation": sorted(lo_shu_route()) == list(range(1, 10)),
        "phase_kernel_exact": phase_kernel()
        == ((8, 1, 3), (1, 3, 5), (3, 5, 7)),
        "matrix_a_exact": a == EXPECTED_A,
        "matrix_b_exact": b == EXPECTED_B,
        "matrix_c_exact": c == EXPECTED_C,
        "a_b_pointwise_72_closure": all(
            a[row][col] + b[row][col] == 72
            for row in range(3)
            for col in range(3)
        ),
        "b_is_mod72_negative_a": _mod_matrix(_negate(a), 72) == b,
        "a_is_mod72_negative_b": _mod_matrix(_negate(b), 72) == a,
        "c_is_e_routed_by_loshu": c == matrix_c(E_VECTOR, lo_shu_route()),
        "c_center_72": c[1][1] == 72,
        "c_center_mod72_zero": c[1][1] % 72 == 0,
        "determinants_exact": (_det3(a), _det3(b), _det3(c))
        == (-18432, 18432, 32256),
        "determinants_divisible_by_72": all(
            determinant % 72 == 0
            for determinant in (_det3(a), _det3(b), _det3(c))
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise Pass220I069TensorError(
            "canonical I Tensor construction failed: " + ",".join(failed)
        )

    source_lane = hash72({"source": VERBATIM_SOURCE})
    generator_lane = hash72(generator_descriptor())
    proof_lane = hash72(
        {
            "checks": checks,
            "authority": AUTHORITY_BOUNDARY,
            "determinants": [_det3(a), _det3(b), _det3(c)],
        }
    )
    receipt_hash216 = source_lane + generator_lane + proof_lane
    if len(receipt_hash216) != 3 * HASH72_POSITIONS:
        raise Pass220I069TensorError("candidate receipt must be exactly 216 glyphs")

    return {
        "schema": SCHEMA,
        "profile": PROFILE,
        "verbatim_source": VERBATIM_SOURCE,
        "generator": generator_descriptor(),
        "matrix_a": [list(row) for row in a],
        "matrix_b": [list(row) for row in b],
        "matrix_c": [list(row) for row in c],
        "determinants": [_det3(a), _det3(b), _det3(c)],
        "normalized_determinants": [-36, 36, 63],
        "checks": checks,
        "source_hash72": source_lane,
        "generator_hash72": generator_lane,
        "proof_hash72": proof_lane,
        "receipt_hash216": receipt_hash216,
        "authority": dict(AUTHORITY_BOUNDARY),
    }


def validate_projection(value: Mapping[str, Any]) -> bool:
    _reject_float(value)
    canonical = materialize_projection()
    required = (
        "schema",
        "verbatim_source",
        "generator",
        "matrix_a",
        "matrix_b",
        "matrix_c",
        "determinants",
        "source_hash72",
        "generator_hash72",
        "proof_hash72",
        "receipt_hash216",
        "authority",
    )
    if any(key not in value for key in required):
        raise Pass220I069TensorError("projection is missing required fields")
    for key in required:
        if value[key] != canonical[key]:
            raise Pass220I069TensorError(f"projection diverges at {key}")
    return True


def self_test() -> dict[str, Any]:
    first = materialize_projection()
    second = materialize_projection()
    checks = {
        "projection_validates": validate_projection(first),
        "deterministic_receipt": first["receipt_hash216"] == second["receipt_hash216"],
        "receipt_width_216": len(first["receipt_hash216"]) == 216,
        "receipt_lane_order": first["receipt_hash216"]
        == first["source_hash72"] + first["generator_hash72"] + first["proof_hash72"],
        "no_float_authority": AUTHORITY_BOUNDARY["floating_point_authority"] is False,
        "no_vm81_mutation_authority": (
            AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"] is False
        ),
        "no_hash72_commit_authority": (
            AUTHORITY_BOUNDARY["canonical_hash72_commit_authority"] is False
        ),
        "no_hash216_commit_authority": (
            AUTHORITY_BOUNDARY["canonical_hash216_commit_authority"] is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [name for name, passed in checks.items() if not passed],
        "checks": checks,
        "receipt_hash216": first["receipt_hash216"],
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
