"""Lineage-preserving packaging and export admission for Pass 077."""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple
import zipfile

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable

from .hhs_pass077_contracts_v1 import (
    ARTIFACT_MANIFEST_SCHEMA,
    COMPILED_ARTIFACT_SCHEMA,
    EXPORT_PACKAGE_SCHEMA,
    LINEAGE_CERTIFICATE_SCHEMA,
    TARGET_ID,
    rooted,
    validate_registered_target_contract,
    verify_rooted,
)
from .hhs_portable_bytecode_v1 import COMPILER_IDENTITY, COMPILER_VERSION, artifact_bytes, canonical_json_bytes


def transition_artifact_status(
    artifact: Mapping[str, Any], *, status: str, equivalence_receipt_root_hash72: str = "",
    lineage_certificate_root_hash72: str = "", export_package_root_hash72: str = "",
) -> Dict[str, Any]:
    if artifact.get("schema") != COMPILED_ARTIFACT_SCHEMA or not verify_rooted("pass077_compiled_artifact", artifact, "artifact_root_hash72"):
        raise ContractError("REJECT_COMPILED_ARTIFACT_ROOT_MISMATCH")
    current = str(artifact.get("status") or "")
    allowed = {
        "CANDIDATE": {"VALIDATED", "REJECTED"},
        "VALIDATED": {"ADMITTED", "REJECTED", "REVOKED"},
        "ADMITTED": {"REVOKED"},
        "REJECTED": set(),
        "REVOKED": set(),
    }
    if status not in allowed.get(current, set()):
        raise ContractError(f"REJECT_ARTIFACT_STATUS_TRANSITION:{current}->{status}")
    body = deepcopy(dict(artifact)); body.pop("artifact_root_hash72", None)
    body["status"] = status
    if equivalence_receipt_root_hash72:
        body["semantic_equivalence_receipt_root_hash72"] = equivalence_receipt_root_hash72
    if lineage_certificate_root_hash72:
        body["lineage_certificate_root_hash72"] = lineage_certificate_root_hash72
    if export_package_root_hash72:
        body["export_package_root_hash72"] = export_package_root_hash72
    body["deployment_authority_conferred"] = False
    return rooted("pass077_compiled_artifact", body, "artifact_root_hash72")


def build_lineage_certificate(
    *, certificate_id: str, artifact: Mapping[str, Any], project_root_hash72: str,
    requirement_root_hash72: str, source_artifact_root_hash72: str,
    typed_ir_root_hash72: str, executable_ir_root_hash72: str,
    compilation_plan_root_hash72: str, target_contract_root_hash72: str,
    interpreter_reference_execution_root_hash72: str, compiled_execution_root_hash72: str,
    semantic_equivalence_receipt_root_hash72: str, test_receipt_root_hash72: str,
    genesis_source_root_hash72: Optional[str] = None,
    parent_artifact_root_hash72: Optional[str] = None,
) -> Dict[str, Any]:
    artifact_bytes(artifact)
    if artifact.get("status") != "VALIDATED":
        raise ContractError("REJECT_LINEAGE_FOR_UNVALIDATED_ARTIFACT")
    if bool(genesis_source_root_hash72) == bool(parent_artifact_root_hash72):
        raise ContractError("REJECT_LINEAGE_REQUIRES_EXACTLY_ONE_GENESIS_OR_PARENT")
    required = {
        "project_root_hash72": project_root_hash72,
        "requirement_root_hash72": requirement_root_hash72,
        "source_artifact_root_hash72": source_artifact_root_hash72,
        "typed_ir_root_hash72": typed_ir_root_hash72,
        "executable_ir_root_hash72": executable_ir_root_hash72,
        "compilation_plan_root_hash72": compilation_plan_root_hash72,
        "target_contract_root_hash72": target_contract_root_hash72,
        "interpreter_reference_execution_root_hash72": interpreter_reference_execution_root_hash72,
        "compiled_execution_root_hash72": compiled_execution_root_hash72,
        "semantic_equivalence_receipt_root_hash72": semantic_equivalence_receipt_root_hash72,
        "test_receipt_root_hash72": test_receipt_root_hash72,
    }
    missing = [key for key, value in required.items() if not str(value or "")]
    if missing:
        raise ContractError("REJECT_ARTIFACT_LINEAGE_GAP:" + ",".join(missing))
    body = {
        "schema": LINEAGE_CERTIFICATE_SCHEMA,
        "certificate_id": certificate_id,
        "artifact_id": artifact.get("artifact_id"),
        "artifact_root_hash72": artifact.get("artifact_payload_root_hash72"),
        "candidate_artifact_object_root_hash72": artifact.get("artifact_root_hash72"),
        "artifact_content_sha256": artifact.get("artifact_content_sha256"),
        **required,
        "parent_artifact_root_hash72": parent_artifact_root_hash72,
        "genesis_source_root_hash72": genesis_source_root_hash72,
        "compiler_identity": COMPILER_IDENTITY,
        "compiler_version": COMPILER_VERSION,
        "sha256_is_transport_integrity_not_hhs_lineage": True,
        "hash72_is_derivation_witness_not_transport_digest": True,
        "lineage_metadata_is_not_program_semantics": True,
        "embedded_validator_self_authorizes": False,
    }
    return rooted("pass077_artifact_lineage_certificate", body, "lineage_root_hash72")


def verify_lineage_certificate(value: Mapping[str, Any]) -> bool:
    if value.get("schema") != LINEAGE_CERTIFICATE_SCHEMA or not verify_rooted("pass077_artifact_lineage_certificate", value, "lineage_root_hash72"):
        return False
    genesis = bool(value.get("genesis_source_root_hash72")); parent = bool(value.get("parent_artifact_root_hash72"))
    return genesis != parent and value.get("embedded_validator_self_authorizes") is False


def _json_file(value: Mapping[str, Any]) -> bytes:
    return json.dumps(stable(value), indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n"


def _deterministic_zip(files: Mapping[str, bytes]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(filename=name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.create_system = 3
            archive.writestr(info, files[name])
    return output.getvalue()


def build_export_package(
    *, package_id: str, artifact: Mapping[str, Any], lineage_certificate: Mapping[str, Any],
    target_contract: Mapping[str, Any], compilation_request: Mapping[str, Any],
    compilation_plan: Mapping[str, Any], target_ir: Mapping[str, Any], optimization_proof: Mapping[str, Any],
    equivalence_receipt: Mapping[str, Any], test_receipt: Mapping[str, Any],
    executable_ir: Mapping[str, Any], interpreter_execution: Mapping[str, Any],
    compiled_execution: Mapping[str, Any], interpreter_projection: Mapping[str, Any],
    compiled_projection: Mapping[str, Any], verifier_source: str,
) -> Tuple[Dict[str, Any], bytes, Dict[str, bytes]]:
    data = artifact_bytes(artifact)
    if artifact.get("status") != "VALIDATED":
        raise ContractError("REJECT_PACKAGE_UNVALIDATED_ARTIFACT")
    if not verify_lineage_certificate(lineage_certificate):
        raise ContractError("REJECT_PACKAGE_INVALID_LINEAGE_CERTIFICATE")
    registration = validate_registered_target_contract(target_contract)
    if equivalence_receipt.get("status") != "SEMANTIC_IDENTITY_VERIFIED":
        raise ContractError("REJECT_PACKAGE_WITHOUT_SEMANTIC_EQUIVALENCE")
    if lineage_certificate.get("artifact_content_sha256") != hashlib.sha256(data).hexdigest():
        raise ContractError("REJECT_PACKAGE_ARTIFACT_DIGEST_MISMATCH")
    files: Dict[str, bytes] = {
        "artifact/program.hhsbc": data,
        "manifest/HHS_COMPILED_ARTIFACT_V1.json": _json_file(artifact),
        "manifest/HHS_ARTIFACT_LINEAGE_CERTIFICATE_V1.json": _json_file(lineage_certificate),
        "manifest/HHS_TARGET_CONTRACT_V1.json": _json_file(registration),
        "receipts/compilation_request.json": _json_file(compilation_request),
        "receipts/compilation_receipt.json": _json_file(compilation_plan),
        "receipts/optimization_proof.json": _json_file(optimization_proof),
        "receipts/test_receipt.json": _json_file(test_receipt),
        "receipts/equivalence_receipt.json": _json_file(equivalence_receipt),
        "receipts/compiled_execution.json": _json_file(compiled_execution),
        "reference/executable_ir.json": _json_file(executable_ir),
        "reference/target_ir.json": _json_file(target_ir),
        "reference/interpreter_execution.json": _json_file(interpreter_execution),
        "reference/interpreter_semantic_projection.json": _json_file(interpreter_projection),
        "reference/compiled_semantic_projection.json": _json_file(compiled_projection),
        "verifier/verify_artifact.py": verifier_source.encode("utf-8"),
        "README.md": (
            "# HHS Pass 077 deterministic artifact package\n\n"
            "The artifact carries evidence for independent verification. It does not self-authorize.\n\n"
            "Run: `python verifier/verify_artifact.py .` after extracting this package.\n"
        ).encode("utf-8"),
    }
    file_records = [
        {"path": name, "sha256": hashlib.sha256(content).hexdigest(), "size_bytes": len(content)}
        for name, content in sorted(files.items())
    ]
    manifest_body = {
        "schema": ARTIFACT_MANIFEST_SCHEMA,
        "package_id": package_id,
        "artifact_path": "artifact/program.hhsbc",
        "artifact_payload_root_hash72": artifact.get("artifact_payload_root_hash72"),
        "artifact_content_sha256": artifact.get("artifact_content_sha256"),
        "target_id": TARGET_ID,
        "target_contract_root_hash72": registration.get("contract_root_hash72"),
        "lineage_certificate_root_hash72": lineage_certificate.get("lineage_root_hash72"),
        "equivalence_receipt_root_hash72": equivalence_receipt.get("receipt_root_hash72"),
        "expected_semantic_projection_root_hash72": interpreter_projection.get("semantic_projection_root_hash72"),
        "package_status": "VALIDATED_PENDING_EXTERNAL_VERIFICATION",
        "embedded_validator_self_authorizes": False,
        "independent_verifier_required": True,
        "files": file_records,
    }
    manifest = rooted("pass077_artifact_manifest", manifest_body, "manifest_root_hash72")
    files["manifest/HHS_ARTIFACT_MANIFEST_V1.json"] = _json_file(manifest)
    package_bytes = _deterministic_zip(files)
    package_body = {
        "schema": EXPORT_PACKAGE_SCHEMA,
        "package_id": package_id,
        "status": "VALIDATED",
        "manifest_root_hash72": manifest.get("manifest_root_hash72"),
        "artifact_payload_root_hash72": artifact.get("artifact_payload_root_hash72"),
        "lineage_certificate_root_hash72": lineage_certificate.get("lineage_root_hash72"),
        "equivalence_receipt_root_hash72": equivalence_receipt.get("receipt_root_hash72"),
        "package_content_sha256": hashlib.sha256(package_bytes).hexdigest(),
        "package_size_bytes": len(package_bytes),
        "package_bytes_base64": base64.b64encode(package_bytes).decode("ascii"),
        "reproducible_from_committed_inputs": True,
        "thread_context_required": False,
        "llm_context_window_required": False,
        "embedded_validator_self_authorizes": False,
        "deployment_authority_conferred": False,
    }
    package = rooted("pass077_export_package", package_body, "package_root_hash72")
    return package, package_bytes, files


def package_bytes(value: Mapping[str, Any]) -> bytes:
    if value.get("schema") != EXPORT_PACKAGE_SCHEMA or not verify_rooted("pass077_export_package", value, "package_root_hash72"):
        raise ContractError("REJECT_EXPORT_PACKAGE_ROOT_MISMATCH")
    try:
        data = base64.b64decode(str(value.get("package_bytes_base64") or ""), validate=True)
    except Exception as exc:
        raise ContractError("REJECT_EXPORT_PACKAGE_BASE64") from exc
    if len(data) != value.get("package_size_bytes") or hashlib.sha256(data).hexdigest() != value.get("package_content_sha256"):
        raise ContractError("REJECT_EXPORT_PACKAGE_TAMPERED")
    return data


def admit_export(
    *, package: Mapping[str, Any], artifact: Mapping[str, Any], external_verification: Mapping[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    package_bytes(package); artifact_bytes(artifact)
    if package.get("status") != "VALIDATED":
        raise ContractError("REJECT_EXPORT_PACKAGE_NOT_VALIDATED")
    if external_verification.get("status") != "REEXECUTED_SEMANTIC_EQUIVALENCE":
        raise ContractError("REJECT_EXPORT_WITHOUT_INDEPENDENT_REEXECUTION")
    package_body = deepcopy(dict(package)); package_body.pop("package_root_hash72", None)
    package_body["status"] = "ADMITTED"
    package_body["external_verification_root_hash72"] = external_verification.get("verification_root_hash72")
    admitted_package = rooted("pass077_export_package", package_body, "package_root_hash72")
    admitted_artifact = transition_artifact_status(
        artifact, status="ADMITTED",
        lineage_certificate_root_hash72=package.get("lineage_certificate_root_hash72"),
        export_package_root_hash72=admitted_package.get("package_root_hash72"),
    )
    registry_body = {
        "schema": "HHS_ADMITTED_ARTIFACT_REGISTRY_ENTRY_V1",
        "artifact_id": artifact.get("artifact_id"),
        "artifact_payload_root_hash72": artifact.get("artifact_payload_root_hash72"),
        "admitted_artifact_object_root_hash72": admitted_artifact.get("artifact_root_hash72"),
        "admitted_package_root_hash72": admitted_package.get("package_root_hash72"),
        "external_verification_root_hash72": external_verification.get("verification_root_hash72"),
        "status": "ADMITTED",
        "deployment_authority_conferred": False,
    }
    registry_entry = rooted("pass077_admitted_artifact_registry_entry", registry_body, "registry_entry_root_hash72")
    return admitted_artifact, {"package": admitted_package, "registry_entry": registry_entry}
