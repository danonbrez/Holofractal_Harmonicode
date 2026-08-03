from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import HydratedMainframe
from hhs_backend.runtime.hhs_pass204_open_cloud_mainframe import (
    HOST_TRUST_BOUNDARY,
    KERNEL_CONSTRAINT_MANIFEST,
    OpenCloudMainframe,
    SANDBOX_POLICY,
)


@pytest.fixture()
def mainframe(monkeypatch: pytest.MonkeyPatch) -> OpenCloudMainframe:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        monkeypatch.setenv("HHS_PASS203_STATE_ROOT", str(root / "pass203"))
        monkeypatch.setenv("HHS_PASS204_STATE_ROOT", str(root / "pass204"))
        repo_root = Path(__file__).resolve().parents[1]
        inherited = HydratedMainframe(repo_root)
        runtime = OpenCloudMainframe(inherited, repo_root)
        counter = {"step": 0}

        def authority(source: str):
            counter["step"] += 1
            return {
                "receipt": {"receipt_hash72": "R" * 71 + str(counter["step"] % 10)},
                "runtime": {"step": counter["step"]},
                "source": source,
            }

        runtime.configure_authority(authority)
        yield runtime


def _canonicalize_target(mainframe: OpenCloudMainframe) -> dict:
    matches = mainframe.list_functions(query="canonicalize_for_hash72", limit=1000)["functions"]
    return next(
        item
        for item in matches
        if item["kind"] == "PYTHON_FUNCTION"
        and item["name"] == "canonicalize_for_hash72"
        and "hhs_general_runtime_layer_v1" in item.get("module", "")
    )


def test_all_indexed_declarations_are_hydrated_callable_and_bound(mainframe: OpenCloudMainframe) -> None:
    report = mainframe.refresh()
    status = mainframe.status()
    assert report["catalog_count"] > 100
    assert report["catalog_count"] == report["hydrated_count"] == report["callable_count"]
    assert report["unbound_count"] == 0
    assert status["all_declarations_executable"] is True
    assert status["unbound_internal_count"] == 0
    assert all(item["hydrated"] and item["callable"] for item in mainframe.catalog())
    assert all(item["binding_gap"] is False for item in mainframe.catalog())
    assert not {
        "ADAPTER_REQUIRED",
        "WORKSPACE_JOB_ADAPTER_REQUIRED",
        "ABI_BINDING_REQUIRED",
        "FORBIDDEN",
    } & {item["execution_mode"] for item in mainframe.catalog()}


def test_fixed_remote_sandbox_and_host_boundary_are_explicit(mainframe: OpenCloudMainframe) -> None:
    status = mainframe.status()
    assert SANDBOX_POLICY["remote_users_automatically_sandboxed"] is True
    assert SANDBOX_POLICY["persistent_capabilities"] is False
    assert SANDBOX_POLICY["direct_host_kernel_access"] is False
    assert SANDBOX_POLICY["caller_adjustable_internal_policy"] is False
    assert KERNEL_CONSTRAINT_MANIFEST["admitted_history_mutable"] is False
    assert KERNEL_CONSTRAINT_MANIFEST["constraint_authority_mutable"] is False
    assert HOST_TRUST_BOUNDARY["weakest_external_operational_layer"] == "CLOUD_SERVER_HARDWARE_ENVIRONMENT"
    assert HOST_TRUST_BOUNDARY["host_fault_can_rewrite_admitted_hash_history"] is False
    assert status["safe_open_cloud_computer_api"] is True
    assert status["valid_api_call_http_error"] is False


def test_formerly_unbound_python_declaration_executes_and_is_recallable(mainframe: OpenCloudMainframe) -> None:
    mainframe.refresh()
    target = _canonicalize_target(mainframe)
    assert target["inherited_execution_mode"] == "ADAPTER_REQUIRED"
    result = mainframe.invoke(target["function_id"], {"obj": {"b": 2, "a": 1}})
    assert result["ok"] is True
    assert result["valid_call_error_returned"] is False
    assert result["execution_status"] == "COMPLETED"
    assert result["result"]["outcome"] == "PYTHON_DECLARATION_EXECUTED"
    assert result["result"]["result"] == {"a": 1, "b": 2}
    assert result["snapshot"]["full_system_state_and_history_encoded"] is True
    assert result["snapshot"]["integrated_system_state"]["history_rewrite_permitted"] is False
    assert result["receipt"]["persistent_capabilities"] is False
    recalled = mainframe.recall(result["snapshot"]["recall_token"])
    assert recalled["ok"] is True
    assert recalled["verified"] is True
    assert recalled["capabilities_restored"] is False
    assert recalled["snapshot"]["snapshot_root"] == result["snapshot"]["snapshot_root"]


def test_canonical_core_native_abi_symbol_executes_immediately(mainframe: OpenCloudMainframe) -> None:
    mainframe.refresh()
    target = next(
        item for item in mainframe.catalog()
        if item["kind"] == "NATIVE_ABI" and item["name"] == "hhs_sizeof_runtime_state"
    )
    result = mainframe.invoke(target["function_id"], {})
    assert result["ok"] is True
    assert result["execution_status"] == "COMPLETED"
    assert result["result"]["outcome"] == "CANONICAL_CTYPES_ABI_EXECUTED"
    assert int(result["result"]["result"]) > 0
    assert result["result"]["raw_pointer_exposed"] is False


def test_project_native_abi_declaration_is_accepted_as_durable_call_job(mainframe: OpenCloudMainframe) -> None:
    mainframe.refresh()
    target = next(
        item
        for item in mainframe.catalog()
        if item["kind"] == "NATIVE_ABI"
        and item["inherited_execution_mode"] == "ABI_BINDING_REQUIRED"
        and str(item["name"]).startswith("hhs_storybook_")
    )
    result = mainframe.invoke(target["function_id"], {})
    assert result["ok"] is True
    assert result["execution_status"] == "ACCEPTED"
    assert result["result"]["outcome"] == "PROJECT_NATIVE_ABI_BUILD_AND_CALL_ACCEPTED"
    assert result["job"]["status"] == "ACCEPTED"
    assert mainframe.job(result["job"]["job_id"])["job_id"] == result["job"]["job_id"]
    assert result["result"]["result"]["native_pointer_exposed"] is False


def test_inherited_mainframe_api_returns_http_success_for_valid_declaration_call(
    mainframe: OpenCloudMainframe,
) -> None:
    import hhs_backend.api.pass203_mainframe_routes as pass203_routes
    import hhs_backend.api.pass204_open_cloud_routes as pass204_routes

    mainframe.refresh()
    pass203_routes.PASS203_MAINFRAME = mainframe
    pass204_routes.PASS204_MAINFRAME = mainframe
    app = FastAPI()
    app.include_router(pass203_routes.router)
    app.include_router(pass204_routes.router)
    client = TestClient(app)

    target = _canonicalize_target(mainframe)
    response = client.post(
        "/api/runtime/mainframe/invoke",
        json={"function_id": target["function_id"], "arguments": {"obj": {"x": 7}}},
    )
    assert response.status_code == 200
    raw = response.json()
    payload = raw.get("data", raw.get("result", raw))
    while isinstance(payload, dict) and "execution_status" not in payload:
        next_value = payload.get("data", payload.get("result"))
        if not isinstance(next_value, dict) or next_value is payload:
            break
        payload = next_value
    assert payload["ok"] is True
    assert payload["execution_status"] == "COMPLETED"

    closure = client.get("/api/runtime/open-cloud/closure")
    assert closure.status_code == 200
    closure_payload = closure.json()
    closure_payload = closure_payload.get("data", closure_payload.get("result", closure_payload))
    assert closure_payload["all_declarations_executable"] is True
    assert closure_payload["binding_gap_count"] == 0
    assert closure_payload["capabilities_restored_on_recall"] is False
