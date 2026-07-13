import asyncio

from hhs_backend.api import runtime_routes
from hhs_backend.api.runtime_routes import RuntimeServiceDispatchRequest, RuntimeStepRequest, SRCGSelfSolveRequest, ClosureHarnessRequest, RuntimeConstraintEnforcementRequest


def test_runtime_step_route_uses_guarded_emulator_chain():
    before = len(runtime_routes.runtime_emulator.tick_history)
    response = asyncio.run(runtime_routes.runtime_step(RuntimeStepRequest(steps=1)))
    after = len(runtime_routes.runtime_emulator.tick_history)

    assert response["schema"] == "HHS_GUARDED_RUNTIME_STEP_RESPONSE_V1"
    assert response["runtime_contract"]["contract_type"] == "api_response"
    assert response["runtime_contract"]["route"] == "/api/runtime/step"
    assert response["guarded"] is True
    assert response["io"]["ingress"]["direction"] == "INGRESS"
    assert response["io"]["egress"]["direction"] == "EGRESS"
    assert response["steps_executed"] == 1
    assert after == before + 1

    latest_tick = runtime_routes.runtime_emulator.tick_history[-1]
    assert latest_tick["authority_audit"]["ok"] is True
    assert latest_tick["receipt"]["authority_audit"]["ok"] is True


def test_runtime_services_are_discoverable_and_guarded_dispatchable():
    service_list = asyncio.run(runtime_routes.list_runtime_services())
    names = {spec["name"] for spec in service_list["services"]}

    assert "authority_gate.self_test" in names
    assert "ledger.verify" in names
    assert "c_bridge.abi_self_test" in names
    assert "io_gateway.self_test" in names
    assert service_list["runtime_contract"]["contract_type"] == "api_response"

    result = asyncio.run(
        runtime_routes.dispatch_runtime_service(
            RuntimeServiceDispatchRequest(
                service="ledger.verify",
                payload={"source": "test_hhs_backend_guarded_routes_v1"},
            )
        )
    )

    assert result["schema"] == "HHS_SERVICE_DISPATCH_RECORD_V1"
    assert result["runtime_contract"]["contract_type"] == "api_response"
    assert result["post_authority_audit"]["ok"] is True
    assert result["unified_ledger"]["entry_count"] >= 1
    assert result["io"]["ingress"]["direction"] == "INGRESS"
    assert result["io"]["egress"]["direction"] == "EGRESS"


def test_runtime_state_and_service_status_routes_emit_api_response_contracts():
    state = asyncio.run(runtime_routes.get_runtime_state())
    status = asyncio.run(runtime_routes.runtime_services_status())

    assert state["runtime_contract"]["contract_type"] == "api_response"
    assert state["runtime_contract"]["route"] == "/api/runtime/state"
    assert status["runtime_contract"]["contract_type"] == "api_response"
    assert status["runtime_contract"]["route"] == "/api/runtime/services/status"


def test_srcg_selfsolve_route_emits_contract_and_kernel_trace():
    response = asyncio.run(
        runtime_routes.srcg_selfsolve(
            SRCGSelfSolveRequest(
                A=1.0005,
                B=1.0,
                max_steps=2,
                quartic_carrier=[["b^4", ["branch"]], ["c^2", "d^2"]],
            )
        )
    )

    assert response["schema"] == "HHS_SRCG_SELFSOLVE_API_RESPONSE_V1"
    assert response["runtime_contract"]["contract_type"] == "api_response"
    assert response["runtime_contract"]["route"] == "/api/runtime/srcg/selfsolve"
    assert response["io"]["ingress"]["direction"] == "INGRESS"
    assert response["io"]["egress"]["direction"] == "EGRESS"
    result = response["result"]
    assert result["schema"] == "HHS_SRCG_STATE_V1"
    assert result["ok"] is True
    assert result["trace"]
    assert result["trace"][-1]["hash72_kernel_witness"]["schema"] == "HHS_HASH72_KERNEL_WITNESS_V1"
    assert result["trace"][-1]["hash72_kernel_witness"]["zero_sum"] is True


def test_system_closure_harness_route_emits_contract_and_converges():
    response = asyncio.run(
        runtime_routes.system_closure_harness(
            ClosureHarnessRequest(cycles=2, A=1.0005, B=1.0, max_steps=2)
        )
    )

    assert response["schema"] == "HHS_SYSTEM_CLOSURE_HARNESS_V1"
    assert response["ok"] is True
    assert response["converged"] is True
    assert response["runtime_contract"]["contract_type"] == "api_response"
    assert response["runtime_contract"]["route"] == "/api/runtime/closure/harness"
    assert response["io"]["ingress"]["direction"] == "INGRESS"
    assert response["io"]["egress"]["direction"] == "EGRESS"
    assert len(set(response["closure_signatures"])) == 1


def test_constraint_enforcement_route_rejects_terminal_value():
    response = asyncio.run(
        runtime_routes.enforce_runtime_admissibility(
            RuntimeConstraintEnforcementRequest(request_class="terminal_value_only")
        )
    )

    assert response["schema"] == "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_DECISION_V1"
    assert response["runtime_contract"]["contract_type"] == "api_response"
    assert response["runtime_contract"]["route"] == "/api/runtime/admissibility/enforce"
    assert response["status"] == "REJECTED_FORGED_TERMINAL_VALUE"
    assert response["admitted"] is False
    assert response["execution_allowed"] is False
    assert response["io"]["ingress"]["direction"] == "INGRESS"
    assert response["io"]["egress"]["direction"] == "EGRESS"
