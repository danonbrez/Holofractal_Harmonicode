from __future__ import annotations

import asyncio


def test_public_runtime_service_list_is_nonempty_and_exposes_self_test():
    from hhs_backend.api.runtime_routes import runtime_service_list

    payload = asyncio.run(runtime_service_list())
    assert payload["ok"] is True, payload
    assert payload["count"] > 0, payload
    names = {item["name"] for item in payload["services"]}
    assert "runtime_contract.self_test" in names, sorted(names)


def test_public_runtime_service_dispatch_executes_runtime_contract_self_test():
    from hhs_backend.api.runtime_routes import RuntimeServiceDispatchRequest, runtime_service_dispatch

    payload = asyncio.run(
        runtime_service_dispatch(
            RuntimeServiceDispatchRequest(
                service="runtime_contract.self_test",
                payload={},
            )
        )
    )
    assert payload["ok"] is True, payload
    assert payload["service"] == "runtime_contract.self_test"
    assert payload["result"]["schema"] == "HHS_RUNTIME_CONTRACT_SELF_TEST_V1"
    assert payload["result"]["ok"] is True
    assert payload["runtime_contract"]["authority"] == "HHS_KERNEL_RUNTIME_V1"
