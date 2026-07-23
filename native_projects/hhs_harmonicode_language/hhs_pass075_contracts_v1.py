"""Product-local Pass 075 contracts.

Pass 075 consumes the frozen Pass 072 platform and the Pass 074 unified
workspace without modifying either parent. Commitments are native-product
commitments and do not claim foundation Hash72 authority.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    ContractError,
    product_root,
    sha256,
    stable,
)

PASS_ID = "PASS_075"
VERSION = "PASS_075_HARMONICODE_TYPED_IR_AND_TEST_ACCELERATION_V1"
PARENT_NATIVE_PASS = "PASS_074"
TYPED_IR_SCHEMA = "HHS_TYPED_IR_V1"
LANGUAGE_DOCUMENT_SCHEMA = "HHS_HARMONICODE_LANGUAGE_DOCUMENT_V1"
LANGUAGE_VALIDATION_SCHEMA = "HHS_TYPED_IR_VALIDATION_V1"
TYPED_IR_ARTIFACT_SCHEMA = "HHS_TYPED_IR_ARTIFACT_V1"
TEST_ACCELERATION_SCHEMA = "HHS_AGENT_COORDINATED_TEST_ACCELERATION_PLAN_V1"
LANGUAGE_REPLAY_CAPSULE_SCHEMA = "HHS_PASS_075_LANGUAGE_REPLAY_CAPSULE_V1"
LANGUAGE_PROGRAM_GRAPH_SCHEMA = "HHS_NATIVE_PROGRAM_REACHABILITY_GRAPH_V1"

REQUIRED_INVARIANT_BINDINGS = (
    "Δe=0",
    "Ψ=0",
    "Θ15=true",
    "Ω=true",
)

TYPE_IDS = {
    "EXACT_INTEGER",
    "EXACT_RATIONAL",
    "BOOLEAN",
    "SYMBOL",
    "ORDERED_PRODUCT",
    "LIST",
    "MATRIX",
    "FUNCTION_CALL",
    "SYMBOLIC_EXPRESSION",
    "CONSTRAINT",
    "GATE",
}

EFFECTS = {
    "PURE_SYMBOLIC",
    "AUDIT_REQUIRED",
    "EXTERNAL_DECLARED",
}


def rooted(label: str, payload: Mapping[str, Any], root_field: str) -> Dict[str, Any]:
    body = stable(dict(payload))
    body[root_field] = product_root(label, body)
    return stable(body)


def verify_rooted(label: str, payload: Mapping[str, Any], root_field: str) -> bool:
    body = dict(payload)
    supplied = str(body.pop(root_field, ""))
    return bool(supplied) and supplied == product_root(label, body)


def require_relative_path(value: Any) -> str:
    text = str(value or "")
    if not text or text.startswith(("/", "\\")) or ":\\" in text or ".." in text.split("/"):
        raise ContractError(f"REJECT_NON_RELATIVE_REPOSITORY_PATH:{text}")
    return text.replace("\\", "/")


def source_commitment(text: str) -> Dict[str, str]:
    return {
        "sha256": sha256(text),
        "product_root_hash72": product_root("pass075_harmonicode_source", {"text": text}),
    }
