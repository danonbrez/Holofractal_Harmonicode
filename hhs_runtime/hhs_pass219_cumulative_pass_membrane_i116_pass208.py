"""Pass 219 I116 inherited Pass 208 GPU branch-manifold membrane."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass209 import pass209_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS208_NUMBER = 208
PASS208_CLASSIFICATION = "WIRED"
PASS208_BIND_SYMBOL = "hhs_exact_pass219_bind_pass208_gpu_branch_manifold"
PASS208_SURFACE_ID = "runtime:pass208.gpu-branch-manifold"
PASS208_CONTRACT_PATH = Path("contracts/pass208/PASS_208_CONTRACT.json")
PASS208_RESTART_PATH = Path("docs/pass208/RESTART_RECORD.md")
PASS208_RUNTIME_PATH = Path("hhs_backend/runtime/hhs_pass208_gpu_branch_manifold_v1.py")
PASS208_ROUTES_PATH = Path("hhs_backend/api/pass208_gpu_manifold_routes.py")
PASS208_PREFLIGHT_PATH = Path("deployment/digitalocean/gpu/hhs-gpu-preflight.sh")
PASS208_VALIDATOR_PATH = Path("deployment/digitalocean/gpu/validate-json-spec-package.py")

REQUIRED_OPERATIONS = (
    "Pass208GPUBranchManifold.status",
    "Pass208GPUBranchManifold.expand",
    "Pass208GPUBranchManifold.expand_and_commit",
    "gpu_manifold_status",
    "gpu_manifold_expand",
    "gpu_manifold_expand_and_commit",
)

FROZEN = {
    "validated_branch_head": "6cc968b9f95d63e1a8701d32008969477caf894f",
    "main_merge_head": "cbeabffff4e70db6207f8c349dd88ea8b7bd6ea9",
    "branch_validation_run": 30918852368,
    "branch_validation_job": 92023855007,
    "contract_blob": "b77413b816a32e61a3b1336b16bc6c4ecb0f4efa",
    "runtime_blob": "54e1e2089cdaeb4e3c613a5139c08cc226061afd",
    "routes_blob": "936bb542379db613805cd709482da7f1932c33e2",
    "restart_blob": "b3faee9ba0e666ff34cc1e3e0bd205788edca46b",
    "validation_workflow_blob": "41146f3d09fd95008cee0d5cf3a52bfb359c364d",
    "runtime_test_blob": "cd060b56ec8c505af67deaa3196e5c886502a416",
    "deployment_test_blob": "a593eeda7925a37c801b96627bb5e390183daa2e",
    "preflight_blob": "ae9e778b25f19e2263f975ef1edb9bc831684942",
    "spec_validator_blob": "78268251e20de4b8c896b7e58f192b557b92ec50",
    "pass209_main_merge_head": "c05cf860e4be5a0865813529baf9ad99e50dbe02",
}


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads(_text(path))
    if not isinstance(value, dict):
        raise RuntimeError("PASS208_OBJECT_REQUIRED")
    return value


def pass208_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load(PASS208_CONTRACT_PATH)
    restart = _text(PASS208_RESTART_PATH)
    runtime = _text(PASS208_RUNTIME_PATH)
    routes = _text(PASS208_ROUTES_PATH)
    preflight = _text(PASS208_PREFLIGHT_PATH)
    validator = _text(PASS208_VALIDATOR_PATH)
    successor = pass209_membrane_source_evidence()

    if contract.get("schema") != "HHS_PASS_208_CONTRACT_V1" or contract.get("pass") != 208:
        raise RuntimeError("PASS208_CONTRACT_IDENTITY_DRIFT")
    if contract.get("contract_id") != "HHS-P208-DIGITALOCEAN-PHYSICAL-GPU-NEURAL-BRANCH-MANIFOLD-VM81-HYDRATION-LATTICE-H72-H216":
        raise RuntimeError("PASS208_CONTRACT_ID_DRIFT")
    if contract.get("implementation_mode") != "ADDITIVE_GPU_MANIFOLD_WITH_SINGLETON_VM81_COMMIT":
        raise RuntimeError("PASS208_IMPLEMENTATION_MODE_DRIFT")

    formal = contract.get("formal_model") or {}
    for key in (
        "same_kernel_bytecode_hydration_lattice",
        "same_parent_snapshot_required",
        "same_constraint_root_required",
        "same_hash216_lineage_required",
        "same_hash72_commit_stream_required",
    ):
        if formal.get(key) is not True:
            raise RuntimeError("PASS208_FORMAL_MODEL_DRIFT:" + key)
    if formal.get("same_q_address_formula") != "q=243s+g" or formal.get("same_vm5184_lane_formula") != "s=64c+o":
        raise RuntimeError("PASS208_ADDRESS_FORMULA_DRIFT")

    branch = contract.get("branch_object") or {}
    if branch.get("candidate_only") is not True or branch.get("canonical_commit_authority") is not False:
        raise RuntimeError("PASS208_BRANCH_AUTHORITY_DRIFT")
    parallel = contract.get("parallelism") or {}
    if parallel.get("vm81_cells") != 81 or parallel.get("logical_hyperthreads_per_cell") != 64:
        raise RuntimeError("PASS208_VM5184_GEOMETRY_DRIFT")
    if parallel.get("physical_completion_order_is_noncanonical") is not True:
        raise RuntimeError("PASS208_COMPLETION_ORDER_DRIFT")
    if parallel.get("stable_branch_order") != ["objective_distance", "branch_candidate_root216", "branch_ordinal"]:
        raise RuntimeError("PASS208_STABLE_RANKING_DRIFT")

    package = contract.get("json_specification_package") or {}
    if package.get("file_count") != 23 or package.get("example_object_count") != 4:
        raise RuntimeError("PASS208_JSON_PACKAGE_DRIFT")
    digitalocean = contract.get("digitalocean") or {}
    if digitalocean.get("runtime_backend") != "OPENCL" or digitalocean.get("required_device_workgroup_size") != 64 or digitalocean.get("physical_gpu_fail_closed") is not True:
        raise RuntimeError("PASS208_PHYSICAL_GPU_BOUNDARY_DRIFT")
    authority = contract.get("authority") or {}
    expected_authority = {
        "gpu_may_expand_candidates": True,
        "gpu_may_rank_candidates": True,
        "gpu_may_commit_hash72": False,
        "gpu_may_persist_canonical_snapshot": False,
        "gpu_may_bypass_vm81": False,
        "cache_hit_authorizes_mutation": False,
        "singleton_vm81_mutation_authority": True,
    }
    for key, expected in expected_authority.items():
        if authority.get(key) is not expected:
            raise RuntimeError("PASS208_AUTHORITY_DRIFT:" + key)
    claims = contract.get("claim_boundary") or {}
    if claims.get("repository_deployment_support_implemented") is not True or claims.get("physical_digitalocean_gpu_provisioned_by_this_repository_change") is not False:
        raise RuntimeError("PASS208_CLAIM_BOUNDARY_DRIFT")

    for token in (
        "class Pass208GPUBranchManifold",
        "runtime.execute_batch(accelerator_batch)",
        '"verified_against_cpu": True',
        '"gpu_may_commit_hash72": False',
        "continuation_runtime.advance(",
        '"selected_branch_recomputed_by_singleton_vm81": True',
        '"gpu_committed_hash72": False',
    ):
        if token not in runtime:
            raise RuntimeError("PASS208_RUNTIME_GUARD_DRIFT:" + token)
    for token in (
        'API_PREFIX = "/api/runtime/gpu-manifold"',
        '@router.get("/status")',
        '@router.post("/expand")',
        '@router.post("/expand-and-commit")',
        "PASS205_CONTINUATION_RUNTIME",
        "PASS208_GPU_BRANCH_MANIFOLD.expand_and_commit",
    ):
        if token not in routes:
            raise RuntimeError("PASS208_ROUTE_GUARD_DRIFT:" + token)
    for token in (
        "HHS_PASS207_REQUIRE_PHYSICAL_GPU",
        "physical GPU fail-closed mode is required",
        "PHYSICAL_GPU_NOT_ACTIVE",
        "OPENCL_GPU_BACKEND_NOT_ACTIVE",
        'driver.get("logical_lanes_per_batch") != 5184',
        'driver.get("logical_hyperthreads_per_cell") != 64',
    ):
        if token not in preflight:
            raise RuntimeError("PASS208_PREFLIGHT_GUARD_DRIFT:" + token)
    for token in (
        'HHS_JSON_SPEC_EXPECTED_FILES", "23"',
        'HHS_JSON_SPEC_EXPECTED_EXAMPLES", "4"',
        "checksum mismatch",
        "required specification domain not evidenced",
        "HHS_PASS_208_JSON_SPEC_PACKAGE_VALIDATION_RECEIPT_V1",
    ):
        if token not in validator:
            raise RuntimeError("PASS208_VALIDATOR_GUARD_DRIFT:" + token)
    for token in (
        "Every physical GPU result must equal the exact CPU VM5184 oracle.",
        "Expansion alone cannot mutate canonical state.",
        "Pass 205 recomputes state, projection, learning, token, receipt, and persistence under singleton VM81 authority.",
    ):
        if token not in restart:
            raise RuntimeError("PASS208_RESTART_BOUNDARY_DRIFT:" + token)

    if successor.get("main_merge_head") != FROZEN["pass209_main_merge_head"]:
        raise RuntimeError("PASS208_PASS209_SUCCESSOR_DRIFT")

    return {
        "contract": contract,
        "restart": restart,
        "successor_pass209": successor,
        **FROZEN,
    }


def pass208_surface_declaration() -> Dict[str, Any]:
    pass208_membrane_source_evidence()
    return {
        "surface_id": PASS208_SURFACE_ID,
        "surface_type": "RUNTIME_ACCELERATOR",
        "module": "hhs_backend.runtime.hhs_pass208_gpu_branch_manifold_v1",
        "symbol": "Pass208GPUBranchManifold",
        "invariant_ids": ["HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS_PASS_208_CONTRACT_V1", "HHS_PASS_208_GPU_BRANCH_MANIFOLD_V1"],
        "witness_schemas": ["HHS_PASS219_PASS208_GPU_BRANCH_MANIFOLD_WITNESS_V1"],
        "validators": [PASS208_BIND_SYMBOL, "Pass207VM81GPURuntime.execute_batch", "Pass205ContinuationRuntime.advance"],
        "guards": [
            "pass208_same_parent_and_constraint_root",
            "pass208_exact_cpu_oracle_equality",
            "pass208_stable_integer_ranking",
            "pass208_gpu_candidate_only",
            "pass208_singleton_vm81_delegated_commit",
            "pass208_physical_gpu_fail_closed",
            "pass208_pass209_successor_gate",
        ],
        "rejection_codes": [
            "GPU_CPU_CANDIDATE_DIVERGENCE",
            "BYTECODE_ROOT_MISMATCH",
            "SELECTED_BRANCH_COMMIT_DIVERGENCE",
            "PHYSICAL_GPU_PROBE_FAILURE",
        ],
        "mutation_policy": "GPU_CANDIDATE_ONLY_DELEGATED_SINGLETON_VM81_COMMIT",
        "persistence_policy": "NO_GPU_CANONICAL_PERSISTENCE",
        "boundedness_policy": "PASS_208_5184_LANES_AND_CONFIGURED_BRANCH_LIMIT_V1",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass208_membrane_manifest() -> Dict[str, Any]:
    source = pass208_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS208_NUMBER,
        "classification": PASS208_CLASSIFICATION,
        "pass219_c_abi_surface": PASS208_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass208GPUBranchManifold",
        "runtime_surface": "Pass208GPUBranchManifold",
        "required_operations": list(REQUIRED_OPERATIONS),
        "main_merge_head": FROZEN["main_merge_head"],
        "logical_lanes_per_branch": 5184,
        "json_spec_file_count": 23,
        "gpu_candidate_expansion_bound": True,
        "exact_cpu_oracle_verification_bound": True,
        "stable_integer_ranking_bound": True,
        "pass205_singleton_vm81_commit_path_bound": True,
        "gpu_hash72_commit_forbidden": True,
        "gpu_canonical_persistence_forbidden": True,
        "gpu_vm81_bypass_forbidden": True,
        "physical_gpu_fail_closed": True,
        "pass209_successor_bound": source["successor_pass209"].get("main_merge_head") == FROZEN["pass209_main_merge_head"],
        "pass219_new_canonical_mutation_authority": False,
        "cxx_mutation_authority": False,
        "direct_gpu_vm81_mutation_authority": False,
        "next_pass_to_census": 207,
    }


def preflight_pass208_membrane(*, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    pass208_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    declaration = pass208_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation, cache=decision_cache) for operation in REQUIRED_OPERATIONS]
    return {"schema": "HHS_PASS219_PASS208_PREFLIGHT_V1", "ok": all(row.get("ok") is True for row in rows), "operations": rows}
