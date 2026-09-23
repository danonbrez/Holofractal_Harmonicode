from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import signal
import stat
import time

import pytest

from hhs_runtime.pass220.ubuntu_guest_runtime import (
    GUEST_RUNTIME_SCHEMA,
    GuestRuntimeConfig,
    GuestRuntimeError,
    UbuntuGuestRuntime,
)


def _write_executable(path: Path, source: str) -> Path:
    path.write_text(source, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def _fixture_runtime(tmp_path: Path) -> UbuntuGuestRuntime:
    base = tmp_path / "ubuntu-base.qcow2"
    base.write_bytes(b"HHS-I043-IMMUTABLE-UBUNTU-BASE\n")
    digest = sha256(base.read_bytes()).hexdigest()

    qemu_img = _write_executable(
        tmp_path / "fake-qemu-img",
        """#!/usr/bin/env python3
import pathlib, sys
pathlib.Path(sys.argv[-1]).write_bytes(b"FAKE-QCOW2-OVERLAY\\n")
""",
    )
    qemu = _write_executable(
        tmp_path / "fake-qemu",
        """#!/usr/bin/env python3
import pathlib, subprocess, sys
args=sys.argv[1:]
pidfile=pathlib.Path(args[args.index("-pidfile")+1])
child=subprocess.Popen(
    ["sleep","300"],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    close_fds=True,
    start_new_session=True,
)
pidfile.parent.mkdir(parents=True, exist_ok=True)
pidfile.write_text(str(child.pid)+"\\n", encoding="utf-8")
""",
    )
    ssh = _write_executable(
        tmp_path / "fake-ssh",
        """#!/usr/bin/env python3
import sys, time
print("FAKE_GUEST_PTY_READY", flush=True)
for line in sys.stdin:
    print("REMOTE:"+line.rstrip("\\r\\n"), flush=True)
""",
    )
    identity = tmp_path / "guest-key"
    identity.write_text("fake-private-key\n", encoding="utf-8")
    known_hosts = tmp_path / "known_hosts"
    known_hosts.write_text("[127.0.0.1]:2222 ssh-ed25519 AAAATEST\n", encoding="utf-8")

    config = GuestRuntimeConfig(
        base_image=base,
        expected_sha256=digest,
        state_root=tmp_path / "state",
        qemu_bin=str(qemu),
        qemu_img_bin=str(qemu_img),
        ssh_bin=str(ssh),
        ssh_identity=identity,
        known_hosts=known_hosts,
        memory_mib=1024,
        cpus=2,
        ssh_port=2222,
    )
    return UbuntuGuestRuntime(config)


def _wait_for_text(session, needle: bytes, timeout: float = 2.0) -> bytes:
    deadline = time.monotonic() + timeout
    data = bytearray()
    while time.monotonic() < deadline:
        chunk = session.read(timeout=0.05)
        if chunk:
            data.extend(chunk)
            if needle in data:
                return bytes(data)
        if session.process.poll() is not None:
            break
    return bytes(data)


def test_base_image_identity_and_overlay_are_fail_closed(tmp_path: Path) -> None:
    runtime = _fixture_runtime(tmp_path)
    verified = runtime.verify_base_image()
    assert verified["identity_verified"] is True

    prepared = runtime.prepare_overlay()
    assert prepared["created"] is True
    assert runtime.overlay.is_file()

    runtime.config.base_image.write_bytes(b"mutated-base\n")
    with pytest.raises(GuestRuntimeError, match="DIGEST_MISMATCH"):
        runtime.verify_base_image()


def test_qemu_command_is_loopback_only_and_preserves_authority_boundary(
    tmp_path: Path,
) -> None:
    runtime = _fixture_runtime(tmp_path)
    runtime.prepare_overlay()
    command = runtime.qemu_command()
    joined = " ".join(command)

    assert "q35,accel=kvm:tcg" in command
    assert "hostfwd=tcp:127.0.0.1:2222-:22" in joined
    assert "hostfwd=tcp:0.0.0.0" not in joined
    assert str(runtime.qmp_socket) in joined
    assert str(runtime.pid_file) in joined

    status = runtime.status()
    assert status["schema"] == GUEST_RUNTIME_SCHEMA
    assert status["canonical_state_authority"] is False
    assert status["new_vm81_authority"] is False
    assert status["new_hash72_mint_authority"] is False
    assert status["new_hash216_persistence_authority"] is False
    assert status["existing_application_vm_control_plane_inside_guest"] is True


def test_fake_qemu_lifecycle_tracks_pid_and_fails_closed_on_stale_pid(
    tmp_path: Path,
) -> None:
    runtime = _fixture_runtime(tmp_path)
    started = runtime.start()
    pid = started["pid"]

    try:
        assert started["running"] is True
        assert started["transition"] == "START"
        assert started["receipt"]["canonical_state_commit"] is False
        assert runtime.manifest_path.is_file()

        stopped = runtime.stop(timeout=2.0)
        assert stopped["running"] is False
        assert stopped["transition"] == "STOP"

        runtime.pid_file.parent.mkdir(parents=True, exist_ok=True)
        runtime.pid_file.write_text("99999999\n", encoding="utf-8")
        with pytest.raises(GuestRuntimeError, match="STALE_PID_FAIL_CLOSED"):
            runtime.start()
    finally:
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, TypeError):
            pass


def test_ssh_transport_requires_identity_known_hosts_and_strict_verification(
    tmp_path: Path,
) -> None:
    runtime = _fixture_runtime(tmp_path)
    command = runtime.ssh_command(["bash", "-lc", "pwd"], allocate_tty=True)
    joined = " ".join(command)

    assert "BatchMode=yes" in joined
    assert "IdentitiesOnly=yes" in joined
    assert "StrictHostKeyChecking=yes" in joined
    assert "UserKnownHostsFile=" in joined
    assert "-tt" in command
    assert command[-2] == "hhs@127.0.0.1"
    assert command[-1] == "bash -lc pwd"


def test_real_local_pty_supports_read_write_resize_signal_and_close(
    tmp_path: Path,
) -> None:
    runtime = _fixture_runtime(tmp_path)
    runtime.prepare_overlay()
    runtime.pid_file.parent.mkdir(parents=True, exist_ok=True)
    runtime.pid_file.write_text(str(os.getpid()) + "\n", encoding="utf-8")

    session = runtime.open_pty(["bash"], rows=30, cols=100)
    try:
        initial = _wait_for_text(session, b"FAKE_GUEST_PTY_READY")
        assert b"FAKE_GUEST_PTY_READY" in initial
        assert session.snapshot()["canonical_state_authority"] is False

        session.resize(rows=40, cols=120)
        session.write("probe-i043\n")
        echoed = _wait_for_text(session, b"REMOTE:probe-i043")
        assert b"REMOTE:probe-i043" in echoed

        session.send_signal(signal.SIGTERM)
        session.wait(timeout=2.0)
        assert session.process.returncode is not None
    finally:
        session.close()


def test_existing_application_vm_shell_is_not_reclassified_as_guest_pty() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "docs/pass220/PASS_220_UBUNTU_APPLICATION_VM_BACKEND_CONTROL_PLANE_V1.md"
    ).read_text(encoding="utf-8")
    checkpoint = (
        Path(__file__).resolve().parents[2]
        / "docs/operations/restart/PASS_220_I043_UBUNTU_GUEST_RUNTIME_PTY_20260923.md"
    ).read_text(encoding="utf-8")

    assert "It is not reclassified as a Bash/PTTY transport." in checkpoint
    assert "hhs-vm shell -- hhs status" in source
