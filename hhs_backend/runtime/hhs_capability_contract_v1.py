"""HHS Capability Contract v1."""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping, Optional
import uuid, time
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "PASS_051_RUNTIME_CANONICAL_OBSERVER_CAPABILITY_PROVIDER_FABRIC_V1"
AUTHORITY = "HHS_RUNTIME_CANONICAL_OBSERVER_AUTHORITY_V1"
CAPABILITY_CONTRACT_SCHEMA = "HHS_CAPABILITY_CONTRACT_V1"
CAPABILITY_CLASSES = ["TEXT_GENERATION","TEXT_EMBEDDING","OCR","IMAGE_ANALYSIS","IMAGE_GENERATION","SPEECH_TO_TEXT","TEXT_TO_SPEECH","AUDIO_ANALYSIS","VIDEO_DECODING","CODE_ANALYSIS","CODE_EXECUTION","DOCUMENT_EXTRACTION","GRAPH_ANALYSIS","SEARCH","MEMORY_RETRIEVAL","COMPILATION","EMULATION"]
DEFAULT_OUTPUT_MODALITY = {"TEXT_GENERATION":"TEXT","TEXT_EMBEDDING":"SEMANTIC_MEMORY_OBJECT","OCR":"TEXT","IMAGE_ANALYSIS":"GRAPH_OBJECT","IMAGE_GENERATION":"IMAGE","SPEECH_TO_TEXT":"TEXT","TEXT_TO_SPEECH":"AUDIO","AUDIO_ANALYSIS":"GRAPH_OBJECT","VIDEO_DECODING":"VIDEO","CODE_ANALYSIS":"GRAPH_OBJECT","CODE_EXECUTION":"RUNTIME_RECEIPT","DOCUMENT_EXTRACTION":"TEXT","GRAPH_ANALYSIS":"GRAPH_OBJECT","SEARCH":"SEMANTIC_MEMORY_OBJECT","MEMORY_RETRIEVAL":"SEMANTIC_MEMORY_OBJECT","COMPILATION":"COMPILED_ARTIFACT","EMULATION":"EMULATOR_STATE"}

def _list(values: Optional[Iterable[Any]]) -> List[str]:
    return sorted(dict.fromkeys(str(v) for v in (values or []) if str(v)))

def build_capability_contract(capability_class: str, *, input_modalities: Optional[Iterable[str]] = None, output_modality: str = "") -> Dict[str, Any]:
    cap = str(capability_class).upper()
    contract = {"schema": CAPABILITY_CONTRACT_SCHEMA, "version": VERSION, "capability_id": f"capability:{cap.lower()}", "capability_class": cap, "input_modalities": _list(input_modalities) or ["TEXT"], "output_modality": output_modality or DEFAULT_OUTPUT_MODALITY.get(cap, "TEXT"), "provider_owns_capability_identity": False, "capability_grants_execution_authority": False, "raw_provider_output_is_canonical": False, "raw_result_must_reenter_universal_modality_pipeline": True, "mutating_capability_requires_explicit_authority_admission": True, "authority_tier": "AUTHORIZED_NONMUTATING" if cap not in {"CODE_EXECUTION","EMULATION"} else "REQUIRES_EXPLICIT_MUTATION_ADMISSION", "authority": AUTHORITY}
    contract["capability_contract_hash72"] = hash72(CAPABILITY_CONTRACT_SCHEMA, contract)
    return contract

def validate_capability_contract(contract: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if contract.get("schema") != CAPABILITY_CONTRACT_SCHEMA: reasons.append("REJECT_PROVIDER_WITHOUT_CAPABILITY_CONTRACT")
    if contract.get("capability_class") not in CAPABILITY_CLASSES: reasons.append("REJECT_UNREGISTERED_CAPABILITY")
    if contract.get("provider_owns_capability_identity") or contract.get("capability_grants_execution_authority"): reasons.append("REJECT_PROVIDER_SELF_AUTHORIZATION")
    if contract.get("raw_provider_output_is_canonical"): reasons.append("REJECT_RAW_PROVIDER_OUTPUT_AS_CANONICAL_SOURCE")
    return {"schema":"HHS_CAPABILITY_CONTRACT_VALIDATION_V1", "version": VERSION, "ok": not reasons, "status": "ADMIT_CAPABILITY_CONTRACT" if not reasons else "REJECT_CAPABILITY_CONTRACT", "reasons": sorted(dict.fromkeys(reasons)), "capability_id": contract.get("capability_id"), "capability_class": contract.get("capability_class")}

def list_capability_contracts() -> List[Dict[str, Any]]:
    return [build_capability_contract(c) for c in CAPABILITY_CLASSES]

def capability_contract_self_test() -> Dict[str, Any]:
    contracts = list_capability_contracts(); validations=[validate_capability_contract(c) for c in contracts]
    bad = dict(build_capability_contract("OCR"), provider_owns_capability_identity=True)
    return {"schema":"HHS_CAPABILITY_CONTRACT_SELF_TEST_V1", "version": VERSION, "ok": bool(all(v["ok"] for v in validations) and not validate_capability_contract(bad)["ok"]), "capability_count": len(contracts), "capability_classes": list(CAPABILITY_CLASSES), "doctrine":"provider != capability; capability != authority"}
if __name__ == "__main__":
    import json; print(json.dumps(capability_contract_self_test(), indent=2, sort_keys=True, default=str))
