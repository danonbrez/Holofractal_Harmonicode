from hhs_runtime.hhs_semantic_plugin_adapter_runtime_v1 import (
    DEFAULT_SEMANTIC_ADAPTER_TARGETS,
    build_semantic_plugin_adapter_execution_manifest,
    execute_semantic_plugin_adapter,
    semantic_plugin_adapter_runtime_self_test,
)


def test_semantic_plugin_adapter_executes_adapter_not_legacy_code():
    result = execute_semantic_plugin_adapter(DEFAULT_SEMANTIC_ADAPTER_TARGETS[0])
    assert result["execution_status"] == "SEMANTIC_ADAPTER_EXECUTED_NO_LEGACY_IMPORT"
    assert result["direct_legacy_import"] is False
    assert result["executed_legacy_code"] is False
    assert result["adapter_kernel_witness"]["authority"] == "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
    assert len(result["adapter_kernel_witness"]["digest72"]) == 72
    assert result["source_summary"]["function"] == DEFAULT_SEMANTIC_ADAPTER_TARGETS[0]["function"]


def test_semantic_plugin_adapter_manifest_is_guarded():
    manifest = build_semantic_plugin_adapter_execution_manifest(targets=DEFAULT_SEMANTIC_ADAPTER_TARGETS[:2])
    assert manifest["schema"] == "HHS_SEMANTIC_PLUGIN_ADAPTER_RUNTIME_V1"
    assert manifest["execution_count"] == 2
    assert manifest["error_count"] == 0
    assert manifest["ledger"]["ok"] is True
    assert len(manifest["hash72_kernel_witness"]["digest72"]) == 72


def test_semantic_plugin_adapter_self_test():
    result = semantic_plugin_adapter_runtime_self_test({"targets": DEFAULT_SEMANTIC_ADAPTER_TARGETS[:1]})
    assert result["ok"] is True
    assert result["execution_count"] == 1
