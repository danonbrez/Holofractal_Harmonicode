from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from typing import Any

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass129_invariant_delta_rational_projection_algebra_v1 import canonical_pass129_request

SCHEMA = "HHS_PASS219B_GLOBAL_RELATION_BRIDGE_PROOF_V3"
PASS_ID = "PASS_219B_I6_ADDITIVE_STRUCTURAL_BRIDGE"
CLOSURE_EXTENSION_SHA256 = "28d89e625af38f7fbc2e2df61050043a6716c803458f2b5e6912a62f384ceb2d"
PARENT_MONOLITHIC_SHA256 = "9f2238981bf509d22ffebb46816346f389fd2d949ccd7956cde3630ab2b56944"
PHASE_QUANTIZATION_OBJECT = (
    "NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),"
    "List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),"
    "List(I^4,I,I^3))),4)"
)
PHASE_QUANTIZATION_SHA256 = "5c4080c9bc87edf358d27c942b55f93e7f5997d6474102cb3a09c1c55ee6a132"
HYDRATION_STATE_COUNT = 81 * 41 * 3 * 5184
PHASE_PROJECTED_STATE_COUNT = HYDRATION_STATE_COUNT * 81

class GlobalZeroSumClosureError(RuntimeError):
    pass

def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))

def _step(proof: dict[str, Any], rule: str) -> dict[str, Any]:
    for item in proof.get("steps", []):
        if item.get("rule") == rule:
            return item
    raise GlobalZeroSumClosureError(f"missing inherited proof step: {rule}")

def _replay_pass129(center_P: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    engine, request = canonical_pass129_request(center_P=center_P)
    proof = engine.prove(request)
    validation = engine.validate(request, proof)
    replay = engine.replay(request, proof)
    if validation["status"] != "PASS_129_PROOF_VALIDATED":
        raise GlobalZeroSumClosureError("inherited Pass129 validation failed")
    if replay["status"] != "PASS_129_DETERMINISTIC_REPLAY_VALIDATED":
        raise GlobalZeroSumClosureError("inherited Pass129 replay failed")
    return request, proof

def prove_global_zero_sum_closure(*, center_P: Any = 4) -> dict[str, Any]:
    if sha256(PHASE_QUANTIZATION_OBJECT.encode("utf-8")).hexdigest() != PHASE_QUANTIZATION_SHA256:
        raise GlobalZeroSumClosureError("phase-quantization source identity mismatch")
    request, inherited = _replay_pass129(center_P)
    P = _fraction(inherited["derived"]["P"])
    p = _fraction(inherited["derived"]["p"])
    q = _fraction(inherited["derived"]["q"])
    delta = _fraction(inherited["derived"]["delta"])
    membrane = _fraction(inherited["derived"]["membrane_residue"])
    p2_minus_pq = _fraction(inherited["derived"]["P_squared_minus_pq"])
    phase_step = _step(inherited, "FOUR_PHASE_CARRIER_ZERO_SUM")
    if delta != 1 or p != P - 1 or q != P + 1 or p2_minus_pq != 1:
        raise GlobalZeroSumClosureError("Pass129 unit-delta closure family mismatch")
    if _fraction(request["native_projection_values"]["XY_PRODUCT"]) != 1 or _fraction(request["zw_product"]) != 1:
        raise GlobalZeroSumClosureError("ordered unit projection mismatch")
    if _fraction(request["xyzw_sum"]) != 0 or phase_step["output"]["sum"] != [0, 0]:
        raise GlobalZeroSumClosureError("zero-sum mismatch")
    if membrane != 1:
        raise GlobalZeroSumClosureError("membrane unit residue mismatch")
    result: dict[str, Any] = {
        "schema": SCHEMA, "pass_id": PASS_ID, "status": "ADDITIVE_GLOBAL_RELATION_BRIDGE_PROVED",
        "closure_family": {"P": inherited["derived"]["P"], "p": inherited["derived"]["p"], "q": inherited["derived"]["q"],
            "delta": inherited["derived"]["delta"], "P_squared_minus_pq": inherited["derived"]["P_squared_minus_pq"],
            "xy_projection": request["native_projection_values"]["XY_PRODUCT"], "zw_projection": request["zw_product"],
            "x_plus_y_plus_z_plus_w": request["xyzw_sum"], "phase_carrier_sum_basis_1_I": deepcopy(phase_step["output"]["sum"]),
            "membrane_residue": inherited["derived"]["membrane_residue"]},
        "global_tensor_binding": {"symbol": "N", "source_sha256": PARENT_MONOLITHIC_SHA256, "indivisible": True},
        "phase_quantization_binding": {"symbol": "D", "source": PHASE_QUANTIZATION_OBJECT, "source_sha256": PHASE_QUANTIZATION_SHA256,
            "recursive_relation": "N/D^4=D^4", "structural_projection_registered": True, "scalar_cancellation_allowed": False},
        "hydration_bridge": {"lo_shu_sudoku_qudit_bound": True, "cell_count81": 81, "lo_shu_group_count41": 41,
            "trit_count3": 3, "vm5184_slot_count": 5184, "hydration_state_count": HYDRATION_STATE_COUNT,
            "phase_origin_count81": 81, "phase_projected_state_count": PHASE_PROJECTED_STATE_COUNT},
        "projection_authority": {"i6_projection_id": "PI-UCE-N-D-HYDRATION-I6-v1", "i6_projection_is_additive": True,
            "uqcel_integer_symmetric_reused_as_subprojection": True, "legacy_full_symbolic_v1_preserved_unsupported": True,
            "legacy_full_symbolic_residual_mask": "HHS_UQCEL_RESIDUAL_FULL_SOURCE", "projection_equality_is_not_native_identity": True,
            "canonical_mutation_authority": False, "canonical_hash72_authority": False, "canonical_persistence_authority": False},
        "inherited_pass129": {"proof_root_hash72": inherited["proof_root_hash72"], "phase_zero_sum_step_root_hash72": phase_step["step_root_hash72"]}}
    result["proof_root_hash72"] = _hash("hhs_pass219b_global_relation_bridge_v3", result)
    return result

def verify_global_zero_sum_closure(proof: dict[str, Any]) -> dict[str, Any]:
    body = deepcopy(proof)
    root = body.pop("proof_root_hash72", None)
    if root != _hash("hhs_pass219b_global_relation_bridge_v3", body): raise GlobalZeroSumClosureError("proof root mismatch")
    if body.get("schema") != SCHEMA or body.get("pass_id") != PASS_ID or body.get("status") != "ADDITIVE_GLOBAL_RELATION_BRIDGE_PROVED":
        raise GlobalZeroSumClosureError("proof identity/status mismatch")
    family = body["closure_family"]; P = _fraction(family["P"])
    if _fraction(family["delta"]) != 1 or _fraction(family["p"]) != P - 1 or _fraction(family["q"]) != P + 1: raise GlobalZeroSumClosureError("zero-sum family mismatch")
    if _fraction(family["P_squared_minus_pq"]) != 1 or _fraction(family["xy_projection"]) != 1 or _fraction(family["zw_projection"]) != 1: raise GlobalZeroSumClosureError("unit projection mismatch")
    if _fraction(family["x_plus_y_plus_z_plus_w"]) != 0 or family["phase_carrier_sum_basis_1_I"] != [0, 0] or _fraction(family["membrane_residue"]) != 1: raise GlobalZeroSumClosureError("closure mismatch")
    if body["global_tensor_binding"] != {"symbol": "N", "source_sha256": PARENT_MONOLITHIC_SHA256, "indivisible": True}: raise GlobalZeroSumClosureError("N binding mismatch")
    expected_phase = {"symbol": "D", "source": PHASE_QUANTIZATION_OBJECT, "source_sha256": PHASE_QUANTIZATION_SHA256, "recursive_relation": "N/D^4=D^4", "structural_projection_registered": True, "scalar_cancellation_allowed": False}
    if body["phase_quantization_binding"] != expected_phase or sha256(PHASE_QUANTIZATION_OBJECT.encode("utf-8")).hexdigest() != PHASE_QUANTIZATION_SHA256: raise GlobalZeroSumClosureError("D binding mismatch")
    expected_hydration = {"lo_shu_sudoku_qudit_bound": True, "cell_count81": 81, "lo_shu_group_count41": 41, "trit_count3": 3, "vm5184_slot_count": 5184, "hydration_state_count": HYDRATION_STATE_COUNT, "phase_origin_count81": 81, "phase_projected_state_count": PHASE_PROJECTED_STATE_COUNT}
    if body["hydration_bridge"] != expected_hydration: raise GlobalZeroSumClosureError("hydration bridge mismatch")
    expected_authority = {"i6_projection_id": "PI-UCE-N-D-HYDRATION-I6-v1", "i6_projection_is_additive": True, "uqcel_integer_symmetric_reused_as_subprojection": True, "legacy_full_symbolic_v1_preserved_unsupported": True, "legacy_full_symbolic_residual_mask": "HHS_UQCEL_RESIDUAL_FULL_SOURCE", "projection_equality_is_not_native_identity": True, "canonical_mutation_authority": False, "canonical_hash72_authority": False, "canonical_persistence_authority": False}
    if body["projection_authority"] != expected_authority: raise GlobalZeroSumClosureError("projection authority mismatch")
    request, inherited = _replay_pass129(P); phase_step = _step(inherited, "FOUR_PHASE_CARRIER_ZERO_SUM")
    if _fraction(inherited["derived"]["p"]) != _fraction(family["p"]) or _fraction(inherited["derived"]["q"]) != _fraction(family["q"]): raise GlobalZeroSumClosureError("Pass129 center replay mismatch")
    if _fraction(request["xyzw_sum"]) != 0 or phase_step["output"]["sum"] != [0, 0]: raise GlobalZeroSumClosureError("Pass129 closure replay mismatch")
    if body["inherited_pass129"] != {"proof_root_hash72": inherited["proof_root_hash72"], "phase_zero_sum_step_root_hash72": phase_step["step_root_hash72"]}: raise GlobalZeroSumClosureError("Pass129 receipt replay mismatch")
    return {"status": "ADDITIVE_GLOBAL_RELATION_BRIDGE_VALIDATED", "proof_root_hash72": root, "legacy_full_symbolic_v1_preserved_unsupported": True}

__all__ = ["SCHEMA", "PASS_ID", "CLOSURE_EXTENSION_SHA256", "PARENT_MONOLITHIC_SHA256", "PHASE_QUANTIZATION_OBJECT", "PHASE_QUANTIZATION_SHA256", "HYDRATION_STATE_COUNT", "PHASE_PROJECTED_STATE_COUNT", "GlobalZeroSumClosureError", "prove_global_zero_sum_closure", "verify_global_zero_sum_closure"]
