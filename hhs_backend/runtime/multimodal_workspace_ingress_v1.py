"""
HHS Multimodal Workspace Ingress v1
==================================

Canonical multimodal ingress substrate for Pass 049.  Ingress preserves source
identity, declares modality, creates bounded derived projections, and registers
workspace objects only through witnessed packets.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional
from base64 import b64encode
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

# Compatibility aliases are transport/profile names, not new authority types.
# They are translated into one of the canonical modality adapters above while
# retaining their original label in the ingress packet.
LEGACY_MODALITY_ALIASES: Dict[str, str] = {
    "HHS": "HARMONICODE_SOURCE",
    "HARMONICODE": "HARMONICODE_SOURCE",
    "HARMONICODE_TEXT": "HARMONICODE_SOURCE",
    "SOURCE": "TEXT",
    "PLAIN_TEXT": "TEXT",
    "TEXT_PLAIN": "TEXT",
    "STRING": "TEXT",
    "SOURCE_CODE": "CODE",
    "SCRIPT": "CODE",
    "PYTHON": "CODE",
    "JAVASCRIPT": "CODE",
    "TYPESCRIPT": "CODE",
    "C": "CODE",
    "CPP": "CODE",
    "CXX": "CODE",
    "RUST": "CODE",
    "SHELL": "CODE",
    "BASH": "CODE",
    "JSON_OBJECT": "JSON",
    "APPLICATION_JSON": "JSON",
    "JSON_EXECUTION_GRAPH": "GRAPH_OBJECT",
    "EXECUTION_GRAPH": "GRAPH_OBJECT",
    "GRAPH": "GRAPH_OBJECT",
    "YML": "YAML",
    "OCTET_STREAM": "BINARY",
    "RAW": "BINARY",
    "BYTES": "BINARY",
    "BYTE_ARRAY": "BINARY",
    "BLOB": "BINARY",
    "FILE": "BINARY",
    "FOLDER": "DIRECTORY",
    "DIR": "DIRECTORY",
    "RECEIPT": "RUNTIME_RECEIPT",
    "LEDGER": "LEDGER_FRAGMENT",
    "MEMORY": "SEMANTIC_MEMORY_OBJECT",
    "ARTIFACT": "COMPILED_ARTIFACT",
    "EXECUTABLE": "COMPILED_ARTIFACT",
    "OBJECT_FILE": "COMPILED_ARTIFACT",
    "SHARED_LIBRARY": "COMPILED_ARTIFACT",
    "VM_STATE": "EMULATOR_STATE",
    "SNAPSHOT": "EMULATOR_STATE",
}

MIME_MODALITY_PREFIXES = (
    ("image/", "IMAGE"),
    ("audio/", "AUDIO"),
    ("video/", "VIDEO"),
    ("text/", "TEXT"),
)

MIME_MODALITY_MAP: Dict[str, str] = {
    "application/json": "JSON",
    "application/ld+json": "JSON",
    "application/yaml": "YAML",
    "application/x-yaml": "YAML",
    "text/yaml": "YAML",
    "text/x-yaml": "YAML",
    "text/csv": "CSV",
    "application/csv": "CSV",
    "application/pdf": "PDF",
    "application/octet-stream": "BINARY",
    "binary/octet-stream": "BINARY",
    "application/x-executable": "COMPILED_ARTIFACT",
    "application/x-pie-executable": "COMPILED_ARTIFACT",
    "application/x-sharedlib": "COMPILED_ARTIFACT",
    "application/x-object": "COMPILED_ARTIFACT",
    "application/vnd.microsoft.portable-executable": "COMPILED_ARTIFACT",
    "application/wasm": "COMPILED_ARTIFACT",
    "inode/directory": "DIRECTORY",
    "application/x-www-form-urlencoded": "JSON",
    "application/xml": "TEXT",
    "text/xml": "TEXT",
    "application/javascript": "CODE",
    "text/javascript": "CODE",
    "application/ecmascript": "CODE",
    "text/ecmascript": "CODE",
    "text/x-python": "CODE",
    "text/x-c": "CODE",
    "text/x-c++": "CODE",
    "text/x-rust": "CODE",
    "application/x-sh": "CODE",
}


def _base_media_type(media_type: Optional[str]) -> str:
    return str(media_type or "").split(";", 1)[0].strip().lower()


def _filename_modality(source_name: str) -> Optional[str]:
    name = str(source_name or "").lower()
    if name.endswith((".hhs", ".harmonicode")):
        return "HARMONICODE_SOURCE"
    if name.endswith(".json"):
        return "JSON"
    if name.endswith((".yaml", ".yml")):
        return "YAML"
    if name.endswith(".csv"):
        return "CSV"
    if name.endswith(".pdf"):
        return "PDF"
    if name.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".svg")):
        return "IMAGE"
    if name.endswith((".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac")):
        return "AUDIO"
    if name.endswith((".mp4", ".mov", ".mkv", ".webm", ".avi")):
        return "VIDEO"
    if name.endswith((".py", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".rs", ".go", ".java", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".bash", ".ps1", ".s", ".asm", ".sql", ".html", ".css")):
        return "CODE"
    if name.endswith((".o", ".a", ".so", ".dll", ".exe", ".wasm", ".bin", ".elf")):
        return "COMPILED_ARTIFACT"
    if name.endswith((".txt", ".md", ".rst", ".log", ".ini", ".cfg", ".conf")):
        return "TEXT"
    return None


def translate_legacy_modality(
    *,
    source_name: str,
    declared_modality: Optional[str] = None,
    media_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Translate legacy/Linux-facing type labels into canonical ingress adapters.

    Unknown external types are preserved as BINARY instead of being rejected.
    The original declaration and media type remain explicit evidence so this
    translation cannot masquerade as source-native canonical typing.
    """

    original = str(declared_modality or "").strip()
    declared = original.upper().replace("-", "_").replace(" ", "_")
    base_media = _base_media_type(media_type)

    canonical: Optional[str] = None
    reason = "UNKNOWN_EXTERNAL_TYPE_FALLBACK_BINARY"

    if declared in SUPPORTED_MODALITIES:
        canonical = declared
        reason = "CANONICAL_MODALITY_PASSTHROUGH"
    elif declared in LEGACY_MODALITY_ALIASES:
        canonical = LEGACY_MODALITY_ALIASES[declared]
        reason = "LEGACY_MODALITY_ALIAS"
    elif base_media in MIME_MODALITY_MAP:
        canonical = MIME_MODALITY_MAP[base_media]
        reason = "MEDIA_TYPE_TRANSLATION"
    else:
        for prefix, modality in MIME_MODALITY_PREFIXES:
            if base_media.startswith(prefix):
                canonical = modality
                reason = "MEDIA_TYPE_PREFIX_TRANSLATION"
                break

    if canonical is None:
        canonical = _filename_modality(source_name)
        if canonical is not None:
            reason = "FILENAME_PROFILE_TRANSLATION"

    if canonical is None:
        canonical = "BINARY"

    # Generic text/* may still carry source code. Let a known file suffix refine
    # TEXT to CODE without losing the original MIME declaration.
    filename_modality = _filename_modality(source_name)
    if canonical == "TEXT" and filename_modality in {"CODE", "HARMONICODE_SOURCE", "JSON", "YAML", "CSV"}:
        canonical = filename_modality
        reason = "TEXT_MEDIA_FILENAME_REFINEMENT"

    return {
        "schema": "HHS_LEGACY_INGRESS_TYPE_TRANSLATION_V1",
        "source_name": source_name,
        "original_declared_modality": original or None,
        "original_media_type": media_type or None,
        "base_media_type": base_media or None,
        "canonical_modality": canonical,
        "translation_reason": reason,
        "translated": bool(
            (original and original.upper() != canonical)
            or (base_media and MIME_MODALITY_MAP.get(base_media) != canonical)
            or reason not in {"CANONICAL_MODALITY_PASSTHROUGH"}
        ),
        "unknown_external_type_preserved": reason == "UNKNOWN_EXTERNAL_TYPE_FALLBACK_BINARY",
        "source_authority_changed": False,
    }


def normalize_legacy_payload(payload: Any) -> Dict[str, Any]:
    """Create a reversible canonical transport representation for legacy bytes."""

    if isinstance(payload, memoryview):
        payload = payload.tobytes()
    if isinstance(payload, bytearray):
        payload = bytes(payload)
    if isinstance(payload, bytes):
        encoded = b64encode(payload).decode("ascii")
        return {
            "payload": {
                "schema": "HHS_REVERSIBLE_BINARY_SOURCE_V1",
                "encoding": "base64",
                "data_b64": encoded,
                "source_size_bytes": len(payload),
            },
            "transport_encoding": "BASE64_REVERSIBLE",
            "source_size_bytes": len(payload),
            "binary_source": True,
        }

    return {
        "payload": payload,
        "transport_encoding": "NATIVE_JSON_VALUE",
        "source_size_bytes": len(str(payload).encode("utf-8")),
        "binary_source": False,
    }


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


def _now_ms() -> int:
    return int(time.time() * 1000)


def detect_modality(
    source_name: str,
    declared_modality: Optional[str] = None,
    media_type: Optional[str] = None,
) -> str:
    return str(
        translate_legacy_modality(
            source_name=source_name,
            declared_modality=declared_modality,
            media_type=media_type,
        )["canonical_modality"]
    )


def build_ingress_packet(
    *,
    project_id: str,
    source_name: str,
    payload: Any,
    declared_modality: str,
    detected_modality: Optional[str] = None,
    projection_policy: str = "PRESERVE_UNRESOLVED_SOURCE",
    media_type: Optional[str] = None,
    compatibility_translation: Optional[Mapping[str, Any]] = None,
    transport_encoding: str = "NATIVE_JSON_VALUE",
    source_size_bytes: Optional[int] = None,
) -> Dict[str, Any]:
    detected = detect_modality(
        source_name,
        detected_modality or declared_modality,
        media_type=media_type,
    )
    adapter = INITIAL_ADAPTERS.get(declared_modality)
    translation = dict(compatibility_translation or {})
    source_commitment = hash72("HHS_WORKSPACE_INGRESS_SOURCE_COMMITMENT_V1", {
        "source_name": source_name,
        "declared_modality": declared_modality,
        "media_type": media_type,
        "transport_encoding": transport_encoding,
        "compatibility_translation": translation,
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
        "mime_type": _base_media_type(media_type) or mimetypes.guess_type(source_name)[0] or "application/octet-stream",
        "source_size_bytes": int(source_size_bytes if source_size_bytes is not None else len(str(payload).encode("utf-8"))),
        "source_declared_modality": translation.get("original_declared_modality"),
        "source_media_type": translation.get("original_media_type") or media_type,
        "compatibility_translation": translation or None,
        "legacy_translation_applied": bool(translation.get("translated")),
        "transport_encoding": transport_encoding,
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
            "source_declared_modality": packet.get("source_declared_modality"),
            "source_media_type": packet.get("source_media_type"),
            "compatibility_translation": packet.get("compatibility_translation"),
            "transport_encoding": packet.get("transport_encoding"),
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
    declared_modality: Optional[str] = None,
    media_type: Optional[str] = None,
) -> Dict[str, Any]:
    translation = translate_legacy_modality(
        source_name=source_name,
        declared_modality=declared_modality,
        media_type=media_type,
    )
    normalized_payload = normalize_legacy_payload(payload)
    canonical_modality = str(translation["canonical_modality"])
    canonical_payload = normalized_payload["payload"]
    packet = build_ingress_packet(
        project_id=str(project.get("project_id")),
        source_name=source_name,
        payload=canonical_payload,
        declared_modality=canonical_modality,
        detected_modality=canonical_modality,
        media_type=media_type,
        compatibility_translation=translation,
        transport_encoding=str(normalized_payload["transport_encoding"]),
        source_size_bytes=int(normalized_payload["source_size_bytes"]),
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
    obj = create_ingressed_workspace_object(packet, canonical_payload)
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
        "compatibility_translation": translation,
        "legacy_ingress_redirected": bool(translation.get("translated")),
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
    legacy_graph = ingest_workspace_source(
        project=project,
        source_name="visual-program.hhsgraph.json",
        payload={"nodes": [], "edges": []},
        declared_modality="JSON_EXECUTION_GRAPH",
        media_type="application/json",
    )
    unknown = ingest_workspace_source(
        project=project,
        source_name="legacy.unknown",
        payload=b"\x00\xfflegacy",
        declared_modality="VENDOR_LEGACY_RECORD",
        media_type="application/x-vendor-legacy",
    )
    return {
        "schema": "HHS_MULTIMODAL_WORKSPACE_INGRESS_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(
            text.get("ok")
            and hhs.get("ok")
            and json_result.get("ok")
            and pdf.get("ok")
            and image.get("ok")
            and video.get("ok")
            and audio.get("ok")
            and legacy_graph.get("ok")
            and legacy_graph.get("packet", {}).get("declared_modality") == "GRAPH_OBJECT"
            and unknown.get("ok")
            and unknown.get("packet", {}).get("declared_modality") == "BINARY"
            and unknown.get("packet", {}).get("transport_encoding") == "BASE64_REVERSIBLE"
        ),
        "supported_initial_modalities": sorted(INITIAL_ADAPTERS.keys()),
        "results": [text, hhs, json_result, pdf, image, video, audio, legacy_graph, unknown],
        "legacy_graph_translation": legacy_graph,
        "unknown_legacy_binary_fallback": unknown,
        "invariant": "LEGACY_EXTERNAL_TYPES_TRANSLATE_OR_PRESERVE_AS_BINARY_WITHOUT_BYPASSING_CANONICAL_ADAPTER_AUTHORITY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(multimodal_workspace_ingress_self_test(), indent=2, sort_keys=True, default=str))
