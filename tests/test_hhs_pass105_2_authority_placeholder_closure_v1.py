from pathlib import Path
import asyncio
import pytest

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import (
    HHSRuntimeLoadError,
    Hash72Authority,
    load_authoritative_kernel,
)
from hhs_backend.runtime.runtime_server import execute_runtime_expression
from hhs_runtime.hhs_pass105_2_authority_placeholder_closure_v1 import run

R = Path(__file__).resolve().parents[1]


def test_core_sandbox_loads_real_authoritative_kernel():
    kernel = load_authoritative_kernel()
    assert callable(kernel.security_hash72_v44)
    authority = Hash72Authority(kernel)
    assert authority.commit({"real": True}, domain="PASS105_2_TEST") == kernel.security_hash72_v44({"real": True}, domain="PASS105_2_TEST")


def test_core_sandbox_fails_closed_for_missing_kernel(tmp_path):
    with pytest.raises(HHSRuntimeLoadError):
        load_authoritative_kernel(tmp_path / "missing.py")


def test_hash72_authority_rejects_missing_kernel():
    with pytest.raises(HHSRuntimeLoadError):
        Hash72Authority(None)


def test_backend_executes_real_harmonicode_workload_not_echo():
    source = "x=x\nx≠y"
    result = asyncio.run(execute_runtime_expression(source))
    assert result["execution_performed"] is True
    assert result["transport"] == "harmonicode_interpreter_solver"
    assert result["result"] != source
    assert result["full_receipt_hash72"] == result["result"]["full_receipt_hash72"]
    assert result["result"]["solver"]["receipt"]["status"] == "SOLVED"


def test_backend_invalid_empty_workload_fails():
    with pytest.raises(ValueError):
        asyncio.run(execute_runtime_expression("  "))


def test_mobile_console_has_no_canonical_mock_fallback():
    text = (R / "gui/hhs-mobile-runtime-console/src/runtimeData.ts").read_text()
    assert "mockSnapshot" not in text
    assert "H72-PROJECTION-DEMO" not in text
    assert "return unavailableSnapshot" in text
    assert "RUNTIME_STATE_UNAVAILABLE" in text


def test_px1_is_real_registered_face_not_placeholder():
    text = (R / "HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py").read_text()
    assert "M7PlaceholderPX1Face" not in text
    assert "class M7ExponentEqualityFace" in text
    assert '"PX1": M7ExponentEqualityFace()' in text


def test_pass105_2_closure_self_test():
    result = run(R)
    assert result["status"] == "PASS"
    assert result["all_repairs_verified"] is True


def test_pass105_2_service_registry_reachability():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    name = "runtime.authority_placeholder_closure.pass105_2"
    assert registry.has_service(name)
    spec = next(item for item in registry.services() if item["name"] == name)
    assert spec["conformance_decision"]["derivation_complete"] is True
