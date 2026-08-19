"""Pass 219 I116 inherited Pass 211 BigInt/HFC carrier membrane."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass212 import pass212_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS211_NUMBER = 211
PASS211_CLASSIFICATION = "WIRED"
PASS211_BIND_SYMBOL = "hhs_exact_pass219_bind_pass211_bigint_hfc_carrier"
PASS211_SURFACE_ID = "runtime:pass211.bigint-hfc-carrier"
PASS211_CONTRACT_PATH = Path("contracts/pass211/PASS_211_CONTRACT.json")
PASS211_EVIDENCE_PATH = Path("evidence/pass211/PASS_211_BIGINT_HFC_REFERENCE_VECTORS.json")
PASS211_RUNTIME_PATH = Path("hhs_backend/runtime/hhs_pass211_bigint_hfc_carrier_v1.py")
PASS211_API_PATH = Path("hhs_backend/api/pass211_bigint_hfc_routes.py")
PASS212_CONTRACT_PATH = Path("contracts/pass212/PASS_212_CONTRACT.json")

REQUIRED_OPERATIONS = (
    "pass211_encode_bigint(ciphertext)",
    "pass211_decode_bigint(package)",
    "pass211_recover_shard(package, shard_index, lost_snapshot_index)",
    "pass211_anchored_compare(package, shard_index, fresh_payload)",
    "packed_bytes_to_register(payload)",
    "register_to_packed_bytes(register, payload_bit_length)",
)

FROZEN = {
    "validated_branch_head": "5c877eeae86e1fd929e30a2c418f705f12921265",
    "main_merge_head": "b80759e60bd78357d9d650aa23c99460f3952fd3",
    "branch_validation_run": 31005616936,
    "main_validation_run": 31005763191,
    "contract_blob": "685c6d1544cbae6966e84c0d05b6bf4b8687d903",
    "restart_blob": "7065102a60501c797407fe7a40cdf760ab6a11b3",
    "runtime_blob": "0d11f3607c81b442b76dcd455b5c47450c9ed7e9",
    "api_blob": "a3df09c2593fc0c3d1c331b103b86826cb1a7084",
    "evidence_blob": "fa8807d66a28a5e38c0294cdac34e214dc39a8b6",
    "validation_blob": "4ae19dab0dd9d0b70398b6b433f92e799a6baf38",
    "pass212_contract_blob": "12f2c577e02f4436ee776366a1994ece5a765fca",
}


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads((ROOT / path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PASS211_OBJECT_REQUIRED")
    return value


def pass211_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load(PASS211_CONTRACT_PATH)
    evidence = _load(PASS211_EVIDENCE_PATH)
    successor_contract = _load(PASS212_CONTRACT_PATH)
    successor = pass212_membrane_source_evidence()
    if contract.get("schema") != "HHS_PASS_211_CONTRACT_V1" or contract.get("pass") != 211:
        raise RuntimeError("PASS211_CONTRACT_DRIFT")
    if contract.get("contract") != "HHS-P211-P133-BIGINT-HFC-MULTIREGISTER-H72-H216":
        raise RuntimeError("PASS211_CONTRACT_ID_DRIFT")
    constants = contract.get("constants") or {}
    expected_constants = {
        "hfc_register_boolean_cells": 5184,
        "packed_shard_bytes": 648,
        "snapshot_count": 36,
        "snapshot_width": 288,
        "snapshot_stride": 144,
        "maximum_shards": 4096,
    }
    for key, value in expected_constants.items():
        if constants.get(key) != value:
            raise RuntimeError("PASS211_CONSTANT_DRIFT:" + key)
    if tuple(contract.get("required_operations") or ()) != REQUIRED_OPERATIONS:
        raise RuntimeError("PASS211_OPERATION_SET_DRIFT")
    boundary = contract.get("compression_claim_boundary") or {}
    if "HFC_ADMISSIBLE_AFFINE_FIBONACCI_MOD2_V1" not in str(boundary.get("domain_restricted") or ""):
        raise RuntimeError("PASS211_STRICT_DOMAIN_BOUNDARY_DRIFT")
    if evidence.get("schema") != "HHS_PASS_211_BIGINT_HFC_REFERENCE_EVIDENCE_V1":
        raise RuntimeError("PASS211_EVIDENCE_SCHEMA_DRIFT")
    if evidence.get("runtime_classification") != "HHS_PASS_211_BIGINT_HFC_CARRIER_RUNTIME_VERIFIED":
        raise RuntimeError("PASS211_RUNTIME_CLASSIFICATION_DRIFT")
    corpus = evidence.get("pass133_independent_corpus") or []
    if len(corpus) != 11 or not all(row.get("roundtrip_exact") is True for row in corpus):
        raise RuntimeError("PASS211_PASS133_CORPUS_DRIFT")
    stress = evidence.get("pass133_stress") or []
    if sum(int(row.get("single_bit_corrected") or 0) for row in stress) != 512 or not all(row.get("double_error_fail_closed") is True for row in stress):
        raise RuntimeError("PASS211_PASS133_STRESS_DRIFT")
    erasures = evidence.get("single_snapshot_erasure_events") or []
    if len(erasures) != 144 or not all(row.get("status") == "PASS211_SHARD_ERASURE_RECOVERY_VERIFIED" for row in erasures):
        raise RuntimeError("PASS211_ERASURE_EVIDENCE_DRIFT")
    replay = evidence.get("deterministic_replay") or {}
    if replay.get("equal") is not True or replay.get("package_root216") != "2a87ecd5755a5bd22801b0b4f528b5edfbd442c8616f1bfde2a204d652ecdee2":
        raise RuntimeError("PASS211_REPLAY_DRIFT")
    multireg = evidence.get("multi_register_boundary") or {}
    if multireg.get("source_bit_length") != 1024 or multireg.get("carrier_byte_length") != 811 or multireg.get("shard_count") != 2 or multireg.get("shard_payload_byte_lengths") != [648, 163]:
        raise RuntimeError("PASS211_MULTIREGISTER_DRIFT")
    anchored = evidence.get("anchored_corruption_drill") or {}
    if anchored.get("disagreement_cells") != [1000] or anchored.get("fresh_projection_self_consistency_is_not_historical_integrity") is not True:
        raise RuntimeError("PASS211_ANCHORED_INTEGRITY_DRIFT")
    negatives = evidence.get("negative_cases") or {}
    for key in ("missing_shard", "duplicate_shard", "reordered_shards", "substituted_shard", "zero", "negative"):
        if key not in negatives:
            raise RuntimeError("PASS211_NEGATIVE_EVIDENCE_DRIFT:" + key)
    runtime_text = (ROOT / PASS211_RUNTIME_PATH).read_text("utf-8")
    for token in ("class Pass211BigIntHFCRuntime", "PASS211_SHARD_SUBSTITUTION_DETECTED", "PASS211_NONZERO_REGISTER_PADDING", "STRICT_DOMAIN_REJECTED"):
        if token not in runtime_text:
            raise RuntimeError("PASS211_RUNTIME_GUARD_DRIFT:" + token)
    api_text = (ROOT / PASS211_API_PATH).read_text("utf-8")
    if "/api/runtime/bigint-hfc-carrier" not in api_text:
        raise RuntimeError("PASS211_API_ROUTE_DRIFT")
    if successor_contract.get("schema") != "HHS_PASS_212_CONTRACT_V1" or contract["contract"] not in (successor_contract.get("inherits") or []):
        raise RuntimeError("PASS211_PASS212_SUCCESSOR_DRIFT")
    if successor.get("contract", {}).get("pass") != 212:
        raise RuntimeError("PASS211_PASS212_MEMBRANE_DRIFT")
    return {"contract": contract, "evidence": evidence, "successor_pass212": successor, **FROZEN}


def pass211_surface_declaration() -> Dict[str, Any]:
    source = pass211_membrane_source_evidence()
    return {
        "surface_id": PASS211_SURFACE_ID,
        "surface_type": "RUNTIME_SERVICE",
        "module": "hhs_backend.runtime.hhs_pass211_bigint_hfc_carrier_v1",
        "symbol": "Pass211BigIntHFCRuntime",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS_PASS_211_CONTRACT_V1", "HHS_PASS_211_BIGINT_HFC_REFERENCE_EVIDENCE_V1"],
        "witness_schemas": ["HHS_PASS219_PASS211_BIGINT_HFC_WITNESS_V1"],
        "validators": [PASS211_BIND_SYMBOL, "Pass211BigIntHFCRuntime.decode"],
        "guards": ["pass211_exact_shard_order", "pass211_minted_anchor_integrity", "pass211_strict_compression_claim_boundary", "pass211_pass212_successor_gate"],
        "rejection_codes": list(source["contract"].get("negative_behavior") or []),
        "mutation_policy": "NO_CANONICAL_RUNTIME_MUTATION",
        "persistence_policy": "AUTHENTICATED_PACKAGE_WITNESSES_ONLY",
        "boundedness_policy": "PASS_211_MAXIMUM_4096_HFC_SHARDS_V1",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass211_membrane_manifest() -> Dict[str, Any]:
    source = pass211_membrane_source_evidence()
    evidence = source["evidence"]
    replay = evidence["deterministic_replay"]
    multireg = evidence["multi_register_boundary"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS211_NUMBER,
        "classification": PASS211_CLASSIFICATION,
        "pass219_c_abi_surface": PASS211_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass211BigIntHFCCarrier",
        "runtime_surface": "Pass211BigIntHFCRuntime",
        "required_operations": list(REQUIRED_OPERATIONS),
        "main_merge_head": FROZEN["main_merge_head"],
        "packed_shard_bytes": 648,
        "snapshot_count": 36,
        "multiregister_shard_count": multireg["shard_count"],
        "deterministic_package_root216": replay["package_root216"],
        "deterministic_package_receipt_hash72": replay["package_receipt_hash72"],
        "pass212_successor_bound": True,
        "pass219_new_canonical_mutation_authority": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "next_pass_to_census": 210,
    }


def preflight_pass211_membrane(*, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    pass211_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    declaration = pass211_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation, cache=decision_cache) for operation in REQUIRED_OPERATIONS]
    return {"schema": "HHS_PASS219_PASS211_PREFLIGHT_V1", "ok": all(row.get("ok") is True for row in rows), "operations": rows}
