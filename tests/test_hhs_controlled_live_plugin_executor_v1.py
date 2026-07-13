import pytest

from hhs_runtime.hhs_controlled_live_plugin_executor_v1 import (
    CONTROLLED_LIVE_ALLOWLIST,
    DEFAULT_CONTROLLED_LIVE_TARGETS,
    HHSControlledLivePluginExecutionError,
    build_controlled_live_plugin_execution_manifest,
    controlled_live_plugin_executor_self_test,
    execute_controlled_live_plugin,
)


def test_controlled_live_rejects_non_allowlisted_target():
    with pytest.raises(HHSControlledLivePluginExecutionError):
        execute_controlled_live_plugin({"path": "README.md", "function": "not_self_test"})


def test_controlled_live_executes_allowlisted_self_test():
    target = {
        "path": "hhs_backend/runtime/runtime_semantic_memory_engine.py",
        "function": "semantic_memory_self_test",
        "controlled_live_authorized": True,
    }
    result = execute_controlled_live_plugin(target)
    assert result["execution_status"] == "CONTROLLED_LIVE_PLUGIN_EXECUTED"
    assert result["live_execution_authorized"] is True
    assert result["live_kernel_witness"]["authority"] == "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
    assert len(result["live_kernel_witness"]["digest72"]) == 72
    assert result["semantic_adapter_execution"]["executed_legacy_code"] is False
    assert result["live_result_summary"]["json_serializable"] is True


def test_controlled_live_manifest_and_self_test():
    manifest = build_controlled_live_plugin_execution_manifest(targets=DEFAULT_CONTROLLED_LIVE_TARGETS[:1])
    assert manifest["schema"] == "HHS_CONTROLLED_LIVE_PLUGIN_EXECUTOR_V1"
    assert manifest["execution_count"] == 1
    assert manifest["error_count"] == 0
    assert len(CONTROLLED_LIVE_ALLOWLIST) >= 1

    self_test = controlled_live_plugin_executor_self_test({"targets": DEFAULT_CONTROLLED_LIVE_TARGETS[:1]})
    assert self_test["ok"] is True
    assert "CONTROLLED_LIVE_PLUGIN_EXECUTIONS_PASS_027.json" in self_test["artifacts"]
