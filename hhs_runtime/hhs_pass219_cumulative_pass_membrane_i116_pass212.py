"""Pass 219 I116 inherited Pass 212 full-hydration recovery membrane."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass213 import (
    PASS213_MAIN_MERGE_HEAD,
    pass213_membrane_source_evidence,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS212_NUMBER = 212
PASS212_CLASSIFICATION = "WIRED"
PASS212_BIND_SYMBOL = "hhs_exact_pass219_bind_pass212_full_hydration_recovery"
PASS212_SURFACE_ID = "runtime:pass212.full-hydration-recovery"
PASS212_CONTRACT_PATH = Path("contracts/pass212/PASS_212_CONTRACT.json")
PASS212_EVIDENCE_PATH = Path("evidence/pass212/PASS_212_FULL_HYDRATION_REFERENCE_VECTORS.json")
PASS212_RUNTIME_PATH = Path("hhs_backend/runtime/hhs_pass212_full_hydration_recovery_v1.py")
PASS212_API_PATH = Path("hhs_backend/api/pass212_full_hydration_recovery_routes.py")
PASS213_RECOVERY_PATH = Path("hhs_backend/runtime/hhs_pass213_recovery_admission_v1.py")

REQUIRED_OPERATIONS = (
    "generate_affine_hydration(seed_bytes)",
    "apply_bit_exceptions(state, positions)",
    "FullHydrationRecoveryRuntime.encode(state)",
    "FullHydrationRecoveryRuntime.decode(package)",
    "FullHydrationRecoveryRuntime.protect_payload(payload)",
    "FullHydrationRecoveryRuntime.recover_payload(protected)",
    "FullHydrationRecoveryRuntime.without_shards(package, refs)",
)

FROZEN = {
    "validated_branch_head": "adc6737d12a371625413c63068de5a898fed0c0f",
    "main_merge_head": "3fc3ec4596062a1f7e37de19165cfe0e6ed88483",
    "branch_validation_run": 31015011012,
    "main_validation_run": 31015122160,
    "contract_blob": "12f2c577e02f4436ee776366a1994ece5a765fca",
    "restart_blob": "c2f2ef336de57a2897397e01e820c69e724fa1cc",
    "runtime_blob": "2688cf46e2f3084589d4ad961d53e89c33b40a7c",
    "api_blob": "0699e1c720f88f47d1d8e4562cb9a73f6a3c0372",
    "evidence_blob": "c27a29e5268bba4361741ed304c31fa293a9e0ae",
    "validation_blob": "923303154fa4703b897aad59c0b1b0411a52a276",
    "pass213_recovery_blob": "df7ee51a72991a10bdb25e1342d17cd26a826b9c",
}


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads((ROOT / path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PASS212_OBJECT_REQUIRED")
    return value


def pass212_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load(PASS212_CONTRACT_PATH)
    evidence = _load(PASS212_EVIDENCE_PATH)
    successor = pass213_membrane_source_evidence()
    if contract.get("schema") != "HHS_PASS_212_CONTRACT_V1" or contract.get("pass") != 212:
        raise RuntimeError("PASS212_CONTRACT_DRIFT")
    if contract.get("contract") != "HHS-P212-FULL-HYDRATION-SUPERFRAME-COMPRESSION-PHYSICAL-ERASURE-RECOVERY-H72-H216":
        raise RuntimeError("PASS212_CONTRACT_ID_DRIFT")
    dims = contract["dimensions"]
    expected = {
        "local_hfc_leaf_bits": 5184, "local_hfc_leaf_bytes": 648,
        "g243_controls": 243, "hydration_lanes": 40, "full_leaf_count": 9720,
        "full_hydration_bits": 50388480, "full_hydration_bytes": 6298560,
        "affine_seed_bits": 19440, "affine_seed_bytes": 2430,
    }
    for key, value in expected.items():
        if dims.get(key) != value:
            raise RuntimeError("PASS212_DIMENSION_DRIFT:" + key)
    if tuple(contract.get("required_operations") or ()) != REQUIRED_OPERATIONS:
        raise RuntimeError("PASS212_OPERATION_SET_DRIFT")
    physical = contract["physical_recovery"]
    for key, value in {
        "data_shards_per_stripe": 243, "parity_shards_per_stripe": 2,
        "recoverable_erasures_per_stripe": 2, "raw_full_state_stripes": 40,
        "raw_full_state_data_shards": 9720, "raw_full_state_parity_shards": 80,
        "raw_full_state_protected_bytes": 6350400,
    }.items():
        if physical.get(key) != value:
            raise RuntimeError("PASS212_PHYSICAL_DRIFT:" + key)
    if evidence.get("schema") != "HHS_PASS_212_FULL_HYDRATION_REFERENCE_VECTORS_V1":
        raise RuntimeError("PASS212_EVIDENCE_SCHEMA_DRIFT")
    summary = evidence["suite_summary"]
    for key in (
        "arbitrary_raw_state_exact", "full_affine_state_exact", "negative_drills_pass",
        "runtime_verified", "sparse_affine_state_exact", "strict_claim_boundary_preserved",
        "two_physical_erasures_per_stripe_verified",
    ):
        if summary.get(key) is not True:
            raise RuntimeError("PASS212_EVIDENCE_DRIFT:" + key)
    affine = evidence["affine_full_hydration"]
    sparse = evidence["sparse_exception_full_hydration"]
    raw = evidence["arbitrary_full_hydration_fallback"]
    if affine.get("compressed_payload_bytes") != 2473 or affine.get("protected_storage_bytes") != 3769:
        raise RuntimeError("PASS212_AFFINE_VECTOR_DRIFT")
    if sparse.get("exception_count") != 4096 or sparse.get("compressed_payload_bytes") != 10665:
        raise RuntimeError("PASS212_SPARSE_VECTOR_DRIFT")
    if raw.get("compressed_payload_bytes") != 6298560 or raw.get("parity_shards") != 80 or raw.get("strict_compression_claim") is not False:
        raise RuntimeError("PASS212_RAW_VECTOR_DRIFT")
    runtime_text = (ROOT / PASS212_RUNTIME_PATH).read_text("utf-8")
    for token in ("class FullHydrationRecoveryRuntime", "PASS212_ERASURE_BUDGET_EXCEEDED", "PASS212_PHYSICAL_SHARD_HASH_MISMATCH"):
        if token not in runtime_text:
            raise RuntimeError("PASS212_RUNTIME_GUARD_DRIFT:" + token)
    api_text = (ROOT / PASS212_API_PATH).read_text("utf-8")
    if '/api/runtime/full-hydration-recovery' not in api_text:
        raise RuntimeError("PASS212_API_ROUTE_DRIFT")
    successor_text = (ROOT / PASS213_RECOVERY_PATH).read_text("utf-8")
    if "get_pass212_runtime" not in successor_text or "physical erasure reconstruction" not in successor_text:
        raise RuntimeError("PASS212_PASS213_SUCCESSOR_DRIFT")
    if successor["main_merge_head"] != PASS213_MAIN_MERGE_HEAD:
        raise RuntimeError("PASS212_PASS213_TERMINAL_DRIFT")
    return {"contract": contract, "evidence": evidence, "successor_pass213": successor, **FROZEN}


def pass212_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": PASS212_SURFACE_ID,
        "surface_type": "RUNTIME_SERVICE",
        "module": "hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1",
        "symbol": "FullHydrationRecoveryRuntime",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS_PASS_212_CONTRACT_V1", "HHS_PASS_212_FULL_HYDRATION_REFERENCE_VECTORS_V1"],
        "witness_schemas": ["HHS_PASS219_PASS212_RECOVERY_WITNESS_V1"],
        "validators": [PASS212_BIND_SYMBOL, "FullHydrationRecoveryRuntime.decode"],
        "guards": ["pass212_two_erasure_budget", "pass212_hash216_hash72_integrity", "pass212_strict_compression_claim_boundary", "pass212_pass213_successor_gate"],
        "rejection_codes": list(pass212_membrane_source_evidence()["contract"]["negative_behavior"]),
        "mutation_policy": "NO_CANONICAL_RUNTIME_MUTATION",
        "persistence_policy": "RECOVERABLE_PACKAGE_BYTES_ONLY",
        "boundedness_policy": "PASS_212_FULL_HYDRATION_50388480_BITS_V1",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass212_membrane_manifest() -> Dict[str, Any]:
    source = pass212_membrane_source_evidence()
    evidence = source["evidence"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": 212,
        "classification": PASS212_CLASSIFICATION,
        "pass219_c_abi_surface": PASS212_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass212FullHydrationRecovery",
        "runtime_surface": "FullHydrationRecoveryRuntime",
        "required_operations": list(REQUIRED_OPERATIONS),
        "main_merge_head": FROZEN["main_merge_head"],
        "full_hydration_bits": 50388480,
        "full_hydration_bytes": 6298560,
        "affine_seed_bytes": 2430,
        "recoverable_erasures_per_stripe": 2,
        "raw_parity_shards": 80,
        "affine_state_hash216": evidence["affine_full_hydration"]["state_hash216"],
        "raw_state_hash216": evidence["arbitrary_full_hydration_fallback"]["state_hash216"],
        "pass213_recovery_successor_bound": True,
        "pass219_new_canonical_mutation_authority": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "next_pass_to_census": 211,
    }


def preflight_pass212_membrane(*, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    pass212_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    declaration = pass212_surface_declaration()
    results = []
    for operation in REQUIRED_OPERATIONS:
        results.append(execute_surface_preflight(declaration, operation=operation, cache=decision_cache))
    return {"schema": "HHS_PASS219_PASS212_PREFLIGHT_V1", "ok": all(row["ok"] is True for row in results), "operations": results}
