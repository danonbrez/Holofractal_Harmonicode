from pathlib import Path

import pytest

from hhs_runtime.hhs_authorized_pure_function_executor_v1 import (
    HHSAuthorizedPureFunctionExecutorError,
    authorized_pure_function_executor_self_test,
    build_authorized_pure_function_execution_manifest,
    execute_authorized_pure_function,
)


def test_authorized_pure_function_executor_self_test_ok():
    result = authorized_pure_function_executor_self_test({"root": str(Path.cwd())})
    assert result["ok"] is True
    assert result["execution_count"] >= 1
    assert result["error_count"] == 0
    assert result["call_performed"] is True
    assert result["argument_mutation_detected"] is False
    assert result["schema_registry_valid"] is True
    assert result["ledger"]["ok"] is True


def test_authorized_pure_function_executes_check_1001_after_dryrun():
    result = execute_authorized_pure_function(
        {
            "path": "hhs_runtime/hhs_srcg_gate_v1.py",
            "function": "check_1001_invariant",
            "arguments": [1, 1],
            "keyword_arguments": {"threshold": 1.001},
        },
        root=Path.cwd(),
    )
    assert result["execution_status"] == "AUTHORIZED_PURE_FUNCTION_EXECUTED"
    assert result["dry_run_trace"]["dry_run_result"]["call_performed"] is False
    assert result["live_result"]["call_performed"] is True
    assert result["live_result"]["result"] is True
    assert result["live_result"]["argument_mutation_detected"] is False
    assert result["result_kernel_witness"]["digest72"]
    assert result["schema_registry_validations"]["execution_request_validation"]["ok"] is True
    assert result["schema_registry_validations"]["runtime_packet_validation"]["ok"] is True


def test_authorized_pure_function_blocks_non_allowlisted_target():
    with pytest.raises(HHSAuthorizedPureFunctionExecutorError):
        execute_authorized_pure_function(
            {
                "path": "hhs_runtime/hhs_srcg_gate_v1.py",
                "function": "selfsolve_ab_gate",
                "arguments": [{"A": 1, "B": 1}],
            },
            root=Path.cwd(),
        )


def test_authorized_pure_manifest_records_zero_errors():
    manifest = build_authorized_pure_function_execution_manifest(Path.cwd())
    assert manifest["schema"] == "HHS_AUTHORIZED_PURE_FUNCTION_EXECUTOR_V1"
    assert manifest["execution_count"] >= 1
    assert manifest["error_count"] == 0
    assert manifest["ledger"]["ok"] is True
