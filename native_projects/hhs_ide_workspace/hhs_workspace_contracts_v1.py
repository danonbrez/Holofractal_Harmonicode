"""Canonical contracts for the Pass 074 unified HHS workspace boundary.

All identities in this product are repository/path independent product-local
commitments. They do not claim Pass 072 foundation Hash72 authority.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Sequence
import hashlib
import json
import re

PASS_ID = "PASS_074"
VERSION = "PASS_074_UNIFIED_HHS_IDE_WORKSPACE_V1"
FROZEN_PASS072_SYSTEM_ROOT_HASH72 = (
    "ZF9bto?tV>P(KcFPL5L+csyy!jxdrAaadua1a!w-uwug8/MeMSqSS3*R>lXIefi)nyjXpc+)"
)
REQUEST_SCHEMA = "HHS_UNIFIED_RUNTIME_REQUEST_V1"
RESPONSE_SCHEMA = "HHS_UNIFIED_RUNTIME_RESPONSE_V1"
PROJECT_SCHEMA = "HHS_NATIVE_WORKSPACE_PROJECT_V1"
SESSION_SCHEMA = "HHS_WORKSPACE_SESSION_V1"
BUFFER_SCHEMA = "HHS_EDITOR_BUFFER_V1"
OBJECT_INDEX_SCHEMA = "HHS_PROJECT_OBJECT_INDEX_V1"
EVENT_SCHEMA = "HHS_RUNTIME_EVENT_STREAM_EVENT_V1"
OPERATION_REGISTRY_SCHEMA = "HHS_API_OPERATION_REGISTRY_V1"
REPLAY_CAPSULE_SCHEMA = "HHS_WORKSPACE_REPLAY_CAPSULE_V1"

DEVELOPMENT_PROTOCOL_SCHEMA = "HHS_OPEN_ENDED_NATIVE_DEVELOPMENT_PROTOCOL_V1"
AGENT_SCHEMA = "HHS_DEVELOPMENT_AGENT_IDENTITY_V1"
CHANGE_PROPOSAL_SCHEMA = "HHS_REPOSITORY_CHANGE_PROPOSAL_V1"
ALIGNMENT_DECISION_SCHEMA = "HHS_POST_FREEZE_ALIGNMENT_DECISION_V1"
TEST_RECORD_SCHEMA = "HHS_TEST_EVIDENCE_RECORD_V1"
HANDOFF_SCHEMA = "HHS_AGENT_HANDOFF_CAPSULE_V1"
HEALING_PLAN_SCHEMA = "HHS_BOUNDED_SELF_HEALING_PLAN_V1"
PRODUCT_COMMITMENT_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()^=!?>"

OPERATION_CLASSES = {"INGRESS", "QUERY", "EXECUTE", "MUTATE", "EMULATE", "COMPILE"}
RESPONSE_STATUSES = {"ADMITTED", "REJECTED", "PARTIAL", "UNAVAILABLE"}
IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,160}$")

class ContractError(ValueError):
    pass


def stable(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(stable(value), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def product_root(label: str, payload: Any) -> str:
    material = canonical_bytes({"label": label, "payload": stable(payload)})
    value = int.from_bytes(hashlib.sha256(material).digest(), "big")
    base = len(PRODUCT_COMMITMENT_ALPHABET)
    chars = []
    for _ in range(72):
        value, remainder = divmod(value, base)
        chars.append(PRODUCT_COMMITMENT_ALPHABET[remainder])
    return "".join(reversed(chars))


def product_witness(label: str, payload: Any) -> Dict[str, Any]:
    return {
        "schema": "HHS_NATIVE_PRODUCT_COMMITMENT_WITNESS_V1",
        "authority": "PRODUCT_LOCAL_COMMITMENT_NOT_FOUNDATION_HASH72_AUTHORITY",
        "label": label,
        "digest72": product_root(label, payload),
        "sha256": sha256({"label": label, "payload": stable(payload)}),
        "product_local_commitment_not_foundation_authority": True,
    }


def require_identifier(name: str, value: Any) -> str:
    text = str(value or "")
    if not IDENTIFIER.fullmatch(text):
        raise ContractError(f"REJECT_INVALID_{name.upper()}:{text}")
    return text


def canonical_request(payload: Mapping[str, Any]) -> Dict[str, Any]:
    value = deepcopy(dict(payload))
    if value.get("schema") != REQUEST_SCHEMA:
        raise ContractError("REJECT_REQUEST_SCHEMA_MISMATCH")
    value["request_id"] = require_identifier("request_id", value.get("request_id"))
    value["project_id"] = require_identifier("project_id", value.get("project_id"))
    value["session_id"] = require_identifier("session_id", value.get("session_id"))
    operation_class = str(value.get("operation_class", ""))
    if operation_class not in OPERATION_CLASSES:
        raise ContractError(f"REJECT_OPERATION_CLASS:{operation_class}")
    value["operation_class"] = operation_class
    value["source_object_refs"] = [require_identifier("source_object_ref", x) for x in value.get("source_object_refs", [])]
    value["payload"] = stable(value.get("payload", {}))
    value["role_contract_ref"] = str(value.get("role_contract_ref") or "")
    value["task_assignment_ref"] = str(value.get("task_assignment_ref") or "")
    value["capability_lease_ref"] = str(value.get("capability_lease_ref") or "")
    value["expected_response_types"] = [str(x) for x in value.get("expected_response_types", [])]
    unsigned = {k: v for k, v in value.items() if k != "request_root_hash72"}
    observed = product_root("hhs_unified_runtime_request_v1", unsigned)
    supplied = str(value.get("request_root_hash72") or "")
    if supplied and supplied != observed:
        raise ContractError("REJECT_REQUEST_ROOT_MISMATCH")
    value["request_root_hash72"] = observed
    return stable(value)


def make_request(
    *, request_id: str, project_id: str, session_id: str, operation_class: str,
    operation_id: str, payload: Mapping[str, Any] | None = None,
    source_object_refs: Sequence[str] = (), role_contract_ref: str = "",
    task_assignment_ref: str = "", capability_lease_ref: str = "",
    expected_response_types: Sequence[str] = (), client_surface: str = "EXTERNAL",
) -> Dict[str, Any]:
    value = {
        "schema": REQUEST_SCHEMA,
        "request_id": request_id,
        "project_id": project_id,
        "session_id": session_id,
        "operation_class": operation_class,
        "source_object_refs": list(source_object_refs),
        "payload": {"operation_id": operation_id, **dict(payload or {})},
        "role_contract_ref": role_contract_ref,
        "task_assignment_ref": task_assignment_ref,
        "capability_lease_ref": capability_lease_ref,
        "expected_response_types": list(expected_response_types),
        "client_surface": client_surface,
    }
    return canonical_request(value)


def response_envelope(
    request: Mapping[str, Any], *, status: str, result_object_refs: Iterable[str] = (),
    artifact_refs: Iterable[str] = (), receipt_refs: Iterable[str] = (),
    diagnostics: Iterable[Mapping[str, Any]] = (), runtime_state_ref: str = "",
    result: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    if status not in RESPONSE_STATUSES:
        raise ContractError(f"REJECT_RESPONSE_STATUS:{status}")
    body = {
        "schema": RESPONSE_SCHEMA,
        "request_id": request["request_id"],
        "project_id": request["project_id"],
        "session_id": request["session_id"],
        "status": status,
        "result_object_refs": list(result_object_refs),
        "artifact_refs": list(artifact_refs),
        "receipt_refs": list(receipt_refs),
        "diagnostics": [stable(x) for x in diagnostics],
        "runtime_state_ref": runtime_state_ref,
        "result": stable(result or {}),
        "request_root_hash72": request["request_root_hash72"],
    }
    body["response_root_hash72"] = product_root("hhs_unified_runtime_response_v1", body)
    return stable(body)
