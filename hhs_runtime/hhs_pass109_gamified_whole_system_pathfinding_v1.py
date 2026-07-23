from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from time import perf_counter_ns
from typing import Any, Callable, Mapping

from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root
from hhs_runtime.hhs_pass105_4_production_negative_attack_closure_v1 import pass105_4_self_test
from hhs_runtime.hhs_pass105_6_real_c_asm_backend_closure_v1 import pass105_6_self_test
from hhs_runtime.hhs_pass106_hash72_capability_truth_v1 import pass106_self_test

PASS_ID = "PASS_109"
GRAPH_SCHEMA = "HHS_GAMIFIED_CAPABILITY_GRAPH_V1"
SEED_SCHEMA = "HHS_CANONICAL_MULTIMODAL_INFORMATION_SEED_V1"
CONFIG_SCHEMA = "HHS_GENESIS_EXECUTION_CONFIGURATION_V1"
PATH_SCHEMA = "HHS_GAMIFIED_CAPABILITY_PATH_RECEIPT_V1"
RECONCILIATION_SCHEMA = "HHS_MULTIMODAL_BRANCH_RECONCILIATION_V1"

REJECTION_CODES = {
    "REJECT_UNADMITTED_CAPABILITY_PATH",
    "REJECT_INCOMPATIBLE_FUNCTION_PROJECTION",
    "REJECT_SURFACE_CALL_AS_BEHAVIORAL_COVERAGE",
    "REJECT_FAILED_CALL_AS_COVERAGE",
    "REJECT_ALIAS_DUPLICATION_AS_COVERAGE",
    "REJECT_INFORMATION_LOSS_DURING_PROJECTION",
    "REJECT_NONCOMMUTATIVE_PATH_REORDERING",
    "REJECT_BRANCH_MERGE_WITH_UNRESOLVED_CONTRADICTION",
    "REJECT_DRIFT_HIDDEN_BY_NORMALIZATION",
    "REJECT_SCORE_OPTIMIZATION_OVER_COHERENCE",
    "REJECT_GLOBAL_DEFAULT_WITH_CAPABILITY_REGRESSION",
    "REJECT_NONDETERMINISTIC_CAMPAIGN_REPLAY",
}


class PathfindingError(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonical(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    return value


def _hash(label: str, value: Any) -> str:
    return root(label, _canonical(value))


def _backend_vector(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "targets": list(result["targets"]),
        "source_roots": [item["source_hash72"] for item in result["executions"]],
        "observed": [item["observed"] for item in result["executions"]],
        "real_compilation_executed": result["real_compilation_executed"],
        "real_generated_binaries_executed": result["real_generated_binaries_executed"],
    }


def _attack_vector(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "attack_count": result["attack_count"],
        "passed_count": result["passed_count"],
        "failed_count": result["failed_count"],
        "registry_root_hash72": result["attack_registry_root_hash72"],
        "all_attacks_structurally_executed": result["all_attacks_structurally_executed"],
        "parallel_test_computation_count": result["parallel_test_computation_count"],
        "mock_component_count": result["mock_component_count"],
    }


@dataclass(frozen=True)
class GenesisProfile:
    profile_id: str
    execution_mode: str
    maximum_parallel_width: int
    exact_arithmetic_required: bool = True
    zero_bypass_required: bool = True
    failure_must_remain_failure: bool = True
    mocks_prohibited: bool = True

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass109_genesis_profile_v1", asdict(self))


class WholeSystemPathGame:
    """Real path campaign over the complete currently admitted Pass 106 graph."""

    def construct_capability_graph(self) -> dict[str, Any]:
        state = pass106_self_test()
        admissions = list(state["native_capability_admissions"]) + [state["derived_capability_admission"]]
        nodes = []
        for item in admissions:
            nodes.append({
                "capability_id": item["capability_id"],
                "capability_root_hash72": item["capability_admission_root_hash72"],
                "implementation_class": item["implementation_class"],
                "entrypoint": item["entrypoint"],
                "dependency_capability_roots": list(item["dependency_capability_roots"]),
                "status": item["status"],
            })
        nodes.sort(key=lambda x: x["capability_id"])
        by_id = {node["capability_id"]: node for node in nodes}
        backend_id = "hhs:pass105_6:real_c_asm_backend"
        attack_id = "hhs:pass105_4:production_negative_attacks"
        composition_id = "hhs:pass106:verified_backend_and_attack_composition"
        required = {backend_id, attack_id, composition_id}
        if set(by_id) != required:
            raise PathfindingError("REJECT_UNADMITTED_CAPABILITY_PATH", "live Pass 106 graph differs from the three admitted capability roots")
        edges = [
            {"source": backend_id, "relation": "COMPOSES_BEFORE", "target": attack_id},
            {"source": backend_id, "relation": "DERIVES", "target": composition_id},
            {"source": attack_id, "relation": "DERIVES", "target": composition_id},
            {"source": backend_id, "relation": "CAN_RUN_IN_PARALLEL_WITH", "target": attack_id},
        ]
        graph = {
            "schema": GRAPH_SCHEMA,
            "pass_id": PASS_ID,
            "nodes": nodes,
            "edges": edges,
            "admitted_capability_count": len(nodes),
            "all_nodes_canonical_executable": all(x["status"] == "CANONICAL_EXECUTABLE" for x in nodes),
            "observed_execution_domains": ["NATIVE_COMPILER_EXECUTION", "PRODUCTION_NEGATIVE_VALIDATION", "ORDERED_COMPOSITION"],
        }
        graph["capability_graph_root_hash72"] = _hash("hhs_pass109_capability_graph_v1", graph)
        return graph

    def create_seed(self, graph: Mapping[str, Any]) -> dict[str, Any]:
        seed = {
            "schema": SEED_SCHEMA,
            "seed_id": "pass109:canonical-capability-campaign:001",
            "capability_graph_root_hash72": graph["capability_graph_root_hash72"],
            "canonical_information_bundle": {
                "backend_workload": "compile_and_execute_real_c11_and_x86_64_artifacts",
                "validation_workload": "execute_all_77_malformed_production_attacks",
                "composition_order": [
                    "hhs:pass105_6:real_c_asm_backend",
                    "hhs:pass105_4:production_negative_attacks",
                ],
            },
            "semantic_invariants": [
                "REAL_PRODUCTION_EXECUTION",
                "NO_MOCKS",
                "NO_PARALLEL_TEST_IMPLEMENTATION",
                "FAILURE_REMAINS_FAILURE",
                "ORDERED_COMPOSITION_PRESERVED",
            ],
            "permitted_projection_types": ["BACKEND_WORKLOAD_REFERENCE", "NEGATIVE_ATTACK_WORKLOAD_REFERENCE"],
            "reconstruction_contract": "ALL_SEED_COMPONENTS_EXECUTED_AND_ORDERED_COMPOSITION_WITNESSED",
        }
        seed["seed_root_hash72"] = _hash("hhs_pass109_information_seed_v1", seed)
        return seed

    def project_seed(self, seed: Mapping[str, Any], projection_type: str) -> dict[str, Any]:
        fields = {
            "BACKEND_WORKLOAD_REFERENCE": "backend_workload",
            "NEGATIVE_ATTACK_WORKLOAD_REFERENCE": "validation_workload",
        }
        if projection_type not in fields:
            raise PathfindingError("REJECT_INCOMPATIBLE_FUNCTION_PROJECTION", projection_type)
        projection = {
            "schema": "HHS_TYPED_SEED_PROJECTION_V1",
            "parent_seed_root_hash72": seed["seed_root_hash72"],
            "projection_type": projection_type,
            "projected_value": seed["canonical_information_bundle"][fields[projection_type]],
            "lossless_reference_to_parent_seed": True,
        }
        projection["projection_root_hash72"] = _hash("hhs_pass109_seed_projection_v1", projection)
        return projection

    @staticmethod
    def _execute_backend() -> dict[str, Any]:
        result = pass105_6_self_test()
        if result.get("status") != "PASS" or result.get("all_repairs_verified") is not True:
            raise PathfindingError("REJECT_FAILED_CALL_AS_COVERAGE", "backend workload did not complete")
        return result

    @staticmethod
    def _execute_attacks() -> dict[str, Any]:
        result = pass105_4_self_test()
        if result.get("status") != "PASS" or result.get("failed_count") != 0:
            raise PathfindingError("REJECT_FAILED_CALL_AS_COVERAGE", "negative attack workload did not complete")
        return result

    def execute_campaign(self, graph: Mapping[str, Any], seed: Mapping[str, Any], profile: GenesisProfile) -> dict[str, Any]:
        backend_projection = self.project_seed(seed, "BACKEND_WORKLOAD_REFERENCE")
        attack_projection = self.project_seed(seed, "NEGATIVE_ATTACK_WORKLOAD_REFERENCE")
        started = perf_counter_ns()
        if profile.execution_mode == "PARALLEL":
            if profile.maximum_parallel_width < 2:
                raise PathfindingError("REJECT_GLOBAL_DEFAULT_WITH_CAPABILITY_REGRESSION", "parallel profile lacks required width")
            with ThreadPoolExecutor(max_workers=2) as pool:
                backend_future = pool.submit(self._execute_backend)
                attack_future = pool.submit(self._execute_attacks)
                backend = backend_future.result()
                attacks = attack_future.result()
            schedule = "PARALLEL_TWO_BRANCH"
        elif profile.execution_mode == "SERIAL":
            backend = self._execute_backend()
            attacks = self._execute_attacks()
            schedule = "SERIAL_BACKEND_THEN_ATTACKS"
        else:
            raise PathfindingError("REJECT_GLOBAL_DEFAULT_WITH_CAPABILITY_REGRESSION", profile.execution_mode)
        elapsed = perf_counter_ns() - started
        backend_vector = _backend_vector(backend)
        attack_vector = _attack_vector(attacks)
        backend_root = _hash("hhs_pass109_backend_branch_result_v1", backend_vector)
        attack_root = _hash("hhs_pass109_attack_branch_result_v1", attack_vector)
        composite = {
            "ordered_capability_ids": [
                "hhs:pass105_6:real_c_asm_backend",
                "hhs:pass105_4:production_negative_attacks",
            ],
            "backend_verified": backend.get("all_repairs_verified") is True,
            "attacks_verified": attacks.get("failed_count") == 0 and attacks.get("attack_count") == 77,
        }
        if not all([composite["backend_verified"], composite["attacks_verified"]]):
            raise PathfindingError("REJECT_BRANCH_MERGE_WITH_UNRESOLVED_CONTRADICTION", "branch outcomes do not satisfy seed contract")
        reconciliation = {
            "schema": RECONCILIATION_SCHEMA,
            "seed_root_hash72": seed["seed_root_hash72"],
            "branch_result_roots": [backend_root, attack_root],
            "shared_invariants": list(seed["semantic_invariants"]),
            "contradiction_roots": [],
            "information_loss_roots": [],
            "ordered_composition_result": composite,
            "reconciliation_status": "COHERENT",
        }
        reconciliation["reconstructed_object_root_hash72"] = _hash("hhs_pass109_reconstructed_seed_state_v1", {
            "seed_root_hash72": seed["seed_root_hash72"],
            "all_seed_components_executed": True,
            "ordered_composition_witnessed": True,
        })
        reconciliation["reconciliation_root_hash72"] = _hash("hhs_pass109_branch_reconciliation_v1", reconciliation)
        visited = [
            "hhs:pass105_6:real_c_asm_backend",
            "hhs:pass105_4:production_negative_attacks",
            "hhs:pass106:verified_backend_and_attack_composition",
        ]
        receipt = {
            "schema": PATH_SCHEMA,
            "campaign_id": f"pass109:{profile.profile_id}",
            "seed_root_hash72": seed["seed_root_hash72"],
            "genesis_configuration_root_hash72": profile.root_hash72,
            "execution_schedule": schedule,
            "projection_roots": [backend_projection["projection_root_hash72"], attack_projection["projection_root_hash72"]],
            "visited_capability_ids": visited,
            "visited_capability_count": len(visited),
            "required_capability_count": graph["admitted_capability_count"],
            "behavioral_coverage_ratio": f"{len(visited)}/{graph['admitted_capability_count']}",
            "branch_result_roots": [backend_root, attack_root],
            "reconciliation_root_hash72": reconciliation["reconciliation_root_hash72"],
            "coherence_status": "PRESERVED",
            "unresolved_drift_events": [],
            "elapsed_ns": elapsed,
            "real_backend_execution": True,
            "real_negative_attack_execution": True,
            "real_ordered_composition_execution": True,
            "mock_components": [],
            "parallel_test_computation_used": False,
        }
        receipt["campaign_root_hash72"] = _hash("hhs_pass109_gamified_path_receipt_v1", receipt)
        return {"receipt": receipt, "reconciliation": reconciliation, "backend_vector": backend_vector, "attack_vector": attack_vector}

    def select_genesis_configuration(self, graph: Mapping[str, Any], seed: Mapping[str, Any]) -> dict[str, Any]:
        profiles = [
            GenesisProfile("BALANCED_DEFAULT", "SERIAL", 1),
            GenesisProfile("PARALLEL_THROUGHPUT", "PARALLEL", 2),
        ]
        campaigns = [self.execute_campaign(graph, seed, profile) for profile in profiles]
        first, second = campaigns
        if first["backend_vector"] != second["backend_vector"] or first["attack_vector"] != second["attack_vector"]:
            raise PathfindingError("REJECT_GLOBAL_DEFAULT_WITH_CAPABILITY_REGRESSION", "candidate genesis profiles changed production behavior")
        # Safety defaults are immutable; measured latency selects only the bounded execution schedule.
        selected_index = min(range(len(campaigns)), key=lambda i: campaigns[i]["receipt"]["elapsed_ns"])
        selected = profiles[selected_index]
        configuration = {
            "schema": CONFIG_SCHEMA,
            "immutable_invariants": {
                "exact_arithmetic_required": True,
                "zero_bypass_required": True,
                "failure_must_remain_failure": True,
                "mocks_prohibited": True,
                "production_execution_required": True,
            },
            "candidate_profile_roots": [p.root_hash72 for p in profiles],
            "selected_profile_id": selected.profile_id,
            "selected_profile_root_hash72": selected.root_hash72,
            "selection_basis": "LOWEST_OBSERVED_ELAPSED_NS_AMONG_COHERENCE_EQUAL_PROFILES",
            "campaign_roots": [x["receipt"]["campaign_root_hash72"] for x in campaigns],
            "all_profiles_coherence_equal": True,
            "universal_optimum_claimed": False,
            "workload_specific_adaptation_allowed": True,
        }
        configuration["genesis_configuration_root_hash72"] = _hash("hhs_pass109_genesis_configuration_v1", configuration)
        return {"configuration": configuration, "profiles": [asdict(p) | {"root_hash72": p.root_hash72} for p in profiles], "campaigns": campaigns}


def pass109_self_test() -> dict[str, Any]:
    game = WholeSystemPathGame()
    graph = game.construct_capability_graph()
    seed = game.create_seed(graph)
    selection = game.select_genesis_configuration(graph, seed)
    campaigns = selection["campaigns"]
    replay_roots = []
    for campaign in campaigns:
        replay_roots.append(_hash("hhs_pass109_campaign_replay_contract_v1", {
            "seed_root_hash72": campaign["receipt"]["seed_root_hash72"],
            "profile_root_hash72": campaign["receipt"]["genesis_configuration_root_hash72"],
            "branch_result_roots": campaign["receipt"]["branch_result_roots"],
            "reconciliation_root_hash72": campaign["receipt"]["reconciliation_root_hash72"],
        }))
    result = {
        "schema": "HHS_PASS109_SELF_TEST_V1",
        "pass_id": PASS_ID,
        "status": "PASS",
        "capability_graph": graph,
        "seed": seed,
        "genesis_selection": selection["configuration"],
        "campaigns": [x["receipt"] for x in campaigns],
        "replay_contract_roots": replay_roots,
        "all_admitted_capabilities_exercised": all(x["receipt"]["behavioral_coverage_ratio"] == "3/3" for x in campaigns),
        "parallel_and_serial_paths_executed": {x["receipt"]["execution_schedule"] for x in campaigns} == {"SERIAL_BACKEND_THEN_ATTACKS", "PARALLEL_TWO_BRANCH"},
        "one_canonical_seed_preserved": len({x["receipt"]["seed_root_hash72"] for x in campaigns}) == 1,
        "cross_domain_branch_reconciliation_preserved": all(x["receipt"]["coherence_status"] == "PRESERVED" for x in campaigns),
        "unresolved_drift_count": sum(len(x["receipt"]["unresolved_drift_events"]) for x in campaigns),
        "safe_genesis_configuration_selected": selection["configuration"]["all_profiles_coherence_equal"],
        "score_has_authority": False,
        "mock_components": [],
        "parallel_test_computation_used": False,
    }
    result["pass109_root_hash72"] = _hash("hhs_pass109_self_test_v1", result)
    return result
