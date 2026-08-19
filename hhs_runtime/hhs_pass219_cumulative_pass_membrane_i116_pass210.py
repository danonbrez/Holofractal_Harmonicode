"""Pass 219 I116 inherited Pass 210 holographic-frame-compression membrane."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass211 import pass211_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS210_NUMBER = 210
PASS210_CLASSIFICATION = "WIRED"
PASS210_BIND_SYMBOL = "hhs_exact_pass219_bind_pass210_holographic_frame_compression"
PASS210_SURFACE_ID = "runtime:pass210.holographic-frame-compression"
PASS210_CONTRACT_PATH = Path("contracts/pass210/PASS_210_CONTRACT.json")
PASS210_EVIDENCE_PATH = Path("evidence/pass210/PASS_210_HFC_REFERENCE_VECTORS.json")
PASS210_RUNTIME_PATH = Path("hhs_backend/runtime/hhs_pass210_holographic_frame_compression_v1.py")
PASS210_API_PATH = Path("hhs_backend/api/pass210_holographic_frame_compression_routes.py")
PASS211_CONTRACT_PATH = Path("contracts/pass211/PASS_211_CONTRACT.json")
PASS211_RUNTIME_PATH = Path("hhs_backend/runtime/hhs_pass211_bigint_hfc_carrier_v1.py")

REQUIRED_OPERATIONS = (
    "hfc_frame_encode",
    "hfc_frame_decode",
    "hfc_snapshot",
    "hfc_section",
    "hfc_matrix",
    "hfc_view_admit",
    "hfc_project",
    "hfc_agree",
    "hfc_recover",
    "hfc_strict_compress",
    "hfc_strict_decompress",
)

FROZEN = {
    "validated_branch_head": "0d1433d30f9fe811dc42a3155afeafa089aa72ff",
    "main_merge_head": "a8cd64e76828fd911e7e6e27ffd9ad02c7d74355",
    "branch_validation_run": 30994827355,
    "main_validation_run": 30994901959,
    "contract_blob": "ac46a61f568b0443794f854cf84e5a3cfc1bf908",
    "restart_blob": "3dee1ac8eb16a9bd151514ddbc4490b51d6d1df8",
    "runtime_blob": "bb85330627cd58a1cb57ab47f3d5520d8b1157b1",
    "api_blob": "6569f8f689ab48aa4239e0e2214ec1d27485dd35",
    "evidence_blob": "221afe26a8d9fd5ddc475c60e2a516aad414d7cd",
    "validation_blob": "939cdc583f3f245282c80217fcc1b132d2471783",
    "pass211_contract_blob": "685c6d1544cbae6966e84c0d05b6bf4b8687d903",
    "pass211_runtime_blob": "0d11f3607c81b442b76dcd455b5c47450c9ed7e9",
}


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads((ROOT / path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PASS210_OBJECT_REQUIRED")
    return value


def pass210_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load(PASS210_CONTRACT_PATH)
    evidence = _load(PASS210_EVIDENCE_PATH)
    successor_contract = _load(PASS211_CONTRACT_PATH)
    successor = pass211_membrane_source_evidence()
    if contract.get("schema") != "HHS_PASS_210_HOLOGRAPHIC_FRAME_COMPRESSION_CONTRACT_V1" or contract.get("pass") != 210:
        raise RuntimeError("PASS210_CONTRACT_DRIFT")
    if contract.get("contract_identifier") != "HHS-P210-HFC-VM81-H72-H216":
        raise RuntimeError("PASS210_CONTRACT_ID_DRIFT")
    constants = contract.get("constants") or {}
    expected = {
        "REGISTER_LEN": 5184,
        "GRID_LO_SHU": 81,
        "LINE_BYTES": 64,
        "HASH72_LEN": 72,
        "SNAPSHOT_WIDTH": 288,
        "SNAPSHOT_STRIDE": 144,
        "SNAPSHOT_COUNT": 36,
        "SECTION_PHI_HI": 89,
        "SECTION_PHI_LO": 55,
        "MATRIX_DIM": 12,
    }
    for key, value in expected.items():
        if constants.get(key) != value:
            raise RuntimeError("PASS210_CONSTANT_DRIFT:" + key)
    if tuple(contract.get("operations") or ()) != REQUIRED_OPERATIONS:
        raise RuntimeError("PASS210_OPERATION_SET_DRIFT")
    if contract.get("floating_point_policy") != "NO_FLOAT_CANONICAL_AUTHORITY":
        raise RuntimeError("PASS210_NUMERIC_AUTHORITY_DRIFT")
    digest = contract.get("digest_decode_boundary") or {}
    if digest.get("hash72_digest_alone_reversible") is not False or digest.get("hash216_digest_alone_reversible") is not False:
        raise RuntimeError("PASS210_DIGEST_BOUNDARY_DRIFT")
    compression = contract.get("compression_claim") or {}
    if compression.get("implemented_admissible_subset") != "HFC_ADMISSIBLE_AFFINE_FIBONACCI_MOD2_V1":
        raise RuntimeError("PASS210_STRICT_DOMAIN_DRIFT")
    if evidence.get("schema") != "HHS_PASS_210_HFC_COMPLETION_EVIDENCE_V1" or evidence.get("runtime_classification") != "HHS_PASS_210_HOLOGRAPHIC_FRAME_COMPRESSION_RUNTIME_VERIFIED":
        raise RuntimeError("PASS210_EVIDENCE_CLASSIFICATION_DRIFT")
    if evidence.get("canonical_float_authority") is not False:
        raise RuntimeError("PASS210_FLOAT_EVIDENCE_DRIFT")
    invariants = evidence.get("invariants") or {}
    if len(invariants) != 10 or not all(invariants.get(f"HFC-I{i}") is True for i in range(1, 11)):
        raise RuntimeError("PASS210_INVARIANT_EVIDENCE_DRIFT")
    erasures = evidence.get("erasure_drills") or []
    if len(erasures) != 36 or not all(row.get("recovered_sha256") == "26232cd54a39e54a9bf9a71cdceebb92133c3787e218b15778783b9b0c16e8ea" for row in erasures):
        raise RuntimeError("PASS210_ERASURE_EVIDENCE_DRIFT")
    corruption = evidence.get("corruption_drills") or []
    if [row.get("modality") for row in corruption] != ["raw", "hash72", "hash216", "phase", "frame"] or not all(row.get("repair_performed") is False for row in corruption):
        raise RuntimeError("PASS210_CORRUPTION_EVIDENCE_DRIFT")
    agreement = evidence.get("clean_multimodal_agreement") or {}
    if agreement.get("agreement") is not True or agreement.get("reference_hash216") != "8997ab0f9c3aaa3b0d158c2855788042c7904060cf51b6f020bec4b25400567b":
        raise RuntimeError("PASS210_AGREEMENT_DRIFT")
    strict = evidence.get("strict_compression") or {}
    package = strict.get("package") or {}
    witness = package.get("admissible_domain_witness") or {}
    if strict.get("canonical_register_bytes") != 5184 or package.get("register_hash216") != "02d1610350a72bace2d05cdb6447d30bd6492dd53c1ae12ecfdce5fedae7b25f":
        raise RuntimeError("PASS210_STRICT_VECTOR_DRIFT")
    if witness.get("domain") != "HFC_ADMISSIBLE_AFFINE_FIBONACCI_MOD2_V1" or package.get("admissible_domain_witness_hash216") != "0832b78e97f63692ad0036d39395124139b563609e6e713a231642fdfcba6258":
        raise RuntimeError("PASS210_STRICT_WITNESS_DRIFT")
    if evidence.get("full_session_receipt_count") != 47 or evidence.get("full_session_receipt_head_hash72") != "7TBLHLh0!9wHuBvCLeNCGyitXUagjDP8colu+WxSD7(f?nR4wCqyf)Fgc+Ct22YWV6uS8yQk":
        raise RuntimeError("PASS210_RECEIPT_CLOSURE_DRIFT")
    runtime_text = (ROOT / PASS210_RUNTIME_PATH).read_text("utf-8")
    for token in ("class HolographicFrameCompressionRuntime", "HFC_STRICT_COMPRESSION_DOMAIN_WITNESS_REQUIRED", "HFC_NON_BIJECTIVE_VIEW_REJECTED"):
        if token not in runtime_text:
            raise RuntimeError("PASS210_RUNTIME_GUARD_DRIFT:" + token)
    api_text = (ROOT / PASS210_API_PATH).read_text("utf-8")
    if "/api/runtime/holographic-frame-compression" not in api_text:
        raise RuntimeError("PASS210_API_ROUTE_DRIFT")
    if successor_contract.get("schema") != "HHS_PASS_211_CONTRACT_V1" or "HHS-P210-HFC-VM81-H72-H216" not in (successor_contract.get("inherits") or []):
        raise RuntimeError("PASS210_PASS211_SUCCESSOR_DRIFT")
    successor_runtime_text = (ROOT / PASS211_RUNTIME_PATH).read_text("utf-8")
    if "hhs_pass210_holographic_frame_compression_v1" not in successor_runtime_text:
        raise RuntimeError("PASS210_PASS211_RUNTIME_DRIFT")
    if successor.get("contract", {}).get("pass") != 211:
        raise RuntimeError("PASS210_PASS211_MEMBRANE_DRIFT")
    return {"contract": contract, "evidence": evidence, "successor_pass211": successor, **FROZEN}


def pass210_surface_declaration() -> Dict[str, Any]:
    source = pass210_membrane_source_evidence()
    return {
        "surface_id": PASS210_SURFACE_ID,
        "surface_type": "RUNTIME_SERVICE",
        "module": "hhs_backend.runtime.hhs_pass210_holographic_frame_compression_v1",
        "symbol": "HolographicFrameCompressionRuntime",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS_PASS_210_HOLOGRAPHIC_FRAME_COMPRESSION_CONTRACT_V1", "HHS_PASS_210_HFC_COMPLETION_EVIDENCE_V1"],
        "witness_schemas": ["HHS_PASS219_PASS210_HFC_WITNESS_V1"],
        "validators": [PASS210_BIND_SYMBOL, "HolographicFrameCompressionRuntime.frame_decode", "HolographicFrameCompressionRuntime.agree"],
        "guards": ["pass210_double_witness_coverage", "pass210_digest_decode_boundary", "pass210_strict_domain_witness", "pass210_pass211_successor_gate"],
        "rejection_codes": list((source["contract"].get("negative_cases") or {}).values()),
        "mutation_policy": "NO_NEW_PASS219_CANONICAL_RUNTIME_MUTATION",
        "persistence_policy": "ORDERED_HASH72_RECEIPT_LEDGER_AND_ADDRESSED_WITNESSES",
        "boundedness_policy": "PASS_210_REGISTER_5184_SNAPSHOTS_36_V1",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass210_membrane_manifest() -> Dict[str, Any]:
    source = pass210_membrane_source_evidence()
    evidence = source["evidence"]
    strict = evidence["strict_compression"]["package"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS210_NUMBER,
        "classification": PASS210_CLASSIFICATION,
        "pass219_c_abi_surface": PASS210_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass210HolographicFrameCompression",
        "runtime_surface": "HolographicFrameCompressionRuntime",
        "required_operations": list(REQUIRED_OPERATIONS),
        "main_merge_head": FROZEN["main_merge_head"],
        "register_len": 5184,
        "snapshot_count": 36,
        "snapshot_width": 288,
        "snapshot_stride": 144,
        "reference_register_hash216": evidence["reference_register"]["register_hash216"],
        "strict_register_hash216": strict["register_hash216"],
        "strict_domain": strict["admissible_domain_witness"]["domain"],
        "pass211_successor_bound": True,
        "pass219_new_canonical_mutation_authority": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "next_pass_to_census": 209,
    }


def preflight_pass210_membrane(*, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    pass210_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    declaration = pass210_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation, cache=decision_cache) for operation in REQUIRED_OPERATIONS]
    return {"schema": "HHS_PASS219_PASS210_PREFLIGHT_V1", "ok": all(row.get("ok") is True for row in rows), "operations": rows}
