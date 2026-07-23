"""Bounded, reversible, product-local repair primitives for Pass 076."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable

from .hhs_pass076_contracts_v1 import (
    MAX_REPAIR_OPERATIONS,
    REPAIR_ROLLBACK_SCHEMA,
    REPAIR_TEST_SCHEMA,
    REPAIR_TRANSACTION_SCHEMA,
    require_product_path,
    rooted,
    verify_rooted,
)


def validate_healing_plan(plan: Mapping[str, Any], *, target_path: str) -> str:
    path = require_product_path(target_path)
    if plan.get("schema") != "HHS_BOUNDED_SELF_HEALING_PLAN_V1":
        raise ContractError("REJECT_REPAIR_HEALING_PLAN_SCHEMA")
    if not verify_rooted("pass074_bounded_healing_plan", plan, "healing_plan_root_hash72"):
        raise ContractError("REJECT_REPAIR_HEALING_PLAN_ROOT")
    if plan.get("foundation_mutation_permitted") is not False:
        raise ContractError("REJECT_REPAIR_PLAN_PERMITS_FOUNDATION_MUTATION")
    if plan.get("rollback_required") is not True:
        raise ContractError("REJECT_REPAIR_PLAN_WITHOUT_ROLLBACK")
    scope = [require_product_path(x) for x in plan.get("repair_scope", [])]
    if not any(path == item or path.startswith(item.rstrip("/") + "/") or item.startswith(path.rstrip("/") + "/") for item in scope):
        raise ContractError("REJECT_REPAIR_TARGET_OUTSIDE_DECLARED_SCOPE")
    return path


def apply_exact_replacements(source: str, replacements: Iterable[Mapping[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    operations = [deepcopy(dict(x)) for x in replacements]
    if not operations or len(operations) > MAX_REPAIR_OPERATIONS:
        raise ContractError("REJECT_REPAIR_OPERATION_BOUND")
    current = source
    receipts: List[Dict[str, Any]] = []
    for index, operation in enumerate(operations):
        old = str(operation.get("old") or "")
        new = str(operation.get("new") or "")
        expected = int(operation.get("expected_count", 1))
        if not old or old == new or expected <= 0:
            raise ContractError(f"REJECT_INVALID_REPAIR_REPLACEMENT:{index}")
        observed = current.count(old)
        if observed != expected:
            raise ContractError(f"REJECT_REPAIR_EXPECTED_COUNT_MISMATCH:{index}:{expected}:{observed}")
        before_root = product_root("pass076_repair_intermediate", {"text": current})
        current = current.replace(old, new)
        after_root = product_root("pass076_repair_intermediate", {"text": current})
        receipts.append({
            "index": index,
            "old": old,
            "new": new,
            "expected_count": expected,
            "observed_count": observed,
            "before_root_hash72": before_root,
            "after_root_hash72": after_root,
        })
    return current, stable(receipts)


def build_rollback_capsule(*, transaction_id: str, pre_artifact: Mapping[str, Any], post_artifact: Mapping[str, Any], target_path: str) -> Dict[str, Any]:
    body = {
        "schema": REPAIR_ROLLBACK_SCHEMA,
        "rollback_id": f"rollback:{transaction_id}",
        "transaction_ref": transaction_id,
        "target_path": require_product_path(target_path),
        "pre_artifact_ref": pre_artifact.get("artifact_id"),
        "pre_artifact_root_hash72": pre_artifact.get("artifact_root_hash72"),
        "post_artifact_ref": post_artifact.get("artifact_id"),
        "post_artifact_root_hash72": post_artifact.get("artifact_root_hash72"),
        "rollback_content": pre_artifact.get("content"),
        "rollback_creates_new_continuation_not_history_erasure": True,
        "foundation_mutation_permitted": False,
    }
    return rooted("pass076_repair_rollback_capsule", body, "rollback_root_hash72")


def build_repair_test_receipt(*, transaction_id: str, validation: Mapping[str, Any], execution_run: Mapping[str, Any]) -> Dict[str, Any]:
    passed = bool(validation.get("valid")) and bool(execution_run.get("closed"))
    body = {
        "schema": REPAIR_TEST_SCHEMA,
        "transaction_ref": transaction_id,
        "validation_ref": validation.get("validation_id"),
        "validation_root_hash72": validation.get("validation_root_hash72"),
        "execution_run_ref": execution_run.get("run_id"),
        "execution_run_root_hash72": execution_run.get("execution_run_root_hash72"),
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "this_receipt_does_not_self_authorize_future_mutation": True,
    }
    return rooted("pass076_repair_test_receipt", body, "repair_test_receipt_root_hash72")


def build_repair_transaction(
    *, transaction_id: str, plan: Mapping[str, Any], target_path: str,
    pre_artifact: Mapping[str, Any], post_artifact: Mapping[str, Any],
    replacement_receipts: Iterable[Mapping[str, Any]], rollback: Mapping[str, Any],
    validation: Mapping[str, Any], execution_run: Mapping[str, Any],
    repair_test_receipt: Mapping[str, Any],
) -> Dict[str, Any]:
    body = {
        "schema": REPAIR_TRANSACTION_SCHEMA,
        "transaction_id": transaction_id,
        "healing_plan_ref": plan.get("healing_plan_id"),
        "healing_plan_root_hash72": plan.get("healing_plan_root_hash72"),
        "target_path": require_product_path(target_path),
        "pre_artifact_ref": pre_artifact.get("artifact_id"),
        "pre_artifact_root_hash72": pre_artifact.get("artifact_root_hash72"),
        "post_artifact_ref": post_artifact.get("artifact_id"),
        "post_artifact_root_hash72": post_artifact.get("artifact_root_hash72"),
        "replacement_receipts": [stable(x) for x in replacement_receipts],
        "rollback_ref": rollback.get("rollback_id"),
        "rollback_root_hash72": rollback.get("rollback_root_hash72"),
        "validation_root_hash72": validation.get("validation_root_hash72"),
        "execution_run_root_hash72": execution_run.get("execution_run_root_hash72"),
        "repair_test_receipt_root_hash72": repair_test_receipt.get("repair_test_receipt_root_hash72"),
        "status": "APPLIED_PRODUCT_LOCAL" if repair_test_receipt.get("passed") else "REJECTED_POSTCONDITION_FAILED",
        "foundation_mutated": False,
        "history_erased": False,
        "rollback_available": True,
        "authority_revalidated_before_apply": True,
    }
    return rooted("pass076_repair_transaction", body, "repair_transaction_root_hash72")
