from hhs_runtime.hhs_guarded_plugin_adapters_v1 import (
    build_guarded_plugin_adapter_manifest,
    guarded_plugin_adapters_self_test,
    DEFAULT_ADAPTER_PATHS,
)


def test_guarded_plugin_adapter_manifest_is_static_and_kernel_witnessed():
    manifest = build_guarded_plugin_adapter_manifest(paths=DEFAULT_ADAPTER_PATHS[:3])
    assert manifest["schema"] == "HHS_GUARDED_PLUGIN_ADAPTERS_V1"
    assert manifest["adapter_count"] == 3
    assert manifest["error_count"] == 0
    assert len(manifest["hash72_kernel_witness"]["digest72"]) == 72
    for adapter in manifest["adapters"]:
        assert adapter["adapter_status"] == "WIRED_STATIC_GUARDED_ADAPTER"
        assert adapter["source_kernel_witness"]["authority"] == "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
        assert len(adapter["source_kernel_witness"]["digest72"]) == 72
        assert adapter["runtime_packet"]["contract_type"] == "runtime_packet"
        assert "NO_DIRECT_EXECUTION" in adapter["runtime_packet"]["payload"]["source_contract"]["execution_policy"]


def test_guarded_plugin_adapter_self_test_writes_artifacts(tmp_path):
    # Use the repository root through the default path; this confirms the full selected batch resolves.
    result = guarded_plugin_adapters_self_test()
    assert result["ok"] is True
    assert result["adapter_count"] >= 8
    assert result["error_count"] == 0
