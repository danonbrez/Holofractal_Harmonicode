"""Pass 219 I116 additive Pass 215 terminal-closure membrane extension.

Pass 215's accepted authority is the bounded Iteration-20 shared-checkpoint
terminal benchmark. This extension authenticates both frozen Pass 215 records
independently against the accepted terminal constants, then binds the later
accepted final head/tree/artifact identity through the already-wired Pass 216
successor record. It does not rerun the 120-minute model benchmark, promote
general generation authority, or reinterpret Pass 215's historical "Pass 216
reserved" handoff as a current claim that the later Pass 216 alignment layer
does not exist.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import (
    ROOT,
    pass216_membrane_source_evidence,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS215_NUMBER = 215
PASS215_CLASSIFICATION = "WIRED"
PASS215_SURFACE_ID = "validator:pass219.inherited.pass215.terminal-closure"
PASS215_BIND_SYMBOL = "hhs_exact_pass219_bind_pass215_terminal_closure"
PASS215_CONTRACT_PATH = Path("contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json")
PASS215_IMPLEMENTATION_RECORD_PATH = Path(
    "evidence/pass215/PASS_215_ITERATION_20_IMPLEMENTATION_RECORD.json"
)
PASS215_RUNTIME_PATH = Path(
    "hhs_backend/runtime/hhs_pass215_iteration20_shared_checkpoint_terminal_v1.py"
)
PASS215_RESTART_PATH = Path("docs/pass215/ITERATION_20_RESTART_RECORD.md")

PASS215_CONTRACT_GIT_BLOB = "9110c6404c7e1a727d2440acb6d6c3b242e090e9"
PASS215_IMPLEMENTATION_RECORD_GIT_BLOB = "26179a42cc7b629a437bf9ffda2c192fb5bf2e63"
PASS215_RUNTIME_GIT_BLOB = "e1fd0f7feb3f417d6737b5afebaaf84ea7b94ff8"
PASS215_RESTART_GIT_BLOB = "b61b491109b60d0055440b414c218355ce89a3dd"

PASS215_FINAL_HEAD = "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc"
PASS215_FINAL_TREE = "17127e80a3f4852aeaedd1b807971fb4b4fba229"
PASS215_MAIN_MERGE = "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086"
PASS215_VALIDATION_RUN = 31325831364
PASS215_VALIDATION_JOB = 93275935886
PASS215_ARTIFACT_SHA256 = "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55"
PASS215_MODEL_SHA256 = "6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04"
PASS215_SELECTED_TOKEN_IDS = (450, 6575, 471, 528, 2827, 322, 278)
PASS215_RECEIPT_HASH72 = "rimw6Mf!E(*xCD5DK1/WGTK)*WRAl<RWjBQyi!qSI+rXW>H0L9AtWuu/3Cs5HKZ!B)JCwUTM"
PASS215_TERMINAL_COMPLETION_ROOT = "3dfb034753309c5f45f56f9bec5bf2178b1eb74974264cc306e46c8d6551f76a"
PASS215_EVIDENCE_ROOT = "5a8a17e10b1dc10db2912bc2df40aa67306fc520439716eab47596dc1e8aac1e"
PASS215_SUITE_ROOT = "3be955aecac999e945cdf48df63e0be13d2c353de8e20c6869a2364c2ba72234"
PASS215_SHARED_CONTENT_STORE_ROOT = "b7a9eb1678f263f20c5b61c0d9d3f01b76b152e2786b7e887ecb8265cbe454da"
PASS215_SHARED_BUNDLE_ROOT = "14953737a095ee9365386e436706cedd7a77328a04eb4dc3d5e45935cd367c8a"
PASS215_SEQUENTIAL_REUSE_ROOT = "52980a2e4b7890d136e549a4812dd859cc75e0ea4f442872dc99392e261ed7c0"

PASS215_CAPABILITIES = (
    "BOUNDED_STRICT_ARGMAX_GENERATION_CLOSURE",
    "EXACT_TWO_CHECKPOINT_RECONSTRUCTION",
    "CONTENT_ADDRESSED_SHARED_CHECKPOINT_REUSE",
    "EXACT_INCREMENTAL_COMPRESSED_BYTE_ACCOUNTING",
    "ZERO_RESTORE_FORWARD_REPLAY",
    "CROSS_PROCESS_SEMANTIC_EXACTNESS",
    "TRANSPORT_COMPRESSION_NON_AUTHORITY",
)


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_float(item) for item in value)
    return False


def _load_json(path: Path) -> Dict[str, Any]:
    value = json.loads((ROOT / path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PASS215_AUTHORITY_OBJECT_REQUIRED")
    if _contains_float(value):
        raise RuntimeError("PASS215_FLOAT_AUTHORITY_DRIFT")
    return value


def _verify_terminal_source(source: Dict[str, Any], *, prefix: str) -> None:
    expected = {
        "cumulative_test_count": 240,
        "selected_token_ids": list(PASS215_SELECTED_TOKEN_IDS),
        "termination_reason": "MAX_NEW_TOKENS",
        "shared_content_store_root_hash216": PASS215_SHARED_CONTENT_STORE_ROOT,
        "shared_checkpoint_bundle_root_hash216": PASS215_SHARED_BUNDLE_ROOT,
        "reused_unique_chunk_count": 36,
        "reused_compressed_blob_bytes": 28_375_966,
        "incremental_later_compressed_blob_bytes": 125_510_422,
        "later_standalone_compressed_blob_bytes": 153_886_388,
        "shared_store_savings_bytes": 28_375_966,
        "sequential_checkpoint_reuse_root_hash216": PASS215_SEQUENTIAL_REUSE_ROOT,
        "pass215_terminal_completion_root_hash216": PASS215_TERMINAL_COMPLETION_ROOT,
        "suite_root_hash216": PASS215_SUITE_ROOT,
        "evidence_root_hash216": PASS215_EVIDENCE_ROOT,
        "receipt_hash72": PASS215_RECEIPT_HASH72,
        "cross_process_replay": True,
        "semantic_exactness": True,
    }
    for field, expected_value in expected.items():
        if source.get(field) != expected_value:
            raise RuntimeError(prefix + ":" + field)


def pass215_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load_json(PASS215_CONTRACT_PATH)
    record = _load_json(PASS215_IMPLEMENTATION_RECORD_PATH)
    successor216 = pass216_membrane_source_evidence()
    pass216_contract = successor216["contract"]

    if contract.get("schema") != "HHS_PASS_215_ITERATION_20_CONTRACT_V1":
        raise RuntimeError("PASS215_CONTRACT_SCHEMA_DRIFT")
    if contract.get("contract") != "HHS-P215-I20-SHARED-CHECKPOINT-TERMINAL-CLOSURE":
        raise RuntimeError("PASS215_CONTRACT_IDENTITY_DRIFT")
    if contract.get("pass") != 215 or contract.get("iteration") != 20:
        raise RuntimeError("PASS215_TERMINAL_ITERATION_DRIFT")

    completion = contract["pass_completion"]
    if completion.get("pass215_contracted_benchmark_implementation_complete") is not True:
        raise RuntimeError("PASS215_TERMINAL_COMPLETION_DRIFT")
    if completion.get("terminal_iteration") != 20:
        raise RuntimeError("PASS215_TERMINAL_ITERATION_DRIFT")
    if completion.get("implemented_iteration_range") != [1, 20]:
        raise RuntimeError("PASS215_ITERATION_RANGE_DRIFT")
    if completion.get("bounded_profile_only") is not True:
        raise RuntimeError("PASS215_BOUNDED_PROFILE_DRIFT")
    if completion.get("broader_generation_authority_promoted") is not False:
        raise RuntimeError("PASS215_BROADER_AUTHORITY_DRIFT")

    workload = contract["contracted_workload"]
    if workload.get("model_sha256") != PASS215_MODEL_SHA256:
        raise RuntimeError("PASS215_MODEL_IDENTITY_DRIFT")
    if workload.get("prompt") != "Hello world!" or workload.get("max_new_tokens") != 7:
        raise RuntimeError("PASS215_BOUNDED_WORKLOAD_DRIFT")
    if workload.get("certification_bits") != 256:
        raise RuntimeError("PASS215_CERTIFICATION_BITS_DRIFT")

    source = contract["source_execution"]
    _verify_terminal_source(source, prefix="PASS215_CONTRACT_SOURCE_DRIFT")

    pruning = contract["output_projection_pruning_assessment"]
    if pruning.get("status") != "EVALUATED_NOT_AUTHORIZED" or pruning.get("candidates_pruned") != 0:
        raise RuntimeError("PASS215_PRUNING_AUTHORITY_DRIFT")
    if pruning.get("strict_argmax_authority_preserved") is not True:
        raise RuntimeError("PASS215_STRICT_ARGMAX_DRIFT")

    constraints = contract["constraints"]
    for field in (
        "output_projection_pruning_executed",
        "probabilistic_sampling_executed",
        "unbounded_or_general_generation_claimed",
        "arbitrary_prompt_or_model_generation_claimed",
        "adaptive_precision_authority_promoted",
        "canonical_float_interpretation_performed",
        "transport_compression_promoted_to_numerical_authority",
        "dense_forward_replaced",
        "runtime_mutation_authority_promoted",
        "canonical_mutation_authorized",
        "migration_active",
    ):
        if constraints.get(field) is not False:
            raise RuntimeError("PASS215_CONSTRAINT_DRIFT:" + field)

    if record.get("schema") != "HHS_PASS_215_ITERATION_20_IMPLEMENTATION_RECORD_V1":
        raise RuntimeError("PASS215_IMPLEMENTATION_RECORD_SCHEMA_DRIFT")
    if record.get("contract") != "HHS-P215-I20-SHARED-CHECKPOINT-TERMINAL-CLOSURE":
        raise RuntimeError("PASS215_IMPLEMENTATION_RECORD_IDENTITY_DRIFT")
    record_source = record["source_execution"]
    _verify_terminal_source(record_source, prefix="PASS215_IMPLEMENTATION_RECORD_SOURCE_DRIFT")

    parent = pass216_contract["parent_binding"]
    if parent.get("final_closure_head") != PASS215_FINAL_HEAD:
        raise RuntimeError("PASS215_FINAL_HEAD_DRIFT")
    if parent.get("final_closure_tree") != PASS215_FINAL_TREE:
        raise RuntimeError("PASS215_FINAL_TREE_DRIFT")
    if parent.get("main_merge_commit") != PASS215_MAIN_MERGE:
        raise RuntimeError("PASS215_MAIN_MERGE_DRIFT")
    if parent.get("final_closure_run") != PASS215_VALIDATION_RUN:
        raise RuntimeError("PASS215_FINAL_RUN_DRIFT")
    if parent.get("final_closure_job") != PASS215_VALIDATION_JOB:
        raise RuntimeError("PASS215_FINAL_JOB_DRIFT")
    if parent.get("final_closure_artifact_sha256") != PASS215_ARTIFACT_SHA256:
        raise RuntimeError("PASS215_ARTIFACT_IDENTITY_DRIFT")
    if parent.get("final_closure_cumulative_controls") != 240:
        raise RuntimeError("PASS215_SUCCESSOR_CONTROL_COUNT_DRIFT")

    historical_handoff = contract["downstream_transition"]
    if historical_handoff.get("pass216_status") != "RESERVED_NUMBER_NO_PASS":
        raise RuntimeError("PASS215_HISTORICAL_HANDOFF_DRIFT")
    if historical_handoff.get("pass217_and_pass219_may_consume_pass215_terminal_closure") is not True:
        raise RuntimeError("PASS215_PASS219_CONSUMPTION_GATE_DRIFT")

    return {
        "contract": contract,
        "implementation_record": record,
        "successor_pass216_contract": pass216_contract,
        "final_head": PASS215_FINAL_HEAD,
        "final_tree": PASS215_FINAL_TREE,
        "main_merge": PASS215_MAIN_MERGE,
        "validation_run": PASS215_VALIDATION_RUN,
        "validation_job": PASS215_VALIDATION_JOB,
        "artifact_sha256": PASS215_ARTIFACT_SHA256,
        "contract_git_blob": PASS215_CONTRACT_GIT_BLOB,
        "implementation_record_git_blob": PASS215_IMPLEMENTATION_RECORD_GIT_BLOB,
        "runtime_git_blob": PASS215_RUNTIME_GIT_BLOB,
        "restart_git_blob": PASS215_RESTART_GIT_BLOB,
    }


def pass215_membrane_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": PASS215_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": PASS215_BIND_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS_215_ITERATION_20_CONTRACT_V1",
            "HHS_PASS_215_ITERATION_20_IMPLEMENTATION_RECORD_V1",
            "HHS_PASS219_INHERITED_PASS215_TERMINAL_CLOSURE_BINDING_1_16",
        ],
        "witness_schemas": [
            "HHS_PASS_215_ITERATION_20_SHARED_CHECKPOINT_TERMINAL_EVIDENCE_V1",
            "HHS_PASS219_PASS215_TERMINAL_CLOSURE_WITNESS_V1",
        ],
        "validators": [PASS215_BIND_SYMBOL, "pass215_terminal_identity_validation"],
        "guards": [
            "pass215_terminal_head_tree_artifact_gate",
            "pass215_bounded_profile_gate",
            "pass215_strict_argmax_gate",
            "pass215_zero_restore_replay_gate",
            "pass215_exact_checkpoint_reuse_gate",
            "pass215_transport_compression_non_authority_gate",
            "pass215_no_pruning_sampling_float_mutation_gate",
            "single_c_vm81_mutation_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS215_TERMINAL_IDENTITY_DRIFT",
            "REJECT_PASS215_BROADER_GENERATION_AUTHORITY",
            "REJECT_PASS215_OUTPUT_PRUNING_OR_SAMPLING",
            "REJECT_PASS215_FLOAT_OR_TRANSPORT_NUMERICAL_AUTHORITY",
            "REJECT_PASS215_RESTORE_REPLAY",
            "REJECT_PASS215_CHECKPOINT_REUSE_DRIFT",
            "REJECT_PASS215_CPP_MUTATION_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_TERMINAL_CLOSURE_IDENTITY_ONLY",
        "boundedness_policy": "PASS_215_ITERATION_20_BOUNDED_PROFILE_ONLY",
        "declared_operations": [PASS215_BIND_SYMBOL],
    }


def pass215_membrane_manifest() -> Dict[str, Any]:
    evidence = pass215_membrane_source_evidence()
    contract = evidence["contract"]
    source = contract["source_execution"]
    constraints = contract["constraints"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS215_NUMBER,
        "classification": PASS215_CLASSIFICATION,
        "authoritative_surface": str(PASS215_RUNTIME_PATH),
        "contract_surface": str(PASS215_CONTRACT_PATH),
        "implementation_record_surface": str(PASS215_IMPLEMENTATION_RECORD_PATH),
        "pass219_c_abi_surface": PASS215_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass215TerminalClosure",
        "capabilities": list(PASS215_CAPABILITIES),
        "final_head": evidence["final_head"],
        "final_tree": evidence["final_tree"],
        "main_merge": evidence["main_merge"],
        "validation_run": evidence["validation_run"],
        "validation_job": evidence["validation_job"],
        "artifact_sha256": evidence["artifact_sha256"],
        "cumulative_test_count": source["cumulative_test_count"],
        "selected_token_ids": source["selected_token_ids"],
        "termination_reason": source["termination_reason"],
        "reused_unique_chunk_count": source["reused_unique_chunk_count"],
        "reused_compressed_blob_bytes": source["reused_compressed_blob_bytes"],
        "incremental_later_compressed_blob_bytes": source["incremental_later_compressed_blob_bytes"],
        "terminal_completion_root_hash216": source["pass215_terminal_completion_root_hash216"],
        "evidence_root_hash216": source["evidence_root_hash216"],
        "receipt_hash72": source["receipt_hash72"],
        "bounded_profile_only": contract["pass_completion"]["bounded_profile_only"],
        "broader_generation_authority_promoted": contract["pass_completion"]["broader_generation_authority_promoted"],
        "output_projection_pruning_executed": constraints["output_projection_pruning_executed"],
        "probabilistic_sampling_executed": constraints["probabilistic_sampling_executed"],
        "canonical_float_interpretation_performed": constraints["canonical_float_interpretation_performed"],
        "transport_compression_numerical_authority": constraints["transport_compression_promoted_to_numerical_authority"],
        "runtime_mutation_authority_promoted": constraints["runtime_mutation_authority_promoted"],
        "canonical_mutation_authorized": constraints["canonical_mutation_authorized"],
        "historical_pass216_status_in_pass215_record": contract["downstream_transition"]["pass216_status"],
        "later_pass216_alignment_authority_present": True,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": "NOT_GRANTED_BY_THIS_BINDING",
        "next_pass_to_census": 214,
    }


def preflight_pass215_membrane(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    pass215_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    return execute_surface_preflight(
        pass215_membrane_surface_declaration(),
        operation=PASS215_BIND_SYMBOL,
        cache=decision_cache,
    )


__all__ = [
    "VERSION",
    "PASS215_NUMBER",
    "PASS215_CLASSIFICATION",
    "PASS215_SURFACE_ID",
    "PASS215_BIND_SYMBOL",
    "PASS215_CAPABILITIES",
    "pass215_membrane_source_evidence",
    "pass215_membrane_surface_declaration",
    "pass215_membrane_manifest",
    "preflight_pass215_membrane",
]
