"""Pass 220 V165 — exact ordered 81-entry Module 194 fractalization source.

The source is preserved as an immutable AST using symbolic factors; this is
a construction/shape witness, NOT a native HNAN algebra equivalence proof.
It composes V164's inherited compiled C HNAN rule-checking path, and does
not replace the authoritative complete 196-module course or native closure.
"""
from __future__ import annotations
from hashlib import sha256
import json
from typing import Any

from hhs_runtime.hhs_pass220_v164_module194_inherited_native_hnan_163_v1 import (
    execute_module194_native_hnan_scope,
)
from hhs_runtime.hhs_pass220_v160_module194_source_address_preflight_v1 import (
    LO_SHU, address,
)

SCHEMA = "HHS_PASS_220_V165_MODULE194_ORDERED_FRACTAL_TENSOR_V1"

# Explicitly ordered source operators. Do not replace noncommutative source
# nodes by evaluated host-language numeric multiplication.
def power(base: tuple | str, n: int) -> tuple:
    return ("Power", base, n)


a_symbol = ("CellSymbol", "a")
b_symbol = ("CellSymbol", "b")
A2 = power(a_symbol, 2)
A4 = power(a_symbol, 4)
B2 = power(b_symbol, 2)
SEEDS = (A2, A4, ("Sum", A4, B2))
ROW_OPS = ("Seed", "Square", "SquarePlusFourth")
LO_SHU_ROWS = ((4, 9, 2), (3, 5, 7), (8, 1, 6))


class V165TensorError(ValueError):
    pass


def fractal_term(seed: tuple, row: int) -> tuple:
    if row == 0:
        return seed
    if row == 1:
        return power(seed, 2)
    if row == 2:
        return ("Sum", power(seed, 2), power(seed, 4))
    raise V165TensorError("V165_INNER_ROW_OUT_OF_RANGE")


def source_tensor() -> tuple:
    """Return all source blocks as nine Lo Shu weighted 3x3 inner kernels."""
    return tuple(
        tuple(
            tuple(
                tuple(("OrderedWeight", LO_SHU_ROWS[i][j],
                       fractal_term(SEEDS[k], r))
                      for k in range(3))
                for r in range(3)
            )
            for j in range(3)
        )
        for i in range(3)
    )


def flattened_source_tensor() -> tuple:
    t = source_tensor()
    return tuple(
        (i, j, r, k, t[i][j][r][k])
        for i in range(3) for j in range(3)
        for r in range(3) for k in range(3)
    )


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return sha256(raw).hexdigest()


def inspect_ordered_tensor(source: bytes, native_library: Any, *,
                           require_upload_identity: bool = True) -> dict:
    """Execute inherited V164 native rules, then witness symbolic tensor shape."""
    inherited = execute_module194_native_hnan_scope(
        source, native_library, require_upload_identity=require_upload_identity
    )
    if (inherited.get("native_inherited_global_hnan_gate_executed") is not True
        or inherited.get("native_mandatory_rule_mask") != 0x7fff
        or inherited.get("native_ordered_hnan_rule_ids_verified") != [10,11,12,13]
        or inherited.get("canonical_vm81_admission") is not False):
        raise V165TensorError("V165_INHERITED_NATIVE_GATE_REJECTED")
    tensor = source_tensor()
    if tuple(len(row) for row in tensor) != (3,3,3):
        raise V165TensorError("V165_LO_SHU_SHAPE_REJECTED")
    entries = flattened_source_tensor()
    if len(entries) != 81:
        raise V165TensorError("V165_81_ENTRY_COUNT_REJECTED")
    for i,j,r,k,term in entries:
        if (term != ("OrderedWeight", LO_SHU_ROWS[i][j],
                     fractal_term(SEEDS[k], r))
            or term[1] != LO_SHU[i*3+j]):
            raise V165TensorError("V165_ORDERED_ENTRY_MISMATCH")
        group = (i*3+j)*9+r*3+k
        x = address(group*64)
        if (x["group"] != group or x["lo_shu"] != LO_SHU_ROWS[i][j]):
            raise V165TensorError("V165_PARTICLE_ADDRESS_MISMATCH")
    return {
        "schema": SCHEMA,
        "module194_source_sha256": inherited["module194_source_sha256"],
        "fractalization_ast_sha256": _digest(tensor),
        "inner_kernel_ast_sha256": _digest(
            tensor[0][0]
        ),
        "ordered_81_source_entries": len(entries),
        "lo_shu_weights_rowmajor": list(LO_SHU),
        "inner_row_operators": list(ROW_OPS),
        "particle_group_address_mapping_checked": True,
        "inherited_native_hnan_global_signature64":
            inherited["native_hnan_system_signature64"],
        "inherited_native_hnan_rules_verified":
            inherited["native_ordered_hnan_rule_ids_verified"],
        "A_LHS_typed": "LHS_81_ADDRESS_TENSOR",
        "B_RHS_typed": "OUTER_HNAN_CLOSURE_BOUNDARY",
        "A_B_distinct_even_if_magnitude_P2": True,
        "ordered_AB_source": "AB=P^4",
        "ordered_BA_source": "BA=-P^4",
        "primitive_source": "e=(0,1)",
        "trinary_source": "(-1,0,+1)",
        "interior_delta_e_source": "Deltae*A=(-1,0,+1)*B/Delta=P^2/Delta",
        "outer_boundary_source": "t^3-t-1=Deltae=0",
        "native_hnan_ab_ba_for_fractal_tensor_proved": False,
        "native_fractal_tensor_operator_equivalence_proved": False,
        "native_interior_outer_delta_e_type_resolution_proved": False,
        "canonical_196_course_complete_source_verified": False,
        "module194_force_producer_provenance_verified": False,
        "vm81_admission": False,
        "hash72_hash216_minted": False,
    }
