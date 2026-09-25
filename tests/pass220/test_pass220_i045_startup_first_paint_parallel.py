from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import types

import pytest

from deployment.digitalocean.configure_runtime_os_static_first import patch_nginx_text
from hhs_backend import runtime_status_probe


ROOT = Path(__file__).resolve().parents[2]


def test_static_first_nginx_serves_only_root_and_assets_without_backend() -> None:
    source = """
server {
    listen 80;
    server_name 159.65.178.254;
    return 308 https://159.65.178.254$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 159.65.178.254;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
    }
}
"""
    patched = patch_nginx_text(source, Path("/var/lib/hhs/runtime-os/current"))
    assert "# HHS_RUNTIME_OS_STATIC_FIRST_V1_BEGIN" in patched
    assert "location = / {" in patched
    assert "location ^~ /assets/ {" in patched
    assert "root /var/lib/hhs/runtime-os/current;" in patched
    assert "try_files /index.html =503;" in patched
    assert "try_files $uri =404;" in patched
    assert patched.count("proxy_pass http://127.0.0.1:8080;") == 1
    assert patched.index("location = / {") < patched.index("location / {")

    # Idempotent update: the marker block is replaced, not duplicated.
    patched_again = patch_nginx_text(patched, Path("/var/lib/hhs/runtime-os/current"))
    assert patched_again.count("# HHS_RUNTIME_OS_STATIC_FIRST_V1_BEGIN") == 1
    assert patched_again.count("# HHS_RUNTIME_OS_STATIC_FIRST_V1_END") == 1


def test_static_first_nginx_rejects_ambiguous_tls_runtime_blocks() -> None:
    block = """
server {
    listen 443 ssl;
    location / { proxy_pass http://127.0.0.1:8080; }
}
"""
    with pytest.raises(RuntimeError, match="TLS_PROXY_BLOCK_COUNT_INVALID"):
        patch_nginx_text(block + block, Path("/var/lib/hhs/runtime-os/current"))


def test_status_probe_overlaps_read_only_routes_but_emits_input_order(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    active = 0
    max_active = 0

    async def app(scope, receive, send) -> None:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.03 if scope["path"] == "/slow" else 0.01)
        payload = json.dumps({"path": scope["path"]}).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": payload})
        active -= 1

    fake_module = types.ModuleType("hhs_backend.visual_server")
    fake_module.app = app
    monkeypatch.setitem(sys.modules, "hhs_backend.visual_server", fake_module)
    monkeypatch.setattr(
        runtime_status_probe,
        "install_read_only_unified_ledger_projection",
        lambda: {
            "mode": "READ_ONLY_UNIFIED_LEDGER",
            "canonical_ledger_mutated": False,
        },
    )

    asyncio.run(runtime_status_probe.run(["/slow", "/fast"], concurrency=2))
    records = [
        json.loads(line)
        for line in capsys.readouterr().out.splitlines()
        if line.strip()
    ]

    assert max_active == 2
    assert [record["path"] for record in records] == ["/slow", "/fast"]
    assert all(record["probe_concurrency"] == 2 for record in records)
    assert all(
        record["ledger_isolation"]["canonical_ledger_mutated"] is False
        for record in records
    )


def test_boot_recovery_defers_heavy_updater_and_bounds_probe_contention() -> None:
    timer = (
        ROOT
        / "deployment/digitalocean/guarded_auto_update/hhs-guarded-update.timer"
    ).read_text(encoding="utf-8")
    service = (
        ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service"
    ).read_text(encoding="utf-8")
    installer = (
        ROOT / "deployment/digitalocean/guarded_auto_update/install.sh"
    ).read_text(encoding="utf-8")

    assert "OnBootSec=10min" in timer
    assert "OnBootSec=3min" not in timer
    assert "HHS_RUNTIME_STATUS_PROBE_START_DELAY_SECONDS=90" in service
    assert "HHS_RUNTIME_STATUS_PROBE_CONCURRENCY=2" in service
    assert "configure_runtime_os_static_first.py" in installer
    assert '--runtime-os-root "$BUNDLE_ROOT/current"' in installer


def test_static_first_projection_does_not_claim_hhs_authority() -> None:
    source = (
        ROOT / "deployment/digitalocean/configure_runtime_os_static_first.py"
    ).read_text(encoding="utf-8")
    assert "CANONICAL_AUTHORITY=0" in source
    assert "Backend/API authority remains on :8080" in source
    assert "VM81" in source
    assert "Hash72" in source
    assert "Hash216" in source
