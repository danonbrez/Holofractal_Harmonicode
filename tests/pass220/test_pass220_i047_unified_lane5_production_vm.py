from __future__ import annotations

from hashlib import sha256
import importlib.util
from pathlib import Path

import pytest

from hhs_runtime.pass220.ubuntu_guest_runtime import (
    GuestRuntimeConfig,
    GuestRuntimeError,
    UbuntuGuestRuntime,
)


ROOT = Path(__file__).resolve().parents[2]


def _load_proxy_module():
    path = ROOT / "deployment/ubuntu/guest_runtime/configure-unified-guest-proxy.py"
    spec = importlib.util.spec_from_file_location("hhs_i047_guest_proxy", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_i047_qemu_exposes_only_loopback_guest_transports(tmp_path: Path) -> None:
    base = tmp_path / "base.img"
    base.write_bytes(b"base")
    overlay = tmp_path / "state/disk/overlay.qcow2"
    overlay.parent.mkdir(parents=True)
    overlay.write_bytes(b"overlay")
    qemu = tmp_path / "qemu"
    qemu.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    qemu.chmod(0o755)

    runtime = UbuntuGuestRuntime(
        GuestRuntimeConfig(
            base_image=base,
            expected_sha256=sha256(base.read_bytes()).hexdigest(),
            state_root=tmp_path / "state",
            qemu_bin=str(qemu),
            memory_mib=1024,
            cpus=1,
        )
    )
    netdev = " ".join(runtime.qemu_command())
    assert "hostfwd=tcp:127.0.0.1:2222-:22" in netdev
    assert "hostfwd=tcp:127.0.0.1:18080-:8080" in netdev
    assert "hostfwd=tcp:127.0.0.1:18720-:8720" in netdev
    assert "hostfwd=tcp:0.0.0.0:" not in netdev
    assert "hostfwd=tcp:[::]:" not in netdev


def test_i047_rejects_host_forward_port_collision(tmp_path: Path) -> None:
    base = tmp_path / "base.img"
    base.write_bytes(b"base")
    with pytest.raises(GuestRuntimeError, match="HHS_GUEST_HOST_PORT_COLLISION"):
        GuestRuntimeConfig(
            base_image=base,
            expected_sha256=sha256(base.read_bytes()).hexdigest(),
            ssh_port=2222,
            runtime_http_port=2222,
        )


def test_i047_host_service_is_vm_supervisor_only() -> None:
    service = (ROOT / "deployment/ubuntu/guest_runtime/hhs-unified-vm.service").read_text(encoding="utf-8")
    manager = (ROOT / "deployment/ubuntu/guest_runtime/manage-unified-vm.sh").read_text(encoding="utf-8")
    assert "HHS Lane 5 BIOS Unified VM Supervisor" in service
    assert "manage-unified-vm.sh start" in service
    assert "manage-unified-vm.sh stop" in service
    assert "uvicorn" not in service
    assert "production_visual_server" not in service
    assert "hhs-guest" in manager
    assert "HHS_GUEST_RUNTIME_HTTP_PORT" in manager
    assert "HHS_GUEST_APPLICATION_API_PORT" in manager


def test_i047_guest_runs_existing_runtime_os_and_application_vm() -> None:
    guest_service = (ROOT / "deployment/ubuntu/guest_runtime/hhs-unified-guest-ide.service").read_text(encoding="utf-8")
    selector = (ROOT / "hhs_backend/pass220_unified_guest_server.py").read_text(encoding="utf-8")
    installer = (ROOT / "deployment/ubuntu/guest_runtime/install-unified-guest-ide.sh").read_text(encoding="utf-8")

    assert "Requires=hhs-application-vm.service" in guest_service
    assert "hhs_backend.pass220_unified_guest_server:app" in guest_service
    assert "hhs_backend.runtime_os_application_server import app" in selector
    assert "hhs_backend.application_ide_server import app" in selector
    assert "hhs_pass220_i047_canonical_authority = False" in selector
    assert "HHS_PASS219_LANE5_STATE_ROOT=/var/lib/hhs/pass219/lane5" in installer
    assert "HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/current" in installer
    assert "HHS_DISABLE_C_AUTOBUILD=1" in installer


def test_i047_real_guest_requires_exact_runtime_os_before_production_cutover() -> None:
    script = (ROOT / "deployment/ubuntu/guest_runtime/run-real-guest-integration.sh").read_text(encoding="utf-8")
    assert "HHS_GUEST_REQUIRE_RUNTIME_OS" in script
    assert 'GUEST_RUNTIME_OS_RELEASE="/var/lib/hhs/runtime-os/releases/$TARGET_SHA"' in script
    assert "hhs-unified-guest-ide.service" in script
    assert "runtime-os-interface.json" in script
    assert '"runtime_os_attached"' in script
    assert '"frontend_transport_ready": True' in script
    assert script.index("HHS_I047_GUEST_IDE_TRANSPORT_VERIFIED") < script.index(
        'ln -sfnT "$STATE_ROOT" "$CURRENT_LINK"'
    )


def test_i047_proxy_cutover_is_reversible_and_guest_only() -> None:
    module = _load_proxy_module()
    source = """
server {
    listen 443 ssl;
    location / {
        proxy_pass http://127.0.0.1:8080;
    }
}
"""
    guest, changed = module.patch_runtime_backend(source, target="guest")
    assert changed is True
    assert "proxy_pass http://127.0.0.1:18080" in guest
    assert "proxy_pass http://127.0.0.1:8080" not in guest
    assert "HHS_PASS_220_I047_UNIFIED_GUEST_DYNAMIC_BACKEND" in guest

    restored, changed_back = module.patch_runtime_backend(guest, target="host")
    assert changed_back is True
    assert "proxy_pass http://127.0.0.1:8080" in restored
    assert "proxy_pass http://127.0.0.1:18080" not in restored


def test_i047_guarded_promotion_orders_guest_before_public_cutover() -> None:
    updater = (ROOT / "deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh").read_text(encoding="utf-8")
    guest = updater.index("Booting and verifying exact-SHA unified Ubuntu guest")
    sync = updater.index("sync_installed_assets", guest)
    start = updater.index("start_units", sync)
    health = updater.index("wait_for_health", start)
    cutover = updater.index("Cutting public dynamic transport from host Python to unified guest")
    promoted = updater.index('write_receipt "promotion" "PROMOTED"', cutover)
    assert guest < sync < start < health < cutover < promoted
    assert "HHS_GUEST_PERSISTENT_VM=1" in updater
    assert "HHS_GUEST_REQUIRE_RUNTIME_OS=1" in updater
    assert "configure-unified-guest-proxy.py" in updater
    assert "systemctl disable --now hhs-application-vm.service" in updater


def test_i047_exact_main_acceptance_rejects_host_application_listener() -> None:
    workflow = (ROOT / ".github/workflows/digitalocean-production-main.yml").read_text(encoding="utf-8")
    assert "HHS Lane 5 BIOS Unified VM Supervisor" in workflow
    assert "host application listener on 8080 remains after unified VM cutover" in workflow
    assert "http://127.0.0.1:18080/api/interface/status" in workflow
    assert "runtime_os_attached" in workflow
    assert "single_vm81_authority_preserved" in workflow
    assert "legacy host application VM listener on 8720 remains after unified VM cutover" in workflow



def test_i047_production_uses_one_persistent_guest_disk_across_sha_receipts() -> None:
    prepare = (ROOT / "deployment/ubuntu/guest_runtime/prepare-real-guest.sh").read_text(encoding="utf-8")
    integration = (ROOT / "deployment/ubuntu/guest_runtime/run-real-guest-integration.sh").read_text(encoding="utf-8")
    assert 'PERSISTENT_VM="${HHS_GUEST_PERSISTENT_VM:-0}"' in prepare
    assert 'RUNTIME_STATE_ROOT="$ROOT/machine"' in prepare
    assert 'instance-id: $INSTANCE_ID' in prepare
    assert 'INSTANCE_ID="hhs-unified-lane5-machine"' in prepare
    assert 'HHS_GUEST_STATE_ROOT=$RUNTIME_STATE_ROOT' in prepare
    assert 'PERSISTENT_VM="${HHS_GUEST_PERSISTENT_VM:-0}"' in integration
    assert "git -C /opt/holofractal-harmonicode checkout --detach" in integration
    assert "application_vm/install.sh" in integration
    assert "install-unified-guest-ide.sh" in integration

def test_i047_independent_host_application_vm_deployment_is_retired() -> None:
    workflow = (ROOT / ".github/workflows/pass220-ubuntu-application-vm-production.yml").read_text(encoding="utf-8")
    assert "Unified Production Contract" in workflow
    assert "Deploy independent Ubuntu application VM release" not in workflow
    assert "ssh " not in workflow
    assert "scp " not in workflow
    assert "HHS_I047_NO_PARALLEL_HOST_APPLICATION_DEPLOYMENT=1" in workflow
