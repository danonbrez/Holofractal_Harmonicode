"""Integrated visual-IDE software lifecycle routes.

The routes compose existing canonical HHS authorities instead of introducing a
parallel interpreter, compiler, emulator, snapshot generator, or receipt path.
"""
from __future__ import annotations

from base64 import b64decode
from hashlib import sha256
import json
import re
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.pass165_multimodal_ingress_routes import SERVICE, snapshot_payload
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass150.genome import Hash216Genome
from hhs_runtime.pass165.ingestion import IngestionError

router = APIRouter(
    prefix="/api/runtime/development",
    tags=["runtime", "visual-ide", "lifecycle", "vm81", "hash216", "multimodal"],
)

TEXT_MODALITIES = {
    "TEXT",
    "MARKDOWN",
    "SOURCE_CODE",
    "JSON",
    "JSONL",
    "CSV",
    "HTML",
    "XML",
    "HHS_CONTRACT",
    "HHS_RECEIPT",
    "HHS_MANIFEST",
    "HHS_VECTOR_PACKET",
}


class DevelopmentLifecycleRequest(BaseModel):
    source_b64: str = Field(min_length=1)
    source_name: str = Field(default="main.hhs", min_length=1, max_length=512)
    declared_media_type: Optional[str] = None
    provenance: str = Field(min_length=1, max_length=2048)
    authorization_scope: str = Field(min_length=1, max_length=512)
    project_id: Optional[str] = None
    project_name: str = Field(default="HHS Visual IDE Project", min_length=1, max_length=512)
    expression: Optional[str] = None
    interpretation_scope: str = Field(default="SOURCE_EXACT_NUMERIC_PROBE", max_length=128)
    target: str = Field(default="HHS_IR", min_length=1, max_length=128)
    steps: int = Field(default=8, ge=1, le=32)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _safe_artifact_name(source_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", source_name).strip(".-") or "source"
    return f"{normalized}.hhs-lifecycle.json"


def _ensure_project(canonical: Any, requested_id: str | None, name: str) -> Dict[str, Any]:
    if requested_id and requested_id in canonical.WORKSPACE_AUTHORITY_LOOP.projects:
        return canonical.WORKSPACE_AUTHORITY_LOOP.projects[requested_id]
    project = canonical.create_workspace_project(name)
    canonical.WORKSPACE_AUTHORITY_LOOP.projects[project["project_id"]] = project
    return project


def _workspace_modality(source_name: str, detected_media_type: str) -> str:
    media = detected_media_type.upper()
    if media == "SOURCE_CODE":
        return "HARMONICODE_SOURCE" if source_name.lower().endswith((".hhs", ".harmonicode")) else "CODE"
    if media in {"MARKDOWN", "HTML", "XML", "HHS_CONTRACT", "HHS_MANIFEST", "HHS_VECTOR_PACKET"}:
        return "TEXT"
    if media == "JSONL":
        return "JSON"
    if media == "HHS_RECEIPT":
        return "RUNTIME_RECEIPT"
    if media == "BINARY_OBJECT":
        return "BINARY"
    return media


def _select_exact_expression(source_text: str, supplied: str | None) -> tuple[str, str]:
    candidates: list[tuple[str, str]] = []
    if supplied is not None:
        candidates.append((supplied, "REQUESTED_EXPRESSION"))
    for raw_line in source_text.splitlines():
        line = re.sub(r"//.*$|#.*$", "", raw_line).strip()
        if not line:
            continue
        candidates.append((line, "SOURCE_LINE"))
        if "=" in line:
            candidates.append((line.rsplit("=", 1)[-1].strip(), "SOURCE_ASSIGNMENT_RHS"))
    for candidate, scope in candidates:
        normalized = re.sub(r"[;,.]+$", "", candidate).strip()
        if re.fullmatch(r"[0-9+*/()\s-]+", normalized) and re.search(r"\d", normalized):
            return normalized, scope
    literal = re.search(r"-?\d+(?:\s*/\s*\d+)?", source_text)
    if literal:
        return literal.group(0), "SOURCE_NUMERIC_LITERAL"
    return "0", "NO_NUMERIC_TOKEN_ZERO_PROBE"


def _workspace_submit(canonical: Any, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return canonical.WORKSPACE_AUTHORITY_LOOP.submit(operation, payload)


def _extract_artifact_id(compilation: Dict[str, Any] | None) -> str | None:
    if not compilation:
        return None
    result = compilation.get("result") or {}
    artifact = result.get("artifact") or {}
    provenance = result.get("source_to_artifact_provenance") or {}
    return artifact.get("artifact_id") or provenance.get("artifact_id")


def _extract_receipt(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str) and (key == "receipt_hash72" or key.endswith("receipt_hash72")):
                return item
        for item in value.values():
            result = _extract_receipt(item)
            if result:
                return result
    elif isinstance(value, list):
        for item in value:
            result = _extract_receipt(item)
            if result:
                return result
    return None


@router.get("/status")
def development_status() -> Dict[str, Any]:
    from hhs_backend import server as canonical

    pass165 = SERVICE.status()
    workspace = canonical.WORKSPACE_AUTHORITY_LOOP.status()
    return {
        "schema": "HHS_VISUAL_IDE_DEVELOPMENT_LIFECYCLE_STATUS_V1",
        "ok": bool(pass165.get("vm81_commit_authority")),
        "stages": [
            "SOURCE_PRESERVING_MULTIMODAL_INGRESS",
            "HASH216_OPERATION_INDEX",
            "EXACT_5184_BIT_VM_SNAPSHOT",
            "HHS_INTERPRETER",
            "HHS_IR_COMPILER",
            "BOUNDED_VM81_EXECUTION",
            "RECEIPT_BOUND_MULTIMODAL_EGRESS",
        ],
        "pass165": pass165,
        "workspace": workspace,
        "frontend_is_authority": False,
    }


@router.post("/lifecycle")
def run_development_lifecycle(request: DevelopmentLifecycleRequest) -> Dict[str, Any]:
    from hhs_backend import server as canonical

    try:
        source_bytes = b64decode(request.source_b64, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=422, detail={"classification": "HHS_IDE_MALFORMED_BASE64"}) from exc

    try:
        ingress = SERVICE.ingest_source(
            source_bytes,
            declared_media_type=request.declared_media_type,
            provenance=request.provenance,
            authorization_scope=request.authorization_scope,
        )
        source_hash = str((ingress.get("source") or {}).get("source_hash") or sha256(source_bytes).hexdigest())
        vm_snapshot = snapshot_payload(source_hash)
    except IngestionError as exc:
        raise HTTPException(
            status_code=422,
            detail={"classification": exc.classification, "detail": exc.detail},
        ) from exc

    project = _ensure_project(canonical, request.project_id, request.project_name)
    project_id = str(project["project_id"])
    detected_media_type = str((ingress.get("source") or {}).get("detected_media_type") or request.declared_media_type or "BINARY_OBJECT")
    source_text = source_bytes.decode("utf-8", errors="strict") if detected_media_type in TEXT_MODALITIES else ""
    source_payload: Any = source_text if source_text else request.source_b64
    workspace_modality = _workspace_modality(request.source_name, detected_media_type)

    workspace_ingress = _workspace_submit(
        canonical,
        "ingress.register",
        {
            "project_id": project_id,
            "source_name": request.source_name,
            "source_payload": source_payload,
            "declared_modality": workspace_modality,
            "pass165_source_hash": source_hash,
            "pass165_projection_hash72": vm_snapshot["projection_hash72"],
            "pass165_operation_hash216": vm_snapshot["ingestion_operation_hash216"],
        },
    )

    interpretation: Dict[str, Any] | None = None
    compilation: Dict[str, Any] | None = None
    execution: Dict[str, Any] | None = None
    interpretation_scope = "NOT_APPLICABLE"

    if detected_media_type in TEXT_MODALITIES:
        expression, interpretation_scope = _select_exact_expression(source_text, request.expression)
        interpretation = _workspace_submit(
            canonical,
            "interpret.execute",
            {
                "project_id": project_id,
                "source_object_id": f"object:{source_hash[:24]}",
                "expression": expression,
                "interpretation_scope": interpretation_scope,
                "vm_snapshot_projection_hash72": vm_snapshot["projection_hash72"],
                "hash216_operation_root": vm_snapshot["ingestion_operation_hash216"],
            },
        )
        compilation = _workspace_submit(
            canonical,
            "compile.execute",
            {
                "project_id": project_id,
                "source_object_id": f"object:{source_hash[:24]}",
                "source_text": source_text,
                "target": request.target,
                "vm_snapshot_projection_hash72": vm_snapshot["projection_hash72"],
                "hash216_operation_root": vm_snapshot["ingestion_operation_hash216"],
            },
        )
        artifact_id = _extract_artifact_id(compilation)
        if compilation.get("ok") and artifact_id:
            created = _workspace_submit(
                canonical,
                "emulator.create",
                {
                    "project_id": project_id,
                    "program_artifact_id": artifact_id,
                    "initial_state": {
                        "snapshot_bits": vm_snapshot["snapshot_bits"],
                        "snapshot_bytes": vm_snapshot["snapshot_bytes"],
                        "projection_b64": vm_snapshot["projection_b64"],
                        "projection_hash72": vm_snapshot["projection_hash72"],
                        "hash216_operation_root": vm_snapshot["ingestion_operation_hash216"],
                        "hash216_positions": vm_snapshot["ingestion_positions_hash216"],
                    },
                },
            )
            session_id = ((created.get("result") or {}).get("session") or {}).get("session_id")
            if created.get("ok") and session_id:
                run = _workspace_submit(
                    canonical,
                    "emulator.run",
                    {
                        "project_id": project_id,
                        "session_id": session_id,
                        "steps": request.steps,
                    },
                )
                snap = _workspace_submit(
                    canonical,
                    "emulator.snapshot",
                    {
                        "project_id": project_id,
                        "session_id": session_id,
                        "vm_snapshot_projection_hash72": vm_snapshot["projection_hash72"],
                    },
                )
                execution = {
                    "ok": bool(created.get("ok") and run.get("ok") and snap.get("ok")),
                    "created": created,
                    "run": run,
                    "snapshot": snap,
                }
            else:
                execution = {"ok": False, "created": created, "status": "EMULATOR_SESSION_NOT_CREATED"}
        else:
            execution = {"ok": False, "status": "COMPILER_ARTIFACT_NOT_EXECUTABLE", "compilation": compilation}

    lifecycle_evidence = {
        "project_id": project_id,
        "source_hash": source_hash,
        "source_name": request.source_name,
        "detected_media_type": detected_media_type,
        "ingress_receipt_hash72": (ingress.get("receipt") or {}).get("receipt_hash72"),
        "projection_hash72": vm_snapshot["projection_hash72"],
        "ingestion_operation_hash216": vm_snapshot["ingestion_operation_hash216"],
        "workspace_ingress_receipt_hash72": _extract_receipt(workspace_ingress),
        "interpretation_receipt_hash72": _extract_receipt(interpretation),
        "compilation_receipt_hash72": _extract_receipt(compilation),
        "execution_receipt_hash72": _extract_receipt(execution),
        "target": request.target,
        "steps": request.steps,
        "interpretation_scope": interpretation_scope,
    }
    lifecycle_positions = Hash216Genome.positions(
        _canonical_bytes(lifecycle_evidence),
        previous_root=vm_snapshot["ingestion_operation_hash216"],
        sequence=int((ingress.get("receipt") or {}).get("ingestion_epoch") or 0),
    )
    lifecycle_hash216 = Hash216Genome.root(lifecycle_positions)
    lifecycle_receipt_body = {
        "schema": "HHS_VISUAL_IDE_DEVELOPMENT_LIFECYCLE_RECEIPT_V1",
        **lifecycle_evidence,
        "lifecycle_hash216": lifecycle_hash216,
        "hash216_position_count": len(lifecycle_positions),
        "snapshot_bits": vm_snapshot["snapshot_bits"],
        "snapshot_bytes": vm_snapshot["snapshot_bytes"],
        "frontend_mutation_authority": False,
    }
    lifecycle_receipt_hash72 = hash72_digest(
        lifecycle_receipt_body,
        b64decode(vm_snapshot["projection_b64"]),
    )

    software_ok = True
    if detected_media_type in TEXT_MODALITIES:
        software_ok = bool(interpretation and interpretation.get("ok") and compilation and compilation.get("ok") and execution and execution.get("ok"))
    overall_ok = bool(ingress and vm_snapshot.get("ok") and workspace_ingress.get("ok") and software_ok)

    egress_manifest = {
        "schema": "HHS_MULTIMODAL_DEVELOPMENT_EGRESS_MANIFEST_V1",
        "artifact_name": _safe_artifact_name(request.source_name),
        "media_type": "application/vnd.hhs.lifecycle+json",
        "project_id": project_id,
        "source": ingress.get("source"),
        "source_b64": request.source_b64,
        "source_sha256": source_hash,
        "source_media_type": detected_media_type,
        "vm_snapshot": {
            "snapshot_bits": vm_snapshot["snapshot_bits"],
            "snapshot_bytes": vm_snapshot["snapshot_bytes"],
            "vm81_cells": vm_snapshot["vm81_cells"],
            "bits_per_cell": vm_snapshot["bits_per_cell"],
            "projection_b64": vm_snapshot["projection_b64"],
            "projection_hash72": vm_snapshot["projection_hash72"],
            "ingestion_operation_hash216": vm_snapshot["ingestion_operation_hash216"],
            "ingestion_positions_hash216": vm_snapshot["ingestion_positions_hash216"],
        },
        "compiled_artifact": (compilation or {}).get("result", {}).get("artifact") if compilation else None,
        "execution_snapshot": (execution or {}).get("snapshot") if execution else None,
        "lifecycle_hash216": lifecycle_hash216,
        "lifecycle_positions_hash216": list(lifecycle_positions),
        "lifecycle_receipt_hash72": lifecycle_receipt_hash72,
        "original_source_preserved": True,
        "projection_replaces_source": False,
    }

    return {
        "schema": "HHS_VISUAL_IDE_DEVELOPMENT_LIFECYCLE_RESULT_V1",
        "ok": overall_ok,
        "status": "HHS_DEVELOPMENT_LIFECYCLE_COMPLETED" if overall_ok else "HHS_DEVELOPMENT_LIFECYCLE_PARTIAL",
        "project": {
            "project_id": project_id,
            "name": project.get("name"),
            "status": project.get("status"),
        },
        "ingress": ingress,
        "workspace_ingress": workspace_ingress,
        "vm_snapshot": vm_snapshot,
        "interpretation": interpretation,
        "compilation": compilation,
        "execution": execution,
        "receipts": {
            "ingress_receipt_hash72": lifecycle_evidence["ingress_receipt_hash72"],
            "workspace_ingress_receipt_hash72": lifecycle_evidence["workspace_ingress_receipt_hash72"],
            "interpretation_receipt_hash72": lifecycle_evidence["interpretation_receipt_hash72"],
            "compilation_receipt_hash72": lifecycle_evidence["compilation_receipt_hash72"],
            "execution_receipt_hash72": lifecycle_evidence["execution_receipt_hash72"],
            "lifecycle_receipt_hash72": lifecycle_receipt_hash72,
            "lifecycle_hash216": lifecycle_hash216,
        },
        "egress": {
            "artifact_name": egress_manifest["artifact_name"],
            "media_type": egress_manifest["media_type"],
            "manifest": egress_manifest,
        },
        "frontend_result_fabricated": False,
        "canonical_authorities": [
            "PASS165_MULTIMODAL_LEARNING_SERVICE",
            "WORKSPACE_AUTHORITY_LOOP",
            "HHS_INTERPRETER",
            "HHS_IR_COMPILER",
            "VM81_VISUAL_EMULATOR",
            "HASH72_RECEIPT",
            "HASH216_INDEX",
        ],
    }


@router.post("/replay")
def replay_development_lifecycle() -> Dict[str, Any]:
    from hhs_backend import server as canonical

    try:
        pass165_replay = SERVICE.replay_ingestion()
    except IngestionError as exc:
        raise HTTPException(status_code=409, detail={"classification": exc.classification}) from exc
    return {
        "schema": "HHS_VISUAL_IDE_DEVELOPMENT_REPLAY_RESULT_V1",
        "ok": bool(pass165_replay.get("deterministic_replay")),
        "pass165_replay": pass165_replay,
        "workspace_command_history": canonical.WORKSPACE_AUTHORITY_LOOP.command_history[-64:],
        "history_erased": False,
        "frontend_result_fabricated": False,
    }
