from __future__ import annotations


def test_runtime_os_installs_i19_as_cumulative_maintenance_membrane():
    from hhs_backend import runtime_os_application_server

    routes = list(runtime_os_application_server.app.router.routes)
    route_paths = {str(getattr(route, "path", "")) for route in routes}
    assert "/api/runtime/pass218/authority/maintenance-postcondition/status" in route_paths
    assert "/api/runtime/pass218/authority/maintenance-postcondition/synchronize" in route_paths
    assert "/api/runtime/pass218/authority/maintenance-postcondition/record" not in route_paths

    control = runtime_os_application_server.PASS218_I19_POSTCONDITION_CONTROL_PLANE
    assert control is runtime_os_application_server.PASS218_I18_CLOSURE_CONTROL_PLANE
    assert control is runtime_os_application_server.PASS218_I17_EXECUTION_CONTROL_PLANE
    assert control is runtime_os_application_server.PASS218_I16_CONSUMPTION_CONTROL_PLANE
    assert control is runtime_os_application_server.PASS218_I15_CONSUMPTION_CONTROL_PLANE

    status = control.status()
    assert status["postcondition_verification_executes_maintenance"] is False
    assert status["postcondition_verification_grants_retry_authority"] is False
    assert status["credential_rotation_requires_external_postcondition_observation"] is True
    assert status["member_replacement_requires_external_postcondition_observation"] is True
    assert status["snapshot_rehearsal_intrinsic_verification_supported"] is True
    assert status["successor_may_redispatch"] is False
    assert status["canonical_authority_minted"] is False
    assert status["canonical_mutation_permitted"] is False
    assert status["action_authority_minted"] is False
