from hhs_python.runtime.hhs_ctypes_bridge import HHSSRCGBridge
from hhs_runtime.hhs_srcg_gate_v1 import selfsolve_ab_gate, srcg_primitive_self_test
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_c_srcg_bridge_exports_and_rolls_back():
    gate = HHSSRCGBridge(1.0005, 1.0)
    assert gate.validate()
    assert gate.step()
    exported = gate.export()
    assert exported["schema"] == "HHS_SRCG_C_KERNEL_STATE_V1"
    assert exported["trace_count"] == 1
    assert exported["unit_unity_valid"] is True

    bad = HHSSRCGBridge(2.0, 1.0)
    assert not bad.validate()
    assert not bad.step()
    assert bad.export()["rolled_back"] is True


def test_srcg_selfsolve_preserves_nested_quartic_carrier_and_hash72_trace():
    carrier = [["b^4", ["nested", "branch"]], ["c^2", "d^2"]]
    result = selfsolve_ab_gate({"A": 1.0005, "B": 1.0, "max_steps": 2, "quartic_carrier": carrier})
    assert result["schema"] == "HHS_SRCG_STATE_V1"
    assert result["ok"] is True
    assert result["trace"]
    assert result["trace"][0]["quartic_carrier_preserved"] is True
    assert result["trace"][0]["hash72_kernel_witness"]["schema"] == "HHS_HASH72_KERNEL_WITNESS_V1"
    assert result["trace"][0]["hash72_kernel_witness"]["zero_sum"] is True


def test_srcg_self_test_and_service_registry_dispatch():
    self_test = srcg_primitive_self_test()
    assert self_test["ok"] is True
    registry = make_default_service_registry()
    assert registry.has_service("srcg.primitive_self_test")
    payload = {"A": 1.0005, "B": 1.0, "max_steps": 1}
    interposition = registry.interpose_dispatch("srcg.selfsolve_ab_gate", payload)
    dispatch = registry.dispatch(
        "srcg.selfsolve_ab_gate",
        payload,
        zero_bypass_interposition_token=interposition["interposition_token"],
    )
    assert dispatch["result"]["schema"] == "HHS_SRCG_STATE_V1"
    assert dispatch["result"]["ok"] is True
    assert dispatch["unified_ledger"]["tip_hash72"]
