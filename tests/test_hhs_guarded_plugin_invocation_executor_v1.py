from hhs_runtime.hhs_guarded_plugin_invocation_executor_v1 import (
    DEFAULT_INVOCATION_TARGETS,
    build_guarded_plugin_invocation_manifest,
    execute_planned_plugin_invocation,
    guarded_plugin_invocation_executor_self_test,
)


def test_execute_planned_plugin_invocation_is_guarded_plan_only():
    result = execute_planned_plugin_invocation(DEFAULT_INVOCATION_TARGETS[0])
    assert result["invocation_status"] == "WIRED_GUARDED_INVOCATION_PLAN"
    assert result["direct_execution_authorized"] is False
    assert result["adapter_result"]["executed_legacy_code"] is False
    assert len(result["invocation_kernel_witness"]["digest72"]) == 72
    assert result["foundational_conformance_pre"]["ok"] is True
    assert result["foundational_conformance_post"]["ok"] is True


def test_build_manifest_has_no_errors_for_small_batch():
    manifest = build_guarded_plugin_invocation_manifest(targets=DEFAULT_INVOCATION_TARGETS[:2])
    assert manifest["schema"] == "HHS_GUARDED_PLUGIN_INVOCATION_EXECUTOR_V1"
    assert manifest["invocation_count"] == 2
    assert manifest["error_count"] == 0
    assert manifest["ledger"]["ok"] is True
    assert len(manifest["hash72_kernel_witness"]["digest72"]) == 72


def test_self_test_writes_artifacts():
    result = guarded_plugin_invocation_executor_self_test({"targets": DEFAULT_INVOCATION_TARGETS[:1]})
    assert result["ok"] is True
    assert result["invocation_count"] == 1
    assert "GUARDED_PLUGIN_INVOCATIONS_PASS_025.json" in result["artifacts"]
