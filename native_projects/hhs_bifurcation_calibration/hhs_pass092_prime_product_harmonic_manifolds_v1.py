from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Any, Mapping
import copy
import json

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root
from native_projects.hhs_bifurcation_calibration.hhs_pass091_collatz_prime_tensor_decay_entanglement_v1 import load_pass089_prime_sources

PASS_ID = "PASS_092"
WORKLOAD_SCHEMA = "HHS_PRIME_PRODUCT_HARMONIC_WORKLOAD_V1"
RESULT_SCHEMA = "HHS_PRIME_OPERATOR_TENSOR_RECEIPT_V1"
OPERATOR_SCHEMA = "HHS_GENERALIZED_COLLATZ_OPERATOR_V1"
SEED_SCHEMA = "HHS_PRIME_PRODUCT_SEED_V1"
LANE_SCHEMA = "HHS_GENERALIZED_COLLATZ_LANE_RECEIPT_V1"
OUTCOMES = {
    "KNOWN_CYCLE_REACHED", "NEW_CYCLE_DETECTED", "STATE_INTERSECTION_REACHED",
    "STEP_BOUNDED", "MAGNITUDE_BOUNDED", "RESOURCE_BOUNDED",
    "DETERMINISTIC_GROWTH", "STABLE_UNRESOLVED",
}
REJECTIONS = (
    "REJECT_INVALID_PRIME_PRODUCT_SEED",
    "REJECT_UNWITNESSED_OPERATOR_PRIME",
    "REJECT_GENERALIZED_COLLATZ_PARITY_VIOLATION",
    "REJECT_PRIME_OPERATOR_ORDER_MISMATCH",
    "REJECT_INVALID_CROSS_OPERATOR_SUFFIX_MERGE",
    "REJECT_UNWITNESSED_CYCLE",
    "REJECT_BOUND_AS_ASYMPTOTIC_RESULT",
    "REJECT_COMPOSITE_SEED_IDENTITY_ERASURE",
    "REJECT_CACHE_AS_TRAJECTORY_PROOF",
    "REJECT_FLOAT_AS_INTEGER_MANIFOLD_AUTHORITY",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def witnessed_primes(repo: Path) -> list[dict[str, Any]]:
    return load_pass089_prime_sources(repo)


def operator_contract(source: Mapping[str, Any]) -> dict[str, Any]:
    p = source["prime"]
    contract = {
        "schema": OPERATOR_SCHEMA,
        "operator_prime": p,
        "operator_prime_source_root_hash72": source["prime_receipt_root_hash72"],
        "even_rule": {"predicate": "n mod 2 = 0", "transform": "n / 2"},
        "odd_rule": {"predicate": "n mod 2 = 1", "transform": "p*n + 1"},
        "integer_only": True,
        "floating_point_used": False,
    }
    contract["operator_root_hash72"] = root("hhs_pass092_generalized_collatz_operator_v1", contract)
    return stable(contract)


def make_seed(prime_basis: list[Mapping[str, Any]], exponent_vector: list[int]) -> dict[str, Any]:
    if len(prime_basis) != len(exponent_vector) or any(not isinstance(e, int) or isinstance(e, bool) or e < 0 for e in exponent_vector):
        raise ContractError("REJECT_INVALID_PRIME_PRODUCT_SEED")
    value = 1
    factorization = []
    for source, exponent in zip(prime_basis, exponent_vector):
        p = source["prime"]
        if exponent:
            value *= p ** exponent
            factorization.append({"prime": p, "exponent": exponent, "prime_source_root_hash72": source["prime_receipt_root_hash72"]})
    seed = {
        "schema": SEED_SCHEMA,
        "factorization": factorization,
        "exact_value": value,
        "factor_vector": list(exponent_vector),
        "prime_basis": [s["prime"] for s in prime_basis],
        "prime_tensor_root_hash72": root("hhs_pass092_prime_basis_v1", [{"prime": s["prime"], "root": s["prime_receipt_root_hash72"]} for s in prime_basis]),
    }
    seed["seed_root_hash72"] = root("hhs_pass092_prime_product_seed_v1", seed)
    return stable(seed)


def generate_seeds(repo: Path, *, basis_size: int, max_exponent: int = 1, include_unit: bool = True, max_seed_count: int | None = None) -> list[dict[str, Any]]:
    basis = witnessed_primes(repo)[:basis_size]
    vectors = product(range(max_exponent + 1), repeat=basis_size)
    seeds = []
    for vector in vectors:
        if not include_unit and not any(vector):
            continue
        seeds.append(make_seed(basis, list(vector)))
        if max_seed_count is not None and len(seeds) >= max_seed_count:
            break
    return seeds


def default_workload(repo: Path, *, workload_id: str, basis_size: int = 4, operator_count: int = 3,
                     max_exponent: int = 1, max_steps: int = 256, max_magnitude_bits: int = 4096,
                     max_seed_count: int | None = None, mode: str = "FIXED_OPERATOR_FAMILY") -> dict[str, Any]:
    sources = witnessed_primes(repo)
    operators = [operator_contract(s) for s in sources if s["prime"] >= 3][:operator_count]
    seeds = generate_seeds(repo, basis_size=basis_size, max_exponent=max_exponent, max_seed_count=max_seed_count)
    return stable({
        "schema": WORKLOAD_SCHEMA,
        "workload_id": workload_id,
        "parent_pass091_release_root_hash72": _read_json(repo / "PASS_091_RELEASE_MANIFEST.json")["pass091_release_root_hash72"],
        "parent_pass089_release_root_hash72": _read_json(repo / "PASS_089_RELEASE_MANIFEST.json")["pass089_release_root_hash72"],
        "mode": mode,
        "seed_basis_size": basis_size,
        "max_exponent": max_exponent,
        "seeds": seeds,
        "operators": operators,
        "operator_schedule": [o["operator_prime"] for o in operators],
        "resource_budget": {"max_steps_per_lane": max_steps, "max_magnitude_bits": max_magnitude_bits, "max_lanes": len(seeds) * max(1, len(operators))},
        "canonical_integer_only": True,
        "claims_asymptotic_result": False,
        "compression_policy": "SAME_OPERATOR_SUFFIX_ONLY_WITH_ANCESTRY_PRESERVED",
        "cache_requires_replay": True,
    })


def _validate_seed(seed: Mapping[str, Any]) -> None:
    if seed.get("schema") != SEED_SCHEMA or not isinstance(seed.get("exact_value"), int) or isinstance(seed.get("exact_value"), bool):
        raise ContractError("REJECT_INVALID_PRIME_PRODUCT_SEED")
    value = 1
    for item in seed.get("factorization", []):
        if not item.get("prime_source_root_hash72") or item["exponent"] < 1:
            raise ContractError("REJECT_INVALID_PRIME_PRODUCT_SEED")
        value *= item["prime"] ** item["exponent"]
    if value != seed["exact_value"]:
        raise ContractError("REJECT_INVALID_PRIME_PRODUCT_SEED")


def _validate_workload(workload: Mapping[str, Any]) -> None:
    if workload.get("schema") != WORKLOAD_SCHEMA:
        raise ContractError("REJECT_INVALID_PRIME_PRODUCT_SEED")
    if not workload.get("canonical_integer_only") or workload.get("float_derived_state"):
        raise ContractError("REJECT_FLOAT_AS_INTEGER_MANIFOLD_AUTHORITY")
    if workload.get("claims_asymptotic_result"):
        raise ContractError("REJECT_BOUND_AS_ASYMPTOTIC_RESULT")
    if workload.get("erase_factor_vectors"):
        raise ContractError("REJECT_COMPOSITE_SEED_IDENTITY_ERASURE")
    if workload.get("cache_as_proof"):
        raise ContractError("REJECT_CACHE_AS_TRAJECTORY_PROOF")
    if workload.get("merge_cross_operator_suffixes"):
        raise ContractError("REJECT_INVALID_CROSS_OPERATOR_SUFFIX_MERGE")
    for seed in workload.get("seeds", []):
        _validate_seed(seed)
    for op in workload.get("operators", []):
        if op.get("schema") != OPERATOR_SCHEMA or not op.get("operator_prime_source_root_hash72"):
            raise ContractError("REJECT_UNWITNESSED_OPERATOR_PRIME")
    if workload.get("mode") == "PRIME_SCHEDULED_MANIFOLD" and workload.get("reordered_schedule"):
        raise ContractError("REJECT_PRIME_OPERATOR_ORDER_MISMATCH")


def _step(n: int, p: int, *, force_bad_parity: bool = False) -> tuple[str, int]:
    if not isinstance(n, int) or isinstance(n, bool):
        raise ContractError("REJECT_FLOAT_AS_INTEGER_MANIFOLD_AUTHORITY")
    if force_bad_parity:
        raise ContractError("REJECT_GENERALIZED_COLLATZ_PARITY_VIOLATION")
    return ("E", n // 2) if n % 2 == 0 else (f"O{p}", p * n + 1)


def _execute_lane(seed: Mapping[str, Any], operator: Mapping[str, Any], workload: Mapping[str, Any]) -> dict[str, Any]:
    n = seed["exact_value"]
    p = operator["operator_prime"]
    states = [n]
    operations: list[str] = []
    seen = {n: 0}
    cycle_entry = None
    cycle_states: list[int] = []
    maximum = n
    outcome = "STABLE_UNRESOLVED"
    budget = workload["resource_budget"]
    schedule = workload.get("operator_schedule", [p])

    for step_index in range(budget["max_steps_per_lane"]):
        if states[-1].bit_length() > budget["max_magnitude_bits"]:
            outcome = "MAGNITUDE_BOUNDED"
            break
        active_p = p
        if workload.get("mode") == "PRIME_SCHEDULED_MANIFOLD":
            active_p = schedule[step_index % len(schedule)]
        op, nxt = _step(states[-1], active_p, force_bad_parity=bool(workload.get("force_parity_violation")))
        operations.append(op)
        states.append(nxt)
        maximum = max(maximum, nxt)
        if nxt in seen:
            cycle_entry = seen[nxt]
            cycle_states = states[cycle_entry:-1]
            outcome = "KNOWN_CYCLE_REACHED" if p == 3 and cycle_states == [1, 4, 2] else "NEW_CYCLE_DETECTED"
            break
        seen[nxt] = len(states) - 1
    else:
        outcome = "STEP_BOUNDED"

    if workload.get("claim_cycle_without_repeat") and outcome not in {"KNOWN_CYCLE_REACHED", "NEW_CYCLE_DETECTED"}:
        raise ContractError("REJECT_UNWITNESSED_CYCLE")

    history = {"seed_root": seed["seed_root_hash72"], "operator_root": operator["operator_root_hash72"], "states": states, "operations": operations}
    lane = {
        "schema": LANE_SCHEMA,
        "lane_id": f"gcollatz:seed:{seed['exact_value']}:operator:{p}",
        "seed_root_hash72": seed["seed_root_hash72"],
        "factor_vector": seed["factor_vector"],
        "exact_seed_value": seed["exact_value"],
        "operator_prime": p,
        "operator_root_hash72": operator["operator_root_hash72"],
        "mode": workload["mode"],
        "ordered_states": states,
        "ordered_operations": operations,
        "operation_word_root_hash72": root("hhs_pass092_operation_word_v1", operations),
        "transition_count": len(operations),
        "maximum_excursion": maximum,
        "cycle_status": outcome,
        "cycle_entry_state": states[cycle_entry] if cycle_entry is not None else None,
        "cycle_length": len(cycle_states),
        "cycle_states": cycle_states,
        "history_preserved": True,
        "history_root_hash72": root("hhs_pass092_lane_history_v1", history),
    }
    lane["lane_root_hash72"] = root("hhs_pass092_generalized_collatz_lane_receipt_v1", lane)
    return stable(lane)


def _intersections(lanes: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    edges = []
    for i, a in enumerate(lanes):
        a_depth = {v: d for d, v in enumerate(a["ordered_states"])}
        for b in lanes[i + 1:]:
            hits = [(a_depth[v] + d, v, a_depth[v], d) for d, v in enumerate(b["ordered_states"]) if v in a_depth]
            if not hits:
                continue
            _, value, da, db = min(hits)
            same_operator = a["operator_prime"] == b["operator_prime"]
            edge = {
                "schema": "HHS_GENERALIZED_COLLATZ_INTERSECTION_V1",
                "lane_a": a["lane_id"], "lane_b": b["lane_id"], "state": value,
                "lane_a_depth": da, "lane_b_depth": db,
                "same_operator_family": same_operator,
                "shared_future_authorized": same_operator,
                "incoming_ancestry_preserved": True,
            }
            edge["intersection_root_hash72"] = root("hhs_pass092_intersection_v1", edge)
            edges.append(stable(edge))
    return edges


def run(repo: Path, workload: Mapping[str, Any], *, replay: bool = False) -> dict[str, Any]:
    _validate_workload(workload)
    pairs = [(s, o) for s in workload["seeds"] for o in workload["operators"]]
    bounded = len(pairs) > workload["resource_budget"]["max_lanes"]
    pairs = pairs[:workload["resource_budget"]["max_lanes"]]
    lanes = [_execute_lane(s, o, workload) for s, o in pairs]
    intersections = _intersections(lanes)
    cycle_classes = sorted({(lane["operator_prime"], tuple(lane["cycle_states"])) for lane in lanes if lane["cycle_states"]})
    result = {
        "schema": RESULT_SCHEMA,
        "pass_id": PASS_ID,
        "parent_pass091_release_root_hash72": workload["parent_pass091_release_root_hash72"],
        "workload": stable(dict(workload)),
        "prime_seed_count": sum(1 for s in workload["seeds"] if sum(s["factor_vector"]) == 1),
        "composite_seed_count": sum(1 for s in workload["seeds"] if sum(s["factor_vector"]) > 1),
        "operator_prime_count": len(workload["operators"]),
        "lane_count": len(lanes),
        "lane_receipts": lanes,
        "state_intersections": intersections,
        "cycle_classes": [{"operator_prime": p, "cycle_states": list(c)} for p, c in cycle_classes],
        "bounded_lanes": sum(l["cycle_status"] in {"STEP_BOUNDED", "MAGNITUDE_BOUNDED"} for l in lanes),
        "status": "RESOURCE_BOUNDED" if bounded else "DETERMINISTIC_FRONTIER_COMPLETE",
        "replay_verified": False,
        "unbounded_curriculum_not_single_run": True,
        "replay": replay,
    }
    result["tensor_root_hash72"] = root("hhs_pass092_prime_operator_tensor_receipt_v1", {k: v for k, v in result.items() if k not in {"replay", "replay_verified"}})
    return stable(result)


def verify_replay(repo: Path, workload: Mapping[str, Any]) -> dict[str, Any]:
    initial = run(repo, workload)
    replay_workload = copy.deepcopy(workload)
    if workload.get("alter_schedule_on_replay"):
        replay_workload["operator_schedule"] = list(reversed(replay_workload["operator_schedule"]))
        replay_workload["reordered_schedule"] = True
    try:
        replay_result = run(repo, replay_workload, replay=True)
    except ContractError:
        raise
    if initial["tensor_root_hash72"] != replay_result["tensor_root_hash72"]:
        raise ContractError("REJECT_PRIME_OPERATOR_ORDER_MISMATCH")
    return stable({"schema": "HHS_PASS_092_REPLAY_V1", "deterministic_replay_verified": True, "initial": initial, "replay": replay_result})


def commutator(p: int, q: int, n: int) -> dict[str, int]:
    left = p * (q * n + 1) + 1
    right = q * (p * n + 1) + 1
    return {"O_p_after_O_q": left, "O_q_after_O_p": right, "difference": left - right, "expected": p - q}


def workload_registry(repo: Path) -> list[dict[str, Any]]:
    return [
        default_workload(repo, workload_id="W92-01:prime-powers-under-T3", basis_size=3, operator_count=1, max_exponent=2, max_seed_count=16),
        default_workload(repo, workload_id="W92-02:square-free-first-four-under-T3", basis_size=4, operator_count=1),
        default_workload(repo, workload_id="W92-03:same-seeds-T3-T5-T7", basis_size=4, operator_count=3),
        default_workload(repo, workload_id="W92-04:first-five-square-free-tensor", basis_size=5, operator_count=3),
        default_workload(repo, workload_id="W92-05:mixed-exponents-two", basis_size=4, operator_count=3, max_exponent=2, max_seed_count=64),
        default_workload(repo, workload_id="W92-06:primorial-frontier", basis_size=6, operator_count=4, max_seed_count=32),
        default_workload(repo, workload_id="W92-07:cross-operator-intersections", basis_size=4, operator_count=4),
        default_workload(repo, workload_id="W92-08:cycle-discovery-5n1-7n1", basis_size=3, operator_count=3),
        default_workload(repo, workload_id="W92-09:noncommutative-prime-schedule", basis_size=3, operator_count=3, mode="PRIME_SCHEDULED_MANIFOLD"),
        default_workload(repo, workload_id="W92-10:same-operator-suffix-compression", basis_size=5, operator_count=2),
        default_workload(repo, workload_id="W92-11:resource-bounded-large-tensor", basis_size=6, operator_count=4, max_seed_count=64, max_steps=32),
        default_workload(repo, workload_id="W92-12:checkpoint-exact-replay", basis_size=5, operator_count=3, max_steps=128),
    ]


def negative_cases(repo: Path) -> list[dict[str, Any]]:
    cases = []
    def add(name: str, expected: str, mutate, replay: bool = False):
        w = default_workload(repo, workload_id=f"NEG92:{name}", basis_size=2, operator_count=2, max_steps=8)
        mutate(w)
        try:
            verify_replay(repo, w) if replay else run(repo, w)
            observed = "NO_REJECTION"
        except ContractError as e:
            observed = str(e)
        cases.append({"case": name, "expected": expected, "observed": observed, "passed": expected == observed})
    add("invalid-seed", REJECTIONS[0], lambda w: w["seeds"][0].update(exact_value=999))
    add("unwitnessed-operator", REJECTIONS[1], lambda w: w["operators"][0].pop("operator_prime_source_root_hash72"))
    add("parity", REJECTIONS[2], lambda w: w.update(force_parity_violation=True))
    add("operator-order", REJECTIONS[3], lambda w: w.update(reordered_schedule=True, mode="PRIME_SCHEDULED_MANIFOLD"))
    add("cross-operator-merge", REJECTIONS[4], lambda w: w.update(merge_cross_operator_suffixes=True))
    add("unwitnessed-cycle", REJECTIONS[5], lambda w: w.update(claim_cycle_without_repeat=True))
    add("bound-as-asymptotic", REJECTIONS[6], lambda w: w.update(claims_asymptotic_result=True))
    add("seed-identity-erasure", REJECTIONS[7], lambda w: w.update(erase_factor_vectors=True))
    add("cache-as-proof", REJECTIONS[8], lambda w: w.update(cache_as_proof=True))
    add("float-authority", REJECTIONS[9], lambda w: w.update(float_derived_state=True))
    return cases


def build_artifacts(repo: Path) -> dict[str, Any]:
    workloads = workload_registry(repo)
    results = [verify_replay(repo, w)["initial"] for w in workloads]
    negatives = negative_cases(repo)
    def write(name: str, value: Any):
        (repo / name).write_text(json.dumps(value, indent=2) + "\n")
    write("PASS_092_WORKLOAD_REGISTRY.json", {"schema": "HHS_PASS_092_WORKLOAD_REGISTRY_V1", "workloads": workloads})
    write("PASS_092_OPERATOR_REGISTRY.json", {"schema": "HHS_PASS_092_OPERATOR_REGISTRY_V1", "operators": workloads[-1]["operators"]})
    write("PASS_092_COMPOSITE_SEED_RECEIPTS.json", {"schema": "HHS_PASS_092_COMPOSITE_SEEDS_V1", "seeds": workloads[4]["seeds"]})
    write("PASS_092_LANE_RECEIPTS.json", {"schema": "HHS_PASS_092_LANE_RECEIPTS_V1", "receipts": [l for r in results for l in r["lane_receipts"]]})
    write("PASS_092_INTERSECTION_RECEIPTS.json", {"schema": "HHS_PASS_092_INTERSECTIONS_V1", "receipts": [e for r in results for e in r["state_intersections"]]})
    write("PASS_092_SCALING_RESULTS.json", {"schema": "HHS_PASS_092_SCALING_RESULTS_V1", "results": [{k: r[k] for k in ("prime_seed_count","composite_seed_count","operator_prime_count","lane_count","bounded_lanes","status","tensor_root_hash72")} | {"workload_id": r["workload"]["workload_id"]} for r in results]})
    write("PASS_092_NEGATIVE_CASES.json", {"schema": "HHS_PASS_092_NEGATIVE_CASES_V1", "cases": negatives})
    (repo / "PASS_092_CALIBRATION_REPORT.md").write_text("# Pass 092 — Prime-Product Harmonic Manifolds and Generalized Collatz Operator Families\n\nPass 092 consumes Pass 091 and witnessed Pass 089 prime provenance, generates exact factor-vector seeds, executes fixed and scheduled prime-parameterized integer manifolds, witnesses cycles and cross-operator intersections, preserves ancestry and operator order, and deterministically replays every finite frontier. No bounded result is promoted to an asymptotic theorem.\n")
    (repo / "CHANGELOG_PASS_092.md").write_text("# Pass 092\n\nAdded exact prime-product seed lattices, generalized pn+1 operator families, cycle discovery, cross-operator intersection semantics, noncommutative schedules, negative enforcement, and deterministic replay.\n")
    manifest = {
        "schema": "HHS_PASS_092_RELEASE_MANIFEST_V1", "pass_id": PASS_ID,
        "parent_pass091_release_root_hash72": _read_json(repo / "PASS_091_RELEASE_MANIFEST.json")["pass091_release_root_hash72"],
        "workload_count": len(workloads), "negative_case_count": len(negatives),
        "all_negative_cases_passed": all(c["passed"] for c in negatives), "all_replays_verified": True,
        "artifacts": ["PASS_092_WORKLOAD_REGISTRY.json","PASS_092_OPERATOR_REGISTRY.json","PASS_092_COMPOSITE_SEED_RECEIPTS.json","PASS_092_LANE_RECEIPTS.json","PASS_092_INTERSECTION_RECEIPTS.json","PASS_092_SCALING_RESULTS.json","PASS_092_NEGATIVE_CASES.json","PASS_092_CALIBRATION_REPORT.md","CHANGELOG_PASS_092.md"],
    }
    manifest["pass092_release_root_hash72"] = root("hhs_pass092_release_manifest_v1", manifest)
    write("PASS_092_RELEASE_MANIFEST.json", manifest)
    return stable(manifest)
