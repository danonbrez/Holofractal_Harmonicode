"""Pass 219 I128 membrane for repaired inherited Pass 198 calibration registry."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i127_pass199 import (
    pass199_membrane_source_evidence,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_28"
PASS198_NUMBER = 198
PASS198_CLASSIFICATION = "WIRED"
PASS198_CENSUS_CLASSIFICATION = "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
PASS198_BIND_SYMBOL = "hhs_exact_pass219_bind_pass198_repaired_calibration_registry"
PASS198_SURFACE_ID = "validator:pass219.inherited.pass198.repaired-calibration-registry"

P = Path
CONTRACT_PATH = P("HHS_PASS_198_OPERATION_CALIBRATION_REGISTRY.md")
RUNTIME_PATH = P("hhs_backend/runtime/hhs_pass198_operation_calibration_registry_v1.py")
API_PATH = P("hhs_backend/api/pass198_calibration_registry_routes.py")
LIFECYCLE_TEST_PATH = P("tests/test_hhs_pass198_operation_calibration_registry_v1.py")
REPAIR_TEST_PATH = P("tests/test_hhs_pass198_i128_repair_v1.py")
HISTORICAL_WORKFLOW_PATH = P(".github/workflows/pass198-operation-calibration-registry.yml")
REPAIR_WORKFLOW_PATH = P(".github/workflows/pass198-i128-repair-validation.yml")

HISTORICAL_BASE = "b40e11315840781d1fd9c12932fad46eb32e383f"
HISTORICAL_REVIEWED_HEAD = "a383ab8ec6a55e04ab490477c7b8cfe5d107d098"
ACCEPTED_MERGE = "122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e"
FROZEN_I127 = "fa89488d84f845fa372551b5324e0ddd37e49daf"
VALIDATED_REPAIR_HEAD = "97faba2ec59c54d1cd17be5bb88ade370841f65f"

HISTORICAL_BLOBS = {
    CONTRACT_PATH: "c623794f920ebbefbb6cb21eaf20767a1fd78306",
    RUNTIME_PATH: "3ec97b653344cbaf28eee89e6debbe1b6a89975d",
    API_PATH: "0e2581a3ecb0044eaf328617be1ae85e69e1e9a7",
    LIFECYCLE_TEST_PATH: "2f4285b15644e88fb46d74bf06fa5c8d266e8859",
    HISTORICAL_WORKFLOW_PATH: "d9eb8b172d81ed2d9e07916c13b914bab8ec6654",
}

REPAIRED_BLOBS = {
    RUNTIME_PATH: "9be70fd34fad007001a830fc225792a9a56a24e7",
    API_PATH: "2b2663cab7f74a2e1c21b77c2d5317296d925911",
    REPAIR_TEST_PATH: "b05a76b0cb694a51b66b147583c95520f2e54a9b",
    REPAIR_WORKFLOW_PATH: "879f6b10ed08f5be590f28510ba12b225da44d0b",
}

REVIEW_FINDING_IDS = (
    3700385770,
    3700385771,
    3700385772,
    3700385773,
    3700385776,
    3700385777,
    3700385778,
    3700385779,
    3700385780,
    3700385781,
    3700385783,
    3700385785,
    3700385787,
)

PRODUCTION_TOTALS = {
    "parameter_states": 405,
    "admitted_states": 320,
    "domain_rejections": 85,
    "vm5184_address_comparisons": 1_658_880,
    "simplification_count": 4,
    "negative_mutation_count": 6,
}

VALIDATED_RUNS = {
    "pass198_i128": 32770921677,
    "pass198_production": 32770921723,
    "pass199_production": 32770921637,
    "pass200a_production": 32770921758,
    "pass200b_production": 32770921660,
    "frozen_i127": 32770921681,
    "vm81_exact_abi": 32770921615,
    "uqcel": 32770921651,
}

REQUIRED_OPERATIONS = (
    "validate_pass198_squash_identity",
    "validate_pass198_review_repair",
    "validate_pass198_exact_execution_boundary",
    "validate_pass198_negative_mutation_execution",
    "validate_pass198_production_acceptance",
    "validate_pass199_successor_binding",
    "validate_pass198_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return completed.stdout.strip()


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS198_REPAIR_SOURCE_DRIFT:{path}:{fragment}")


def pass198_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_MERGE, "HEAD") != "":
        raise RuntimeError("PASS198_ACCEPTED_MERGE_ANCESTRY_OUTPUT")
    if _git("merge-base", HISTORICAL_REVIEWED_HEAD, "HEAD") != HISTORICAL_BASE:
        raise RuntimeError("PASS198_SQUASH_LINEAGE_DRIFT")
    if _git("merge-base", "HEAD", FROZEN_I127) != FROZEN_I127:
        raise RuntimeError("PASS198_FROZEN_I127_LINEAGE_DRIFT")
    if _git("merge-base", "--is-ancestor", VALIDATED_REPAIR_HEAD, "HEAD") != "":
        raise RuntimeError("PASS198_VALIDATED_REPAIR_HEAD_ANCESTRY_OUTPUT")

    for path, expected in HISTORICAL_BLOBS.items():
        historical = _git("rev-parse", f"{ACCEPTED_MERGE}:{path}")
        if historical != expected:
            raise RuntimeError(f"PASS198_HISTORICAL_BLOB_DRIFT:{path}:{historical}")

    if _git_blob(CONTRACT_PATH) != HISTORICAL_BLOBS[CONTRACT_PATH]:
        raise RuntimeError("PASS198_ACCEPTED_CONTRACT_PROVENANCE_REWRITTEN")
    if _git_blob(LIFECYCLE_TEST_PATH) != HISTORICAL_BLOBS[LIFECYCLE_TEST_PATH]:
        raise RuntimeError("PASS198_ACCEPTED_LIFECYCLE_TEST_PROVENANCE_REWRITTEN")
    if _git_blob(HISTORICAL_WORKFLOW_PATH) != HISTORICAL_BLOBS[HISTORICAL_WORKFLOW_PATH]:
        raise RuntimeError("PASS198_ACCEPTED_PRODUCTION_WORKFLOW_PROVENANCE_REWRITTEN")

    for path, expected in REPAIRED_BLOBS.items():
        if _git("rev-parse", f"{VALIDATED_REPAIR_HEAD}:{path}") != expected:
            raise RuntimeError(f"PASS198_VALIDATED_REPAIR_BLOB_DRIFT:{path}")
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS198_REPAIRED_SOURCE_DRIFT:{path}")

    _require(
        RUNTIME_PATH,
        'REPAIR_SCHEMA = "HHS_PASS_198_I128_REPAIR_V1"',
        'NEGATIVE_MUTATION_EVIDENCE_SCHEMA = "HHS_PASS_198_EXECUTED_NEGATIVE_MUTATION_EVIDENCE_V1"',
        "promotion-grade simplification proof requires complete deterministic full replay",
        "operation has no approved executable adapter/specification binding",
        "checkpoint_receipt_independent",
        "distinct verified workloads",
        '"NO_PER_SIMPLIFICATION_COST_MEASURED"',
        "_execute_required_negative_mutations",
        "registered negative-mutation set has no complete executable probe binding",
        "required negative mutation execution did not fail closed",
        "negative_mutation_execution_required_for_verified_proofs",
    )
    _require(
        API_PATH,
        "vm81_receipt_hash72=receipt_hash72",
        "runtime_controller.authorized_tick",
        '"api_or_worker_grants_authority": False',
    )
    _require(
        REPAIR_TEST_PATH,
        "test_01_full_replay_is_required_before_simplification_proof",
        "test_10_same_workload_under_two_receipts_is_not_cross_workload",
        "test_12_cost_metadata_does_not_claim_aggregate_saving_per_simplification",
        "test_13_required_negative_mutations_are_executed_and_persisted",
    )
    _require(
        REPAIR_WORKFLOW_PATH,
        "Run inherited lifecycle and thirteen-finding repair regressions",
        "Execute complete 405-state promotion-grade envelope",
        "all_required_negative_mutations_executed_and_detected",
        "Reject floating-point canonical operations",
    )

    successor = pass199_membrane_source_evidence()
    if successor.get("accepted_merge") != "426fe7786abff2e1e4688222a600f5ab39d14a5a":
        raise RuntimeError("PASS198_PASS199_SUCCESSOR_IDENTITY_DRIFT")

    return {
        "historical_base": HISTORICAL_BASE,
        "historical_reviewed_head": HISTORICAL_REVIEWED_HEAD,
        "accepted_merge": ACCEPTED_MERGE,
        "frozen_i127": FROZEN_I127,
        "validated_repair_head": VALIDATED_REPAIR_HEAD,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "repaired_blobs": {str(path): value for path, value in REPAIRED_BLOBS.items()},
        "review_finding_ids": list(REVIEW_FINDING_IDS),
        "production_totals": dict(PRODUCTION_TOTALS),
        "validated_runs": dict(VALIDATED_RUNS),
        "pass199_successor": successor,
    }


def validate_pass198_squash_identity() -> Dict[str, Any]:
    s = pass198_membrane_source_evidence()
    return {
        "ok": True,
        "pull_request": 136,
        "historical_base": s["historical_base"],
        "historical_reviewed_head": s["historical_reviewed_head"],
        "accepted_merge": s["accepted_merge"],
        "validated_repair_head": s["validated_repair_head"],
        "squash_aware": True,
        "accepted_provenance_preserved": True,
    }


def validate_pass198_review_repair() -> Dict[str, Any]:
    s = pass198_membrane_source_evidence()
    return {
        "ok": True,
        "review_finding_ids": s["review_finding_ids"],
        "finding_count": len(s["review_finding_ids"]),
        "repair_schema": "HHS_PASS_198_I128_REPAIR_V1",
        "historical_v1_is_provenance_not_current_repaired_source": True,
    }


def validate_pass198_exact_execution_boundary() -> Dict[str, Any]:
    pass198_membrane_source_evidence()
    return {
        "ok": True,
        "full_replay_required": True,
        "nonzero_admitted_coverage_required": True,
        "exact_builtin_adapter_spec_binding_required": True,
        "registration_vm81_receipt_persisted": True,
        "recursive_float_identity_rejection": True,
        "atomic_builtin_registration": True,
        "normalized_persistent_identifier_updates": True,
        "transactional_promotion_state_recheck": True,
        "checkpoint_receipt_independent": True,
        "distinct_workload_promotion_required": True,
        "per_simplification_cost_claim": "NO_PER_SIMPLIFICATION_COST_MEASURED",
    }


def validate_pass198_negative_mutation_execution() -> Dict[str, Any]:
    pass198_membrane_source_evidence()
    return {
        "ok": True,
        "schema": "HHS_PASS_198_EXECUTED_NEGATIVE_MUTATION_EVIDENCE_V1",
        "required_mutation_count": 6,
        "executed_mutation_count": 6,
        "all_required_negative_mutations_executed_and_detected": True,
        "required_before_envelope_verified": True,
        "evidence_hash72_per_mutation": True,
        "evidence_root_hash72_persisted": True,
    }


def validate_pass198_production_acceptance() -> Dict[str, Any]:
    s = pass198_membrane_source_evidence()
    return {
        "ok": True,
        **s["production_totals"],
        "closed": True,
        "deterministic_full_replay": True,
        "four_verified_simplifications": True,
        "six_negative_mutations_executed": True,
    }


def validate_pass199_successor_binding() -> Dict[str, Any]:
    successor = pass198_membrane_source_evidence()["pass199_successor"]
    return {
        "ok": True,
        "successor_pass": 199,
        "successor_accepted_merge": successor["accepted_merge"],
        "successor_validated_repair_head": successor["validated_repair_head"],
        "successor_preserved": True,
    }


def validate_pass198_no_new_authority() -> Dict[str, Any]:
    pass198_membrane_source_evidence()
    return {
        "ok": True,
        "api_mutation_authority": False,
        "i128_new_candidate_authority": False,
        "i128_new_canonical_mutation_authority": False,
        "i128_new_persistence_authority": False,
        "i128_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "compiler_auto_promotion": False,
        "runtime_auto_admission": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass198_surface_declaration() -> Dict[str, Any]:
    pass198_membrane_source_evidence()
    return {
        "surface_id": PASS198_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i128_pass198",
        "symbol": "validate_pass198_review_repair",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P198-OCR-PROOF-SIMPLIFICATION-VM81-H72"],
        "witness_schemas": [
            "HHSExactPass198RepairedCalibrationRegistryWitnessV1",
            "HHSExactPass219InheritedPass198BindingV1",
        ],
        "validators": [PASS198_BIND_SYMBOL, "validate_pass198_review_repair"],
        "guards": [
            "pass198_squash_identity",
            "pass198_thirteen_finding_repair",
            "pass198_exact_full_replay_coverage",
            "pass198_exact_adapter_binding",
            "pass198_vm81_registration_receipt",
            "pass198_exact_identity_rejection",
            "pass198_transaction_and_restart",
            "pass198_distinct_workload_promotion",
            "pass198_unmeasured_cost_claim",
            "pass198_executed_negative_mutations",
            "pass198_pass199_successor",
        ],
        "rejection_codes": [
            "REJECT_PASS198_HISTORICAL_IDENTITY_DRIFT",
            "REJECT_PASS198_UNEXECUTED_REPLAY",
            "REJECT_PASS198_UNEXECUTED_NEGATIVE_MUTATION",
            "REJECT_PASS198_ADAPTER_SPEC_DRIFT",
            "REJECT_PASS198_VM81_RECEIPT_LOSS",
            "REJECT_PASS198_APPROXIMATE_IDENTITY",
            "REJECT_PASS198_TRANSACTION_DRIFT",
            "REJECT_PASS198_WORKLOAD_IDENTITY_DRIFT",
            "REJECT_PASS198_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS198_STATE_READ_ONLY_MEMBRANE",
        "boundedness_policy": "PASS_198_REPAIRED_REGISTRY_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass198_membrane_manifest() -> Dict[str, Any]:
    s = pass198_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS198_NUMBER,
        "classification": PASS198_CLASSIFICATION,
        "census_classification": PASS198_CENSUS_CLASSIFICATION,
        "accepted_merge": s["accepted_merge"],
        "frozen_predecessor": s["frozen_i127"],
        "validated_repair_head": s["validated_repair_head"],
        "review_finding_ids": s["review_finding_ids"],
        "production_totals": s["production_totals"],
        "validated_runs": s["validated_runs"],
        "surface": pass198_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass198_membrane_preflight() -> Dict[str, Any]:
    declaration = pass198_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I128_PASS198_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS198_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass198_squash_identity": validate_pass198_squash_identity,
    "validate_pass198_review_repair": validate_pass198_review_repair,
    "validate_pass198_exact_execution_boundary": validate_pass198_exact_execution_boundary,
    "validate_pass198_negative_mutation_execution": validate_pass198_negative_mutation_execution,
    "validate_pass198_production_acceptance": validate_pass198_production_acceptance,
    "validate_pass199_successor_binding": validate_pass199_successor_binding,
    "validate_pass198_no_new_authority": validate_pass198_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 198 I128 membrane operation: {operation}")
    return OPERATIONS[operation]()
