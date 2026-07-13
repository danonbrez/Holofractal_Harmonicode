"""
HHS Multimodal Workspace Ingress v1
==================================

Canonical multimodal ingress substrate for Pass 049.  Ingress preserves source
identity, declares modality, creates bounded derived projections, and registers
workspace objects only through witnessed packets.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional
import mimetypes
import time
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import (
    AUTHORITY,
    VERSION,
    create_workspace_object,
    hash72,
    validate_workspace_object,
)
from hhs_backend.runtime.runtime_workspace_project_v1 import create_workspace_project, register_project_object
from hhs_backend.runtime.hhs_universal_modality_adapter_v1 import (
    build_universal_adapter_contract,
    validate_adapter_contract,
)

INGRESS_SCHEMA = "HHS_MULTIMODAL_INGRESS_PACKET_V1"
SUPPORTED_MODALITIES = [
    "TEXT",
    "HARMONICODE_SOURCE",
    "CODE",
    "JSON",
    "YAML",
    "CSV",
    "PDF",
    "IMAGE",
    "AUDIO",
    "VIDEO",
    "BINARY",
    "DIRECTORY",
    "RUNTIME_RECEIPT",
    "LEDGER_FRAGMENT",
    "SEMANTIC_MEMORY_OBJECT",
    "GRAPH_OBJECT",
    "COMPILED_ARTIFACT",
    "EMULATOR_STATE",
]

INITIAL_ADAPTERS: Dict[str, Dict[str, Any]] = {
    modality: {
        "adapter_id": build_universal_adapter_contract(modality)["adapter_id"],
        "lossy": modality in {"PDF", "IMAGE", "AUDIO", "VIDEO"},
        "object_type": (
            "SYMBOLIC_SOURCE_DOCUMENT" if modality == "HARMONICODE_SOURCE"
            else "COMPILED_ARTIFACT" if modality == "COMPILED_ARTIFACT"
            else "EMULATOR_SESSION" if modality == "EMULATOR_STATE"
            else "RUNTIME_GRAPH_OBJECT" if modality == "GRAPH_OBJECT"
            else "SEMANTIC_MEMORY_OBJECT" if modality == "SEMANTIC_MEMORY_OBJECT"
            else "MULTIMODAL_OBJECT"
        ),
        "adapter_contract": build_universal_adapter_contract(modality),
    }
    for modality in SUPPORTED_MODALITIES
}

REJECTION_CODES = [
    "REJECT_UNSUPPORTED_MODALITY",
    "REJECT_MODALITY_ADAPTER_UNDECLARED",
    "REJECT_SILENT_MODALITY_RECLASSIFICATION",
    "REJECT_LOSSY_PROJECTION_UNMARKED",
]


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


def _now_ms() -> int:
    return int(time.time() * 1000)


def detect_modality(source_name: str, declared_modality: Optional[str] = None) -> str:
    if declared_modality:
        return str(declared_modality).upper()
    name = source_name.lower()
    if name.endswith((".hhs", ".harmonicode")):
        return "HARMONICODE_SOURCE"
    if name.endswith(".json"):
        return "JSON"
    if name.endswith(".pdf"):
        return "PDF"
    if name.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
        return "IMAGE"
    if name.endswith((".py", ".c", ".ts", ".tsx", ".js")):
        return "CODE"
    return "TEXT"


def build_ingress_packet(
    *,
    project_id: str,
    source_name: str,
    payload: Any,
    declared_modality: str,
    detected_modality: Optional[str] = None,
    projection_policy: str = "PRESERVE_UNRESOLVED_SOURCE",
) -> Dict[str, Any]:
    detected = detect_modality(source_name, detected_modality or declared_modality)
    adapter = INITIAL_ADAPTERS.get(declared_modality)
    source_commitment = hash72("HHS_WORKSPACE_INGRESS_SOURCE_COMMITMENT_V1", {
        "source_name": source_name,
        "declared_modality": declared_modality,
        "payload": payload,
    })
    packet = {
        "schema": INGRESS_SCHEMA,
        "version": VERSION,
        "ingress_id": _unique("ingress"),
        "project_id": project_id,
        "source_name": source_name,
        "declared_modality": declared_modality,
        "detected_modality": detected,
        "mime_type": mimetypes.guess_type(source_name)[0] or "application/octet-stream",
        "source_size_bytes": len(str(payload).encode("utf-8")),
        "source_commitment_hash72": source_commitment,
        "adapter_id": adapter.get("adapter_id") if adapter else "UNDECLARED_ADAPTER",
        "projection_policy": projection_policy,
        "expanded_metadata_policy": "BOUNDED_TEMPORARY",
        "universal_adapter_schema": "HHS_UNIVERSAL_MODALITY_ADAPTER_V1",
        "universal_adapter_contract_hash72": (adapter.get("adapter_contract") or {}).get("adapter_contract_hash72") if adapter else "",
        "source_projection_artifact_separation": "source != projection != artifact != execution_authority",
        "authority_required": True,
        "created_at_unix_ms": _now_ms(),
        "authority": AUTHORITY,
    }
    packet["ingress_packet_hash72"] = hash72(INGRESS_SCHEMA, packet)
    return packet


def validate_ingress_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    declared = str(packet.get("declared_modality") or "")
    detected = str(packet.get("detected_modality") or "")
    adapter = str(packet.get("adapter_id") or "")
    if declared not in SUPPORTED_MODALITIES:
        reasons.append("REJECT_UNSUPPORTED_MODALITY")
    if declared not in INITIAL_ADAPTERS:
        reasons.append("REJECT_MODALITY_ADAPTER_UNDECLARED")
    else:
        adapter_validation = validate_adapter_contract(INITIAL_ADAPTERS[declared].get("adapter_contract") or {})
        if not adapter_validation.get("ok"):
            reasons.extend(adapter_validation.get("reasons") or [])
    if detected and declared and detected != declared:
        reasons.append("REJECT_SILENT_MODALITY_RECLASSIFICATION")
    if INITIAL_ADAPTERS.get(declared, {}).get("lossy") and packet.get("projection_policy") != "PRESERVE_UNRESOLVED_SOURCE":
        reasons.append("REJECT_LOSSY_PROJECTION_UNMARKED")
    if adapter == "UNDECLARED_ADAPTER":
        reasons.append("REJECT_MODALITY_ADAPTER_UNDECLARED")
    ok = not reasons
    return {
        "schema": "HHS_MULTIMODAL_INGRESS_PACKET_VALIDATION_V1",
        "version": VERSION,
        "ok": ok,
        "status": "ADMIT_MULTIMODAL_INGRESS" if ok else "REJECT_MULTIMODAL_INGRESS",
        "reasons": sorted(dict.fromkeys(reasons)),
        "ingress_id": packet.get("ingress_id"),
        "source_commitment_hash72": packet.get("source_commitment_hash72"),
    }


def create_ingressed_workspace_object(packet: Mapping[str, Any], payload: Any) -> Dict[str, Any]:
    modality = str(packet.get("declared_modality"))
    adapter = INITIAL_ADAPTERS.get(modality, {})
    obj = create_workspace_object(
        project_id=str(packet.get("project_id")),
        object_type=str(adapter.get("object_type") or "MULTIMODAL_OBJECT"),
        modality=modality,
        name=str(packet.get("source_name") or "ingressed-object"),
        payload=payload,
        schema_id="HHS_SYMBOLIC_SOURCE_DOCUMENT_V1" if modality == "HARMONICODE_SOURCE" else "HHS_MULTIMODAL_WORKSPACE_OBJECT_V1",
        lifecycle_state="INGRESSED",
        source_provenance={
            "source_uri": f"workspace://{packet.get('project_id')}/ingress/{packet.get('ingress_id')}",
            "ingress_id": packet.get("ingress_id"),
            "source_commitment_hash72": packet.get("source_commitment_hash72"),
            "adapter_id": packet.get("adapter_id"),
            "lossy_projection": bool(adapter.get("lossy")),
        },
    )
    obj["ingress_packet_hash72"] = packet.get("ingress_packet_hash72")
    obj["source_preserved"] = True
    obj["derived_projection_policy"] = "DERIVED_OBJECTS_DO_NOT_REPLACE_SOURCE"
    obj["object_root_hash72"] = hash72("HHS_INGRESSED_WORKSPACE_OBJECT_V1", obj)
    return obj


def ingest_workspace_source(
    *,
    project: Mapping[str, Any],
    source_name: str,
    payload: Any,
    declared_modality: str,
) -> Dict[str, Any]:
    packet = build_ingress_packet(
        project_id=str(project.get("project_id")),
        source_name=source_name,
        payload=payload,
        declared_modality=declared_modality,
    )
    validation = validate_ingress_packet(packet)
    if not validation.get("ok"):
        return {
            "schema": "HHS_WORKSPACE_INGRESS_RESULT_V1",
            "version": VERSION,
            "ok": False,
            "status": "WORKSPACE_INGRESS_REJECTED",
            "packet": packet,
            "validation": validation,
        }
    obj = create_ingressed_workspace_object(packet, payload)
    obj_validation = validate_workspace_object(obj)
    registration = register_project_object(project, obj) if obj_validation.get("ok") else {"ok": False, "validation": obj_validation}
    result = {
        "schema": "HHS_WORKSPACE_INGRESS_RESULT_V1",
        "version": VERSION,
        "ok": bool(registration.get("ok")),
        "status": "WORKSPACE_INGRESS_COMPLETED" if registration.get("ok") else "WORKSPACE_INGRESS_REJECTED",
        "packet": packet,
        "validation": validation,
        "workspace_object": obj,
        "registration": registration,
        "source_preserved": True,
        "projection_is_canonical_source": False,
    }
    result["ingress_result_hash72"] = hash72("HHS_WORKSPACE_INGRESS_RESULT_V1", result)
    return result


def multimodal_workspace_ingress_self_test() -> Dict[str, Any]:
    project = create_workspace_project("Ingress Workspace")
    text = ingest_workspace_source(project=project, source_name="note.txt", payload="meaning is conserved", declared_modality="TEXT")
    hhs = ingest_workspace_source(project=project, source_name="main.hhs", payload="a²+b²=c²", declared_modality="HARMONICODE_SOURCE")
    json_result = ingest_workspace_source(project=project, source_name="object.json", payload={"a²": 1, "b²": 2}, declared_modality="JSON")
    pdf = ingest_workspace_source(project=project, source_name="paper.pdf", payload="%PDF-source-bytes", declared_modality="PDF")
    image = ingest_workspace_source(project=project, source_name="glyph.png", payload="PNG-source-bytes", declared_modality="IMAGE")
    video = ingest_workspace_source(project=project, source_name="clip.mp4", payload="video", declared_modality="VIDEO")
    audio = ingest_workspace_source(project=project, source_name="tone.wav", payload="audio", declared_modality="AUDIO")
    rejected = ingest_workspace_source(project=project, source_name="unknown.xyz", payload="unknown", declared_modality="UNKNOWN_MODALITY")
    return {
        "schema": "HHS_MULTIMODAL_WORKSPACE_INGRESS_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(text.get("ok") and hhs.get("ok") and json_result.get("ok") and pdf.get("ok") and image.get("ok") and video.get("ok") and audio.get("ok") and not rejected.get("ok")),
        "supported_initial_modalities": sorted(INITIAL_ADAPTERS.keys()),
        "results": [text, hhs, json_result, pdf, image, video, audio],
        "unsupported_modality_rejection": rejected,
        "invariant": "NO_PROJECTION_REPLACES_ITS_SOURCE_AND_ALL_MODALITIES_SHARE_HHS_UNIVERSAL_MODALITY_ADAPTER_V1",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(multimodal_workspace_ingress_self_test(), indent=2, sort_keys=True, default=str))
