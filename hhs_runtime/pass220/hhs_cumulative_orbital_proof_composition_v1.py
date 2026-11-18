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
    load_pass089_prime_sources,
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


def ordered_affine_orbit_witness(
    *, seed: int, ordered_states: Sequence[int], operation_word: str,
    odd_multiplier: int = 3,
) -> dict[str, Any]:
    """Compose EVERY ordered inherited parity operation as exact integer data.

    For an observed prefix, its affine representation is (A*seed+B)/D,
    with A, B, D integers and D>0. E doubles D; O sends
    (A,B,D) to (p*A,p*B+D,D). No reassociation, orbit sorting, float
    arithmetic, or change to the underlying parent-root proof records.
    """
    if (type(seed) is not int or seed <= 0
        or type(odd_multiplier) is not int or odd_multiplier < 1
        or not isinstance(operation_word, str)
        or not isinstance(ordered_states, (list, tuple))
        or not ordered_states or ordered_states[0] != seed
        or len(ordered_states) != len(operation_word) + 1):
        raise CumulativeOrbitalProofError("ORDERED_AFFINE_INPUT_INVALID")
    a, b, d = 1, 0, 1
    prefixes = []
    for i, operation in enumerate(operation_word):
        state = ordered_states[i]
        target = ordered_states[i + 1]
        if type(state) is not int or type(target) is not int or state <= 0 or target <= 0:
            raise CumulativeOrbitalProofError("ORDERED_AFFINE_NONINTEGER_STATE")
        if a * seed + b != d * state:
            raise CumulativeOrbitalProofError("ORDERED_AFFINE_PREFIX_MISMATCH")
        if operation == "E":
            if state % 2 or target != state // 2:
                raise CumulativeOrbitalProofError("ORDERED_AFFINE_PARITY_OR_SUCCESSOR_MISMATCH")
            d *= 2
        elif operation == "O":
            if state % 2 == 0 or target != odd_multiplier * state + 1:
                raise CumulativeOrbitalProofError("ORDERED_AFFINE_PARITY_OR_SUCCESSOR_MISMATCH")
            a, b = odd_multiplier * a, odd_multiplier * b + d
        else:
            raise CumulativeOrbitalProofError("ORDERED_AFFINE_UNKNOWN_OPERATOR")
        if a * seed + b != d * target:
            raise CumulativeOrbitalProofError("ORDERED_AFFINE_PREFIX_MISMATCH")
        prefixes.append({"depth": i + 1, "operation": operation,
                         "A": str(a), "B": str(b), "D": str(d),
                         "integer_state": str(target)})
    return {
        "seed": str(seed), "operator_prime": str(odd_multiplier),
        "ordered_operation_word": operation_word,
        "A": str(a), "B": str(b), "D": str(d),
        "terminal_integer_state": str(ordered_states[-1]),
        "exact_ordered_endpoint_identity": True,
        "prefixes": prefixes,
        "projection_only": True,
        "source_equations_preserved": True,
        "native_vm81_admission": False,
    }


def compose_pass092_prime_product_orbits(
    root: Path, workload: Mapping[str, Any],
) -> dict[str, Any]:
    """Join actual Pass 092 seed factorization and ordered prime operator lanes.

    Source receipts, factor vectors, operator roots, and deterministic
    replay are preserved. Scheduled prime choices are verified per edge.
    Unverified cross-operator suffixes NEVER acquire shared-future authority.
    """
    from native_projects.hhs_bifurcation_calibration.hhs_pass092_prime_product_harmonic_manifolds_v1 import (
        verify_replay as verify_pass092_replay,
        _step as native_generalized_step,
        make_seed,
        operator_contract,
    )
    if workload.get("claims_asymptotic_result") or workload.get("cache_as_proof"):
        raise CumulativeOrbitalProofError("PASS092_ASYMPTOTIC_OR_CACHE_PROOF_NOT_AUTHORIZED")
    replay = verify_pass092_replay(root, workload)
    if replay.get("deterministic_replay_verified") is not True:
        raise CumulativeOrbitalProofError("PASS092_ORIGINAL_REPLAY_REQUIRED")
    original = replay["initial"]
    seeds = workload["seeds"]
    source_primes = {
        item["prime"]: item for item in load_pass089_prime_sources(root)
    }
    for seed in seeds:
        basis = seed["prime_basis"]
        roots = [source_primes.get(p) for p in basis]
        if any(x is None for x in roots):
            raise CumulativeOrbitalProofError("PASS092_UNWITNESSED_PRIME_BASIS")
        if make_seed(roots, seed["factor_vector"]) != seed:
            raise CumulativeOrbitalProofError("PASS092_COMPOSITE_SEED_PROVENANCE_MISMATCH")
    for op in workload["operators"]:
        source = source_primes.get(op["operator_prime"])
        if source is None or operator_contract(source) != op:
            raise CumulativeOrbitalProofError("PASS092_OPERATOR_PROVENANCE_MISMATCH")
    seed_by_root = {s["seed_root_hash72"]: s for s in seeds}
    op_by_root = {o["operator_root_hash72"]: o for o in workload["operators"]}
    checked = []
    for lane in original["lane_receipts"]:
        seed = seed_by_root.get(lane["seed_root_hash72"])
        operator = op_by_root.get(lane["operator_root_hash72"])
        if seed is None or operator is None:
            raise CumulativeOrbitalProofError("PASS092_LANE_PARENT_UNKNOWN")
        states = lane["ordered_states"]
        operations = lane["ordered_operations"]
        if not states or states[0] != seed["exact_value"] or len(states) != len(operations) + 1:
            raise CumulativeOrbitalProofError("PASS092_LANE_ORDERED_STATE_MISMATCH")
        schedule = workload["operator_schedule"]
        if workload["mode"] == "PRIME_SCHEDULED_MANIFOLD" and not schedule:
            raise CumulativeOrbitalProofError("PASS092_EMPTY_OPERATOR_SCHEDULE")
        a, b, d = 1, 0, 1
        prefixes = []
        for i, word in enumerate(operations):
            p = (schedule[i % len(schedule)]
                 if workload["mode"] == "PRIME_SCHEDULED_MANIFOLD"
                 else lane["operator_prime"])
            if p not in source_primes or p not in {o["operator_prime"] for o in workload["operators"]}:
                raise CumulativeOrbitalProofError("PASS092_UNWITNESSED_SCHEDULE_OPERATOR")
            native_word, next_value = native_generalized_step(states[i], p)
            if word != native_word or next_value != states[i + 1]:
                raise CumulativeOrbitalProofError("PASS092_ORDERED_NATIVE_TRANSITION_MISMATCH")
            if a * seed["exact_value"] + b != d * states[i]:
                raise CumulativeOrbitalProofError("PASS092_ORDERED_PREFIX_IDENTITY_MISMATCH")
            if word == "E":
                d *= 2
            else:
                a, b = p * a, p * b + d
            if a * seed["exact_value"] + b != d * next_value:
                raise CumulativeOrbitalProofError("PASS092_ORDERED_PREFIX_IDENTITY_MISMATCH")
            prefixes.append({"depth": i + 1, "ordered_operator": word,
                             "source_operator_prime": p,
                             "A": str(a), "B": str(b), "D": str(d),
                             "integer_state": str(next_value)})
        checked.append({
            "lane_id": lane["lane_id"],
            "lane_root_hash72": lane["lane_root_hash72"],
            "history_root_hash72": lane["history_root_hash72"],
            "seed_root_hash72": seed["seed_root_hash72"],
            "factor_vector": seed["factor_vector"],
            "prime_basis": seed["prime_basis"],
            "operator_root_hash72": lane["operator_root_hash72"],
            "mode": workload["mode"],
            "operator_order_preserved": True,
            "exact_affine_prefixes": prefixes,
            "all_prefixes_verified": True,
            "cycle_status": lane["cycle_status"],
            "asymptotic_result_proved": False,
        })
    if len(checked) != len(original["lane_receipts"]):
        raise CumulativeOrbitalProofError("PASS092_LANES_DROPPED")
    intersections = []
    by_id = {x["lane_id"]: x for x in original["lane_receipts"]}
    for edge in original["state_intersections"]:
        left, right = by_id[edge["lane_a"]], by_id[edge["lane_b"]]
        if (left["ordered_states"][edge["lane_a_depth"]] != edge["state"]
            or right["ordered_states"][edge["lane_b_depth"]] != edge["state"]):
            raise CumulativeOrbitalProofError("PASS092_INTERSECTION_SOURCE_MISMATCH")
        # The inherited Pass 092 same-operator boolean is preserved verbatim;
        # scheduled state-dependent transitions need more than this boolean.
        intersections.append({**edge,
            "phase_scheduled_shared_future_not_inferred":
                workload["mode"] == "PRIME_SCHEDULED_MANIFOLD",
            "full_tensor_equivalence_proved": False,
        })
    result = {
        "schema": "HHS_PASS220_CUMULATIVE_PASS092_PRIME_PRODUCT_ORBIT_COMPOSITION_V1",
        "parent_pass092_tensor_root_hash72": original["tensor_root_hash72"],
        "parent_pass091_release_root_hash72": original["parent_pass091_release_root_hash72"],
        "deterministic_pass092_replay_verified": True,
        "prime_product_seed_count": len(seeds),
        "lane_count": len(checked),
        "ordered_composite_and_prime_lanes": checked,
        "original_state_intersections": intersections,
        "operator_schedule": workload["operator_schedule"],
        "cache_as_trajectory_proof": False,
        "universal_orbit_embedding_proved": False,
        "canonical_vm81_admission": False,
    }
    result["composition_sha256"] = sha256(_typed_json(result).encode()).hexdigest()
    return result


def ordered_shared_suffix_witnesses(
    lanes: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Recover all lane-pair intersections and exactly equal observed suffixes.

    The universal deterministic-successor continuation follows by induction
    from equal scalar states; it does NOT identify distinct native ancestry,
    ordered-phase/tensor states, or prove termination of either trajectory.
    """
    if any(
        not isinstance(lane.get("ordered_states"), list)
        or not isinstance(lane.get("state_nodes"), list)
        or len(lane["ordered_states"]) != len(lane["state_nodes"])
        for lane in lanes
    ):
        raise CumulativeOrbitalProofError("SHARED_SUFFIX_SOURCE_STRUCTURE_INVALID")
    result: list[dict[str, Any]] = []
    for left_index, left in enumerate(lanes):
        la = left["ordered_states"]
        for right in lanes[left_index + 1:]:
            rb = right["ordered_states"]
            locations: dict[int, list[int]] = {}
            for j, value in enumerate(rb):
                locations.setdefault(value, []).append(j)
            candidates = [
                (i, j) for i, value in enumerate(la)
                for j in locations.get(value, ())
            ]
            if not candidates:
                continue
            i, j = min(candidates)
            matched_steps = min(len(la) - i, len(rb) - j)
            for depth in range(matched_steps):
                a, b = la[i + depth], rb[j + depth]
                if type(a) is not int or type(b) is not int or a != b:
                    raise CumulativeOrbitalProofError("ORDERED_SHARED_SUFFIX_MISMATCH")
                if depth + 1 < matched_steps:
                    op_a, next_a = _next_state(a)
                    op_b, next_b = _next_state(b)
                    if next_a != la[i + depth + 1] or next_b != rb[j + depth + 1] or op_a != op_b:
                        raise CumulativeOrbitalProofError("SHARED_SUFFIX_NATIVE_SUCCESSOR_MISMATCH")
            an = left["state_nodes"][i]
            bn = right["state_nodes"][j]
            result.append({
                "left_lane_id": left["lane_id"],
                "right_lane_id": right["lane_id"],
                "left_depth": i,
                "right_depth": j,
                "intersection_value": la[i],
                "exact_observed_successor_count": matched_steps - 1,
                "same_deterministic_successor_rule": True,
                "equal_future_scalar_successors_by_induction": True,
                "full_native_state_equivalence_proved": False,
                "left_intersection_root_hash72": an["state_root_hash72"],
                "right_intersection_root_hash72": bn["state_root_hash72"],
                "left_independent_prefix_root_hash72": left["independent_prefix_root_hash72"],
                "right_independent_prefix_root_hash72": right["independent_prefix_root_hash72"],
                "distinct_ancestry_preserved": True,
            })
    return result


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
        affine = ordered_affine_orbit_witness(
            seed=seed, ordered_states=states, operation_word=word,
        )
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
            "exact_ordered_affine_orbit": affine,
            "terminal_cycle_reached": lane["terminal_cycle_reached"],
            "outcome": lane["outcome"],
        })

    shared_suffixes = ordered_shared_suffix_witnesses(lanes)
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
        "ordered_shared_suffix_witnesses": shared_suffixes,
        "shared_suffix_pair_count": len(shared_suffixes),
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
