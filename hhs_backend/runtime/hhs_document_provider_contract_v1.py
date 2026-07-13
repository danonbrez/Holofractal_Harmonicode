"""HHS Document Provider Contract v1.

Pass 052 establishes document perception providers as non-canonical observers.
Providers may observe PDF/image/document regions, but their outputs remain typed
projections that must re-enter the Runtime canonical observer and Pass 050
universal modality pipeline before they can participate in workspace state.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional
import time
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_runtime_canonical_observer_v1 import (
    AUTHORITY as OBSERVER_AUTHORITY,
    observe_external_surface,
    admit_runtime_identity,
)
from hhs_backend.runtime.hhs_capability_resolution_v1 import resolve_capability
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import build_provider_execution_proposal
from hhs_backend.runtime.hhs_capability_policy_gate_v1 import evaluate_capability_policy_gate

VERSION = "PASS_052_DEEP_DETERMINISTIC_DOCUMENT_PERCEPTION_V1"
AUTHORITY = "HHS_DOCUMENT_PERCEPTION_RUNTIME_AUTHORITY_V1"
CONTRACT_SCHEMA = "HHS_DOCUMENT_PROVIDER_CONTRACT_V1"

DOCUMENT_CAPABILITIES = [
    "DOCUMENT_EXTRACTION",
    "OCR",
    "IMAGE_ANALYSIS",
]

DOCUMENT_MODALITIES = ["PDF", "IMAGE", "DOCUMENT", "BINARY"]

PROJECTION_TYPES = [
    "PDF_NATIVE_TEXT_PROJECTION",
    "PAGE_LAYOUT_PROJECTION",
    "PAGE_IMAGE_REGION_PROJECTION",
    "OCR_TEXT_PROJECTION",
    "TABLE_PROJECTION",
    "DOCUMENT_GRAPH_PROJECTION",
    "DOCUMENT_STRUCTURE_FUSION_RECORD",
    "DOCUMENT_AMBIGUITY_RECORD",
]

REJECTION_CODES = [
    "REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY",
    "REJECT_OCR_TEXT_AS_DOCUMENT_SOURCE",
    "REJECT_PDF_TEXT_AS_COMPLETE_DOCUMENT",
    "REJECT_TABLE_EXTRACTION_WITHOUT_REGION_SOURCE",
    "REJECT_DOCUMENT_FUSION_WITHOUT_PROVENANCE",
    "REJECT_UNMARKED_DOCUMENT_EXTRACTION_LOSS",
    "REJECT_PROVIDER_DISAGREEMENT_COLLAPSED_SILENTLY",
    "REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION",
]


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _list(values: Optional[Iterable[Any]]) -> List[str]:
    return sorted(dict.fromkeys(str(v) for v in (values or []) if str(v)))


def build_document_provider_contract(
    *,
    provider_id: str,
    capability_class: str,
    observed_modalities: Optional[Iterable[str]] = None,
    projection_types: Optional[Iterable[str]] = None,
    loss_profile: str = "DECLARED_MIXED_LOSSLESS_AND_LOSSY",
    provider_authority: bool = False,
) -> Dict[str, Any]:
    cap = str(capability_class).upper()
    contract = {
        "schema": CONTRACT_SCHEMA,
        "version": VERSION,
        "contract_id": _unique("document-provider-contract"),
        "provider_id": provider_id,
        "capability_class": cap,
        "observed_modalities": _list(observed_modalities or DOCUMENT_MODALITIES),
        "projection_types": _list(projection_types or PROJECTION_TYPES),
        "loss_profile": loss_profile,
        "source_preserved": True,
        "projection_replaces_source": False,
        "provider_is_canonical_authority": bool(provider_authority),
        "provider_output_is_canonical_source": False,
        "requires_runtime_canonical_ingress": True,
        "requires_universal_modality_pipeline": True,
        "requires_reconstruction_recipe": True,
        "rejection_codes": list(REJECTION_CODES),
        "authority": AUTHORITY,
        "created_at_unix_ms": _now_ms(),
    }
    contract["contract_root_hash72"] = hash72(CONTRACT_SCHEMA, contract)
    return contract


def validate_document_provider_contract(contract: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if contract.get("schema") != CONTRACT_SCHEMA:
        reasons.append("REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY")
    if contract.get("provider_is_canonical_authority"):
        reasons.append("REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY")
    if contract.get("provider_output_is_canonical_source"):
        reasons.append("REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY")
    if contract.get("projection_replaces_source"):
        reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    if not contract.get("loss_profile"):
        reasons.append("REJECT_UNMARKED_DOCUMENT_EXTRACTION_LOSS")
    if not contract.get("requires_reconstruction_recipe"):
        reasons.append("REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION")
    ok = not reasons
    decision = {
        "schema": "HHS_DOCUMENT_PROVIDER_CONTRACT_VALIDATION_V1",
        "version": VERSION,
        "ok": ok,
        "status": "ADMIT_DOCUMENT_PROVIDER_CONTRACT" if ok else "REJECT_DOCUMENT_PROVIDER_CONTRACT",
        "reasons": sorted(dict.fromkeys(reasons)),
        "provider_id": contract.get("provider_id"),
        "capability_class": contract.get("capability_class"),
        "contract_root_hash72": contract.get("contract_root_hash72"),
        "provider_never_becomes_canonical_authority": not bool(contract.get("provider_is_canonical_authority")),
        "authority": AUTHORITY,
    }
    decision["decision_root_hash72"] = hash72("HHS_DOCUMENT_PROVIDER_CONTRACT_VALIDATION_V1", decision)
    return decision


def build_document_provider_admission(
    *,
    contract: Mapping[str, Any],
    project_id: str = "project:default",
    input_payload: Any = "document-observation",
) -> Dict[str, Any]:
    """Bind a document provider to the Pass 051 capability policy chain."""
    capability_class = str(contract.get("capability_class") or "DOCUMENT_EXTRACTION")
    resolution = resolve_capability(capability_class, project_id=project_id, constraints={"document_perception": True})
    proposal = build_provider_execution_proposal(
        capability_class=capability_class,
        project_id=project_id,
        input_payload=input_payload,
        requested_operation="document_provider.observe",
        constraints={"provider_id": contract.get("provider_id"), "document_perception": True},
    )
    policy = evaluate_capability_policy_gate(proposal)
    observation = observe_external_surface(
        surface_type="DOCUMENT_PROVIDER",
        surface_id=str(contract.get("provider_id")),
        payload={"contract_root_hash72": contract.get("contract_root_hash72"), "input_payload": str(input_payload)[:256]},
        declared_role="PROVIDER_OBSERVATION",
    )
    contract_validation = validate_document_provider_contract(contract)
    admission = admit_runtime_identity(
        observation=observation,
        translated_record={"schema": CONTRACT_SCHEMA, "contract_root_hash72": contract.get("contract_root_hash72")},
        authority_decision={"ok": bool(policy.get("ok") and contract_validation.get("ok")), "status": policy.get("status")},
    )
    record = {
        "schema": "HHS_DOCUMENT_PROVIDER_ADMISSION_RECORD_V1",
        "version": VERSION,
        "ok": bool(resolution.get("ok") and policy.get("ok") and contract_validation.get("ok") and admission.get("ok")),
        "provider_id": contract.get("provider_id"),
        "capability_class": capability_class,
        "contract": dict(contract),
        "contract_validation": contract_validation,
        "capability_resolution": resolution,
        "execution_proposal": proposal,
        "policy_gate_decision": policy,
        "runtime_observation": observation,
        "runtime_admission": admission,
        "provider_never_becomes_canonical_authority": True,
        "authority": AUTHORITY,
    }
    record["admission_record_root_hash72"] = hash72("HHS_DOCUMENT_PROVIDER_ADMISSION_RECORD_V1", record)
    return record


def document_provider_contract_self_test() -> Dict[str, Any]:
    native = build_document_provider_contract(provider_id="provider:pdf-native-text", capability_class="DOCUMENT_EXTRACTION", observed_modalities=["PDF"], projection_types=["PDF_NATIVE_TEXT_PROJECTION"])
    ocr = build_document_provider_contract(provider_id="provider:deterministic-ocr", capability_class="OCR", observed_modalities=["IMAGE", "PDF"], projection_types=["OCR_TEXT_PROJECTION"])
    bad = build_document_provider_contract(provider_id="provider:bad-authority", capability_class="OCR", provider_authority=True)
    native_admission = build_document_provider_admission(contract=native, project_id="project:pass052", input_payload="%PDF")
    return {
        "schema": "HHS_DOCUMENT_PROVIDER_CONTRACT_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(validate_document_provider_contract(native)["ok"] and validate_document_provider_contract(ocr)["ok"] and not validate_document_provider_contract(bad)["ok"] and native_admission["ok"]),
        "native_contract": native,
        "ocr_contract": ocr,
        "bad_contract_rejection": validate_document_provider_contract(bad),
        "native_admission": native_admission,
        "observer_authority": OBSERVER_AUTHORITY,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(document_provider_contract_self_test(), indent=2, sort_keys=True, default=str))
