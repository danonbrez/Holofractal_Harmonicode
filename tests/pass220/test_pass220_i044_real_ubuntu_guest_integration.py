from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
import stat

from hhs_runtime.pass220.ubuntu_guest_runtime import (
    GuestRuntimeConfig,
    GuestRuntimeError,
    UbuntuGuestRuntime,
)


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_IMAGE_SHA = "612b2c0cc1bc413a6cb8c38fd611794caf0f2b436c50013d8b3794db12ad7354"


def _executable(path: Path) -> Path:
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_i044_manifest_pins_released_ubuntu_qcow2_and_no_authority() -> None:
    manifest = json.loads(
        (
            ROOT / "deployment/ubuntu/guest_runtime/ubuntu-24.04-amd64-image.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["schema"] == "HHS_PASS_220_I044_UBUNTU_GUEST_IMAGE_V1"
    assert manifest["release"] == "20260911"
    assert manifest["architecture"] == "amd64"
    assert manifest["format"] == "qcow2"
    assert manifest["filename"] == "ubuntu-24.04-server-cloudimg-amd64.img"
    assert manifest["sha256"] == EXPECTED_IMAGE_SHA
    assert manifest["url"].startswith(
        "https://cloud-images.ubuntu.com/releases/releases/noble/release-20260911/"
    )
    assert manifest["authority"]["canonical_hhs_state_authority"] is False
    assert manifest["authority"]["vm81_authority"] is False


def test_i043_runtime_attaches_existing_seed_readonly(tmp_path: Path) -> None:
    base = tmp_path / "base.img"
    base.write_bytes(b"base")
    overlay = tmp_path / "state/disk/overlay.qcow2"
    overlay.parent.mkdir(parents=True)
    overlay.write_bytes(b"overlay")
    seed = tmp_path / "seed.img"
    seed.write_bytes(b"seed")
    qemu = _executable(tmp_path / "qemu")

    runtime = UbuntuGuestRuntime(
        GuestRuntimeConfig(
            base_image=base,
            expected_sha256=sha256(base.read_bytes()).hexdigest(),
            state_root=tmp_path / "state",
            qemu_bin=str(qemu),
            seed_image=seed,
            memory_mib=1024,
            cpus=1,
        )
    )
    command = runtime.qemu_command()
    assert f"file={seed},if=virtio,format=raw,readonly=on" in command
    assert "hostfwd=tcp:127.0.0.1:2222-:22" in " ".join(command)
    status = runtime.status()
    assert status["seed_image"] == str(seed)
    assert status["seed_image_present"] is True
    assert status["canonical_state_authority"] is False


def test_i043_runtime_rejects_missing_configured_seed(tmp_path: Path) -> None:
    base = tmp_path / "base.img"
    base.write_bytes(b"base")
    qemu = _executable(tmp_path / "qemu")
    runtime = UbuntuGuestRuntime(
        GuestRuntimeConfig(
            base_image=base,
            expected_sha256=sha256(base.read_bytes()).hexdigest(),
            state_root=tmp_path / "state",
            qemu_bin=str(qemu),
            seed_image=tmp_path / "missing-seed.img",
            memory_mib=1024,
            cpus=1,
        )
    )
    runtime.overlay.parent.mkdir(parents=True)
    runtime.overlay.write_bytes(b"overlay")
    try:
        runtime.qemu_command()
    except GuestRuntimeError as exc:
        assert "HHS_GUEST_SEED_IMAGE_MISSING" in str(exc)
    else:
        raise AssertionError("missing configured seed did not fail closed")


def test_i044_preparation_is_digest_bound_release_scoped_and_strict_ssh() -> None:
    script = (
        ROOT / "deployment/ubuntu/guest_runtime/prepare-real-guest.sh"
    ).read_text(encoding="utf-8")
    assert 'STATE_ROOT="$RELEASE_ROOT/$TARGET_SHA"' in script
    assert 'sha256sum "$BASE_IMAGE"' in script
    assert 'sha256sum "$PART"' in script
    assert 'cloud-localds "$SEED_IMAGE"' in script
    assert 'ssh-keygen -q -t ed25519' in script
    assert "ssh_pwauth" in script
    assert "lock_passwd" in script
    assert "HHS_GUEST_SEED_IMAGE=$SEED_IMAGE" in script
    assert "canonical_state_authority" in script
    assert "HHS_APPLICATION_VM_REQUIRE_GUI=0" in script


def test_i044_real_gate_requires_guest_app_vm_and_real_pty_before_promotion() -> None:
    script = (
        ROOT / "deployment/ubuntu/guest_runtime/run-real-guest-integration.sh"
    ).read_text(encoding="utf-8")
    assert "sudo cloud-init status --wait --long" in script
    assert '[[ "$GUEST_SHA" == "$TARGET_SHA" ]]' in script
    assert "systemctl is-active --quiet hhs-application-vm.service" in script
    assert "http://127.0.0.1:8720/health" in script
    assert "single_vm81_authority_preserved" in script
    assert "guest pty-exec" in script
    assert "HHS_I044_PTY_OK" in script
    assert 'ln -sfnT "$STATE_ROOT" "$CURRENT_LINK"' in script
    assert script.index("HHS_I044_PTY_OK") < script.index(
        'ln -sfnT "$STATE_ROOT" "$CURRENT_LINK"'
    )


def test_i044_workflow_real_host_job_is_manual_only() -> None:
    workflow = (
        ROOT / ".github/workflows/pass220-i044-real-ubuntu-guest.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" in workflow
    assert "run_real_guest:" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "inputs.run_real_guest == true" in workflow
    assert "HHS_DIGITALOCEAN_SSH_PRIVATE_KEY" in workflow
    assert "StrictHostKeyChecking=yes" in workflow
    assert "run-real-guest-integration.sh" in workflow
