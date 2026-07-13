from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_default_service_registry_reports_all_services_derived():
    registry = make_default_service_registry()
    status = registry.status()
    assert status["service_count"] >= 50
    assert status["derived_service_count"] == status["service_count"]
    assert status["underived_service_count"] == 0
    assert status["conformance_root_hash72"]


def test_new_conformance_services_are_registered():
    registry = make_default_service_registry()
    names = {s["name"] for s in registry.services()}
    assert "kernel_invariant_registry.self_test" in names
    assert "kernel_conformance_surface_map.self_test" in names
    assert "kernel_conformance_decision.self_test" in names
    assert "kernel_conformance_registration.self_test" in names
