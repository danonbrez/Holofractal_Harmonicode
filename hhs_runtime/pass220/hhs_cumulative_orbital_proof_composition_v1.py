"""Pass 220 cumulative orbital proof composition over existing HHS services.

This is a real join of independently recorded runtime witnesses, not a corpus
filename match or a scalar replacement theorem. Every supplied Pass 091 lane
is replayed, every prime seed receives its existing typed p/q geometry, and
global/phase/theory receipts remain intact and distinguishable. The original
universal theorem is NOT inferred from any finite execution trace.

The native HNAN gate is invoked only with the caller's actual existing branch
claims and built ABI. This code does not synthesize favorable claims, bypass
VM81, or convert candidate hashes to canonical admissions.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence
from hashlib import sha256
import json

from native_projects.hhs_bifurcation_calibration.hhs_pass091_collatz_prime_tensor_decay_entanglement_v1 import (
    verify_replay,
    _next_state,
)
from hhs_runtime.hhs_phase_inverted_pythagorean_geometry_v1 import (
    full_geometry_witness,
    pq_orientation_witness,
)
from hhs_runtime.hhs_recursive_global_constraint_bundle_v1 import (
    enforce_recursive_global_constraint_bundle,
)
from hhs_runtime.hhs_pass220_i072_theory_constructor_hash216_hydration_v1 import (
    build_theory_constructor,
    hydrate_theory_constructor,
    validate_theory_constructor,
)

SCHEMA = "HHS_PASS220_CUMULATIVE_ORBITAL_NATIVE_PROOF_COMPOSITION_V1"


class CumulativeOrbitalProofError(ValueError):
    pass


def _typed_json(value: Any) -> str:
    # The stored structural witnesses remain untouched; JSON is only the
    # additive replay receipt representation, not mathematical evaluation.
    from fractions import Fraction
    from decimal import Decimal
    def encode(item: Any) -> Any:
        if isinstance(item, Fraction):
            return {"fraction": [item.numerator, item.denominator]}
        if isinstance(item, Decimal):
            return {"decimal": str(item)}
        raise TypeError(f"unserializable witness type: {type(item).__name__}")
    return json.dumps(value, default=encode, sort_keys=True,
                      ensure_ascii=False, allow_nan=False,
                      separators=(",", ":"))


def compose_inherited_orbital_proof(
    root: Path,
    workload: Mapping[str, Any],
    *,
    native_library: str | None = None,
    native_branches: Sequence[Mapping[str, object]] | None = None,
    runtime_authority_state: Mapping[str, Any] | None = None,
    runtime_authority_receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if (native_library is None) != (native_branches is None):
        raise CumulativeOrbitalProofError("NATIVE_LIBRARY_AND_ACTUAL_CLAIMS_REQUIRED_TOGETHER")
    if runtime_authority_receipt is not None and runtime_authority_state is None:
        raise CumulativeOrbitalProofError("ACTUAL_AUTHORITY_STATE_REQUIRED")
    if workload.get("claims_collatz_theorem"):
        raise CumulativeOrbitalProofError("BOUNDED_TRACE_IS_NOT_UNIVERSAL_PROOF")

    replay = verify_replay(root, workload)
    original = replay["initial"]
    lanes = original["lane_receipts"]
    if not lanes or len(lanes) != len(workload["prime_sources"]):
        raise CumulativeOrbitalProofError("ALL_PRIME_LANES_REQUIRED")
    if replay.get("deterministic_replay_verified") is not True:
        raise CumulativeOrbitalProofError("INHERITED_REPLAY_FAILED")
    checked_lanes = []
    for lane in lanes:
        seed = lane["prime_seed"]
        if type(seed) is not int or seed <= 2 or seed % 2 == 0:
            raise CumulativeOrbitalProofError("ODD_PRIME_ORBITAL_SEED_REQUIRED")
        states = lane["ordered_states"]
        word = lane["operation_word"]
        nodes = lane["state_nodes"]
        if not states or len(states) != len(word) + 1 or len(nodes) != len(states):
            raise CumulativeOrbitalProofError("ORBITAL_LENGTH_OR_ANCESTRY_MISMATCH")
        for i, symbol in enumerate(word):
            op, nxt = _next_state(states[i])
            if symbol != op or states[i+1] != nxt:
                raise CumulativeOrbitalProofError("ORBITAL_NATIVE_SUCCESSOR_MISMATCH")
            if nodes[i]["successor_integer_value"] != nxt:
                raise CumulativeOrbitalProofError("ORBITAL_NODE_LINK_MISMATCH")
            if nodes[i+1]["parent_state_root_hash72"] != nodes[i]["state_root_hash72"]:
                raise CumulativeOrbitalProofError("ORBITAL_ANCESTRY_LINK_MISMATCH")
        pq = pq_orientation_witness(p=seed-1, q=seed+1, P=seed)
        if not pq["orientation_quotient_closed"]:
            raise CumulativeOrbitalProofError("EXACT_PQ_BRIDGE_NOT_CLOSED")
        checked_lanes.append({
            "lane_id": lane["lane_id"], "prime_seed": seed,
            "prime_source_root_hash72": lane["prime_source_root_hash72"],
            "ordered_history_root_hash72": lane["ordered_history_root_hash72"],
            "independent_prefix_root_hash72": lane["independent_prefix_root_hash72"],
            "state_roots": [n["state_root_hash72"] for n in nodes],
            "tensor_address": {
                "tensor_coordinate": lane["tensor_coordinate"],
                "vm81_cell": lane["vm81_cell"],
                "lo_shu_value": lane["lo_shu_value"],
                "u72_offset": lane["u72_offset"],
            },
            "exact_prime_centered_orientation": pq,
            "terminal_cycle_reached": lane["terminal_cycle_reached"],
            "outcome": lane["outcome"],
        })

    geometry = full_geometry_witness()
    global_constraints = enforce_recursive_global_constraint_bundle()
    theory = build_theory_constructor()
    hydrate = hydrate_theory_constructor(theory)
    validation = validate_theory_constructor(theory)
    if hydrate.get("roundtrip_exact") is not True:
        raise CumulativeOrbitalProofError("INHERITED_THEORY_HYDRATION_REPLAY_FAILED")
    if validation is False:
        raise CumulativeOrbitalProofError("INHERITED_THEORY_CONSTRUCTOR_REPLAY_FAILED")

    hnan = None
    if native_library is not None:
        from hhs_runtime.pass220.hnan_all_branch_native_trace_v1 import (
            inspect_all_native_hnan_branches,
        )
        hnan = inspect_all_native_hnan_branches(
            native_branches, native_library=native_library,
            parent_receipt_hash72=original["result_root_hash72"],
            parent_root216=theory["theory_hash216"],
        )
    authority = None
    if runtime_authority_state is not None:
        from hhs_runtime.hhs_authority_gate_v1 import audit_runtime_authority
        audit = audit_runtime_authority(
            runtime_authority_state,
            source="hhs_cumulative_orbital_proof_composition_v1",
            receipt=runtime_authority_receipt,
        )
        authority = audit.to_dict()

    result = {
        "schema": SCHEMA,
        "parent_pass091_result_root_hash72": original["result_root_hash72"],
        "native_deterministic_replay": True,
        "all_provided_odd_prime_lanes": checked_lanes,
        "lane_count": len(checked_lanes),
        "original_prime_entanglement_graph": original["entanglement_graph"],
        "full_geometry_witness": geometry,
        "full_recursive_constraint_bundle": global_constraints,
        "inherited_i072_theory_constructor": theory,
        "inherited_i072_hydration_validation": validation,
        "native_hnan_all_branch_trace": hnan,
        "actual_runtime_authority_audit": authority,
        "unprovided_native_hnan_is_not_success": hnan is None,
        "unprovided_vm81_authority_is_not_success": authority is None,
        "all_lanes_terminal": all(x["terminal_cycle_reached"] for x in checked_lanes),
        "finite_orbital_receipts_do_not_prove_universal_closure": True,
        "global_theorem_completed": False,
        "candidate_only": True,
        "canonical_vm81_admission": False,
        "hash216_minted": False,
    }
    result["composition_sha256"] = sha256(_typed_json(result).encode()).hexdigest()
    return result
