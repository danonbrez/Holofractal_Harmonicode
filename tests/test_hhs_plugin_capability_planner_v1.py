from hhs_runtime.hhs_plugin_capability_planner_v1 import (
    DEFAULT_CAPABILITY_PLAN_PATHS,
    build_plugin_capability_plan_manifest,
    inspect_capability_plan,
    plugin_capability_planner_self_test,
)


def test_capability_plan_manifest_is_plan_only_and_kernel_witnessed():
    manifest = build_plugin_capability_plan_manifest(paths=DEFAULT_CAPABILITY_PLAN_PATHS[:4])
    assert manifest["schema"] == "HHS_PLUGIN_CAPABILITY_PLANNER_V1"
    assert manifest["plan_count"] == 4
    assert manifest["error_count"] == 0
    assert len(manifest["hash72_kernel_witness"]["digest72"]) == 72
    for plan in manifest["plans"]:
        assert plan["adapter_status"] == "WIRED_CAPABILITY_PLAN_ONLY"
        assert plan["safe_invocation_plan"]["direct_execution_authorized"] is False
        assert plan["source_kernel_witness"]["authority"] == "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
        assert len(plan["plan_kernel_witness"]["digest72"]) == 72
        assert plan["runtime_packet"]["contract_type"] == "runtime_packet"
        assert "NO_DIRECT_EXECUTION" in plan["safe_invocation_plan"]["schema"] or plan["execution_policy"].startswith("plan/")


def test_capability_plan_preserves_runtime_semantic_module_identity():
    plan = inspect_capability_plan(None, "hhs_backend/runtime/runtime_semantic_memory_engine.py").to_dict()
    assert plan["path"].endswith("runtime_semantic_memory_engine.py")
    assert "semantic_memory" in plan["capabilities"]
    assert plan["safe_invocation_plan"]["required_runtime_path"][-1] == "closure_harness_coverage"
    assert plan["foundational_audit"]["ok"] is True


def test_plugin_capability_planner_self_test_writes_artifacts():
    result = plugin_capability_planner_self_test()
    assert result["ok"] is True
    assert result["plan_count"] >= 20
    assert result["error_count"] == 0
    assert "PLUGIN_CAPABILITY_PLANS_PASS_024.json" in result["artifacts"]
