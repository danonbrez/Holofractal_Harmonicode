"""Product-local contracts for Pass 076.

Pass 076 consumes the frozen Pass 072 platform and the Pass 074/075 native
products without modifying them. All roots here are product-local commitment
witnesses and do not claim foundation Hash72 authority.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    ContractError,
    product_root,
    sha256,
    stable,
)

PASS_ID = "PASS_076"
VERSION = "PASS_076_HARMONICODE_INTERPRETER_AND_BOUNDED_REPAIR_V1"
PARENT_NATIVE_PASS = "PASS_075"
EXECUTABLE_IR_SCHEMA = "HHS_EXECUTABLE_IR_V1"
EXECUTABLE_STATEMENT_SCHEMA = "HHS_EXECUTABLE_IR_STATEMENT_V1"
INTERPRETER_STATE_SCHEMA = "HHS_HARMONICODE_INTERPRETER_STATE_V1"
INTERPRETER_STEP_RECEIPT_SCHEMA = "HHS_INTERPRETER_STEP_RECEIPT_V1"
INTERPRETER_RUN_SCHEMA = "HHS_INTERPRETER_EXECUTION_RUN_V1"
INTERPRETER_REPLAY_SCHEMA = "HHS_INTERPRETER_REPLAY_VERIFICATION_V1"
REPAIR_TRANSACTION_SCHEMA = "HHS_BOUNDED_PRODUCT_REPAIR_TRANSACTION_V1"
REPAIR_ROLLBACK_SCHEMA = "HHS_PRODUCT_REPAIR_ROLLBACK_CAPSULE_V1"
REPAIR_TEST_SCHEMA = "HHS_REPAIR_VALIDATION_EXECUTION_RECEIPT_V1"
REPLAY_CAPSULE_SCHEMA = "HHS_PASS_076_INTERPRETER_REPLAY_CAPSULE_V1"
PROGRAM_GRAPH_SCHEMA = "HHS_NATIVE_PROGRAM_REACHABILITY_GRAPH_V1"

MAX_EXECUTION_STEPS = 256
MAX_REPAIR_OPERATIONS = 16
ALLOWED_REPAIR_PREFIX = "native_projects/"
FORBIDDEN_FOUNDATION_PREFIXES = (
    "hhs_foundation/",
    "hhs_runtime/c/",
    "hhs_runtime/include/",
    "hhs_runtime/src/",
)
REQUIRED_INVARIANT_EXPECTATIONS = {
    "Δe": {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1},
    "Ψ": {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1},
    "Θ15": {"type": "BOOLEAN", "value": True},
    "Ω": {"type": "BOOLEAN", "value": True},
}


def rooted(label: str, payload: Mapping[str, Any], root_field: str) -> Dict[str, Any]:
    body = stable(dict(payload))
    body[root_field] = product_root(label, body)
    return stable(body)


def verify_rooted(label: str, payload: Mapping[str, Any], root_field: str) -> bool:
    body = deepcopy(dict(payload))
    supplied = str(body.pop(root_field, ""))
    return bool(supplied) and supplied == product_root(label, body)


def require_product_path(path: Any) -> str:
    value = str(path or "").replace("\\", "/")
    if not value or value.startswith("/") or ":" in value.split("/")[0] or ".." in value.split("/"):
        raise ContractError(f"REJECT_NON_RELATIVE_PRODUCT_PATH:{value}")
    if any(value.startswith(prefix) for prefix in FORBIDDEN_FOUNDATION_PREFIXES):
        raise ContractError(f"REJECT_REPAIR_TARGETS_FROZEN_FOUNDATION:{value}")
    if not value.startswith(ALLOWED_REPAIR_PREFIX):
        raise ContractError(f"REJECT_REPAIR_OUTSIDE_NATIVE_PRODUCT_NAMESPACE:{value}")
    return value


def content_identity(text: str) -> Dict[str, str]:
    return {
        "sha256": sha256(text),
        "product_root_hash72": product_root("pass076_product_content", {"text": text}),
    }
