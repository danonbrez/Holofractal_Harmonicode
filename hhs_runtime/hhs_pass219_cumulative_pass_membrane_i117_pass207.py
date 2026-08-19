"Pass 219 I117 inherited Pass 207 VM81 GPU hyperthread-driver membrane."
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass208 import pass208_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_17"
PASS207_NUMBER = 207
PASS207_CLASSIFICATION = "WIRED"
PASS207_BIND_SYMBOL = "hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver"
PASS207_SURFACE_ID = "runtime:pass207.vm81-gpu-hyperthread-driver"

PASS207_CONTRACT_PATH = Path("contracts/pass207/PASS_207_CONTRACT.json")
PASS207_MANIFEST_PATH = Path("artifacts/pass207/GPU_DRIVER_PLUGIN_MANIFEST.json")
PASS207_RESTART_PATH = Path("docs/pass207/RESTART_RECORD.md")
PASS207_RUNTIME_PATH = Path("hhs_backend/runtime/hhs_pass207_vm81_gpu_runtime_v1.py")
PASS207_BRIDGE_PATH = Path("hhs_python/runtime/hhs_pass207_gpu_driver_bridge.py")
PASS207_NATIVE_PATH = Path("hhs_python/runtime/hhs_pass207_gpu_driver_native.py")
PASS207_DRIVER_HEADER_PATH = Path("hhs_runtime/c/hhs_pass207_gpu_driver.h")
PASS207_DRIVER_SOURCE_PATH = Path("hhs_runtime/c/hhs_pass207_gpu_driver.c")

REQUIRED_OPERATIONS = (
    "Pass207VM81GPURuntime.status",
    "Pass207VM81GPURuntime.execute_batch",
    "Pass207VM81GPURuntime.execute",
    "Pass207VM81GPURuntime.rank_hash72_vectors",
    "Pass207GPUDriver.status",
    "Pass207GPUDriver.dispatch",
    "Pass207GPUDriver.vector_distance72",
)

FROZEN = {
    "validated_branch_head": "406eee3d68ec6c06017374085a46c9992d5778e3",
    "main_merge_head": "b350afea4f7d5a45ba8b8b0bb9740e40731cdb97",
    "branch_validation_run": 30915233211,
    "branch_validation_job": 92011562422,
    "contract_blob": "727660f3b48c87a78d7e274a5b71ded1bf6e4910",
    "manifest_blob": "2f8bb40210b77430a3e6861338d99d06b2ab5596",
    "driver_header_blob": "d73b80f53f8843a8c015ebdd735ee419f0877ae0",
    "driver_source_blob": "d812005e5be19383472193a7a9cdc50efbe96277",
    "driver_part1_blob": "97bef9b58357f44e4801b35de1cda2fea3a726d3",
    "driver_part2_blob": "ca8245293cfecc2d73afc063af512e7ff6322a02",
    "driver_part3_blob": "c76665697aa3417a1cc8789c794dcebf0219c282",
    "driver_part4_blob": "85f8acf834487ff6dc6fa062bebc509b2ab526b7",
    "driver_part5_blob": "dbc87a68e0ecdccceb37bb0f6f99bd9491489a0b",
    "native_bridge_blob": "f66249e67b6a70b2e5d6bdd42e57e814043fe4d1",
    "python_bridge_blob": "53e409665471f126925e6119f9f20ead3978766b",
    "runtime_blob": "66a1f25489cde4748fe034bb4b050aef74942a49",
    "restart_blob": "af3c4d8ec508de5f5e99431df22ed65f58021205",
    "validation_workflow_blob": "5f6ff36b68cf02ec43b6a65b0493afbb56cee7d4",
    "native_test_blob": "326546d25004e5789a526ac83aadb22b17b57c7d",
    "python_test_blob": "88ad4fec4f883f284858d4850e429245438fe98d",
    "pass208_main_merge_head": "cbeabffff4e70db6207f8c349dd88ea8b7bd6ea9",
}


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads(_text(path))
    if not isinstance(value, dict):
        raise RuntimeError("PASS207_OBJECT_REQUIRED")
    return value


def pass207_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load(PASS207_CONTRACT_PATH)
    manifest = _load(PASS207_MANIFEST_PATH)
    restart = _text(PASS207_RESTART_PATH)
    runtime = _text(PASS207_RUNTIME_PATH)
    bridge = _text(PASS207_BRIDGE_PATH)
    native = _text(PASS207_NATIVE_PATH)
    driver_header = _text(PASS207_DRIVER_HEADER_PATH)
    driver_source = _text(PASS207_DRIVER_SOURCE_PATH)
    successor = pass208_membrane_source_evidence()

    if contract.get("schema") != "HHS_PASS_207_CONTRACT_V1" or contract.get("pass") != 207:
        raise RuntimeError("PASS207_CONTRACT_IDENTITY_DRIFT")
    if contract.get("contract_id") != "HHS-P207-VM81-5184-GPU-HYPERTHREAD-DRIVER-VECTOR-BUFFER-CACHE-H72-H216":
        raise RuntimeError("PASS207_CONTRACT_ID_DRIFT")
    if contract.get("implementation_mode") != "ADDITIVE_CORE_PRESERVING_PLUGIN":
        raise RuntimeError("PASS207_IMPLEMENTATION_MODE_DRIFT")

    authority = contract.get("authority") or {}
    expected_authority = {
        "canonical_mutation_authority": "VM81_KERNEL",
        "canonical_mutation_authority_count": 1,
        "canonical_hash72_commit_stream_count": 1,
        "gpu_role": "PARALLEL_CANDIDATE_CALCULATION_ONLY",
        "gpu_may_commit_hash72": False,
        "gpu_may_bypass_vm81_admission": False,
        "parallel_canonical_authorities_allowed": False,
    }
    for key, expected in expected_authority.items():
        if authority.get(key) != expected:
            raise RuntimeError("PASS207_AUTHORITY_DRIFT:" + key)

    topology = contract.get("topology") or {}
    expected_topology = {
        "vm81_cells": 81,
        "logical_hyperthreads_per_cell": 64,
        "logical_lanes_per_batch": 5184,
        "lane_formula": "lane=64*cell+hyperthread",
        "phase_square_dimension": 72,
        "phase_formula": "phase_row=floor(lane/72), phase_column=lane mod 72",
        "bijection": "81*64=72*72=5184",
        "opencl_workgroup_size": 64,
        "opencl_workgroups_per_batch": 81,
    }
    for key, expected in expected_topology.items():
        if topology.get(key) != expected:
            raise RuntimeError("PASS207_TOPOLOGY_DRIFT:" + key)

    determinism = contract.get("determinism") or {}
    if determinism.get("stable_lane_identity") is not True:
        raise RuntimeError("PASS207_STABLE_LANE_DRIFT")
    if determinism.get("physical_completion_order_is_noncanonical") is not True:
        raise RuntimeError("PASS207_COMPLETION_ORDER_DRIFT")
    if determinism.get("lane_writes_are_disjoint") is not True:
        raise RuntimeError("PASS207_LANE_WRITE_DRIFT")
    if determinism.get("cell_pack_reduction_order") != "hyperthread_0_through_63":
        raise RuntimeError("PASS207_CELL_PACK_ORDER_DRIFT")
    if determinism.get("projection_order") != "channel_then_cell_then_batch":
        raise RuntimeError("PASS207_PROJECTION_ORDER_DRIFT")
    if determinism.get("vector_ranking_order") != ["distance", "candidate_hash72", "candidate_id", "source_ordinal"]:
        raise RuntimeError("PASS207_VECTOR_RANKING_DRIFT")
    if determinism.get("integer_only_canonical_fields") is not True or determinism.get("canonical_float_fields") != 0:
        raise RuntimeError("PASS207_EXACT_INTEGER_AUTHORITY_DRIFT")
    if determinism.get("cpu_vm5184_equivalence_required") is not True:
        raise RuntimeError("PASS207_CPU_ORACLE_DRIFT")

    cache = contract.get("buffer_cache") or {}
    if cache.get("mode") != "CONTENT_KEYED_LRU_HOST_AND_DEVICE_BUFFER_CACHE":
        raise RuntimeError("PASS207_CACHE_MODE_DRIFT")
    if cache.get("key_width_bits") != 256 or cache.get("cache_hit_authorizes_mutation") is not False:
        raise RuntimeError("PASS207_CACHE_AUTHORITY_DRIFT")
    if cache.get("cache_reuse_requires_same_content_identity") is not True:
        raise RuntimeError("PASS207_CACHE_IDENTITY_DRIFT")

    safety = contract.get("safety") or {}
    for key in (
        "unknown_backend_fails_closed",
        "required_physical_gpu_unavailable_fails_closed",
        "hydration_mismatch_fails_closed",
        "gpu_cpu_mismatch_fails_closed",
        "duplicate_delta_cell_fails_closed",
        "invalid_control_or_uint_width_fails_closed",
        "cache_cannot_mutate_canonical_state",
        "no_vendor_driver_or_host_kernel_authority",
    ):
        if safety.get(key) is not True:
            raise RuntimeError("PASS207_SAFETY_DRIFT:" + key)

    core = contract.get("core_preservation") or {}
    if core.get("modifies_pass205_core_abi") is not False or core.get("modifies_pass206_frozen_core") is not False:
        raise RuntimeError("PASS207_CORE_REPLACEMENT_DRIFT")
    if core.get("uses_existing_pass205_translation_contract") is not True or core.get("uses_existing_vm81_single_authority_boundary") is not True:
        raise RuntimeError("PASS207_INHERITED_AUTHORITY_DRIFT")

    claims = contract.get("claim_boundary") or {}
    if claims.get("software_driver_implemented") is not True:
        raise RuntimeError("PASS207_IMPLEMENTATION_CLAIM_DRIFT")
    if claims.get("physical_gpu_execution_claimed") is not False:
        raise RuntimeError("PASS207_PHYSICAL_GPU_CLAIM_DRIFT")

    if manifest.get("schema") != "HHS_PASS_207_GPU_DRIVER_PLUGIN_MANIFEST_V1":
        raise RuntimeError("PASS207_MANIFEST_IDENTITY_DRIFT")
    if manifest.get("classification") != "ADDITIVE_CORE_PRESERVING_RUNTIME_PLUGIN":
        raise RuntimeError("PASS207_MANIFEST_CLASSIFICATION_DRIFT")
    manifest_authority = manifest.get("authority") or {}
    expected_manifest_authority = {
        "may_propose_candidate": True,
        "may_commit_hash72": False,
        "may_mutate_canonical_state": False,
        "may_bypass_vm81": False,
        "may_reorder_noncommutative_operations": False,
    }
    for key, expected in expected_manifest_authority.items():
        if manifest_authority.get(key) is not expected:
            raise RuntimeError("PASS207_MANIFEST_AUTHORITY_DRIFT:" + key)

    for token in (
        "class Pass207VM81GPURuntime",
        "verify_against_cpu=True",
        "self.translation.execute_cpu_reference(batch)",
        "GPU child state differs from exact Pass 205 CPU oracle",
        "GPU projection differs from exact Pass 205 CPU oracle",
        "GPU dependency frontier differs from exact Pass 205 CPU oracle",
        '"candidate_only": True',
        '"verified_against_cpu": True',
        '"gpu_may_commit_hash72": False',
        '"vm81_single_admission_authority": True',
        '"stable_tie_break": [',
    ):
        if token not in runtime:
            raise RuntimeError("PASS207_RUNTIME_GUARD_DRIFT:" + token)

    for token in (
        "class Pass207GPUDriver",
        "def lane_address(",
        "def lane_decode(",
        "def lane_phase_coordinate(",
        "def status(",
        "def dispatch(",
        "def vector_distance72(",
        "_LIB.hhs_pass207_gpu_dispatch(",
        "_LIB.hhs_pass207_gpu_vector_distance72(",
        '"gpu_may_commit_hash72": False',
        '"vm81_single_admission_authority": True',
    ):
        if token not in bridge:
            raise RuntimeError("PASS207_BRIDGE_GUARD_DRIFT:" + token)

    for token in (
        "HHS_PASS207_LOGICAL_HYPERTHREADS 64u",
        "HHS_PASS207_LOGICAL_LANES 5184u",
        "HHS_PASS207_PHASE_DIMENSION 72u",
        "HHS_PASS207_PROJECTION_CHANNELS 32u",
        "hhs_pass207_gpu_dispatch(",
        "hhs_pass207_gpu_vector_distance72(",
    ):
        if token not in driver_header:
            raise RuntimeError("PASS207_HEADER_GUARD_DRIFT:" + token)

    for token in (
        '#include "hhs_pass207_gpu_driver_part1.inc"',
        '#include "hhs_pass207_gpu_driver_part2.inc"',
        '#include "hhs_pass207_gpu_driver_part3.inc"',
        '#include "hhs_pass207_gpu_driver_part4.inc"',
        '#include "hhs_pass207_gpu_driver_part5.inc"',
    ):
        if token not in driver_source:
            raise RuntimeError("PASS207_DRIVER_SEGMENT_DRIFT:" + token)

    for token in (
        "5,184 stable logical lanes per batch",
        "GPU output is always a candidate and is verified",
        "against the exact CPU reference before it can be returned as verified",
    ):
        if token not in native:
            raise RuntimeError("PASS207_NATIVE_BRIDGE_DRIFT:" + token)

    for token in (
        "rejects every physical GPU result that differs from the CPU VM5184 oracle",
        "physical OpenCL GPU execution",
        "fails closed when physical GPU execution is explicitly required and unavailable",
    ):
        if token not in restart:
            raise RuntimeError("PASS207_RESTART_BOUNDARY_DRIFT:" + token)

    if successor.get("main_merge_head") != FROZEN["pass208_main_merge_head"]:
        raise RuntimeError("PASS207_PASS208_SUCCESSOR_DRIFT")

    return {
        "contract": contract,
        "manifest": manifest,
        "restart": restart,
        "successor_pass208": successor,
        **FROZEN,
    }


def pass207_surface_declaration() -> Dict[str, Any]:
    pass207_membrane_source_evidence()
    return {
        "surface_id": PASS207_SURFACE_ID,
        "surface_type": "RUNTIME_ACCELERATOR",
        "module": "hhs_backend.runtime.hhs_pass207_vm81_gpu_runtime_v1",
        "symbol": "Pass207VM81GPURuntime",
        "invariant_ids": ["HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS_PASS_207_CONTRACT_V1", "HHS_PASS_207_VM81_GPU_HYPERTHREAD_RUNTIME_V1"],
        "witness_schemas": ["HHS_PASS219_PASS207_GPU_HYPERTHREAD_WITNESS_V1"],
        "validators": [
            PASS207_BIND_SYMBOL,
            "Pass205AcceleratorTranslation.execute_cpu_reference",
            "Pass207GPUDriver.dispatch",
        ],
        "guards": [
            "pass207_stable_vm5184_lane_identity",
            "pass207_lane_phase_bijection",
            "pass207_ordered_cell_pack_and_hydration",
            "pass207_exact_cpu_oracle_equality",
            "pass207_content_keyed_cache_no_mutation",
            "pass207_stable_hash72_vector_ranking",
            "pass207_singleton_vm81_admission",
            "pass207_physical_gpu_fail_closed",
            "pass207_pass208_successor_gate",
        ],
        "rejection_codes": [
            "PASS207_GPU_CPU_DIVERGENCE",
            "PASS207_HYDRATION_MISMATCH",
            "PASS207_BACKEND_UNAVAILABLE",
            "PASS207_CACHE_IDENTITY_MISMATCH",
        ],
        "mutation_policy": "GPU_CANDIDATE_ONLY_SINGLETON_VM81_ADMISSION",
        "persistence_policy": "NO_GPU_CANONICAL_PERSISTENCE",
        "boundedness_policy": "PASS_207_81X64_5184_LANES_V1",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass207_membrane_manifest() -> Dict[str, Any]:
    source = pass207_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS207_NUMBER,
        "classification": PASS207_CLASSIFICATION,
        "pass219_c_abi_surface": PASS207_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass207GPUHyperthreadDriver",
        "runtime_surface": "Pass207VM81GPURuntime",
        "required_operations": list(REQUIRED_OPERATIONS),
        "main_merge_head": FROZEN["main_merge_head"],
        "vm81_cells": 81,
        "logical_hyperthreads_per_cell": 64,
        "logical_lanes_per_batch": 5184,
        "phase_dimension": 72,
        "projection_channels": 32,
        "stable_vm5184_lane_dispatch_bound": True,
        "lane_phase_bijection_bound": True,
        "ordered_cell_pack_bound": True,
        "ordered_hydration_bound": True,
        "exact_cpu_oracle_verification_bound": True,
        "content_keyed_cache_bound": True,
        "stable_vector_ranking_bound": True,
        "candidate_only_bound": True,
        "gpu_hash72_commit_forbidden": True,
        "gpu_canonical_mutation_forbidden": True,
        "gpu_vm81_bypass_forbidden": True,
        "pass205_singleton_vm81_admission_bound": True,
        "physical_gpu_fail_closed": True,
        "pass208_successor_bound": source["successor_pass208"].get("main_merge_head") == FROZEN["pass208_main_merge_head"],
        "pass219_new_canonical_mutation_authority": False,
        "cxx_mutation_authority": False,
        "direct_gpu_vm81_mutation_authority": False,
        "next_pass_to_census": 206,
    }


def preflight_pass207_membrane(*, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    pass207_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    declaration = pass207_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation, cache=decision_cache) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_PASS207_PREFLIGHT_V1",
        "ok": all(row.get("ok") is True for row in rows),
        "operations": rows,
    }
