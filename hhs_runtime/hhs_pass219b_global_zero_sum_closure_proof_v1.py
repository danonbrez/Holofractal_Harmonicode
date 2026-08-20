from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from typing import Any

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass129_invariant_delta_rational_projection_algebra_v1 import (
    canonical_pass129_request,
)

SCHEMA = "HHS_PASS219B_GLOBAL_ZERO_SUM_CLOSURE_PROOF_V1"
PASS_ID = "PASS_219B_I6"
CLOSURE_EXTENSION_SHA256 = "8c386a42e12b4adc9d3dccad706781229a16e82288678a8ed18c5a1601041528"
PARENT_MONOLITHIC_SHA256 = "9f2238981bf509d22ffebb46816346f389fd2d949ccd7956cde3630ab2b56944"


class GlobalZeroSumClosureError(RuntimeError):
    pass


def _read_fraction(fd: dict[str, int]) -> Fraction:
    return Fraction(int(fd["numerator"]), int(fd["denominator"]))


def _step(proof: dict[str, Any], rule: str) -> dict[str, Any]:
    for item in proof.get("steps", []):
        if item.get("rule") == rule:
            return item
    raise GlobalZeroSumClosureError(f"missing inherited proof step: {rule}")


def prove_global_zero_sum_closure(*, center_P: Any = 4) -> dict[str, Any]:
    """Bind the exact inherited closure family without solving x,y,z,w.

    This proves the necessary global zero-sum closure package. It deliberately
    does not claim to evaluate the full Pass-219 monolithic recursive chain.
    """

    engine, request = canonical_pass129_request(center_P=center_P)
    inherited = engine.prove(request)
    validation = engine.validate(request, inherited)
    replay = engine.replay(request, inherited)

    delta = _read_fraction(inherited["derived"]["delta"])
    p = _read_fraction(inherited["derived"]["p"])
    P = _read_fraction(inherited["derived"]["P"])
    q = _read_fraction(inherited["derived"]["q"])
    p2_minus_pq = _read_fraction(inherited["derived"]["P_squared_minus_pq"])
    membrane = _read_fraction(inherited["derived"]["membrane_residue"])

    idempotent = _step(inherited, "NONZERO_RATIONAL_IDEMPOTENT_CLOSURE")
    membrane_step = _step(inherited, "THREE_WAY_MEMBRANE_CLOSURE")
    phase_step = _step(inherited, "FOUR_PHASE_CARRIER_ZERO_SUM")

    phase_sum = phase_step["output"]["sum"]
    xyzw_sum = _read_fraction(request["xyzw_sum"])
    zw_product = _read_fraction(request["zw_product"])
    xy_product = _read_fraction(request["native_projection_values"]["XY_PRODUCT"])

    if delta != 1:
        raise GlobalZeroSumClosureError(f"delta closure != 1: {delta}")
    if p != P - 1 or q != P + 1:
        raise GlobalZeroSumClosureError("symmetric center family mismatch")
    if p2_minus_pq != 1:
        raise GlobalZeroSumClosureError(f"P^2-pq != 1: {p2_minus_pq}")
    if xy_product != 1 or zw_product != 1:
        raise GlobalZeroSumClosureError("xy/zw unit projection mismatch")
    if xyzw_sum != 0:
        raise GlobalZeroSumClosureError(f"center sum != 0: {xyzw_sum}")
    if phase_sum != [0, 0]:
        raise GlobalZeroSumClosureError(f"phase carrier sum != 0: {phase_sum}")
    if membrane != 1:
        raise GlobalZeroSumClosureError(f"membrane residue != 1: {membrane}")

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "pass_id": PASS_ID,
        "status": "GLOBAL_ZERO_SUM_CLOSURE_PROVED",
        "closure_family": {
            "P": inherited["derived"]["P"],
            "p": inherited["derived"]["p"],
            "q": inherited["derived"]["q"],
            "delta": inherited["derived"]["delta"],
            "P_squared_minus_pq": inherited["derived"]["P_squared_minus_pq"],
            "xy_projection": request["native_projection_values"]["XY_PRODUCT"],
            "zw_projection": request["zw_product"],
            "x_plus_y_plus_z_plus_w": request["xyzw_sum"],
            "phase_carrier_sum_basis_1_I": deepcopy(phase_sum),
            "membrane_residue": inherited["derived"]["membrane_residue"],
        },
        "logical_derivation": [
            "P^2-pq = delta^2 by symmetric p=P-delta, q=P+delta",
            "the required common residue also states P^2-pq = delta",
            "delta != 0 and delta^2=delta over the exact rational projection imply delta=1",
            "therefore p=P-1, q=P+1, P^2-pq=1",
            "the registered closure fixture has xy=1, zw=1, x+y+z+w=0",
            "the three-way membrane therefore closes to the unit residue 1",
            "I+I^2+I^3+I^4 is represented by (0,1)+(-1,0)+(0,-1)+(1,0)=(0,0)",
        ],
        "denominator_projection_binding": {
            "unit_symbol": "1=u^72",
            "unit_perimeter_cells": 8,
            "center": "x+y+z+w=0/u^72",
            "recursive_relation": "N/D^4=D^4",
            "recursive_relation_evaluated": False,
        },
        "global_enforcement": {
            "necessary_for_full_symbolic_uqcel": True,
            "monolithic_chain_still_required": True,
            "full_monolithic_evaluated": False,
            "compatibility_profile_is_not_full_proof": True,
            "canonical_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_persistence_authority": False,
        },
        "source_identity": {
            "parent_monolithic_sha256": PARENT_MONOLITHIC_SHA256,
            "closure_extension_sha256": CLOSURE_EXTENSION_SHA256,
        },
        "inherited_pass129": {
            "proof_root_hash72": inherited["proof_root_hash72"],
            "validation": validation["status"],
            "replay": replay["status"],
            "idempotent_step_root_hash72": idempotent["step_root_hash72"],
            "membrane_step_root_hash72": membrane_step["step_root_hash72"],
            "phase_zero_sum_step_root_hash72": phase_step["step_root_hash72"],
        },
    }
    result["proof_root_hash72"] = _hash("hhs_pass219b_global_zero_sum_closure_v1", result)
    return result


def verify_global_zero_sum_closure(proof: dict[str, Any]) -> dict[str, Any]:
    body = deepcopy(proof)
    root = body.pop("proof_root_hash72", None)
    if root != _hash("hhs_pass219b_global_zero_sum_closure_v1", body):
        raise GlobalZeroSumClosureError("proof root mismatch")
    if body.get("status") != "GLOBAL_ZERO_SUM_CLOSURE_PROVED":
        raise GlobalZeroSumClosureError("status mismatch")
    family = body["closure_family"]
    if _read_fraction(family["delta"]) != 1:
        raise GlobalZeroSumClosureError("delta mismatch")
    if _read_fraction(family["P_squared_minus_pq"]) != 1:
        raise GlobalZeroSumClosureError("P^2-pq mismatch")
    if _read_fraction(family["xy_projection"]) != 1 or _read_fraction(family["zw_projection"]) != 1:
        raise GlobalZeroSumClosureError("ordered unit projection mismatch")
    if _read_fraction(family["x_plus_y_plus_z_plus_w"]) != 0:
        raise GlobalZeroSumClosureError("center zero-sum mismatch")
    if family["phase_carrier_sum_basis_1_I"] != [0, 0]:
        raise GlobalZeroSumClosureError("phase zero-sum mismatch")
    if body["denominator_projection_binding"]["recursive_relation_evaluated"] is not False:
        raise GlobalZeroSumClosureError("recursive relation was promoted without evaluator")
    if body["global_enforcement"]["full_monolithic_evaluated"] is not False:
        raise GlobalZeroSumClosureError("full monolithic chain was promoted without evaluator")
    return {
        "schema": "HHS_PASS219B_GLOBAL_ZERO_SUM_CLOSURE_VALIDATION_V1",
        "status": "GLOBAL_ZERO_SUM_CLOSURE_VALIDATED",
        "proof_root_hash72": root,
    }
