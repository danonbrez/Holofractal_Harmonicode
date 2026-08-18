"""Pass 219 I116 additive Pass 213 compiled-ROM/governed-dispatch membrane.

This module does not create a second mutation authority. It binds the accepted
Pass 213 Iteration-11 closure and exposes its already-governed Iteration-10
native dispatch authority through kernel-derived Pass 219 reachability. The raw
fixed-width C dispatch remains an implementation primitive behind
GovernedNativeDispatchAuthority.execute; direct C++ or direct VM81 mutation is
not granted by this membrane.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass214 import (
    PASS213_GATE_PRESERVATION_ROOT,
    pass214_membrane_source_evidence,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS213_NUMBER = 213
PASS213_CLASSIFICATION = "WIRED"
PASS213_BIND_SYMBOL = "hhs_exact_pass219_bind_pass213_compiled_rom_authority"
PASS213_EXECUTE_SYMBOL = "GovernedNativeDispatchAuthority.execute"
PASS213_VALIDATOR_SURFACE_ID = "validator:pass219.inherited.pass213.compiled-rom-authority"
PASS213_EXECUTION_SURFACE_ID = "runtime_authority:pass213.governed-native-dispatch"

PASS213_CONTRACT_PATH = Path("contracts/pass213/PASS_213_CONTRACT.json")
PASS213_RESTART_PATH = Path("docs/pass213/RESTART_RECORD.md")
PASS213_FINAL_EVIDENCE_PATH = Path("hhs_backend/runtime/hhs_pass213_final_evidence_v1.py")
PASS213_GOVERNED_AUTHORITY_PATH = Path(
    "hhs_backend/runtime/hhs_pass213_native_dispatch_authority_v1.py"
)
PASS213_NATIVE_DISPATCH_SOURCE_PATH = Path("native/pass213/hhs_pass213_native_dispatch.c")
PASS213_SECURE_ARENA_SOURCE_PATH = Path("native/pass213/hhs_pass213_secure_arena.c")

PASS213_CONTRACT_GIT_BLOB = "4787901cb2e52e594431a92ae3a40e2cd87623ec"
PASS213_RESTART_GIT_BLOB = "46bd8c51272bb09105ae1c4599113bc6236f6e10"
PASS213_FINAL_EVIDENCE_GIT_BLOB = "089290d4b1baff61d8848e655d1fb4c3ef31bfb4"
PASS213_GOVERNED_AUTHORITY_GIT_BLOB = "aea2ab6e7a2287fd066d99e0a2bb2c0481deb6e4"
PASS213_NATIVE_DISPATCH_SOURCE_GIT_BLOB = "a1dd0f29e1d4f166e1c9bae4ca14c8c2b5ebe75f"
PASS213_SECURE_ARENA_SOURCE_GIT_BLOB = "d92c36d904b77810b54593e60235491fc300d85d"

PASS213_FINAL_BRANCH_HEAD = "383ef8741f904ff1b770dd428530824640fbc83b"
PASS213_MAIN_MERGE_HEAD = "86ec461818682fc87232740758769602e8f9fe05"
PASS213_BRANCH_VALIDATION_RUN = 31065370870
PASS213_BRANCH_VALIDATION_JOB = 92501866672
PASS213_MAIN_VALIDATION_RUN = 31065471241
PASS213_MAIN_VALIDATION_JOB = 92502158212
PASS213_BRANCH_ARTIFACT_SHA256 = (
    "4541fdfef0b353257f16a58a6d1d9088f1dfe3dbbe37b8f0178fde1a86ebbc28"
)
PASS213_MAIN_ARTIFACT_SHA256 = (
    "93b478f73bbc2df96d67d86fc93ea85b6b48b0c960d9d35c16d7430a1551b6d6"
)
PASS213_SEMANTIC_ROOT_HASH216 = (
    "b783eaf39ca3cdff05d31dbe1406dc4ed45943a48b1cf89f3ee451a2c0326c0d"
)
PASS213_TERMINAL_RECEIPT_HASH72 = (
    "mO(Wo87dXeN)Ua2hbw96>2mLKi)iBlLT0Qy-qsjl>1icjig(7cc/d)FJd<9(gmvC20YL?twn"
)
PASS213_OBSERVATION_ROOT_HASH216 = (
    "d4bc7fdd97dac1d334711f6ce11e9a2ccdb16dcb1d89d23da8c5a178444d9c53"
)

PASS213_NATIVE_DISPATCH_IDS = (
    "hhs.native.u64.add.v1",
    "hhs.native.u64.sub.v1",
    "hhs.native.u64.xor.v1",
    "hhs.native.u64.and.v1",
    "hhs.native.u64.or.v1",
    "hhs.native.u64.mul_mod.v1",
    "hhs.native.u64.rotl.v1",
    "hhs.native.u64.eq.v1",
    "hhs.native.u64.select.v1",
)

PASS213_CAPABILITIES = (
    "IMMUTABLE_HASH216_COMPILED_ROM",
    "CORRECTION_BEFORE_INTERPRETATION_AND_EXECUTION",
    "SEALED_NATIVE_PROTECTED_MEMORY",
    "DEPENDENCY_SCOPED_PARAMETRIC_ADMISSION",
    "PERSISTENT_AUTHENTICATED_INVENTORY_AND_TOMBSTONES",
    "PQC_CHECKPOINT_ENCLOSURE",
    "RFC3161_TRUSTED_TIMESTAMP_ANCHOR",
    "EXACT_MOVING_TENSOR_VM5184_G243_FULL_HYDRATION",
    "CAPABILITY_GOVERNED_PROJECTION_SURFACES",
    "GOVERNED_SINGLETON_VM81_NATIVE_DISPATCH",
    "INTERRUPTION_RECOVERY_AND_REPLAY_CLOSURE",
)


def _load_json(path: Path) -> Dict[str, Any]:
    value = json.loads((ROOT / path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PASS213_AUTHORITY_OBJECT_REQUIRED")
    return value


def pass213_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load_json(PASS213_CONTRACT_PATH)
    successor214 = pass214_membrane_source_evidence()

    if contract.get("contract_id") != "HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243":
        raise RuntimeError("PASS213_CONTRACT_ID_DRIFT")
    if contract.get("pass_number") != 213:
        raise RuntimeError("PASS213_PASS_NUMBER_DRIFT")
    if contract.get("version") != "1.0.0-final":
        raise RuntimeError("PASS213_VERSION_DRIFT")
    if contract.get("classification") != "CONTRACT_IMPLEMENTATION_COMPLETE":
        raise RuntimeError("PASS213_CLASSIFICATION_DRIFT")
    if contract.get("final_iteration") != 11:
        raise RuntimeError("PASS213_FINAL_ITERATION_DRIFT")

    inheritance = contract["cumulative_inheritance"]
    if inheritance.get("passes_001_through_212") is not True:
        raise RuntimeError("PASS213_INHERITANCE_DRIFT")
    if inheritance.get("superseded_authorities") != []:
        raise RuntimeError("PASS213_SUPERSEDED_AUTHORITY_DRIFT")

    required = contract["required_invariants"]
    true_invariants = (
        "correction_before_interpretation",
        "correction_before_execution",
        "recovery_admission_required_for_canonical_insert",
        "native_protected_memory_required",
        "zeroization_before_release_required",
        "dependency_scoped_semantic_revalidation",
        "persistent_inventory_and_tombstones_required",
        "unauthorized_deletion_detectable",
        "ml_kem_768_required",
        "ml_dsa_65_required",
        "slh_dsa_sha2_128s_required",
        "rfc3161_external_timestamp_required",
        "timestamp_prior_anchor_and_hash216_lineage_continuity",
        "trusted_timestamp_anchor_required_for_tensor",
        "no_float_canonical_authority",
        "tensor_coordinate_map_reversible",
        "full_domain_closure_proof_required",
        "governed_surface_projection_only",
        "api_cli_shared_dispatcher_required",
        "network_capability_issuance_forbidden",
        "protected_fields_and_bytes_never_public",
        "physical_tensor_mapping_never_public",
        "singleton_vm81_admission",
        "immutable_compiled_rom_entries",
        "native_dispatch_real_c_abi_required",
        "native_dispatch_dynamic_allocation_forbidden",
        "native_dispatch_ambient_state_forbidden",
        "native_dispatch_exact_compiled_identity_required",
        "native_dispatch_current_policy_measurement_lineage_tensor_and_timestamp_required",
        "native_dispatch_exact_access_sets_required",
        "native_dispatch_stale_parent_rejected",
        "native_dispatch_successor_hash216_required",
        "native_dispatch_hash72_receipt_required",
        "native_dispatch_append_only_authenticated_ledger_required",
        "interrupted_resumed_replay_equality_required",
        "semantic_and_observation_roots_separate",
        "performance_timings_noncanonical",
    )
    for field in true_invariants:
        if required.get(field) is not True:
            raise RuntimeError("PASS213_REQUIRED_INVARIANT_DRIFT:" + field)

    domains = contract["domains"]
    expected_domains = {
        "vm81_cells": 81,
        "ordered_opcodes": 64,
        "vm5184": 5184,
        "g243": 243,
        "vm5184_g243": 1259712,
        "hydration_lanes": 40,
        "full_hydration_bits": 50388480,
        "full_hydration_bytes": 6298560,
        "local_hydration_frames": 9720,
        "affine_seed_bytes": 2430,
        "native_dispatch_unsigned_width": 64,
        "native_dispatch_max_operands": 8,
        "native_dispatch_max_results": 4,
    }
    for field, expected in expected_domains.items():
        if domains.get(field) != expected:
            raise RuntimeError("PASS213_DOMAIN_DRIFT:" + field)

    if tuple(contract.get("native_dispatch_ids") or ()) != PASS213_NATIVE_DISPATCH_IDS:
        raise RuntimeError("PASS213_NATIVE_DISPATCH_ID_SET_DRIFT")

    profile = contract["terminal_evidence_profile"]
    expected_profile = {
        "exact_lookup_iterations": 2048,
        "parametric_iterations": 512,
        "tensor_route_iterations": 8192,
        "dispatch_iterations": 32,
        "recovery_boundary_sequence": 16,
    }
    for field, expected in expected_profile.items():
        if profile.get(field) != expected:
            raise RuntimeError("PASS213_TERMINAL_PROFILE_DRIFT:" + field)

    semantic = contract["terminal_semantic_evidence"]
    if semantic.get("semantic_root_hash216") != PASS213_SEMANTIC_ROOT_HASH216:
        raise RuntimeError("PASS213_SEMANTIC_ROOT_DRIFT")
    if semantic.get("receipt_hash72") != PASS213_TERMINAL_RECEIPT_HASH72:
        raise RuntimeError("PASS213_TERMINAL_RECEIPT_DRIFT")
    if semantic.get("compressed_payload_bytes") != 2473:
        raise RuntimeError("PASS213_COMPRESSED_PAYLOAD_DRIFT")
    if semantic.get("missing_shard_count") != 2:
        raise RuntimeError("PASS213_RECOVERY_COUNT_DRIFT")
    if semantic.get("dispatch_final_sequence") != 32:
        raise RuntimeError("PASS213_DISPATCH_SEQUENCE_DRIFT")
    if semantic.get("uninterrupted_and_resumed_receipts_equal") is not True:
        raise RuntimeError("PASS213_REPLAY_EQUALITY_DRIFT")
    if semantic.get("ledger_chains_valid") is not True:
        raise RuntimeError("PASS213_LEDGER_CHAIN_DRIFT")

    observation = contract["reference_performance_observation"]
    if observation.get("hardware_specific") is not True or observation.get("timings_canonical") is not False:
        raise RuntimeError("PASS213_OBSERVATION_AUTHORITY_DRIFT")
    if observation.get("observation_root_hash216") != PASS213_OBSERVATION_ROOT_HASH216:
        raise RuntimeError("PASS213_OBSERVATION_ROOT_DRIFT")

    closure = contract["closure"]
    if closure.get("implementation_complete") is not True or closure.get("remaining_iterations") != []:
        raise RuntimeError("PASS213_CLOSURE_DRIFT")
    if closure.get("deterministic_replay_complete") is not True:
        raise RuntimeError("PASS213_REPLAY_CLOSURE_DRIFT")

    authority_text = (ROOT / PASS213_GOVERNED_AUTHORITY_PATH).read_text("utf-8")
    native_text = (ROOT / PASS213_NATIVE_DISPATCH_SOURCE_PATH).read_text("utf-8")
    if "class GovernedNativeDispatchAuthority" not in authority_text or "def execute(" not in authority_text:
        raise RuntimeError("PASS213_GOVERNED_EXECUTION_AUTHORITY_DRIFT")
    if "PASS213_NATIVE_DISPATCH_SINGLETON_VM81_REENTRY" not in authority_text:
        raise RuntimeError("PASS213_SINGLETON_VM81_GUARD_DRIFT")
    for token in (
        "PASS213_NATIVE_DISPATCH_STALE_PARENT",
        "PASS213_NATIVE_DISPATCH_KERNEL_POLICY_MISMATCH",
        "PASS213_NATIVE_DISPATCH_TIMESTAMP_NOT_MONOTONIC",
        "PASS213_NATIVE_DISPATCH_TENSOR_ROOT_MISMATCH",
    ):
        if token not in authority_text:
            raise RuntimeError("PASS213_GOVERNED_ADMISSION_GUARD_DRIFT:" + token)
    if "hhs_pass213_native_dispatch_execute" not in native_text:
        raise RuntimeError("PASS213_NATIVE_C_ABI_DRIFT")
    if "malloc(" in native_text or "calloc(" in native_text or "realloc(" in native_text:
        raise RuntimeError("PASS213_NATIVE_DYNAMIC_ALLOCATION_DRIFT")

    pass214_contract = successor214["contract"]
    pass213_foundation = pass214_contract["pass213_foundation"]
    if pass213_foundation.get("authoritative_merge") != PASS213_MAIN_MERGE_HEAD:
        raise RuntimeError("PASS213_PASS214_SUCCESSOR_MERGE_DRIFT")
    if successor214["pass213_gate_preservation_root_hash216"] != PASS213_GATE_PRESERVATION_ROOT:
        raise RuntimeError("PASS213_PASS214_GATE_PRESERVATION_DRIFT")

    return {
        "contract": contract,
        "successor_pass214": successor214,
        "final_branch_head": PASS213_FINAL_BRANCH_HEAD,
        "main_merge_head": PASS213_MAIN_MERGE_HEAD,
        "branch_validation_run": PASS213_BRANCH_VALIDATION_RUN,
        "branch_validation_job": PASS213_BRANCH_VALIDATION_JOB,
        "main_validation_run": PASS213_MAIN_VALIDATION_RUN,
        "main_validation_job": PASS213_MAIN_VALIDATION_JOB,
        "branch_artifact_sha256": PASS213_BRANCH_ARTIFACT_SHA256,
        "main_artifact_sha256": PASS213_MAIN_ARTIFACT_SHA256,
        "semantic_root_hash216": PASS213_SEMANTIC_ROOT_HASH216,
        "terminal_receipt_hash72": PASS213_TERMINAL_RECEIPT_HASH72,
        "observation_root_hash216": PASS213_OBSERVATION_ROOT_HASH216,
        "pass214_gate_preservation_root_hash216": PASS213_GATE_PRESERVATION_ROOT,
        "git_blobs": {
            "contract": PASS213_CONTRACT_GIT_BLOB,
            "restart": PASS213_RESTART_GIT_BLOB,
            "final_evidence": PASS213_FINAL_EVIDENCE_GIT_BLOB,
            "governed_authority": PASS213_GOVERNED_AUTHORITY_GIT_BLOB,
            "native_dispatch_source": PASS213_NATIVE_DISPATCH_SOURCE_GIT_BLOB,
            "secure_arena_source": PASS213_SECURE_ARENA_SOURCE_GIT_BLOB,
        },
    }


def pass213_validator_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": PASS213_VALIDATOR_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": PASS213_BIND_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243",
            "HHS_PASS219_INHERITED_PASS213_COMPILED_ROM_BINDING_1_16",
        ],
        "witness_schemas": [
            "HHS_PASS_213_FINAL_EVIDENCE_V1",
            "HHS_PASS219_PASS213_CLOSURE_WITNESS_V1",
        ],
        "validators": [PASS213_BIND_SYMBOL, "pass213_terminal_closure_identity_validation"],
        "guards": [
            "pass213_compiled_rom_identity_gate",
            "pass213_pass214_successor_gate",
            "pass213_no_parallel_mutation_authority_gate",
            "zero_bypass_runtime_interposer",
        ],
        "rejection_codes": [
            "REJECT_PASS213_TERMINAL_IDENTITY_DRIFT",
            "REJECT_PASS213_PASS214_SUCCESSOR_DRIFT",
            "REJECT_PASS213_PARALLEL_MUTATION_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_CLOSURE_IDENTITY_ONLY",
        "boundedness_policy": "PASS_213_ACCEPTED_TERMINAL_CLOSURE_ONLY",
        "declared_operations": [PASS213_BIND_SYMBOL],
    }


def pass213_execution_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": PASS213_EXECUTION_SURFACE_ID,
        "surface_type": "RUNTIME_AUTHORITY",
        "module": "hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1",
        "symbol": PASS213_EXECUTE_SYMBOL,
        "invariant_ids": [
            "HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I013", "HHS-I014"
        ],
        "contract_schemas": [
            "HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243",
            "HHS_PASS_213_NATIVE_DISPATCH_REQUEST_V1",
            "HHS_PASS_213_NATIVE_DISPATCH_RECEIPT_V1",
        ],
        "witness_schemas": [
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_PASS213_NATIVE_DISPATCH_LEDGER_RECEIPT_V1",
            "HHS_PASS217_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1",
        ],
        "validators": [
            "GovernedNativeDispatchAuthority.execute",
            "NativeDispatchLedger.verify_chain",
            "validate_authority_reachability",
        ],
        "guards": [
            "runtime_constraint_enforcement",
            "zero_bypass_runtime_interposer",
            "kernel_runtime_autocomposer",
            "pass213_exact_compiled_identity_gate",
            "pass213_current_parent_policy_measurement_lineage_timestamp_tensor_gate",
            "pass213_singleton_vm81_gate",
            "pass213_authenticated_ledger_commit_gate",
        ],
        "rejection_codes": [
            "PASS213_NATIVE_DISPATCH_SINGLETON_VM81_REENTRY",
            "PASS213_NATIVE_DISPATCH_STALE_PARENT",
            "PASS213_NATIVE_DISPATCH_KERNEL_POLICY_MISMATCH",
            "PASS213_NATIVE_DISPATCH_TIMESTAMP_NOT_MONOTONIC",
            "PASS213_NATIVE_DISPATCH_TENSOR_ROOT_MISMATCH",
            "REJECT_INHERITED_EXECUTION_AUTHORITY_REACHABILITY",
        ],
        "mutation_policy": "CONTROLLED_RUNTIME_MUTATION",
        "persistence_policy": "CANONICAL_MUTATION_RECEIPT",
        "boundedness_policy": "PASS_213_FIXED_WIDTH_SINGLETON_VM81_DISPATCH_V1",
        "declared_operations": [PASS213_EXECUTE_SYMBOL],
        "raw_native_c_symbol": "hhs_pass213_native_dispatch_execute",
        "raw_native_c_symbol_directly_reachable": False,
        "inherited_authority": True,
        "pass219_new_mutation_authority": False,
    }


def pass213_membrane_manifest() -> Dict[str, Any]:
    evidence = pass213_membrane_source_evidence()
    contract = evidence["contract"]
    profile = contract["terminal_evidence_profile"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS213_NUMBER,
        "classification": PASS213_CLASSIFICATION,
        "contract_surface": str(PASS213_CONTRACT_PATH),
        "pass219_c_abi_surface": PASS213_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass213CompiledROMAuthority",
        "governed_execution_surface": PASS213_EXECUTE_SYMBOL,
        "capabilities": list(PASS213_CAPABILITIES),
        "final_iteration": 11,
        "main_merge_head": evidence["main_merge_head"],
        "main_validation_run": evidence["main_validation_run"],
        "main_artifact_sha256": evidence["main_artifact_sha256"],
        "semantic_root_hash216": evidence["semantic_root_hash216"],
        "terminal_receipt_hash72": evidence["terminal_receipt_hash72"],
        "pass214_gate_preservation_root_hash216": evidence[
            "pass214_gate_preservation_root_hash216"
        ],
        "native_dispatch_id_count": len(PASS213_NATIVE_DISPATCH_IDS),
        "native_dispatch_iterations": profile["dispatch_iterations"],
        "recovery_boundary_sequence": profile["recovery_boundary_sequence"],
        "inherited_governed_canonical_mutation_authority": True,
        "pass219_new_mutation_authority": False,
        "cxx_mutation_authority": False,
        "vm81_direct_mutation_authority": False,
        "raw_native_dispatch_bypass_forbidden": True,
        "no_float_canonical_authority": True,
        "performance_timings_canonical": False,
        "next_pass_to_census": 212,
    }


def preflight_pass213_membrane(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    pass213_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    validator = execute_surface_preflight(
        pass213_validator_surface_declaration(),
        operation=PASS213_BIND_SYMBOL,
        cache=decision_cache,
    )
    execution = execute_surface_preflight(
        pass213_execution_surface_declaration(),
        operation=PASS213_EXECUTE_SYMBOL,
        cache=decision_cache,
    )
    return {
        "schema": "HHS_PASS219_PASS213_COMPOSED_PREFLIGHT_V1",
        "ok": validator["ok"] is True and execution["ok"] is True,
        "validator": validator,
        "execution": execution,
    }
