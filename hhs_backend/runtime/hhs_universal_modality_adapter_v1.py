"""HHS Universal Modality Adapter v1.

One adapter contract for every Pass 050 modality.  This prevents PDF/image/audio/
code/compiler/emulator inputs from growing private truth pipelines.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional
import time
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
AUTHORITY = "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1"

def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"

def _now_ms() -> int:
    return int(time.time() * 1000)

def _list(values: Optional[Iterable[Any]]) -> List[str]:
    return sorted(dict.fromkeys(str(v) for v in (values or []) if str(v)))

from hhs_backend.runtime.hhs_modality_source_commitment_v1 import SUPPORTED_MODALITIES, build_source_commitment, validate_source_commitment

ADAPTER_SCHEMA = "HHS_UNIVERSAL_MODALITY_ADAPTER_V1"
LOSS_PROFILE_SCHEMA = "HHS_MODALITY_LOSS_PROFILE_V1"

LOSSLESS_MODALITIES = {"TEXT", "HARMONICODE_SOURCE", "CODE", "JSON", "YAML", "CSV", "BINARY", "DIRECTORY", "RUNTIME_RECEIPT", "LEDGER_FRAGMENT", "SEMANTIC_MEMORY_OBJECT", "GRAPH_OBJECT", "COMPILED_ARTIFACT", "EMULATOR_STATE"}
LOSSY_MODALITIES = {"PDF", "IMAGE", "AUDIO", "VIDEO"}

DEFAULT_PROJECTIONS = {
    "TEXT": ["TEXT_PROJECTION", "TOKEN_PROJECTION"],
    "HARMONICODE_SOURCE": ["SOURCE_TEXT_PROJECTION", "SYMBOLIC_AST_PROJECTION", "HHS_GRAPH_PROJECTION"],
    "CODE": ["SOURCE_TEXT_PROJECTION", "LANGUAGE_AST_PROJECTION"],
    "JSON": ["STRUCTURE_PROJECTION", "CANONICAL_JSON_PROJECTION"],
    "YAML": ["STRUCTURE_PROJECTION"],
    "CSV": ["TABLE_PROJECTION"],
    "PDF": ["TEXT_PROJECTION", "PAGE_IMAGE_PROJECTION", "STRUCTURE_PROJECTION"],
    "IMAGE": ["RASTER_PROJECTION", "VISUAL_FEATURE_PROJECTION", "OCR_TEXT_PROJECTION"],
    "AUDIO": ["WAVEFORM_PROJECTION", "TRANSCRIPT_PROJECTION", "HARMONIC_TIME_PROJECTION"],
    "VIDEO": ["FRAME_PROJECTION", "AUDIO_TRACK_PROJECTION", "TEMPORAL_SCENE_PROJECTION"],
    "BINARY": ["BYTE_MANIFEST_PROJECTION"],
    "DIRECTORY": ["DIRECTORY_MANIFEST_PROJECTION"],
    "RUNTIME_RECEIPT": ["RECEIPT_FIELD_PROJECTION"],
    "LEDGER_FRAGMENT": ["LEDGER_CHAIN_PROJECTION"],
    "SEMANTIC_MEMORY_OBJECT": ["SEMANTIC_RELATION_PROJECTION"],
    "GRAPH_OBJECT": ["GRAPH_TOPOLOGY_PROJECTION"],
    "COMPILED_ARTIFACT": ["ARTIFACT_METADATA_PROJECTION", "IR_PROJECTION"],
    "EMULATOR_STATE": ["STATE_REGISTER_PROJECTION", "REPLAY_TIMELINE_PROJECTION"],
}


def build_loss_profile(modality: str) -> Dict[str, Any]:
    modality = modality.upper()
    lossy = modality in LOSSY_MODALITIES
    profile = {
        "schema": LOSS_PROFILE_SCHEMA,
        "version": VERSION,
        "modality": modality,
        "loss_profile": "MIXED_LOSSLESS_AND_LOSSY" if lossy else "LOSSLESS_SOURCE_COMMITMENT_WITH_DERIVED_PROJECTIONS",
        "lossy_projection_possible": lossy,
        "source_preserved": True,
        "lossy_outputs_must_be_marked": True,
        "projection_replaces_source": False,
    }
    profile["loss_profile_hash72"] = hash72(LOSS_PROFILE_SCHEMA, profile)
    return profile


def build_universal_adapter_contract(modality: str) -> Dict[str, Any]:
    modality = modality.upper()
    projections = DEFAULT_PROJECTIONS.get(modality, ["UNRESOLVED_PROJECTION"])
    loss_profile = build_loss_profile(modality)
    contract = {
        "schema": ADAPTER_SCHEMA,
        "version": VERSION,
        "adapter_id": f"adapter:{modality.lower()}.universal_modality",
        "supported_modalities": [modality],
        "source_modality": modality,
        "input_schema": "HHS_MODALITY_SOURCE_COMMITMENT_V1",
        "output_projection_types": projections,
        "loss_profile": loss_profile["loss_profile"],
        "loss_profile_record": loss_profile,
        "chunking_policy": "ROOTED_CHUNK_MANIFEST_FOR_LARGE_SOURCES",
        "metadata_policy": "BOUNDED_TEMPORARY_EXPANDED_METADATA_COMPACTS_TO_RESIDUE",
        "witness_strategy": "HASH72_U72_SOURCE_PROJECTION_ARTIFACT_WITNESS_CHAIN",
        "reconstruction_strategy": "SOURCE_ROOT_PLUS_PROJECTION_RECIPE_PLUS_ARTIFACT_LINEAGE",
        "artifact_targets": ["WORKSPACE_OBJECT", "DERIVED_ARTIFACT", "CROSS_MODAL_TRANSFORMATION_PLAN"],
        "authority_tier": "AUTHORIZED_NONMUTATING",
        "source_preserved": True,
        "projection_replaces_source": False,
        "private_truth_pipeline_allowed": False,
        "failure_modes": [
            "REJECT_MODALITY_WITHOUT_ADAPTER_CONTRACT",
            "REJECT_PROJECTION_REPLACES_SOURCE",
            "REJECT_LOSSY_PROJECTION_UNMARKED",
            "REJECT_ADAPTER_PRIVATE_TRUTH_PIPELINE",
        ],
        "authority": AUTHORITY,
    }
    contract["adapter_contract_hash72"] = hash72(ADAPTER_SCHEMA, contract)
    return contract


def list_default_adapter_contracts() -> List[Dict[str, Any]]:
    return [build_universal_adapter_contract(m) for m in SUPPORTED_MODALITIES]


def validate_adapter_contract(contract: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    modality = str(contract.get("source_modality") or "")
    if contract.get("schema") != ADAPTER_SCHEMA:
        reasons.append("REJECT_MODALITY_WITHOUT_ADAPTER_CONTRACT")
    if modality not in SUPPORTED_MODALITIES:
        reasons.append("REJECT_UNSUPPORTED_MODALITY_APPROXIMATION")
    if not contract.get("source_preserved") or contract.get("projection_replaces_source"):
        reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    if contract.get("private_truth_pipeline_allowed"):
        reasons.append("REJECT_ADAPTER_PRIVATE_TRUTH_PIPELINE")
    if not contract.get("output_projection_types"):
        reasons.append("REJECT_MODALITY_WITHOUT_ADAPTER_CONTRACT")
    ok = not reasons
    return {
        "schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_VALIDATION_V1",
        "version": VERSION,
        "ok": ok,
        "status": "ADMIT_UNIVERSAL_MODALITY_ADAPTER" if ok else "REJECT_UNIVERSAL_MODALITY_ADAPTER",
        "reasons": sorted(dict.fromkeys(reasons)),
        "adapter_id": contract.get("adapter_id"),
        "source_modality": modality,
    }


def adapt_source(*, project_id: str, source_name: str, payload: Any, modality: str) -> Dict[str, Any]:
    contract = build_universal_adapter_contract(modality)
    validation = validate_adapter_contract(contract)
    source = build_source_commitment(project_id=project_id, source_name=source_name, payload=payload, modality=modality)
    source_validation = validate_source_commitment(source)
    result = {
        "schema": "HHS_UNIVERSAL_MODALITY_ADAPTATION_RESULT_V1",
        "version": VERSION,
        "ok": bool(validation["ok"] and source_validation["ok"]),
        "status": "ADMIT_UNIVERSAL_MODALITY_ADAPTATION" if validation["ok"] and source_validation["ok"] else "REJECT_UNIVERSAL_MODALITY_ADAPTATION",
        "adapter_contract": contract,
        "adapter_validation": validation,
        "source_commitment": source,
        "source_validation": source_validation,
        "source_never_replaced_by_projection": True,
    }
    result["adaptation_root_hash72"] = hash72("HHS_UNIVERSAL_MODALITY_ADAPTATION_RESULT_V1", result)
    return result


def universal_modality_adapter_self_test() -> Dict[str, Any]:
    contracts = list_default_adapter_contracts()
    validations = [validate_adapter_contract(c) for c in contracts]
    image = adapt_source(project_id="project:pass050", source_name="glyph.png", payload="PNG", modality="IMAGE")
    bad = dict(build_universal_adapter_contract("TEXT"), private_truth_pipeline_allowed=True)
    bad_validation = validate_adapter_contract(bad)
    return {
        "schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(all(v["ok"] for v in validations) and image["ok"] and not bad_validation["ok"]),
        "adapter_count": len(contracts),
        "modalities": [c["source_modality"] for c in contracts],
        "image_adaptation": image,
        "private_truth_pipeline_rejection": bad_validation,
        "doctrine": "NO_MODALITY_OWNS_A_PRIVATE_TRUTH_PIPELINE",
    }

if __name__ == "__main__":
    import json
    print(json.dumps(universal_modality_adapter_self_test(), indent=2, sort_keys=True, default=str))
