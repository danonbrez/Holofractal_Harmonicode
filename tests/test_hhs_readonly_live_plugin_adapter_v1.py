import pytest

from hhs_runtime.hhs_readonly_live_plugin_adapter_v1 import (
    DEFAULT_READONLY_LIVE_TARGETS,
    HHSReadOnlyLivePluginAdapterError,
    build_readonly_live_adapter_manifest,
    execute_readonly_live_adapter,
    readonly_live_plugin_adapter_self_test,
)


def test_readonly_live_rejects_non_allowlisted_target():
    with pytest.raises(HHSReadOnlyLivePluginAdapterError):
        execute_readonly_live_adapter({"path": "README.md", "mode": "MODULE_INTROSPECTION"})


def test_readonly_live_introspects_allowlisted_module():
    result = execute_readonly_live_adapter(DEFAULT_READONLY_LIVE_TARGETS[0])
    assert result["execution_status"] == "READONLY_LIVE_PLUGIN_ADAPTER_EXECUTED"
    assert result["read_only_authorized"] is True
    assert result["execution_policy"]["mutation_allowed"] is False
    assert result["module_summary"]["body_execution_performed"] is False
    assert result["module_summary"]["mutation_performed"] is False
    assert result["module_summary"]["public_function_count"] >= 1
    assert result["kernel_witness"]["authority"] == "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
    assert len(result["kernel_witness"]["digest72"]) == 72


def test_readonly_live_manifest_and_self_test():
    manifest = build_readonly_live_adapter_manifest(targets=DEFAULT_READONLY_LIVE_TARGETS[:1])
    assert manifest["schema"] == "HHS_READONLY_LIVE_PLUGIN_ADAPTER_V1"
    assert manifest["execution_count"] == 1
    assert manifest["error_count"] == 0

    self_test = readonly_live_plugin_adapter_self_test({"targets": DEFAULT_READONLY_LIVE_TARGETS[:1]})
    assert self_test["ok"] is True
    assert "READONLY_LIVE_PLUGIN_ADAPTERS_PASS_028.json" in self_test["artifacts"]
