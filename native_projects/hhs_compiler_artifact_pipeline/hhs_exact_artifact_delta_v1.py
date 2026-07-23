"""Deterministic auditable delta packaging for exact artifact reconstruction."""
from __future__ import annotations

import base64
import hashlib
from typing import Any, Dict, Mapping, Tuple

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable

from .hhs_artifact_lineage_pipeline_v1 import verify_lineage_certificate
from .hhs_pass077_contracts_v1 import DELTA_RECEIPT_SCHEMA, DELTA_SCHEMA, rooted, verify_rooted
from .hhs_portable_bytecode_v1 import artifact_bytes


def create_delta(*, delta_id: str, base_artifact: Mapping[str, Any], target_artifact: Mapping[str, Any], target_lineage: Mapping[str, Any]) -> Dict[str, Any]:
    base = artifact_bytes(base_artifact)
    target = artifact_bytes(target_artifact)
    if not verify_lineage_certificate(target_lineage):
        raise ContractError("REJECT_DELTA_WITHOUT_TARGET_LINEAGE")
    if target_lineage.get("artifact_root_hash72") != target_artifact.get("artifact_payload_root_hash72"):
        raise ContractError("REJECT_DELTA_TARGET_LINEAGE_MISMATCH")
    prefix = 0
    while prefix < len(base) and prefix < len(target) and base[prefix] == target[prefix]:
        prefix += 1
    suffix = 0
    while (
        suffix < len(base) - prefix and suffix < len(target) - prefix
        and base[len(base) - 1 - suffix] == target[len(target) - 1 - suffix]
    ):
        suffix += 1
    delete_length = len(base) - prefix - suffix
    insert = target[prefix:len(target) - suffix if suffix else len(target)]
    body = {
        "schema": DELTA_SCHEMA,
        "delta_id": delta_id,
        "base_artifact_root_hash72": base_artifact.get("artifact_payload_root_hash72"),
        "base_artifact_content_sha256": hashlib.sha256(base).hexdigest(),
        "target_artifact_root_hash72": target_artifact.get("artifact_payload_root_hash72"),
        "target_artifact_content_sha256": hashlib.sha256(target).hexdigest(),
        "target_lineage_certificate_root_hash72": target_lineage.get("lineage_root_hash72"),
        "ordered_byte_range_replacements": [{
            "offset": prefix,
            "delete_length": delete_length,
            "insert_bytes_base64": base64.b64encode(insert).decode("ascii"),
        }],
        "format": "ORDERED_BYTE_RANGE_REPLACEMENTS_V1",
        "deployment_authority_conferred": False,
    }
    return rooted("pass077_exact_artifact_delta", body, "delta_root_hash72")


def apply_delta(*, base_artifact: Mapping[str, Any], delta: Mapping[str, Any]) -> Tuple[bytes, Dict[str, Any]]:
    base = artifact_bytes(base_artifact)
    if not verify_rooted("pass077_exact_artifact_delta", delta, "delta_root_hash72"):
        raise ContractError("REJECT_DELTA_ROOT_MISMATCH")
    if delta.get("base_artifact_root_hash72") != base_artifact.get("artifact_payload_root_hash72"):
        raise ContractError("REJECT_DELTA_BASE_ROOT_MISMATCH")
    if delta.get("base_artifact_content_sha256") != hashlib.sha256(base).hexdigest():
        raise ContractError("REJECT_DELTA_BASE_ROOT_MISMATCH")
    current = base
    previous_end = -1
    for replacement in delta.get("ordered_byte_range_replacements", []):
        offset = int(replacement.get("offset", -1)); delete_length = int(replacement.get("delete_length", -1))
        if offset < 0 or delete_length < 0 or offset < previous_end or offset + delete_length > len(current):
            raise ContractError("REJECT_DELTA_INVALID_ORDERED_REPLACEMENT")
        try:
            insert = base64.b64decode(str(replacement.get("insert_bytes_base64") or ""), validate=True)
        except Exception as exc:
            raise ContractError("REJECT_DELTA_INSERT_ENCODING") from exc
        current = current[:offset] + insert + current[offset + delete_length:]
        previous_end = offset + len(insert)
    observed = hashlib.sha256(current).hexdigest()
    matches = observed == delta.get("target_artifact_content_sha256")
    body = {
        "schema": DELTA_RECEIPT_SCHEMA,
        "delta_root_hash72": delta.get("delta_root_hash72"),
        "base_artifact_root_hash72": base_artifact.get("artifact_payload_root_hash72"),
        "target_artifact_root_hash72": delta.get("target_artifact_root_hash72"),
        "observed_target_content_sha256": observed,
        "expected_target_content_sha256": delta.get("target_artifact_content_sha256"),
        "exact_target_bytes_reconstructed": matches,
        "status": "EXACT_RECONSTRUCTION_VERIFIED" if matches else "REJECTED",
        "deployment_authority_conferred": False,
    }
    receipt = rooted("pass077_delta_reconstruction_receipt", body, "reconstruction_receipt_root_hash72")
    if not matches:
        raise ContractError("REJECT_DELTA_RECONSTRUCTION_DIGEST_MISMATCH")
    return current, receipt
