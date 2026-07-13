from pathlib import Path

import pytest

from hhs_runtime.hhs_dryrun_live_plugin_executor_v1 import (
    HHSDryRunLivePluginExecutorError,
    build_dryrun_live_plugin_execution_manifest,
    dryrun_live_plugin_executor_self_test,
    execute_dryrun_live_plugin,
)


def test_dryrun_live_plugin_executor_self_test_ok():
    result = dryrun_live_plugin_executor_self_test({"root": str(Path.cwd())})
    assert result["ok"] is True
    assert result["execution_count"] >= 1
    assert result["error_count"] == 0
    assert result["call_performed"] is False
    assert result["ledger"]["ok"] is True


def test_dryrun_live_plugin_trace_does_not_execute_function_body():
    result = execute_dryrun_live_plugin(
        {
            "path": "hhs_runtime/hhs_srcg_gate_v1.py",
            "function": "check_1001_invariant",
            "sample_payload": {"A": 1, "B": 1, "threshold": 1.001},
        },
        root=Path.cwd(),
    )
    assert result["execution_status"] == "DRYRUN_LIVE_PLUGIN_TRACE_GENERATED"
    assert result["dry_run_result"]["call_performed"] is False
    assert result["dry_run_result"]["mutation_performed"] is False
    assert result["function_surface"]["body_execution_performed"] is False
    assert result["dryrun_kernel_witness"]["digest72"]


def test_dryrun_live_plugin_blocks_non_allowlisted_target():
    with pytest.raises(HHSDryRunLivePluginExecutorError):
        execute_dryrun_live_plugin(
            {"path": "hhs_runtime/hhs_srcg_gate_v1.py", "function": "not_allowlisted"},
            root=Path.cwd(),
        )


def test_dryrun_manifest_records_zero_errors():
    manifest = build_dryrun_live_plugin_execution_manifest(Path.cwd())
    assert manifest["schema"] == "HHS_DRYRUN_LIVE_PLUGIN_EXECUTOR_V1"
    assert manifest["execution_count"] >= 1
    assert manifest["error_count"] == 0
    assert manifest["ledger"]["ok"] is True
