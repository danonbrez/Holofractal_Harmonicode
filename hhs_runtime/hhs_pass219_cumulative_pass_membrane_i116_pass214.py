"""Pass 219 I116 additive Pass 214 benchmark-authority membrane extension.

Pass 214's accepted authority is its repaired Iteration-8 repository-wide
compound benchmark closure, cumulatively revalidated on main and then extended
by proof-backed semantic-equivalence/reuse registration. A later repair-forward
rebound the Pass 214 VM81 adapter freeze to the exact integer/modular VM81
kernel. These are composed as distinct temporal authorities: the terminal
benchmark roots stay frozen, the reuse extension remains non-authoritative for
canonical execution, and the exact-kernel rebind supersedes only the obsolete
historical runtime-blob expectation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass215 import (
    pass215_membrane_source_evidence,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS214_NUMBER = 214
PASS214_CLASSIFICATION = "WIRED"
PASS214_SURFACE_ID = "validator:pass219.inherited.pass214.benchmark-authority"
PASS214_BIND_SYMBOL = "hhs_exact_pass219_bind_pass214_benchmark_authority"

PASS214_AUTHORITY_PATH = Path(
    "HHS_PASS_214_REPOSITORY_WIDE_COMPOUND_OPTIMIZATION_BENCHMARK_AUTHORITY.md"
)
PASS214_CONTRACT_PATH = Path("contracts/pass214/PASS_214_CONTRACT.json")
PASS214_I8_RECORD_PATH = Path("evidence/pass214/PASS_214_ITERATION_8_IMPLEMENTATION_RECORD.json")
PASS214_SEMANTIC_REUSE_PATH = Path("evidence/pass214/PASS_214_SEMANTIC_EQUIVALENCE_REUSE_V1.json")
PASS215_I1_CONTRACT_PATH = Path("contracts/pass215/PASS_215_ITERATION_1_CONTRACT.json")
PASS215_PROFILE_PATH = Path("contracts/pass215/PASS_215_BENCHMARK_PROFILE.json")
PASS214_VM81_REBIND_SCRIPT_PATH = Path("scripts/run_pass214_vm81_ir_adapter_validation.sh")
PASS214_VM81_REBIND_TEST_PATH = Path("tests/test_hhs_pass214_vm81_ir_adapter_v1.py")
EXACT_VM81_RUNTIME_PATH = Path("hhs_runtime/HARMONICODE_VM_RUNTIME.c")

PASS214_AUTHORITY_GIT_BLOB = "20424f170e66fa5b822f38019f303b15a1e64fd5"
PASS214_CONTRACT_GIT_BLOB = "c123c9c25685ea0dcd34f90fa67bbd9d65d766f2"
PASS214_I8_RECORD_GIT_BLOB = "b8c565f4b443b139249dfded44a1b36c70b43e70"
PASS214_SEMANTIC_REUSE_GIT_BLOB = "60ff714c1de5976bfb428ccf33c82f8a208d8fe4"
PASS215_I1_CONTRACT_GIT_BLOB = "6ce1a0ea7ed2ca61597398b1197387fec8e3505d"
PASS215_PROFILE_GIT_BLOB = "b458d674a75a4cfc64a32b9203dd693e3603576e"
PASS214_VM81_REBIND_SCRIPT_GIT_BLOB = "4abd1387926c214ee8b07867aae05a1545ff7efe"
PASS214_VM81_REBIND_TEST_GIT_BLOB = "8120feb77ad1c2adef05ef9857a779df6c9b8414"
EXACT_VM81_RUNTIME_GIT_BLOB = "81d9699b2d28d5d6a09ea4763653f3ba9eda9e15"

PASS214_VALIDATED_TERMINAL_HEAD = "fb167f0ae88346c7894d60b794eeba0e1967a971"
PASS214_MERGE_COMMIT = "1114a50c677f3f205d5858bc09b1249d3d365842"
PASS214_MAIN_CLOSURE_COMMIT = "063bcc1426b5bba106e139cb7dba1c540df090df"
PASS214_MAIN_CLOSURE_TREE = "9b21320cc72f3c77c79a9d76b083fe8b0c97f9d5"
PASS214_MAIN_CLOSURE_RUN = 31195458960
PASS214_MAIN_CLOSURE_ARTIFACT_SHA256 = (
    "8b2dc496bb856cc5627f1c66c79ee878b6305a2e5bdc4ff0bec94b0ff1a615c6"
)

PASS214_ROOTS = {
    "PASS214_REPOSITORY_SCAN_ROOT_HASH216":
        "8d527e0a562e05b0bac6a180cce1601f5808f22e2c1c9e5455b12b024b3d3d6a",
    "PASS214_OPTIMIZATION_REGISTRY_ROOT_HASH216":
        "32d73ff8e68fd8893fc347fb4aa97c4c8027b75dfd61bc3dab45aeae44f6a5dc",
    "PASS214_COMPATIBILITY_GRAPH_ROOT_HASH216":
        "b229bddea971f76b386b615316a0926473a4f66b37de9e49ec661b85567a6439",
    "PASS214_WORKLOAD_CORPUS_ROOT_HASH216":
        "c4f00ab874c2f1daaffd073ff6c0a85113314a4e6c70b5c30474ced43ece1f99",
    "PASS214_BENCHMARK_METHOD_ROOT_HASH216":
        "b1973a3145e370f4a85503dac540a5b9a12f7050bd6ccdb14f11f6a7506c6b0f",
    "PASS214_COMPOUND_EVIDENCE_ROOT_HASH216":
        "983a947ac2f625b8bdca689d6fc15b270f9ea7b8550c814484a158d96e624361",
    "PASS214_AUTHORITY_ROOT_HASH216":
        "c1d7875acd45f02da75101f5953541b6e1ce8ea3bb2cac39645004ab2509aeb8",
    "PASS215_BENCHMARK_PROFILE_ROOT_HASH216":
        "a3079f0f0b94d9fb485970662455482d4dab86e01802ca5bfdef6af3fbb6d85e",
}
PASS213_GATE_PRESERVATION_ROOT = (
    "214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092"
)
PASS214_COMPOUND_BENCHMARK_ROOT = (
    "3193f1cf30306d193b3d4a19e0670e396f26943c148c29ef45d20ffad456e21b"
)
PASS214_TERMINAL_RECEIPT_HASH72 = (
    "!(KTNH1zFC/ikVVJ1qCp8OKfOX8IoP<O8-/Df(NcNLYbY<<i+ICL5g2luJlws)AOvyX9XvJD"
)

PASS214_SEMANTIC_REUSE_HEAD = "54295e674d6bae1868bdb66b5d2aff0edaaac1d4"
PASS214_SEMANTIC_REUSE_TREE = "9e28fcb36de76440e2ee5909c2b82c1bf5a4314d"
PASS214_SEMANTIC_REUSE_RUN = 31259979177
PASS214_SEMANTIC_REUSE_ARTIFACT_SHA256 = (
    "33a237ee8d76c598656b253f70ecf2a72a285a5e71d165414b6bf938b4f103f8"
)
PASS214_VM81_REBIND_SCRIPT_COMMIT = "cf18b65bd1e3d7a3dce0081b97e1d4ff89b2c7d0"
PASS214_VM81_REBIND_TEST_COMMIT = "2b753167522c0829a4f7e23eb4378d824c82eafe"

PASS214_CAPABILITIES = (
    "REPOSITORY_WIDE_OPTIMIZATION_CENSUS",
    "CALLABLE_CONFORMANCE_AND_AUTHORITY_RECONCILIATION",
    "COMPOUND_AND_ABLATION_BENCHMARK_AUTHORITY",
    "EIGHT_ROOT_TERMINAL_CLOSURE",
    "FROZEN_PASS215_BENCHMARK_PROFILE_AUTHORIZATION",
    "PASS213_GATE_PRESERVATION",
    "PROOF_BACKED_SEMANTIC_EQUIVALENCE_REUSE",
    "EXACT_VM81_KERNEL_ADAPTER_REBIND",
)


def _load_json(path: Path) -> Dict[str, Any]:
    value = json.loads((ROOT / path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PASS214_AUTHORITY_OBJECT_REQUIRED")
    return value


def pass214_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load_json(PASS214_CONTRACT_PATH)
    iteration8 = _load_json(PASS214_I8_RECORD_PATH)
    semantic = _load_json(PASS214_SEMANTIC_REUSE_PATH)
    pass215_i1 = _load_json(PASS215_I1_CONTRACT_PATH)
    successor215 = pass215_membrane_source_evidence()

    if contract.get("schema") != "HHS_PASS_214_CONTRACT_V2":
        raise RuntimeError("PASS214_CONTRACT_SCHEMA_DRIFT")
    if contract.get("pass") != 214:
        raise RuntimeError("PASS214_CONTRACT_PASS_DRIFT")
    if contract.get("authorization_state") != "CONTRACT_AUTHORIZED_FULL_IMPLEMENTATION_REQUIRED":
        raise RuntimeError("PASS214_CONTRACT_AUTHORIZATION_DRIFT")
    if contract.get("terminal_roots") != list(PASS214_ROOTS):
        raise RuntimeError("PASS214_TERMINAL_ROOT_NAME_SET_DRIFT")
    pass213 = contract["pass213_foundation"]
    if pass213.get("authoritative_merge") != "86ec461818682fc87232740758769602e8f9fe05":
        raise RuntimeError("PASS214_PASS213_FOUNDATION_DRIFT")

    if iteration8.get("schema") != "HHS_PASS_214_ITERATION_8_IMPLEMENTATION_RECORD_V3":
        raise RuntimeError("PASS214_I8_SCHEMA_DRIFT")
    if iteration8.get("pass") != 214 or iteration8.get("iteration") != 8:
        raise RuntimeError("PASS214_I8_IDENTITY_DRIFT")
    if iteration8.get("classification") != (
        "HHS_PASS_214_FINAL_BENCHMARK_AUTHORITY_REPAIRED_FOR_CONTRACT_ORDERING_AND_SERIALIZATION"
    ):
        raise RuntimeError("PASS214_I8_CLASSIFICATION_DRIFT")
    boundary = iteration8["benchmark_boundary"]
    expected_boundary = {
        "workload_families": 15,
        "workload_modes_per_family": 11,
        "mode_executions": 165,
        "mandatory_ablations": 26,
        "a0_a9_stages": 10,
        "pass197_address_comparisons": 1658880,
        "pass212_full_hydration_bits": 50388480,
        "pass212_full_state_recoveries": 3,
        "cross_process_replays": 15,
        "multimodal_ml_compound_exercised": True,
        "multimodal_ml_ablation_exercised": True,
        "negative_controls_fail_closed": True,
        "complete_cost_accounting": True,
        "physical_compression_claim_boundary_preserved": True,
    }
    for field, expected in expected_boundary.items():
        if boundary.get(field) != expected:
            raise RuntimeError("PASS214_I8_BENCHMARK_BOUNDARY_DRIFT:" + field)

    if iteration8.get("terminal_roots") != list(PASS214_ROOTS):
        raise RuntimeError("PASS214_I8_TERMINAL_ROOT_NAME_SET_DRIFT")
    scope = iteration8["authority_scope"]
    if scope.get("pass213_runtime_mutation_authority") != "NOT_PROMOTED_BY_PASS214":
        raise RuntimeError("PASS214_PASS213_MUTATION_AUTHORITY_DRIFT")
    if scope.get("canonical_mutation_authorized_by_pass214") is not False:
        raise RuntimeError("PASS214_CANONICAL_MUTATION_AUTHORITY_DRIFT")
    if scope.get("migration_active") is not False:
        raise RuntimeError("PASS214_MIGRATION_AUTHORITY_DRIFT")
    if scope.get("pass215_authorization_scope") != "FROZEN_BENCHMARK_PROFILE_AND_NEXT_PASS_DEVELOPMENT":
        raise RuntimeError("PASS214_PASS215_AUTHORIZATION_SCOPE_DRIFT")

    if pass215_i1.get("schema") != "HHS_PASS_215_ITERATION_1_CONTRACT_V1":
        raise RuntimeError("PASS214_SUCCESSOR_SCHEMA_DRIFT")
    inherited = pass215_i1["inherits"]
    successor_expected = {
        "pass214_main_closure_commit": PASS214_MAIN_CLOSURE_COMMIT,
        "pass214_main_closure_tree": PASS214_MAIN_CLOSURE_TREE,
        "pass214_authority_root_hash216": PASS214_ROOTS["PASS214_AUTHORITY_ROOT_HASH216"],
        "pass215_benchmark_profile_root_hash216": PASS214_ROOTS[
            "PASS215_BENCHMARK_PROFILE_ROOT_HASH216"
        ],
        "pass213_gate_preservation_root_hash216": PASS213_GATE_PRESERVATION_ROOT,
        "pass214_terminal_receipt_hash72": PASS214_TERMINAL_RECEIPT_HASH72,
    }
    for field, expected in successor_expected.items():
        if inherited.get(field) != expected:
            raise RuntimeError("PASS214_SUCCESSOR_BINDING_DRIFT:" + field)
    frozen = pass215_i1["frozen_instrument"]
    if frozen.get("git_blob_sha1") != PASS215_PROFILE_GIT_BLOB:
        raise RuntimeError("PASS214_PASS215_PROFILE_BLOB_DRIFT")
    if frozen.get("post_hoc_redefinition_forbidden") is not True:
        raise RuntimeError("PASS214_POST_HOC_PROFILE_REDEFINITION_DRIFT")
    if frozen.get("profile_content_must_not_be_modified") is not True:
        raise RuntimeError("PASS214_PASS215_PROFILE_MUTABILITY_DRIFT")

    if semantic.get("schema") != "HHS_PASS_214_SEMANTIC_EQUIVALENCE_REUSE_EVIDENCE_V1":
        raise RuntimeError("PASS214_SEMANTIC_REUSE_SCHEMA_DRIFT")
    if semantic.get("classification") != (
        "PASS_214_SEMANTIC_EQUIVALENCE_REUSE_AND_FIRST_MODULE_PROMOTION_VALIDATED"
    ):
        raise RuntimeError("PASS214_SEMANTIC_REUSE_CLASSIFICATION_DRIFT")
    if semantic.get("validated_implementation_head") != PASS214_SEMANTIC_REUSE_HEAD:
        raise RuntimeError("PASS214_SEMANTIC_REUSE_HEAD_DRIFT")
    if semantic.get("validated_implementation_tree") != PASS214_SEMANTIC_REUSE_TREE:
        raise RuntimeError("PASS214_SEMANTIC_REUSE_TREE_DRIFT")
    authority = semantic["authority"]
    for field in (
        "execution_authority_changed",
        "automatic_semantic_promotion",
        "name_similarity_is_equivalence_proof",
        "no_float_canonical_authority_changed",
    ):
        if authority.get(field) is not False:
            raise RuntimeError("PASS214_SEMANTIC_REUSE_AUTHORITY_DRIFT:" + field)
    if authority.get("pass213_governed_mutation_authority_preserved") is not True:
        raise RuntimeError("PASS214_SEMANTIC_REUSE_PASS213_GATE_DRIFT")
    reconciliation = semantic["semantic_reconciliation"]
    if reconciliation.get("reusable_registry_entries") != 306:
        raise RuntimeError("PASS214_REUSABLE_REGISTRY_COUNT_DRIFT")
    if semantic["isolation_accounting"].get("remaining_reusable_extraction_backlog") != 1383:
        raise RuntimeError("PASS214_REUSE_BACKLOG_DRIFT")
    promotion = semantic["first_reusable_module_promotion"]
    if promotion.get("canonical_mutation_authority") != "NONE":
        raise RuntimeError("PASS214_REUSE_PROMOTION_AUTHORITY_DRIFT")
    validated_runs = semantic.get("validated_runs") or []
    semantic_run = next(
        (row for row in validated_runs if row.get("run_id") == PASS214_SEMANTIC_REUSE_RUN),
        None,
    )
    if semantic_run is None or semantic_run.get("status") != "SUCCESS":
        raise RuntimeError("PASS214_SEMANTIC_REUSE_VALIDATION_DRIFT")
    if semantic_run.get("artifact_digest") != "sha256:" + PASS214_SEMANTIC_REUSE_ARTIFACT_SHA256:
        raise RuntimeError("PASS214_SEMANTIC_REUSE_ARTIFACT_DRIFT")

    script_text = (ROOT / PASS214_VM81_REBIND_SCRIPT_PATH).read_text("utf-8")
    test_text = (ROOT / PASS214_VM81_REBIND_TEST_PATH).read_text("utf-8")
    if EXACT_VM81_RUNTIME_GIT_BLOB not in script_text or EXACT_VM81_RUNTIME_GIT_BLOB not in test_text:
        raise RuntimeError("PASS214_EXACT_VM81_REBIND_IDENTITY_DRIFT")
    if "PASS214_VM81_IR_ADAPTER_DIRECT_MUTATION_BYPASS" not in script_text:
        raise RuntimeError("PASS214_VM81_DIRECT_MUTATION_GUARD_DRIFT")

    successor_manifest_contract = successor215["contract"]
    if successor_manifest_contract.get("pass") != 215:
        raise RuntimeError("PASS214_SUCCESSOR_PASS215_TERMINAL_DRIFT")

    return {
        "contract": contract,
        "iteration8": iteration8,
        "semantic_reuse": semantic,
        "pass215_iteration1_contract": pass215_i1,
        "successor_pass215_terminal": successor215,
        "validated_terminal_head": PASS214_VALIDATED_TERMINAL_HEAD,
        "merge_commit": PASS214_MERGE_COMMIT,
        "main_closure_commit": PASS214_MAIN_CLOSURE_COMMIT,
        "main_closure_tree": PASS214_MAIN_CLOSURE_TREE,
        "main_closure_run": PASS214_MAIN_CLOSURE_RUN,
        "main_closure_artifact_sha256": PASS214_MAIN_CLOSURE_ARTIFACT_SHA256,
        "terminal_roots": dict(PASS214_ROOTS),
        "pass213_gate_preservation_root_hash216": PASS213_GATE_PRESERVATION_ROOT,
        "compound_benchmark_root_hash216": PASS214_COMPOUND_BENCHMARK_ROOT,
        "terminal_receipt_hash72": PASS214_TERMINAL_RECEIPT_HASH72,
        "semantic_reuse_head": PASS214_SEMANTIC_REUSE_HEAD,
        "semantic_reuse_tree": PASS214_SEMANTIC_REUSE_TREE,
        "semantic_reuse_run": PASS214_SEMANTIC_REUSE_RUN,
        "semantic_reuse_artifact_sha256": PASS214_SEMANTIC_REUSE_ARTIFACT_SHA256,
        "exact_vm81_kernel_git_blob": EXACT_VM81_RUNTIME_GIT_BLOB,
        "vm81_rebind_script_commit": PASS214_VM81_REBIND_SCRIPT_COMMIT,
        "vm81_rebind_test_commit": PASS214_VM81_REBIND_TEST_COMMIT,
        "git_blobs": {
            "authority": PASS214_AUTHORITY_GIT_BLOB,
            "contract": PASS214_CONTRACT_GIT_BLOB,
            "iteration8": PASS214_I8_RECORD_GIT_BLOB,
            "semantic_reuse": PASS214_SEMANTIC_REUSE_GIT_BLOB,
            "pass215_iteration1": PASS215_I1_CONTRACT_GIT_BLOB,
            "pass215_profile": PASS215_PROFILE_GIT_BLOB,
            "vm81_rebind_script": PASS214_VM81_REBIND_SCRIPT_GIT_BLOB,
            "vm81_rebind_test": PASS214_VM81_REBIND_TEST_GIT_BLOB,
            "exact_vm81_runtime": EXACT_VM81_RUNTIME_GIT_BLOB,
        },
    }


def pass214_membrane_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": PASS214_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": PASS214_BIND_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS_214_CONTRACT_V2",
            "HHS_PASS_214_ITERATION_8_IMPLEMENTATION_RECORD_V3",
            "HHS_PASS_214_SEMANTIC_EQUIVALENCE_REUSE_EVIDENCE_V1",
            "HHS_PASS219_INHERITED_PASS214_BENCHMARK_AUTHORITY_BINDING_1_16",
        ],
        "witness_schemas": [
            "HHS_PASS214_CUMULATIVE_MAIN_TERMINAL_CLOSURE_V1",
            "HHS_PASS219_PASS214_BENCHMARK_AUTHORITY_WITNESS_V1",
        ],
        "validators": [PASS214_BIND_SYMBOL, "pass214_benchmark_authority_identity_validation"],
        "guards": [
            "pass214_eight_root_terminal_closure_gate",
            "pass214_pass215_profile_freeze_gate",
            "pass214_pass213_gate_preservation_gate",
            "pass214_semantic_reuse_non_authority_gate",
            "pass214_exact_vm81_kernel_rebind_gate",
            "pass214_no_runtime_or_canonical_mutation_gate",
            "single_c_vm81_mutation_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS214_TERMINAL_ROOT_DRIFT",
            "REJECT_PASS214_PASS215_PROFILE_DRIFT",
            "REJECT_PASS214_PASS213_GATE_BYPASS",
            "REJECT_PASS214_SEMANTIC_REUSE_AUTHORITY_ESCALATION",
            "REJECT_PASS214_STALE_VM81_KERNEL_REBIND",
            "REJECT_PASS214_CPP_OR_VM81_MUTATION_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_BENCHMARK_AND_REUSE_IDENTITY_ONLY",
        "boundedness_policy": "PASS_214_ACCEPTED_TERMINAL_AND_NONAUTHORITY_EXTENSIONS_ONLY",
        "declared_operations": [PASS214_BIND_SYMBOL],
    }


def pass214_membrane_manifest() -> Dict[str, Any]:
    evidence = pass214_membrane_source_evidence()
    iteration8 = evidence["iteration8"]
    boundary = iteration8["benchmark_boundary"]
    semantic = evidence["semantic_reuse"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS214_NUMBER,
        "classification": PASS214_CLASSIFICATION,
        "authoritative_surface": "hhs_backend/runtime/hhs_pass214_iteration8_terminal_freeze_v3.py",
        "contract_surface": str(PASS214_CONTRACT_PATH),
        "semantic_reuse_surface": str(PASS214_SEMANTIC_REUSE_PATH),
        "pass219_c_abi_surface": PASS214_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass214BenchmarkAuthority",
        "capabilities": list(PASS214_CAPABILITIES),
        "validated_terminal_head": evidence["validated_terminal_head"],
        "merge_commit": evidence["merge_commit"],
        "main_closure_commit": evidence["main_closure_commit"],
        "main_closure_tree": evidence["main_closure_tree"],
        "main_closure_run": evidence["main_closure_run"],
        "main_closure_artifact_sha256": evidence["main_closure_artifact_sha256"],
        "terminal_roots": evidence["terminal_roots"],
        "pass213_gate_preservation_root_hash216": evidence[
            "pass213_gate_preservation_root_hash216"
        ],
        "compound_benchmark_root_hash216": evidence["compound_benchmark_root_hash216"],
        "terminal_receipt_hash72": evidence["terminal_receipt_hash72"],
        "workload_families": boundary["workload_families"],
        "mode_executions": boundary["mode_executions"],
        "mandatory_ablations": boundary["mandatory_ablations"],
        "benchmark_stages": boundary["a0_a9_stages"],
        "semantic_reuse_head": evidence["semantic_reuse_head"],
        "semantic_reuse_registry_entries": semantic["semantic_reconciliation"][
            "reusable_registry_entries"
        ],
        "semantic_reuse_remaining_backlog": semantic["isolation_accounting"][
            "remaining_reusable_extraction_backlog"
        ],
        "execution_authority_changed_by_semantic_reuse": False,
        "automatic_semantic_promotion": False,
        "exact_vm81_kernel_git_blob": evidence["exact_vm81_kernel_git_blob"],
        "pass213_gates_preserved": True,
        "runtime_mutation_authority_promoted": False,
        "canonical_mutation_authorized": False,
        "migration_active": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "next_pass_to_census": 213,
    }


def preflight_pass214_membrane(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    pass214_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    return execute_surface_preflight(
        pass214_membrane_surface_declaration(),
        operation=PASS214_BIND_SYMBOL,
        cache=decision_cache,
    )
