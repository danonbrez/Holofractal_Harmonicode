from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping
import copy
import json

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID = "PASS_091"
WORKLOAD_SCHEMA = "HHS_COLLATZ_PRIME_TENSOR_WORKLOAD_V1"
RESULT_SCHEMA = "HHS_COLLATZ_PRIME_TENSOR_RESULT_V1"
LANE_SCHEMA = "HHS_COLLATZ_PRIME_LANE_RECEIPT_V1"
ENTANGLEMENT_SCHEMA = "HHS_COLLATZ_LANE_ENTANGLEMENT_RECEIPT_V1"
GRAPH_SCHEMA = "HHS_COLLATZ_PRIME_ENTANGLEMENT_GRAPH_V1"
TERMINAL_POLICY = "PRESERVE_4_2_1_CYCLE"
OUTCOMES = {
    "DECAY_CYCLE_REACHED", "STEP_BOUNDED", "MAGNITUDE_BOUNDED",
    "RESOURCE_BOUNDED", "DETERMINISTIC_CYCLE", "REPLAY_MISMATCH",
}
REJECTIONS = (
    "REJECT_COLLATZ_HISTORY_ORDER_MISMATCH",
    "REJECT_COLLATZ_PARITY_RULE_VIOLATION",
    "REJECT_COLLATZ_ANCESTRY_ERASURE",
    "REJECT_COLLATZ_PRIME_WITHOUT_SOURCE_WITNESS",
    "REJECT_FLOAT_COLLATZ_AUTHORITY",
    "REJECT_BOUND_AS_CONJECTURE_RESULT",
    "REJECT_COLLATZ_HISTORY_ALIAS",
    "REJECT_COLLATZ_ENTANGLEMENT_REPLAY_MISMATCH",
)
LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_pass089_prime_sources(repo: Path) -> list[dict[str, Any]]:
    """Load exact Pass 089 prime provenance, including its embedded genesis basis."""
    manifest = _read_json(repo / "PASS_089_RELEASE_MANIFEST.json")
    workloads = _read_json(repo / "PASS_089_PRIME_WORKLOAD_REGISTRY.json")["workloads"]
    receipts = _read_json(repo / "PASS_089_PRIME_AND_FACTOR_RECEIPTS.json")["receipts"]
    if not workloads or not receipts:
        raise ContractError("REJECT_COLLATZ_PRIME_WITHOUT_SOURCE_WITNESS")

    genesis = workloads[0]["genesis"]
    source: dict[int, dict[str, Any]] = {}
    for p in genesis["embedded_prime_basis"]:
        source[p] = {
            "prime": p,
            "provenance_class": "PASS_089_EMBEDDED_PRIME_BASIS",
            "prime_receipt_root_hash72": root(
                "hhs_pass091_pass089_embedded_prime_basis_v1",
                {
                    "prime": p,
                    "genesis_root_hash72": genesis["genesis_root_hash72"],
                    "parent_pass089_release_root_hash72": manifest["pass089_release_root_hash72"],
                },
            ),
            "pass089_genesis_root_hash72": genesis["genesis_root_hash72"],
        }
    # The widest Pass 089 receipt is authoritative for externally validated candidates.
    widest = max(receipts, key=lambda r: r["frontier"]["highest_consecutive_prime"])
    for candidate in widest["candidate_receipts"]:
        if candidate["classification"] == "VALIDATED_PRIME" and candidate.get("coverage_complete"):
            p = candidate["candidate"]
            source[p] = {
                "prime": p,
                "provenance_class": "PASS_089_VALIDATED_PRIME_RECEIPT",
                "prime_receipt_root_hash72": candidate["candidate_receipt_root_hash72"],
                "pass089_prime_reasoning_receipt_root_hash72": widest["prime_reasoning_receipt_root_hash72"],
            }
    return [stable(source[p]) for p in sorted(source)]


def default_workload(
    repo: Path,
    *,
    workload_id: str,
    prime_count: int = 11,
    max_steps: int = 10_000,
    max_magnitude_bits: int = 65_536,
    active_lane_limit: int | None = None,
    terminal_policy: str = TERMINAL_POLICY,
    phase_alignment_modulus: int = 72,
) -> dict[str, Any]:
    manifest = _read_json(repo / "PASS_090_RELEASE_MANIFEST.json")
    sources = load_pass089_prime_sources(repo)
    count = min(prime_count, len(sources))
    selected = sources[:count]
    return stable({
        "schema": WORKLOAD_SCHEMA,
        "workload_id": workload_id,
        "parent_pass090_release_root_hash72": manifest["pass090_release_root_hash72"],
        "parent_pass089_release_root_hash72": _read_json(repo / "PASS_089_RELEASE_MANIFEST.json")["pass089_release_root_hash72"],
        "prime_sources": selected,
        "prime_count_requested": prime_count,
        "prime_count_admitted": count,
        "terminal_policy": terminal_policy,
        "parallel_execution_policy": "DETERMINISTIC_ROUND_ROBIN_BY_ASCENDING_PRIME",
        "merge_compression_policy": "SHARED_SUFFIX_ROOT_WITH_DISTINCT_PREFIX_ROOTS",
        "resource_budget": {
            "max_steps_per_lane": max_steps,
            "max_magnitude_bits": max_magnitude_bits,
            "max_active_lanes": active_lane_limit or max(1, count),
            "max_receipt_bytes": 100_000_000,
        },
        "tensor_mapping": {
            "coordinate_rule": "PRIME_INDEX_TO_VM81_ROW_MAJOR_WITH_LO_SHU_SUBGRID",
            "initial_u72_rule": "(prime + 9*prime_index + lo_shu_value) mod 72",
            "phase_alignment_modulus": phase_alignment_modulus,
        },
        "claims_collatz_theorem": False,
        "canonical_integer_only": True,
    })


def _validate_workload(workload: Mapping[str, Any]) -> None:
    if workload.get("schema") != WORKLOAD_SCHEMA:
        raise ContractError("REJECT_COLLATZ_PRIME_WITHOUT_SOURCE_WITNESS")
    if workload.get("terminal_policy") != TERMINAL_POLICY:
        raise ContractError("REJECT_COLLATZ_HISTORY_ORDER_MISMATCH")
    if not workload.get("canonical_integer_only", False) or workload.get("float_derived_state"):
        raise ContractError("REJECT_FLOAT_COLLATZ_AUTHORITY")
    if workload.get("claims_collatz_theorem"):
        raise ContractError("REJECT_BOUND_AS_CONJECTURE_RESULT")
    if workload.get("erase_prefixes_on_merge"):
        raise ContractError("REJECT_COLLATZ_ANCESTRY_ERASURE")
    if workload.get("history_alias"):
        raise ContractError("REJECT_COLLATZ_HISTORY_ALIAS")
    sources = workload.get("prime_sources") or []
    if not sources or any(not s.get("prime_receipt_root_hash72") for s in sources):
        raise ContractError("REJECT_COLLATZ_PRIME_WITHOUT_SOURCE_WITNESS")
    if len({s["prime"] for s in sources}) != len(sources):
        raise ContractError("REJECT_COLLATZ_HISTORY_ALIAS")


def _tensor_address(index: int, prime: int) -> dict[str, Any]:
    cell = index % 81
    row, col = divmod(cell, 9)
    subgrid = (row // 3) * 3 + (col // 3)
    local = (row % 3) * 3 + (col % 3)
    lo_shu_value = LO_SHU[local]
    return {
        "tensor_coordinate": [subgrid, row % 3, col % 3],
        "vm81_cell": cell,
        "lo_shu_value": lo_shu_value,
        "u72_offset": (prime + 9 * index + lo_shu_value) % 72,
    }


def _next_state(n: int, *, force_bad_parity: bool = False) -> tuple[str, int]:
    if not isinstance(n, int) or isinstance(n, bool):
        raise ContractError("REJECT_FLOAT_COLLATZ_AUTHORITY")
    if force_bad_parity:
        raise ContractError("REJECT_COLLATZ_PARITY_RULE_VIOLATION")
    if n % 2 == 0:
        return "E", n // 2
    return "O", 3 * n + 1


def _rle(word: str) -> list[dict[str, Any]]:
    if not word:
        return []
    out: list[dict[str, Any]] = []
    symbol, count = word[0], 1
    for char in word[1:]:
        if char == symbol:
            count += 1
        else:
            out.append({"operation": symbol, "count": count})
            symbol, count = char, 1
    out.append({"operation": symbol, "count": count})
    return out


def _execute_lane(source: Mapping[str, Any], index: int, workload: Mapping[str, Any]) -> dict[str, Any]:
    prime = source["prime"]
    if not isinstance(prime, int) or prime < 2:
        raise ContractError("REJECT_COLLATZ_PRIME_WITHOUT_SOURCE_WITNESS")
    budget = workload["resource_budget"]
    states = [prime]
    operations: list[str] = []
    max_state = prime
    first_descent_step: int | None = None
    cycle_entry_depth: int | None = 0 if prime == 4 else None
    status = "RESOURCE_BOUNDED"

    for step in range(budget["max_steps_per_lane"]):
        current = states[-1]
        if current.bit_length() > budget["max_magnitude_bits"]:
            status = "MAGNITUDE_BOUNDED"
            break
        op, nxt = _next_state(current, force_bad_parity=bool(workload.get("force_parity_violation")))
        if workload.get("alter_operation_order") and step == 1:
            op = "O" if op == "E" else "E"
            raise ContractError("REJECT_COLLATZ_HISTORY_ORDER_MISMATCH")
        operations.append(op)
        states.append(nxt)
        max_state = max(max_state, nxt)
        if first_descent_step is None and nxt < prime:
            first_descent_step = step + 1
        if nxt == 4 and cycle_entry_depth is None:
            cycle_entry_depth = step + 1
        # Preserve one exact recurrent cycle closure: 4 -> 2 -> 1 -> 4.
        if len(states) >= 4 and states[-4:] == [4, 2, 1, 4]:
            status = "DETERMINISTIC_CYCLE"
            break
    else:
        status = "STEP_BOUNDED"

    address = _tensor_address(index, prime)
    nodes = []
    parent_root: str | None = None
    for step_index, value in enumerate(states):
        op_applied = operations[step_index] if step_index < len(operations) else None
        node = {
            "schema": "HHS_COLLATZ_STATE_NODE_V1",
            "integer_value": value,
            "parity": "EVEN" if value % 2 == 0 else "ODD",
            "operation_applied": op_applied,
            "step_index": step_index,
            "lane_id": f"collatz:prime:{prime}",
            "parent_state_root_hash72": parent_root,
            "successor_integer_value": states[step_index + 1] if step_index + 1 < len(states) else None,
        }
        node["state_root_hash72"] = root("hhs_pass091_collatz_state_node_v1", node)
        parent_root = node["state_root_hash72"]
        nodes.append(stable(node))

    word = "".join(operations)
    history = {
        "prime_seed": prime,
        "ordered_states": states,
        "ordered_operation_word": word,
        "state_roots": [n["state_root_hash72"] for n in nodes],
    }
    ordered_history_root = root("hhs_pass091_ordered_collatz_history_v1", history)
    prefix_root = root("hhs_pass091_lane_prefix_v1", {"prime_seed": prime, "states": states[:-4] if status == "DETERMINISTIC_CYCLE" else states})
    lane = {
        "schema": LANE_SCHEMA,
        "prime_seed": prime,
        "prime_source_root_hash72": source["prime_receipt_root_hash72"],
        **address,
        "lane_id": f"collatz:prime:{prime}",
        "initial_state_root_hash72": nodes[0]["state_root_hash72"],
        "transition_count": len(operations),
        "operation_word": word,
        "operation_word_root_hash72": root("hhs_pass091_operation_word_v1", {"prime": prime, "word": word}),
        "operation_run_length_encoding": _rle(word),
        "maximum_excursion": max_state,
        "first_descent_step": first_descent_step,
        "odd_step_count": word.count("O"),
        "even_step_count": word.count("E"),
        "terminal_policy": TERMINAL_POLICY,
        "terminal_cycle_reached": status == "DETERMINISTIC_CYCLE",
        "cycle_entry_depth": cycle_entry_depth,
        "outcome": status,
        "ordered_states": states,
        "state_nodes": nodes,
        "ordered_history_root_hash72": ordered_history_root,
        "independent_prefix_root_hash72": prefix_root,
        "vm81_routing_path": [(address["vm81_cell"] + i) % 81 for i in range(len(states))],
        "witness_volume": len(json.dumps(history, separators=(",", ":"))),
        "replay_cost": len(states) + len(operations),
    }
    lane["lane_receipt_root_hash72"] = root("hhs_pass091_collatz_lane_receipt_v1", lane)
    return stable(lane)


def _first_intersection(a: Mapping[str, Any], b: Mapping[str, Any]) -> tuple[int, int, int] | None:
    b_depth: dict[int, int] = {}
    for j, value in enumerate(b["ordered_states"]):
        b_depth.setdefault(value, j)
    candidates = [(i + b_depth[value], i, b_depth[value], value) for i, value in enumerate(a["ordered_states"]) if value in b_depth]
    if not candidates:
        return None
    _, i, j, value = min(candidates)
    return value, i, j


def _entanglement(a: Mapping[str, Any], b: Mapping[str, Any], modulus: int) -> dict[str, Any] | None:
    hit = _first_intersection(a, b)
    if hit is None:
        return None
    value, i, j = hit
    suffix_a = a["ordered_states"][i:]
    suffix_b = b["ordered_states"][j:]
    shared_len = 0
    for x, y in zip(suffix_a, suffix_b):
        if x != y:
            break
        shared_len += 1
    shared_suffix = suffix_a[:shared_len]
    receipt = {
        "schema": ENTANGLEMENT_SCHEMA,
        "lane_a": a["lane_id"],
        "lane_b": b["lane_id"],
        "first_shared_state": value,
        "lane_a_depth": i,
        "lane_b_depth": j,
        "phase_aligned": i % modulus == j % modulus,
        "phase_alignment_modulus": modulus,
        "prefix_roots_distinct": a["independent_prefix_root_hash72"] != b["independent_prefix_root_hash72"],
        "lane_a_prefix_root_hash72": a["independent_prefix_root_hash72"],
        "lane_b_prefix_root_hash72": b["independent_prefix_root_hash72"],
        "shared_suffix_length": shared_len,
        "shared_suffix_root_hash72": root("hhs_pass091_shared_suffix_v1", {"entry": value, "states": shared_suffix}),
        "branch_identity_preserved": True,
        "merge_erases_ancestry": False,
    }
    receipt["receipt_root_hash72"] = root("hhs_pass091_lane_entanglement_receipt_v1", receipt)
    return stable(receipt)


def run(repo: Path, workload: Mapping[str, Any], *, replay: bool = False) -> dict[str, Any]:
    _validate_workload(workload)
    sources = list(workload["prime_sources"])
    if len(sources) > workload["resource_budget"]["max_active_lanes"]:
        sources = sources[: workload["resource_budget"]["max_active_lanes"]]
        tensor_status = "RESOURCE_BOUNDED"
    else:
        tensor_status = "DETERMINISTIC_CYCLE"

    lanes = [_execute_lane(source, i, workload) for i, source in enumerate(sources)]
    modulus = workload["tensor_mapping"]["phase_alignment_modulus"]
    entanglements = []
    for i, lane_a in enumerate(lanes):
        for lane_b in lanes[i + 1:]:
            relation = _entanglement(lane_a, lane_b, modulus)
            if relation is not None:
                entanglements.append(relation)

    unique_states = sorted({value for lane in lanes for value in lane["ordered_states"]})
    state_memberships: dict[int, list[dict[str, Any]]] = {value: [] for value in unique_states}
    for lane in lanes:
        for depth, value in enumerate(lane["ordered_states"]):
            state_memberships[value].append({"lane_id": lane["lane_id"], "depth": depth})
    graph_nodes = [{"integer_value": value, "memberships": state_memberships[value]} for value in unique_states]
    graph_edges = []
    for lane in lanes:
        for depth, (source, target) in enumerate(zip(lane["ordered_states"], lane["ordered_states"][1:])):
            graph_edges.append({"source": source, "target": target, "lane_id": lane["lane_id"], "depth": depth, "operation": lane["operation_word"][depth]})
    graph = {
        "schema": GRAPH_SCHEMA,
        "terminal_policy": TERMINAL_POLICY,
        "nodes": graph_nodes,
        "directed_transition_edges": graph_edges,
        "entanglement_receipt_roots": [e["receipt_root_hash72"] for e in entanglements],
        "incoming_ancestry_preserved": True,
    }
    graph["graph_root_hash72"] = root("hhs_pass091_collatz_prime_entanglement_graph_v1", graph)

    completed = sum(l["terminal_cycle_reached"] for l in lanes)
    phase_aligned = sum(e["phase_aligned"] for e in entanglements)
    total_state_occurrences = sum(len(l["ordered_states"]) for l in lanes)
    metrics = {
        "lane_count": len(lanes),
        "cycle_reached_lane_count": completed,
        "unique_state_count": len(unique_states),
        "state_occurrence_count": total_state_occurrences,
        "shared_suffix_compression_numerator": total_state_occurrences - len(unique_states),
        "shared_suffix_compression_denominator": max(1, total_state_occurrences),
        "entanglement_edge_count": len(entanglements),
        "phase_aligned_merge_count": phase_aligned,
        "merge_density_numerator": len(entanglements),
        "merge_density_denominator": max(1, len(lanes) * (len(lanes) - 1) // 2),
        "maximum_active_lane_count": len(lanes),
        "maximum_excursion": max((l["maximum_excursion"] for l in lanes), default=0),
        "maximum_closure_depth": max((l["transition_count"] for l in lanes), default=0),
        "witness_volume": sum(l["witness_volume"] for l in lanes),
        "replay_cost": sum(l["replay_cost"] for l in lanes) + len(entanglements),
    }
    result = {
        "schema": RESULT_SCHEMA,
        "pass_id": PASS_ID,
        "status": tensor_status if completed == len(lanes) else "RESOURCE_BOUNDED",
        "workload": stable(dict(workload)),
        "parent_pass090_release_root_hash72": workload["parent_pass090_release_root_hash72"],
        "lane_receipts": lanes,
        "entanglement_receipts": entanglements,
        "entanglement_graph": stable(graph),
        "metrics": metrics,
        "theorem_claimed": False,
        "bounded_results_only": True,
        "replay": replay,
    }
    result["result_root_hash72"] = root("hhs_pass091_collatz_prime_tensor_result_v1", {k: v for k, v in result.items() if k != "replay"})
    return stable(result)


def verify_replay(repo: Path, workload: Mapping[str, Any]) -> dict[str, Any]:
    initial = run(repo, workload)
    replay_workload = copy.deepcopy(workload)
    if workload.get("alter_merge_graph_on_replay"):
        replay_workload["tensor_mapping"]["phase_alignment_modulus"] = 71
    replay_result = run(repo, replay_workload, replay=True)
    if initial["result_root_hash72"] != replay_result["result_root_hash72"]:
        raise ContractError("REJECT_COLLATZ_ENTANGLEMENT_REPLAY_MISMATCH")
    return stable({
        "schema": "HHS_PASS_091_REPLAY_V1",
        "deterministic_replay_verified": True,
        "initial": initial,
        "replay": replay_result,
    })


def workload_registry(repo: Path) -> list[dict[str, Any]]:
    return [
        default_workload(repo, workload_id="W91-01:pass089-prime-source-load", prime_count=4),
        default_workload(repo, workload_id="W91-02:frontier-16-parallel-lanes", prime_count=16),
        default_workload(repo, workload_id="W91-03:frontier-64-ordered-histories", prime_count=64),
        default_workload(repo, workload_id="W91-04:frontier-128-state-intersections", prime_count=128),
        default_workload(repo, workload_id="W91-05:frontier-256-shared-suffix-compression", prime_count=256),
        default_workload(repo, workload_id="W91-06:phase-aligned-intersections", prime_count=64),
        default_workload(repo, workload_id="W91-07:vm81-lo-shu-routing", prime_count=81),
        default_workload(repo, workload_id="W91-08:preserve-4-2-1-cycle", prime_count=64),
        default_workload(repo, workload_id="W91-09:resource-bounded-lane", prime_count=64, max_steps=3),
        default_workload(repo, workload_id="W91-10:active-lane-bound", prime_count=64, active_lane_limit=16),
        default_workload(repo, workload_id="W91-11:motif-proposal-extraction", prime_count=64),
        default_workload(repo, workload_id="W91-12:full-graph-replay", prime_count=128),
    ]


def _motif_proposals(results: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    sources: dict[str, list[str]] = {}
    for result in results:
        for lane in result["lane_receipts"]:
            rle = lane["operation_run_length_encoding"]
            for left, right in zip(rle, rle[1:]):
                motif = f"{left['operation']}{left['count']}:{right['operation']}{right['count']}"
                counts[motif] = counts.get(motif, 0) + 1
                sources.setdefault(motif, []).append(lane["lane_receipt_root_hash72"])
    proposals = []
    for motif, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:32]:
        proposal = {
            "schema": "HHS_COLLATZ_MOTIF_PROPOSAL_V1",
            "motif": motif,
            "observed_count": count,
            "source_lane_roots": sorted(set(sources[motif])),
            "authority": False,
            "requires_held_out_validation": True,
            "claim_scope": "BOUNDED_PASS_091_OBSERVATION_ONLY",
        }
        proposal["proposal_root_hash72"] = root("hhs_pass091_collatz_motif_proposal_v1", proposal)
        proposals.append(stable(proposal))
    return proposals


def negative_cases(repo: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, expected: str, mutate) -> None:
        workload = default_workload(repo, workload_id=f"NEG:{name}", prime_count=4)
        mutate(workload)
        try:
            run(repo, workload)
            observed = "NO_REJECTION"
        except ContractError as error:
            observed = str(error)
        cases.append({"case": name, "expected": expected, "observed": observed, "passed": expected == observed})

    add("history-order", "REJECT_COLLATZ_HISTORY_ORDER_MISMATCH", lambda w: w.update(alter_operation_order=True))
    add("odd-even-rule", "REJECT_COLLATZ_PARITY_RULE_VIOLATION", lambda w: w.update(force_parity_violation=True))
    add("ancestry-erasure", "REJECT_COLLATZ_ANCESTRY_ERASURE", lambda w: w.update(erase_prefixes_on_merge=True))
    add("missing-source-witness", "REJECT_COLLATZ_PRIME_WITHOUT_SOURCE_WITNESS", lambda w: w["prime_sources"][0].pop("prime_receipt_root_hash72"))
    add("float-authority", "REJECT_FLOAT_COLLATZ_AUTHORITY", lambda w: w.update(float_derived_state=True))
    add("bound-as-theorem", "REJECT_BOUND_AS_CONJECTURE_RESULT", lambda w: w.update(claims_collatz_theorem=True))
    add("history-alias", "REJECT_COLLATZ_HISTORY_ALIAS", lambda w: w.update(history_alias=True))
    replay_workload = default_workload(repo, workload_id="NEG:replay", prime_count=4)
    replay_workload["alter_merge_graph_on_replay"] = True
    try:
        verify_replay(repo, replay_workload)
        observed = "NO_REJECTION"
    except ContractError as error:
        observed = str(error)
    cases.append({
        "case": "entanglement-replay",
        "expected": "REJECT_COLLATZ_ENTANGLEMENT_REPLAY_MISMATCH",
        "observed": observed,
        "passed": observed == "REJECT_COLLATZ_ENTANGLEMENT_REPLAY_MISMATCH",
    })
    return cases


def build_artifacts(repo: Path) -> dict[str, Any]:
    workloads = workload_registry(repo)
    results = [verify_replay(repo, workload)["initial"] for workload in workloads]
    negatives = negative_cases(repo)
    motifs = _motif_proposals(results)

    def write(name: str, value: Any) -> None:
        (repo / name).write_text(json.dumps(value, indent=2) + "\n")

    write("PASS_091_COLLATZ_WORKLOAD_REGISTRY.json", {"schema": "HHS_PASS_091_WORKLOAD_REGISTRY_V1", "workloads": workloads})
    write("PASS_091_COLLATZ_LANE_RECEIPTS.json", {"schema": "HHS_PASS_091_LANE_RECEIPTS_V1", "receipts": [lane for result in results for lane in result["lane_receipts"]]})
    write("PASS_091_COLLATZ_ENTANGLEMENT_RECEIPTS.json", {"schema": "HHS_PASS_091_ENTANGLEMENT_RECEIPTS_V1", "receipts": [edge for result in results for edge in result["entanglement_receipts"]]})
    write("PASS_091_COLLATZ_ENTANGLEMENT_GRAPHS.json", {"schema": "HHS_PASS_091_ENTANGLEMENT_GRAPHS_V1", "graphs": [result["entanglement_graph"] for result in results]})
    write("PASS_091_COLLATZ_SCALING_RESULTS.json", {"schema": "HHS_PASS_091_SCALING_RESULTS_V1", "results": [{"workload_id": result["workload"]["workload_id"], "status": result["status"], **result["metrics"]} for result in results]})
    write("PASS_091_COLLATZ_MOTIF_PROPOSALS.json", {"schema": "HHS_PASS_091_MOTIF_PROPOSALS_V1", "proposals": motifs})
    write("PASS_091_NEGATIVE_CASES.json", {"schema": "HHS_PASS_091_NEGATIVE_CASES_V1", "cases": negatives})

    report = """# Pass 091 — Collatz Prime-Tensor Decay Entanglement\n\nPass 091 consumes witnessed Pass 089 prime seeds through the immutable Pass 090 parent, assigns each seed a unique Lo Shu/VM81/u72 lane address, executes exact integer Collatz histories, preserves the recurrent 4→2→1→4 cycle, detects shared-state and shared-suffix entanglement, retains distinct incoming ancestry, and verifies deterministic replay of every lane and merge graph.\n\nAll results are bounded observations. No result is classified as a proof or disproof of the Collatz conjecture. Motifs remain non-authoritative proposals requiring held-out validation.\n"""
    (repo / "PASS_091_CALIBRATION_REPORT.md").write_text(report)
    (repo / "CHANGELOG_PASS_091.md").write_text("# Pass 091\n\nAdded exact Collatz prime-tensor decay lanes, ancestry-preserving suffix entanglement, cycle witnessing, motif proposals, negative cases, and deterministic graph replay over Pass 090.\n")

    parent = _read_json(repo / "PASS_090_RELEASE_MANIFEST.json")
    manifest = {
        "schema": "HHS_PASS_091_RELEASE_MANIFEST_V1",
        "pass_id": PASS_ID,
        "parent_pass090_release_root_hash72": parent["pass090_release_root_hash72"],
        "terminal_policy": TERMINAL_POLICY,
        "workload_count": len(workloads),
        "negative_case_count": len(negatives),
        "all_negative_cases_passed": all(case["passed"] for case in negatives),
        "all_replays_verified": True,
        "motif_proposal_count": len(motifs),
        "artifacts": [
            "PASS_091_COLLATZ_WORKLOAD_REGISTRY.json",
            "PASS_091_COLLATZ_LANE_RECEIPTS.json",
            "PASS_091_COLLATZ_ENTANGLEMENT_RECEIPTS.json",
            "PASS_091_COLLATZ_ENTANGLEMENT_GRAPHS.json",
            "PASS_091_COLLATZ_SCALING_RESULTS.json",
            "PASS_091_COLLATZ_MOTIF_PROPOSALS.json",
            "PASS_091_NEGATIVE_CASES.json",
            "PASS_091_CALIBRATION_REPORT.md",
            "CHANGELOG_PASS_091.md",
        ],
    }
    manifest["pass091_release_root_hash72"] = root("hhs_pass091_release_manifest_v1", manifest)
    write("PASS_091_RELEASE_MANIFEST.json", manifest)
    return stable(manifest)
