from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from hhs_backend.application_vm_api_server import create_application_vm_api
from hhs_runtime.pass220.application_vm_control_plane import ApplicationVMControlPlane


ROOT = Path(__file__).resolve().parents[2]
SECRET = "pass220-ubuntu-application-vm-" + ("x" * 48)


def make_control(tmp_path: Path, *, secret: str | None = SECRET) -> ApplicationVMControlPlane:
    return ApplicationVMControlPlane.create(
        repository_root=ROOT,
        state_root=tmp_path / "state",
        database_path=tmp_path / "state" / "authority.sqlite3",
        capability_secret=secret,
        require_pinned_python=False,
    )


def token(control: ApplicationVMControlPlane) -> str:
    return control.issue_token(
        principal="pass220-test",
        scopes=(
            "runtime.mutate",
            "workspace:read",
            "workspace:write",
            "artifact:read",
            "artifact:write",
        ),
        ttl_seconds=900,
    )


def test_backend_control_plane_preserves_single_authority(tmp_path: Path) -> None:
    control = make_control(tmp_path)
    status = control.status()
    assert status["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
    assert status["frontend_attached"] is False
    assert status["fastapi_frontend_authority"] is False
    assert status["single_vm81_authority_preserved"] is True
    assert status["pass190"]["governed_operation_count"] == 52
    assert control.health()["new_vm81_authority"] is False


def test_cli_and_openapi_share_pass190_operation_authority(tmp_path: Path) -> None:
    control = make_control(tmp_path)
    credential = token(control)

    direct = control.invoke(
        "python.len",
        {"value": [1, 2, 3]},
        authorization_token=credential,
    )
    shell = control.shell(
        "hhs invoke python.len '{\"value\":[1,2,3]}'",
        authorization_token=credential,
    )
    assert direct["operation_id"] == shell["operation_id"] == "python.len"
    assert direct["result"] == shell["result"] == 3

    client = TestClient(create_application_vm_api(control))
    auth = {"Authorization": "HHS-Capability " + credential}

    assert client.get("/health").status_code == 200
    denied = client.get("/v1/vm/status")
    assert denied.status_code == 401

    status = client.get("/v1/vm/status", headers=auth)
    assert status.status_code == 200
    assert status.json()["frontend_attached"] is False

    capabilities = client.get("/v1/vm/capabilities", headers=auth)
    assert capabilities.status_code == 200
    assert capabilities.json()["operation_count"] == 52

    shell_http = client.post(
        "/v1/vm/shell",
        headers=auth,
        json={"command": "hhs status"},
    )
    assert shell_http.status_code == 200
    assert shell_http.json()["operation_id"] == "system.status"

    pure_http = client.post(
        "/v1/vm/operations/python.len",
        headers=auth,
        json={"arguments": {"value": [1, 2, 3]}},
    )
    assert pure_http.status_code == 200
    assert pure_http.json()["result"] == 3

    mutation = client.post(
        "/v1/vm/operations/state.counter.advance",
        headers=auth,
        json={"arguments": {"delta": 1}},
    )
    assert mutation.status_code == 200
    receipt_hash = mutation.json()["receipt"]["hash72"]

    replay = client.post(
        f"/v1/vm/replay/{receipt_hash}",
        headers=auth,
    )
    assert replay.status_code == 200
    assert replay.json()["replay_verified"] is True


def test_openapi_declares_security_without_remote_token_issuer(tmp_path: Path) -> None:
    control = make_control(tmp_path)
    client = TestClient(create_application_vm_api(control))
    document = client.get("/openapi.json").json()

    assert document["x-hhs-application-vm"]["backend_first"] is True
    assert document["x-hhs-application-vm"]["frontend_attached"] is False
    assert document["x-hhs-application-vm"]["remote_token_issuance"] is False
    assert "HhsCapabilityToken" in document["components"]["securitySchemes"]
    assert not any("token" in path.lower() for path in document["paths"])


def test_unconfigured_security_fails_closed(tmp_path: Path) -> None:
    control = make_control(tmp_path, secret=None)
    client = TestClient(create_application_vm_api(control))
    assert client.get("/health").json()["security_configured"] is False
    response = client.get(
        "/v1/vm/status",
        headers={"Authorization": "HHS-Capability invalid"},
    )
    assert response.status_code == 503


def test_standalone_pass190_shell_reads_capability_secret_from_environment(
    tmp_path: Path,
) -> None:
    control = make_control(tmp_path)
    credential = token(control)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    env["HHS_PASS190_CAPABILITY_SECRET"] = SECRET
    database = tmp_path / "standalone-shell.sqlite3"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hhs_runtime.pass190.shell",
            "--database",
            str(database),
            "--repository-root",
            str(ROOT),
            "--capability-token",
            credential,
            "invoke",
            "state.counter.advance",
            '{"delta":1}',
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert '"operation_id":"state.counter.advance"' in completed.stdout
