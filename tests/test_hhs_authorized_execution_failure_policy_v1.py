from pathlib import Path

from hhs_runtime.hhs_authorized_execution_failure_policy_v1 import (
    authorized_execution_failure_policy_self_test,
    build_authorized_execution_failure_policy_manifest,
    evaluate_authorized_execution_request,
    preflight_authorized_execution_target,
)


def test_authorized_execution_failure_policy_self_test_ok():
    result = authorized_execution_failure_policy_self_test({"root": str(Path.cwd())})
    assert result["ok"] is True
    assert result["failure_record_count"] >= 3
    assert result["all_rejections_prevented_execution"] is True
    assert result["schema_registry_valid"] is True
    assert result["execution_performed"] is False
    assert result["ledger"]["ok"] is True


def test_failure_policy_blocks_non_allowlisted_function_without_execution():
    record = evaluate_authorized_execution_request(
        {
            "path": "hhs_runtime/hhs_srcg_gate_v1.py",
            "function": "selfsolve_ab_gate",
            "arguments": [{"A": 1, "B": 1}],
        },
        root=Path.cwd(),
    )
    assert record["schema"] == "HHS_AUTHORIZED_EXECUTION_FAILURE_RECORD_V1"
    assert record["execution_status"] == "REJECTED_WITHOUT_EXECUTION"
    assert record["reason_code"] == "NOT_ALLOWLISTED_FUNCTION"
    assert record["execution_performed"] is False
    assert record["call_performed"] is False
    assert record["function_body_execution_performed"] is False
    assert record["schema_registry_classification"]["family"] == "FAILURE_RECORD"
    assert record["schema_registry_validation"]["ok"] is True
    assert record["failure_kernel_witness"]["digest72"]
    assert record["ledger"]["ledger_hash72"]


def test_failure_policy_blocks_forbidden_authorization_flags():
    preflight = preflight_authorized_execution_target(
        {
            "path": "hhs_runtime/hhs_runtime_contract_v1.py",
            "function": "is_hash72",
            "arguments": ["0" * 72],
            "mutation_authorized": True,
        }
    )
    assert preflight["ok"] is False
    assert preflight["reason_code"] == "FORBIDDEN_AUTHORIZATION_FLAG"


def test_failure_policy_manifest_records_failure_families():
    manifest = build_authorized_execution_failure_policy_manifest(Path.cwd())
    assert manifest["schema"] == "HHS_AUTHORIZED_EXECUTION_FAILURE_POLICY_V1"
    assert manifest["ok"] is True
    assert manifest["failure_record_count"] >= 3
    assert manifest["all_rejections_prevented_execution"] is True
    assert manifest["schema_registry_classified_as_failure_record"] is True
    assert all(item["execution_status"] == "REJECTED_WITHOUT_EXECUTION" for item in manifest["failure_records"])
