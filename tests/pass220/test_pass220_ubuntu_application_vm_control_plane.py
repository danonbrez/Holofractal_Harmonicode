from __future__ import annotations

import json
import os
from pathlib import Path
import runpy
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


def test_application_vm_cli_preserves_json_and_capability_boundaries(
    tmp_path: Path,
) -> None:
    control = make_control(tmp_path)
    credential = token(control)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    env["HHS_PASS190_CAPABILITY_SECRET"] = SECRET
    state_root = tmp_path / "standalone-vm"
    database = state_root / "authority.sqlite3"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hhs_runtime.pass220.application_vm_cli",
            "--repository-root",
            str(ROOT),
            "--state-root",
            str(state_root),
            "--database",
            str(database),
            "--capability-token",
            credential,
            "shell",
            "--",
            "hhs",
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


def test_installed_hhs_vm_wrapper_resolves_env_repository_and_python(
    tmp_path: Path,
) -> None:
    state_root = tmp_path / "installed-state"
    env_file = tmp_path / "application-vm.env"
    env_file.write_text(
        "\n".join(
            (
                f"HHS_APPLICATION_VM_REPOSITORY_ROOT={ROOT}",
                f"HHS_APPLICATION_VM_STATE_ROOT={state_root}",
                f"HHS_PASS190_DATABASE={state_root / 'authority.sqlite3'}",
                f"HHS_PASS190_CAPABILITY_SECRET={SECRET}",
                f"HHS_APPLICATION_VM_PYTHON_BIN={sys.executable}",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["HHS_APPLICATION_VM_ENV_FILE"] = str(env_file)
    env["HHS_APPLICATION_VM_PYTHON_BIN"] = sys.executable

    completed = subprocess.run(
        ["sh", "bin/hhs-vm", "status"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
    assert payload["security_configured"] is True
    assert payload["frontend_attached"] is False


def test_service_template_uses_deployment_python_runtime() -> None:
    service = (
        ROOT
        / "deployment/ubuntu/application_vm/hhs-application-vm.service.template"
    ).read_text(encoding="utf-8")
    installer = (
        ROOT / "deployment/ubuntu/application_vm/install.sh"
    ).read_text(encoding="utf-8")

    assert "ExecStart=@@PYTHON_BIN@@ -m uvicorn" in service
    assert "HHS_APPLICATION_VM_PYTHON_BIN=$PYTHON_BIN" in installer
    assert "systemctl restart hhs-application-vm.service" in installer


def test_production_nginx_include_targets_only_tls_runtime_server() -> None:
    namespace = runpy.run_path(
        str(
            ROOT
            / "deployment/ubuntu/application_vm/configure_production_nginx.py"
        )
    )
    inject = namespace["inject_application_vm_include"]
    source = """
server {
    listen 80;
    server_name 165.227.220.193;
    return 308 https://165.227.220.193$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 165.227.220.193;

    location / {
        proxy_pass http://127.0.0.1:8080;
    }
}
"""
    updated, changed = inject(source)
    assert changed is True
    assert updated.count("include /etc/nginx/snippets/hhs-application-vm.conf;") == 1

    http_block, tls_block = updated.split("server {", 2)[1:]
    assert "hhs-application-vm.conf" not in http_block
    assert "hhs-application-vm.conf" in tls_block

    repeated, changed_again = inject(updated)
    assert changed_again is False
    assert repeated == updated


def test_installer_accepts_versioned_git_worktree_releases() -> None:
    installer = (
        ROOT / "deployment/ubuntu/application_vm/install.sh"
    ).read_text(encoding="utf-8")

    assert 'git -C "$REPO_ROOT" rev-parse --is-inside-work-tree' in installer
    assert '[[ -d "$REPO_ROOT/.git" ]]' not in installer


def test_production_workflow_is_backend_first_and_frontend_independent() -> None:
    workflow = (
        ROOT / ".github/workflows/pass220-ubuntu-application-vm-production.yml"
    ).read_text(encoding="utf-8")

    assert "workflow_run:" not in workflow
    assert "push:" in workflow
    assert "SOURCE_REPO=/opt/hhs/app" in workflow
    assert 'RELEASE_ROOT="$STATE_ROOT/releases"' in workflow
    assert 'git -C "$SOURCE_REPO" worktree add --detach "$RELEASE" "$TARGET_SHA"' in workflow
    assert "DigitalOcean Production Exact Main" not in workflow
    assert "systemctl is-active --quiet hhs.service" not in workflow
    assert "HHS_APPLICATION_VM_PUBLIC_SECURE_OPENAPI_VERIFIED" in workflow
    assert "HHS_PASS_220_APPLICATION_VM_PRODUCTION_RECEIPT_V1" in workflow


def test_installer_prebuilds_native_runtime_before_service_restart() -> None:
    installer = (
        ROOT / "deployment/ubuntu/application_vm/install.sh"
    ).read_text(encoding="utf-8")
    verifier = (
        ROOT / "deployment/ubuntu/application_vm/verify.sh"
    ).read_text(encoding="utf-8")

    build = 'timeout 900s make -B c-abi'
    library = 'hhs_runtime/builds/libhhs_runtime.so'
    restart = 'systemctl restart hhs-application-vm.service'

    assert build in installer
    assert library in installer
    assert 'HHS_DISABLE_C_AUTOBUILD=1' in installer
    assert 'HHS_APPLICATION_VM_PREBUILT_NATIVE_IMPORT_VERIFIED' in installer
    assert installer.index(build) < installer.index(restart)

    assert library in verifier
    assert 'production C autobuild must be disabled after prebuild' in verifier
    assert 'HHS_APPLICATION_VM_NATIVE_RUNTIME_LOAD_VERIFIED' in verifier


def test_application_vm_workflows_require_prebuilt_native_runtime() -> None:
    focused = (
        ROOT / ".github/workflows/pass220-ubuntu-application-vm.yml"
    ).read_text(encoding="utf-8")
    production = (
        ROOT / ".github/workflows/pass220-ubuntu-application-vm-production.yml"
    ).read_text(encoding="utf-8")

    for workflow in (focused, production):
        assert "make -B c-abi" in workflow
        assert "test -s hhs_runtime/builds/libhhs_runtime.so" in workflow
        assert "HHS_DISABLE_C_AUTOBUILD=1" in workflow
        assert "hhs_exact_abi_validate" in workflow
        assert "hhs_hash216_compute" in workflow
