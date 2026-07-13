import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import interpose_service_registration
from hhs_runtime.hhs_service_registry_v1 import HHSServiceRegistry, HHSServiceRegistryError, HHSServiceSpec


def test_known_hhs_service_registration_is_derived():
    decision = interpose_service_registration({
        "name": "kernel_conformance_decision.self_test",
        "module": "hhs_runtime.hhs_kernel_conformance_decision_v1",
        "function": "kernel_conformance_decision_self_test",
        "service_type": "conformance",
    })
    assert decision["ok"] is True
    assert "HHS-I015" in decision["declaration"]["invariant_ids"]


def test_unknown_underived_service_registration_is_rejected():
    registry = HHSServiceRegistry()
    spec = HHSServiceSpec(name="external.random", module="external.random", function="run", service_type="external")
    with pytest.raises(HHSServiceRegistryError):
        registry.register(spec, lambda payload: {"ok": True})
