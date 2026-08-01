"""HHS Capability Provider Registry v1."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import (
    VERSION,
    AUTHORITY,
    CAPABILITY_CLASSES,
    build_capability_contract,
    validate_capability_contract,
)

PROVIDER_SCHEMA = "HHS_CAPABILITY_PROVIDER_RECORD_V1"
REGISTRY_SCHEMA = "HHS_CAPABILITY_PROVIDER_REGISTRY_V1"
LITERT_LM_PROVIDER_ID = "provider:hhs.litert_lm.gemma4"
KIMI_K3_PROVIDER_ID = "provider:hhs.moonshot.kimi_k3"


def build_provider_record(
    *,
    provider_id: str,
    provider_name: str,
    capability_classes: Iterable[str],
    provider_kind: str = "LOCAL_STUB_PROVIDER",
    output_modality: str = "",
) -> Dict[str, Any]:
    caps = [str(c).upper() for c in capability_classes]
    contracts = [
        build_capability_contract(
            c,
            output_modality=output_modality if len(caps) == 1 else "",
        )
        for c in caps
    ]
    provider = {
        "schema": PROVIDER_SCHEMA,
        "version": VERSION,
        "provider_id": provider_id,
        "provider_name": provider_name,
        "provider_kind": provider_kind,
        "capability_classes": caps,
        "capability_contracts": contracts,
        "provider_is_canonical_authority": False,
        "provider_self_authorizes": False,
        "provider_output_replaces_source": False,
        "private_truth_pipeline_allowed": False,
        "result_ingress_required": True,
        "authority_scope": "PROVIDE_RAW_RESULT_ONLY",
        "authority": AUTHORITY,
    }
    provider["provider_root_hash72"] = hash72(PROVIDER_SCHEMA, provider)
    return provider


def validate_provider_record(provider: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if provider.get("schema") != PROVIDER_SCHEMA:
        reasons.append("REJECT_PROVIDER_WITHOUT_CAPABILITY_CONTRACT")
    if provider.get("provider_is_canonical_authority"):
        reasons.append("REJECT_PROVIDER_AS_CANONICAL_AUTHORITY")
    if provider.get("provider_self_authorizes"):
        reasons.append("REJECT_PROVIDER_SELF_AUTHORIZATION")
    if provider.get("private_truth_pipeline_allowed"):
        reasons.append("REJECT_PROVIDER_PRIVATE_TRUTH_PIPELINE")
    if provider.get("provider_output_replaces_source"):
        reasons.append("REJECT_RAW_PROVIDER_OUTPUT_AS_CANONICAL_SOURCE")
    contracts = list(provider.get("capability_contracts") or [])
    if not contracts:
        reasons.append("REJECT_PROVIDER_WITHOUT_CAPABILITY_CONTRACT")
    for contract in contracts:
        validation = validate_capability_contract(contract)
        if not validation["ok"]:
            reasons.extend(validation["reasons"])
    for capability in provider.get("capability_classes") or []:
        if capability not in CAPABILITY_CLASSES:
            reasons.append("REJECT_UNREGISTERED_CAPABILITY")
    return {
        "schema": "HHS_CAPABILITY_PROVIDER_VALIDATION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": (
            "ADMIT_CAPABILITY_PROVIDER"
            if not reasons
            else "REJECT_CAPABILITY_PROVIDER"
        ),
        "reasons": sorted(dict.fromkeys(reasons)),
        "provider_id": provider.get("provider_id"),
        "capability_classes": provider.get("capability_classes", []),
    }


def build_default_provider_registry() -> Dict[str, Any]:
    providers = [
        build_provider_record(
            provider_id=LITERT_LM_PROVIDER_ID,
            provider_name="HHS LiteRT-LM Gemma 4 Conversational Provider",
            capability_classes=["TEXT_GENERATION"],
            provider_kind="LITERT_LM_OPENAI_COMPATIBLE_LOCAL_PROVIDER",
            output_modality="TEXT",
        ),
        build_provider_record(
            provider_id=KIMI_K3_PROVIDER_ID,
            provider_name="Moonshot Kimi K3 Multimodal Content Planning Provider",
            capability_classes=[
                "TEXT_GENERATION",
                "IMAGE_ANALYSIS",
                "VIDEO_DECODING",
                "CODE_ANALYSIS",
                "GRAPH_ANALYSIS",
            ],
            provider_kind="MOONSHOT_KIMI_K3_OPENAI_COMPATIBLE_EXTERNAL_PROVIDER",
        ),
        build_provider_record(
            provider_id="provider:hhs.local.text",
            provider_name="HHS Local Text Provider",
            capability_classes=[
                "TEXT_GENERATION",
                "TEXT_EMBEDDING",
                "SEARCH",
                "MEMORY_RETRIEVAL",
            ],
        ),
        build_provider_record(
            provider_id="provider:hhs.local.document",
            provider_name="HHS Local Document Provider",
            capability_classes=["OCR", "DOCUMENT_EXTRACTION"],
        ),
        build_provider_record(
            provider_id="provider:hhs.local.media",
            provider_name="HHS Local Media Provider",
            capability_classes=[
                "IMAGE_ANALYSIS",
                "AUDIO_ANALYSIS",
                "VIDEO_DECODING",
                "SPEECH_TO_TEXT",
                "TEXT_TO_SPEECH",
            ],
        ),
        build_provider_record(
            provider_id="provider:hhs.local.code",
            provider_name="HHS Local Code Provider",
            capability_classes=[
                "CODE_ANALYSIS",
                "CODE_EXECUTION",
                "COMPILATION",
                "EMULATION",
                "GRAPH_ANALYSIS",
            ],
        ),
        build_provider_record(
            provider_id="provider:hhs.local.image_gen",
            provider_name="HHS Local Image Proposal Provider",
            capability_classes=["IMAGE_GENERATION"],
            output_modality="IMAGE",
        ),
    ]
    validations = [validate_provider_record(provider) for provider in providers]
    registry = {
        "schema": REGISTRY_SCHEMA,
        "version": VERSION,
        "providers": providers,
        "provider_count": len(providers),
        "capability_count": len(CAPABILITY_CLASSES),
        "validations": validations,
        "provider_private_truth_pipeline_allowed": False,
        "authority": AUTHORITY,
    }
    registry["provider_registry_root_hash72"] = hash72(REGISTRY_SCHEMA, registry)
    return registry


def capability_provider_registry_self_test() -> Dict[str, Any]:
    registry = build_default_provider_registry()
    bad = dict(registry["providers"][0], provider_self_authorizes=True)
    selected_text_provider = sorted(
        provider["provider_id"]
        for provider in registry["providers"]
        if "TEXT_GENERATION" in provider["capability_classes"]
    )[0]
    kimi_provider = next(
        provider
        for provider in registry["providers"]
        if provider["provider_id"] == KIMI_K3_PROVIDER_ID
    )
    return {
        "schema": "HHS_CAPABILITY_PROVIDER_REGISTRY_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(
            all(validation["ok"] for validation in registry["validations"])
            and not validate_provider_record(bad)["ok"]
            and selected_text_provider == LITERT_LM_PROVIDER_ID
            and "IMAGE_ANALYSIS" in kimi_provider["capability_classes"]
            and not kimi_provider["provider_is_canonical_authority"]
        ),
        "registry": registry,
        "bad_validation": validate_provider_record(bad),
        "selected_text_provider": selected_text_provider,
        "kimi_k3_provider_id": KIMI_K3_PROVIDER_ID,
        "doctrine":
            "provider output returns through Runtime ingress before canonical identity",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(
        capability_provider_registry_self_test(),
        indent=2,
        sort_keys=True,
        default=str,
    ))
