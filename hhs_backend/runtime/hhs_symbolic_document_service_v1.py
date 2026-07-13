"""HHS symbolic document service for Pass 049 workspace source mutations."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, create_workspace_object, hash72

SYMBOLIC_DOCUMENT_SCHEMA = "HHS_SYMBOLIC_SOURCE_DOCUMENT_V1"
PATCH_SCHEMA = "HHS_SYMBOLIC_SOURCE_PATCH_V1"
MUTATION_RECEIPT_SCHEMA = "HHS_WORKSPACE_MUTATION_RECEIPT_V1"

AMBIGUITY_MARKERS = ["??", "<ambiguous>", "FIXME_APPROXIMATE", "float("]
FORBIDDEN_FLOAT_MARKERS = ["0.1", "0.333", "float", "double"]


def create_symbolic_document(project_id: str, name: str, source_text: str) -> Dict[str, Any]:
    obj = create_workspace_object(
        project_id=project_id,
        object_type="SYMBOLIC_SOURCE_DOCUMENT",
        modality="HARMONICODE_SOURCE",
        name=name,
        payload=source_text,
        schema_id=SYMBOLIC_DOCUMENT_SCHEMA,
        lifecycle_state="EDITABLE",
        source_provenance={"source_uri": f"workspace://{project_id}/source/{name}"},
    )
    obj["source_text_hash72"] = hash72(SYMBOLIC_DOCUMENT_SCHEMA, source_text)
    obj["semantic_role"] = "AUTHORITATIVE_SOURCE_OBJECT"
    obj["object_root_hash72"] = hash72(SYMBOLIC_DOCUMENT_SCHEMA, obj)
    return obj


def propose_source_patch(
    *,
    document: Mapping[str, Any],
    replacement_text: str,
    actor_id: str = "actor:human",
    actor_type: str = "HUMAN",
) -> Dict[str, Any]:
    pre_root = document.get("current_root_hash72") or document.get("object_root_hash72")
    patch = {
        "schema": PATCH_SCHEMA,
        "version": VERSION,
        "patch_id": f"patch:{uuid.uuid4().hex}",
        "object_id": document.get("object_id"),
        "project_id": document.get("project_id"),
        "actor_id": actor_id,
        "actor_type": actor_type,
        "authority_scope": "REQUEST_ONLY" if actor_type == "HUMAN" else "PROPOSE_ONLY",
        "pre_state_root_hash72": pre_root,
        "replacement_text_hash72": hash72("HHS_SYMBOLIC_SOURCE_PATCH_REPLACEMENT_V1", replacement_text),
        "buffer_is_authoritative": False,
        "local_buffer_state": "NON_AUTHORITATIVE_EDIT_BUFFER",
        "requires_authority": True,
    }
    patch["patch_root_hash72"] = hash72(PATCH_SCHEMA, patch)
    return patch


def validate_symbolic_patch(patch: Mapping[str, Any], replacement_text: str) -> Dict[str, Any]:
    reasons: List[str] = []
    if patch.get("buffer_is_authoritative"):
        reasons.append("REJECT_GUI_DIRECT_WORKSPACE_MUTATION")
    if any(marker in replacement_text for marker in AMBIGUITY_MARKERS):
        reasons.append("REJECT_SYMBOLIC_PARSE_AMBIGUITY")
    if any(marker in replacement_text for marker in FORBIDDEN_FLOAT_MARKERS):
        reasons.append("REJECT_EXACT_SYMBOLIC_VALUE_REPLACED_BY_FLOAT")
    if patch.get("actor_type") == "HHS_AGENT" and patch.get("authority_scope") != "PROPOSE_ONLY":
        reasons.append("REJECT_AI_DIRECT_EDIT")
    if not patch.get("pre_state_root_hash72"):
        reasons.append("REJECT_WORKSPACE_OBJECT_ROOT_MISMATCH")
    ok = not reasons
    return {
        "schema": "HHS_SYMBOLIC_SOURCE_PATCH_VALIDATION_V1",
        "version": VERSION,
        "ok": ok,
        "status": "ADMIT_SYMBOLIC_SOURCE_PATCH" if ok else "REJECT_SYMBOLIC_SOURCE_PATCH",
        "reasons": sorted(dict.fromkeys(reasons)),
        "patch_id": patch.get("patch_id"),
        "patch_root_hash72": patch.get("patch_root_hash72"),
    }


def admit_symbolic_patch(document: Mapping[str, Any], patch: Mapping[str, Any], replacement_text: str) -> Dict[str, Any]:
    validation = validate_symbolic_patch(patch, replacement_text)
    if not validation.get("ok"):
        return {
            "schema": "HHS_SYMBOLIC_SOURCE_MUTATION_RESULT_V1",
            "version": VERSION,
            "ok": False,
            "status": "MUTATION_REJECTED",
            "validation": validation,
        }
    post_root = hash72("HHS_SYMBOLIC_SOURCE_DOCUMENT_POST_STATE_V1", {
        "object_id": document.get("object_id"),
        "text": replacement_text,
        "patch_root_hash72": patch.get("patch_root_hash72"),
    })
    transformation = {
        "schema": "HHS_SYMBOLIC_SOURCE_TRANSFORMATION_V1",
        "operation": "source.patch",
        "pre_state_root_hash72": patch.get("pre_state_root_hash72"),
        "post_state_root_hash72": post_root,
        "semantic_mutation_not_formatting": True,
    }
    transformation["transformation_hash72"] = hash72("HHS_SYMBOLIC_SOURCE_TRANSFORMATION_V1", transformation)
    receipt = {
        "schema": MUTATION_RECEIPT_SCHEMA,
        "version": VERSION,
        "receipt_id": f"receipt:{uuid.uuid4().hex}",
        "operation": "source.patch",
        "object_id": document.get("object_id"),
        "pre_state_hash72": patch.get("pre_state_root_hash72"),
        "transformation_hash72": transformation["transformation_hash72"],
        "post_state_hash72": post_root,
        "authority": AUTHORITY,
        "websocket_feedback_required": True,
    }
    receipt["receipt_hash72"] = hash72(MUTATION_RECEIPT_SCHEMA, receipt)
    updated = dict(document)
    updated["current_root_hash72"] = post_root
    updated["mutation_sequence"] = int(updated.get("mutation_sequence") or 0) + 1
    updated["receipt_tip_hash72"] = receipt["receipt_hash72"]
    updated["lifecycle_state"] = "MUTATION_ADMITTED"
    updated["object_root_hash72"] = hash72(SYMBOLIC_DOCUMENT_SCHEMA, updated)
    return {
        "schema": "HHS_SYMBOLIC_SOURCE_MUTATION_RESULT_V1",
        "version": VERSION,
        "ok": True,
        "status": "MUTATION_ADMITTED",
        "document": updated,
        "validation": validation,
        "transformation": transformation,
        "mutation_receipt": receipt,
    }


def symbolic_document_service_self_test() -> Dict[str, Any]:
    doc = create_symbolic_document("project:pass049", "main.hhs", "a²+b²=c²")
    patch = propose_source_patch(document=doc, replacement_text="a²=1\nb²=2\nc²=3")
    admitted = admit_symbolic_patch(doc, patch, "a²=1\nb²=2\nc²=3")
    ambiguous = propose_source_patch(document=doc, replacement_text="x ?? y")
    rejected = admit_symbolic_patch(doc, ambiguous, "x ?? y")
    ai_patch = propose_source_patch(document=doc, replacement_text="d²=5", actor_id="actor:hhs-agent", actor_type="HHS_AGENT")
    ai_validation = validate_symbolic_patch(ai_patch, "d²=5")
    return {
        "schema": "HHS_SYMBOLIC_DOCUMENT_SERVICE_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(admitted.get("ok") and not rejected.get("ok") and ai_validation.get("ok")),
        "admitted": admitted,
        "ambiguous_rejection": rejected,
        "ai_suggestion_policy": ai_validation,
        "hard_invariant": "AI_SUGGESTIONS_ARE_PROPOSALS_NOT_DIRECT_EDITS",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(symbolic_document_service_self_test(), indent=2, sort_keys=True, default=str))
