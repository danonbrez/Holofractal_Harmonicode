from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import threading

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.api.pass184_runtime_routes import router
from hhs_runtime.pass184.runtime import (
    APP_IMPORT,
    CONTRACT_ID,
    PROFILE_SEEDS,
    Pass184Error,
    PortableRuntimeAuthority,
    ensure_within,
    resolve_profile_components,
    write_completion_receipt,
)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return
        body = b'{"ok":true,"status":"HHS_IDE_SERVICE_REACHABLE"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


@pytest.fixture
def authority() -> PortableRuntimeAuthority:
    return PortableRuntimeAuthority()


@pytest.fixture
def repository_root(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    (root / "hhs_backend").mkdir(parents=True)
    (root / "hhs_backend" / "application_ide_server.py").write_text("app = object()\n", encoding="utf-8")
    return root


def fixed_environment(repository_root: Path, writable_root: Path) -> dict[str, object]:
    return {
        "schema": "HHS_PASS_184_ENVIRONMENT_SNAPSHOT_V1",
        "repository_root": str(repository_root),
        "writable_root": str(writable_root),
        "environment_identity": "e" * 64,
    }


def build_full(authority: PortableRuntimeAuthority, repository_root: Path, install_root: Path):
    plan = authority.plan(
        profile="full",
        install_root=install_root,
        repository_root=repository_root,
        host="0.0.0.0",
        port=8080,
        environment=fixed_environment(repository_root, install_root.parent),
    )
    return plan, authority.build(plan, clean=True)


def test_all_profiles_have_authority_closure() -> None:
    for profile in PROFILE_SEEDS:
        components = resolve_profile_components(profile)
        assert components
        assert components.index("vm81") < components.index("hash72") < components.index("hash216")
        assert "service" in components
        assert "receipts" in components
    full = resolve_profile_components("full")
    for required in ("application_ide", "workspace", "assistant", "multimodal", "video", "games"):
        assert required in full


def test_unknown_profile_and_invalid_port_fail_closed(authority: PortableRuntimeAuthority, tmp_path: Path) -> None:
    with pytest.raises(Pass184Error, match="unknown profile") as profile_error:
        authority.plan(profile="unknown", install_root=tmp_path / "x", port=8080)
    assert profile_error.value.status == "P184_REJECT_UNKNOWN_PROFILE"
    with pytest.raises(Pass184Error) as port_error:
        authority.plan(profile="full", install_root=tmp_path / "x", port=0)
    assert port_error.value.status == "P184_REJECT_INVALID_PORT"


def test_plan_identity_is_deterministic(authority: PortableRuntimeAuthority, repository_root: Path, tmp_path: Path) -> None:
    install = tmp_path / "package"
    environment = fixed_environment(repository_root, tmp_path)
    left = authority.plan(
        profile="multimodal",
        install_root=install,
        repository_root=repository_root,
        environment=environment,
    )
    right = authority.plan(
        profile="multimodal",
        install_root=install,
        repository_root=repository_root,
        environment=environment,
    )
    assert left.to_dict() == right.to_dict()
    assert len(left.plan_identity) == 64


def test_package_build_verify_and_rebuild_are_stable(authority: PortableRuntimeAuthority, repository_root: Path, tmp_path: Path) -> None:
    install = tmp_path / "hhs-runtime"
    plan, first = build_full(authority, repository_root, install)
    second = authority.build(plan, clean=True)
    assert first["manifest_identity"] == second["manifest_identity"]
    assert first["manifest_sha256"] == second["manifest_sha256"]
    verification = authority.verify(install)
    assert verification["classification"] == "HHS_PASS_184_PORTABLE_RUNTIME_PACKAGE_VERIFIED"
    assert verification["verified_file_count"] == 5

    launcher = (install / "bin" / "hhs-runtime").read_text(encoding="utf-8")
    environment = (install / "configuration" / "hhs.env").read_text(encoding="utf-8")
    service = (install / "service" / "hhs.service").read_text(encoding="utf-8")
    assert "exec" in launcher
    assert "hhs_runtime.pass184.cli serve" in launcher
    assert APP_IMPORT in environment
    assert "Type=simple" in service
    assert "Restart=on-failure" in service
    assert "ExecStart=" in service
    assert "&" not in service


def test_manifest_tamper_and_unexpected_file_are_rejected(authority: PortableRuntimeAuthority, repository_root: Path, tmp_path: Path) -> None:
    install = tmp_path / "hhs-runtime"
    build_full(authority, repository_root, install)
    environment = install / "configuration" / "hhs.env"
    environment.write_text(environment.read_text(encoding="utf-8") + "MUTATED=1\n", encoding="utf-8")
    with pytest.raises(Pass184Error) as tamper_error:
        authority.verify(install)
    assert tamper_error.value.status == "P184_REJECT_PACKAGE_TAMPER"

    build_full(authority, repository_root, install)
    (install / "bin" / "unauthorized").write_text("shadow authority\n", encoding="utf-8")
    with pytest.raises(Pass184Error) as file_set_error:
        authority.verify(install)
    assert file_set_error.value.status == "P184_REJECT_PACKAGE_FILE_SET"


def test_package_root_escape_rejected(tmp_path: Path) -> None:
    root = tmp_path / "packages"
    root.mkdir()
    assert ensure_within(root, root / "allowed") == (root / "allowed").resolve()
    with pytest.raises(Pass184Error) as error:
        ensure_within(root, tmp_path / "outside")
    assert error.value.status == "P184_REJECT_PACKAGE_ROOT_ESCAPE"


def test_listener_and_http_health_probe(authority: PortableRuntimeAuthority) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = authority.probe(host="127.0.0.1", port=server.server_port, timeout=2)
        assert result["classification"] == "HHS_PASS_184_HTTP_HEALTH_READY"
        assert result["ready"] is True
        assert result["tcp_listener"] is True
        assert result["http_health"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_process_running_without_listener_is_not_ready(authority: PortableRuntimeAuthority) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]
    result = authority.probe(host="127.0.0.1", port=port, timeout=0.2)
    assert result["classification"] == "HHS_PASS_184_PROCESS_RUNNING_NO_LISTENER"
    assert result["ready"] is False
    assert result["tcp_listener"] is False


def test_occupied_port_and_missing_application_module_fail_preflight(authority: PortableRuntimeAuthority, repository_root: Path, tmp_path: Path) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        with pytest.raises(Pass184Error) as occupied:
            authority.supervised_command(repository_root=repository_root, host="127.0.0.1", port=port)
        assert occupied.value.status == "P184_REJECT_PORT_OCCUPIED"

    with pytest.raises(Pass184Error) as missing:
        authority.supervised_command(repository_root=tmp_path / "missing", host="127.0.0.1", port=65431)
    assert missing.value.status == "P184_REJECT_APPLICATION_MODULE_MISSING"


def test_api_plan_package_verify_and_probe_boundaries(monkeypatch: pytest.MonkeyPatch, repository_root: Path, tmp_path: Path) -> None:
    package_root = tmp_path / "api-packages"
    monkeypatch.setenv("HHS_REPOSITORY_ROOT", str(repository_root))
    monkeypatch.setenv("HHS_PASS184_PACKAGE_ROOT", str(package_root))
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    status = client.get("/api/v1/pass184/status")
    assert status.status_code == 200
    assert status.json()["contract"] == CONTRACT_ID

    request = {"profile": "full", "install_name": "server-a", "host": "0.0.0.0", "port": 8080}
    plan = client.post("/api/v1/pass184/plan", json=request)
    assert plan.status_code == 200
    assert plan.json()["classification"] == "HHS_PASS_184_DETERMINISTIC_PACKAGE_PLAN_VERIFIED"

    package = client.post("/api/v1/pass184/package", json={**request, "clean": True})
    assert package.status_code == 200
    assert package.json()["classification"] == "HHS_PASS_184_PORTABLE_RUNTIME_PACKAGE_BUILT_AND_VERIFIED"

    verify = client.post("/api/v1/pass184/verify", json={"install_name": "server-a"})
    assert verify.status_code == 200
    assert verify.json()["verified_file_count"] == 5

    escape = client.post("/api/v1/pass184/plan", json={**request, "install_name": "../escape"})
    assert escape.status_code == 400
    assert escape.json()["detail"]["status"] == "P184_REJECT_INSTALL_NAME"

    remote = client.post("/api/v1/pass184/probe", json={"host": "example.com", "port": 80})
    assert remote.status_code == 400
    assert remote.json()["detail"]["status"] == "P184_REJECT_NON_LOOPBACK_PROBE"


def test_completion_receipt_requires_all_checks(tmp_path: Path) -> None:
    receipt_path = tmp_path / "PASS_184_COMPLETION.json"
    receipt = write_completion_receipt(
        receipt_path,
        {
            "deterministic_package": True,
            "manifest_verification": True,
            "listener_readiness": True,
            "systemd_foreground_authority": True,
        },
    )
    assert receipt["classification"].endswith("AUTHORITY_VERIFIED")
    assert len(receipt["receipt_sha256"]) == 64
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["receipt_sha256"] == receipt["receipt_sha256"]
    with pytest.raises(Pass184Error):
        write_completion_receipt(tmp_path / "bad.json", {"deterministic_package": False})


def test_repository_visible_deployment_and_studio_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    start = (root / "deployment" / "pass184" / "start.sh").read_text(encoding="utf-8")
    service = (root / "deployment" / "pass184" / "hhs.service.template").read_text(encoding="utf-8")
    html = (root / "applications" / "runtime_package_studio" / "index.html").read_text(encoding="utf-8")
    javascript = (root / "applications" / "runtime_package_studio" / "app.js").read_text(encoding="utf-8")
    composition = (root / "hhs_backend" / "application_ide_server.py").read_text(encoding="utf-8")

    assert "exec \"$PYTHON_BIN\" -m hhs_runtime.pass184.cli serve" in start
    assert "Type=simple" in service and "Restart=on-failure" in service
    assert "&" not in service
    assert "Runtime Package Studio" in html
    assert "/api/v1/pass184" in javascript
    assert "pass184_runtime_routes" in composition
    assert '"/runtime-package"' in composition
