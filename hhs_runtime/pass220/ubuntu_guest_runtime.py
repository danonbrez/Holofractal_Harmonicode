"""Pass 220 I043 host-side Ubuntu guest lifecycle and PTY transport.

This module sits *beneath* the existing Ubuntu application-VM control plane.
It owns guest artifact identity, QEMU lifecycle, and authenticated SSH/PTTY
transport only. It never commits VM81/Hash72/Hash216 state and never replaces
the Pass 190 operation authority running inside the guest.
"""
from __future__ import annotations

from dataclasses import dataclass
import errno
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
import pty
import select
import shlex
import shutil
import signal
import socket
import struct
import subprocess
import termios
import time
from typing import Any, Mapping, Sequence
from uuid import uuid4


GUEST_RUNTIME_SCHEMA = "HHS_PASS_220_I043_UBUNTU_GUEST_RUNTIME_V1"
GUEST_PTY_SCHEMA = "HHS_PASS_220_I043_UBUNTU_GUEST_PTY_V1"
DEFAULT_STATE_ROOT = Path(".hhs_runtime_state/pass220/ubuntu-guest")


class GuestRuntimeError(RuntimeError):
    """Fail-closed guest runtime or transport rejection."""


def file_sha256(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _tool(explicit: str | None, fallback: str) -> str:
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        resolved = shutil.which(explicit)
        if resolved:
            return resolved
        raise GuestRuntimeError(f"HHS_GUEST_TOOL_NOT_EXECUTABLE:{explicit}")
    resolved = shutil.which(fallback)
    if not resolved:
        raise GuestRuntimeError(f"HHS_GUEST_TOOL_MISSING:{fallback}")
    return resolved


@dataclass(frozen=True)
class GuestRuntimeConfig:
    base_image: Path
    expected_sha256: str
    state_root: Path = DEFAULT_STATE_ROOT
    base_format: str = "qcow2"
    guest_name: str = "hhs-ubuntu"
    memory_mib: int = 4096
    cpus: int = 4
    ssh_port: int = 2222
    runtime_http_port: int = 18080
    guest_runtime_http_port: int = 8080
    application_api_port: int = 18720
    guest_application_api_port: int = 8720
    ssh_user: str = "hhs"
    ssh_identity: Path | None = None
    known_hosts: Path | None = None
    seed_image: Path | None = None
    qemu_bin: str | None = None
    qemu_img_bin: str | None = None
    ssh_bin: str | None = None

    def __post_init__(self) -> None:
        digest = self.expected_sha256.lower().strip()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise GuestRuntimeError("HHS_GUEST_EXPECTED_SHA256_INVALID")
        if self.base_format not in {"qcow2", "raw"}:
            raise GuestRuntimeError("HHS_GUEST_BASE_FORMAT_UNSUPPORTED")
        if not 1 <= self.cpus <= 256:
            raise GuestRuntimeError("HHS_GUEST_CPU_COUNT_INVALID")
        if not 256 <= self.memory_mib <= 1048576:
            raise GuestRuntimeError("HHS_GUEST_MEMORY_INVALID")
        if not 1024 <= self.ssh_port <= 65535:
            raise GuestRuntimeError("HHS_GUEST_SSH_PORT_INVALID")
        if not 1024 <= self.runtime_http_port <= 65535:
            raise GuestRuntimeError("HHS_GUEST_RUNTIME_HTTP_PORT_INVALID")
        if not 1 <= self.guest_runtime_http_port <= 65535:
            raise GuestRuntimeError("HHS_GUEST_RUNTIME_GUEST_PORT_INVALID")
        if not 1024 <= self.application_api_port <= 65535:
            raise GuestRuntimeError("HHS_GUEST_APPLICATION_API_PORT_INVALID")
        if not 1 <= self.guest_application_api_port <= 65535:
            raise GuestRuntimeError("HHS_GUEST_APPLICATION_API_GUEST_PORT_INVALID")
        if len({self.ssh_port, self.runtime_http_port, self.application_api_port}) != 3:
            raise GuestRuntimeError("HHS_GUEST_HOST_PORT_COLLISION")
        if not self.ssh_user or any(ch.isspace() for ch in self.ssh_user):
            raise GuestRuntimeError("HHS_GUEST_SSH_USER_INVALID")

    @classmethod
    def from_environment(cls) -> "GuestRuntimeConfig":
        base = os.environ.get("HHS_GUEST_BASE_IMAGE")
        digest = os.environ.get("HHS_GUEST_BASE_SHA256")
        if not base:
            raise GuestRuntimeError("HHS_GUEST_BASE_IMAGE_REQUIRED")
        if not digest:
            raise GuestRuntimeError("HHS_GUEST_BASE_SHA256_REQUIRED")
        identity = os.environ.get("HHS_GUEST_SSH_IDENTITY")
        known_hosts = os.environ.get("HHS_GUEST_SSH_KNOWN_HOSTS")
        seed_image = os.environ.get("HHS_GUEST_SEED_IMAGE")
        return cls(
            base_image=Path(base).expanduser().resolve(),
            expected_sha256=digest,
            state_root=Path(
                os.environ.get("HHS_GUEST_STATE_ROOT", DEFAULT_STATE_ROOT)
            ).expanduser().resolve(),
            base_format=os.environ.get("HHS_GUEST_BASE_FORMAT", "qcow2"),
            guest_name=os.environ.get("HHS_GUEST_NAME", "hhs-ubuntu"),
            memory_mib=int(os.environ.get("HHS_GUEST_MEMORY_MIB", "4096")),
            cpus=int(os.environ.get("HHS_GUEST_CPUS", "4")),
            ssh_port=int(os.environ.get("HHS_GUEST_SSH_PORT", "2222")),
            runtime_http_port=int(os.environ.get("HHS_GUEST_RUNTIME_HTTP_PORT", "18080")),
            guest_runtime_http_port=int(os.environ.get("HHS_GUEST_RUNTIME_GUEST_PORT", "8080")),
            application_api_port=int(os.environ.get("HHS_GUEST_APPLICATION_API_PORT", "18720")),
            guest_application_api_port=int(os.environ.get("HHS_GUEST_APPLICATION_API_GUEST_PORT", "8720")),
            ssh_user=os.environ.get("HHS_GUEST_SSH_USER", "hhs"),
            ssh_identity=Path(identity).expanduser().resolve() if identity else None,
            known_hosts=(
                Path(known_hosts).expanduser().resolve() if known_hosts else None
            ),
            seed_image=(
                Path(seed_image).expanduser().resolve() if seed_image else None
            ),
            qemu_bin=os.environ.get("HHS_GUEST_QEMU_BIN"),
            qemu_img_bin=os.environ.get("HHS_GUEST_QEMU_IMG_BIN"),
            ssh_bin=os.environ.get("HHS_GUEST_SSH_BIN"),
        )


class GuestPTYSession:
    """One authenticated remote shell backed by a real local PTY."""

    def __init__(
        self,
        command: Sequence[str],
        *,
        rows: int = 24,
        cols: int = 80,
        env: Mapping[str, str] | None = None,
    ) -> None:
        if rows < 1 or cols < 1:
            raise GuestRuntimeError("HHS_GUEST_PTY_SIZE_INVALID")
        self.session_id = uuid4().hex
        self.command = tuple(command)
        self.created_monotonic = time.monotonic()
        master_fd, slave_fd = pty.openpty()
        self.master_fd = master_fd
        self._closed = False
        self.resize(rows=rows, cols=cols)
        flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
        fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        try:
            self.process = subprocess.Popen(
                list(command),
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True,
                start_new_session=True,
                env=dict(env) if env is not None else None,
            )
        finally:
            os.close(slave_fd)

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": GUEST_PTY_SCHEMA,
            "session_id": self.session_id,
            "pid": self.process.pid,
            "running": self.process.poll() is None,
            "exit_status": self.process.poll(),
            "command": list(self.command),
            "canonical_state_authority": False,
        }

    def read(self, *, max_bytes: int = 65536, timeout: float = 0.0) -> bytes:
        if self._closed:
            return b""
        if max_bytes < 1 or max_bytes > 1024 * 1024:
            raise GuestRuntimeError("HHS_GUEST_PTY_READ_SIZE_INVALID")
        ready, _, _ = select.select([self.master_fd], [], [], max(0.0, timeout))
        if not ready:
            return b""
        try:
            return os.read(self.master_fd, max_bytes)
        except OSError as exc:
            if exc.errno in {errno.EIO, errno.EBADF}:
                return b""
            raise

    def write(self, data: bytes | str) -> int:
        if self._closed:
            raise GuestRuntimeError("HHS_GUEST_PTY_SESSION_CLOSED")
        raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
        return os.write(self.master_fd, raw)

    def resize(self, *, rows: int, cols: int) -> None:
        if rows < 1 or cols < 1 or rows > 4096 or cols > 4096:
            raise GuestRuntimeError("HHS_GUEST_PTY_SIZE_INVALID")
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    def send_signal(self, sig: int) -> None:
        if self.process.poll() is None:
            os.killpg(self.process.pid, sig)

    def wait(self, timeout: float | None = None) -> int:
        return self.process.wait(timeout=timeout)

    def close(self, *, timeout: float = 2.0) -> int | None:
        if self._closed:
            return self.process.poll()
        try:
            if self.process.poll() is None:
                self.send_signal(signal.SIGHUP)
                try:
                    self.process.wait(timeout=max(0.0, timeout))
                except subprocess.TimeoutExpired:
                    os.killpg(self.process.pid, signal.SIGKILL)
                    self.process.wait(timeout=2.0)
            return self.process.returncode
        finally:
            self._closed = True
            try:
                os.close(self.master_fd)
            except OSError:
                pass

    def __enter__(self) -> "GuestPTYSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class UbuntuGuestRuntime:
    """Host-side guest artifact, lifecycle, and transport authority."""

    def __init__(self, config: GuestRuntimeConfig) -> None:
        self.config = config
        self.state_root = config.state_root
        self.overlay = self.state_root / "disk" / "overlay.qcow2"
        self.pid_file = self.state_root / "run" / "qemu.pid"
        self.qmp_socket = self.state_root / "run" / "qmp.sock"
        self.manifest_path = self.state_root / "guest-runtime.receipt.json"

    def verify_base_image(self) -> dict[str, Any]:
        path = self.config.base_image
        if not path.is_file():
            raise GuestRuntimeError(f"HHS_GUEST_BASE_IMAGE_MISSING:{path}")
        actual = file_sha256(path)
        expected = self.config.expected_sha256.lower()
        if actual != expected:
            raise GuestRuntimeError(
                f"HHS_GUEST_BASE_IMAGE_DIGEST_MISMATCH:{expected}:{actual}"
            )
        return {
            "path": str(path),
            "format": self.config.base_format,
            "sha256": actual,
            "identity_verified": True,
        }

    def prepare_overlay(self) -> dict[str, Any]:
        base = self.verify_base_image()
        self.overlay.parent.mkdir(parents=True, exist_ok=True)
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        if self.overlay.exists():
            return {
                "schema": GUEST_RUNTIME_SCHEMA,
                "prepared": True,
                "created": False,
                "base": base,
                "overlay": str(self.overlay),
            }
        qemu_img = _tool(self.config.qemu_img_bin, "qemu-img")
        command = [
            qemu_img,
            "create",
            "-f",
            "qcow2",
            "-F",
            self.config.base_format,
            "-b",
            str(self.config.base_image),
            str(self.overlay),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode != 0 or not self.overlay.exists():
            raise GuestRuntimeError(
                "HHS_GUEST_OVERLAY_CREATE_FAILED:"
                + (completed.stderr.strip() or completed.stdout.strip())
            )
        return {
            "schema": GUEST_RUNTIME_SCHEMA,
            "prepared": True,
            "created": True,
            "base": base,
            "overlay": str(self.overlay),
            "command": command,
        }

    def qemu_command(self) -> list[str]:
        qemu = _tool(self.config.qemu_bin, "qemu-system-x86_64")
        command = [
            qemu,
            "-name",
            self.config.guest_name,
            "-machine",
            "q35,accel=kvm:tcg",
            "-m",
            str(self.config.memory_mib),
            "-smp",
            str(self.config.cpus),
            "-drive",
            f"file={self.overlay},if=virtio,format=qcow2,cache=none",
        ]
        if self.config.seed_image is not None:
            seed = self.config.seed_image
            if not seed.is_file():
                raise GuestRuntimeError(f"HHS_GUEST_SEED_IMAGE_MISSING:{seed}")
            command.extend(
                [
                    "-drive",
                    f"file={seed},if=virtio,format=raw,readonly=on",
                ]
            )
        command.extend(
            [
                "-netdev",
                (
                    "user,id=hhsnet0,"
                    f"hostfwd=tcp:127.0.0.1:{self.config.ssh_port}-:22,"
                    f"hostfwd=tcp:127.0.0.1:{self.config.runtime_http_port}-:{self.config.guest_runtime_http_port},"
                    f"hostfwd=tcp:127.0.0.1:{self.config.application_api_port}-:{self.config.guest_application_api_port}"
                ),
                "-device",
                "virtio-net-pci,netdev=hhsnet0",
                "-qmp",
                f"unix:{self.qmp_socket},server=on,wait=off",
                "-display",
                "none",
                "-serial",
                "none",
                "-daemonize",
                "-pidfile",
                str(self.pid_file),
            ]
        )
        return command

    def _pid(self) -> int | None:
        if not self.pid_file.is_file():
            return None
        raw = self.pid_file.read_text(encoding="utf-8", errors="replace").strip()
        if not raw.isdigit():
            return None
        return int(raw)

    @staticmethod
    def _pid_alive(pid: int | None) -> bool:
        if not pid or pid <= 1:
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            pass

        # kill(pid, 0) succeeds for Linux zombies. Treat a zombie as stopped so
        # lifecycle polling cannot preserve a dead QEMU process indefinitely.
        proc_stat = Path(f"/proc/{pid}/stat")
        try:
            suffix = proc_stat.read_text(
                encoding="utf-8", errors="replace"
            ).rsplit(") ", 1)[1]
            state = suffix.split(None, 1)[0]
            if state == "Z":
                return False
        except (OSError, IndexError):
            # /proc is Linux-specific and can race with process exit. The
            # successful kill(0) probe remains the portable fallback.
            pass
        return True

    def status(self) -> dict[str, Any]:
        pid = self._pid()
        running = self._pid_alive(pid)
        stale = pid is not None and not running
        base: dict[str, Any]
        try:
            base = self.verify_base_image()
        except GuestRuntimeError as exc:
            base = {"identity_verified": False, "error": str(exc)}
        return {
            "schema": GUEST_RUNTIME_SCHEMA,
            "guest_name": self.config.guest_name,
            "state": "RUNNING" if running else ("STALE_PID" if stale else "STOPPED"),
            "running": running,
            "stale_pid": stale,
            "pid": pid,
            "qmp_socket": str(self.qmp_socket),
            "qmp_socket_present": self.qmp_socket.exists(),
            "overlay": str(self.overlay),
            "overlay_present": self.overlay.is_file(),
            "seed_image": (
                str(self.config.seed_image) if self.config.seed_image is not None else None
            ),
            "seed_image_present": bool(
                self.config.seed_image is not None and self.config.seed_image.is_file()
            ),
            "base": base,
            "ssh": {
                "host": "127.0.0.1",
                "port": self.config.ssh_port,
                "user": self.config.ssh_user,
                "loopback_only": True,
            },
            "hypervisor": "QEMU",
            "accelerator_policy": "KVM_THEN_TCG",
            "existing_application_vm_control_plane_inside_guest": True,
            "canonical_state_authority": False,
            "new_vm81_authority": False,
            "new_hash72_mint_authority": False,
            "new_hash216_persistence_authority": False,
        }

    def _receipt(self, *, transition: str, qemu_command: Sequence[str] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": GUEST_RUNTIME_SCHEMA,
            "transition": transition,
            "guest_name": self.config.guest_name,
            "base_image": str(self.config.base_image),
            "base_sha256": self.config.expected_sha256.lower(),
            "overlay": str(self.overlay),
            "seed_image": (
                str(self.config.seed_image) if self.config.seed_image is not None else None
            ),
            "pid_file": str(self.pid_file),
            "qmp_socket": str(self.qmp_socket),
            "ssh_host": "127.0.0.1",
            "ssh_port": self.config.ssh_port,
            "ssh_user": self.config.ssh_user,
            "canonical_state_commit": False,
            "new_vm81_authority": False,
        }
        if qemu_command is not None:
            payload["qemu_command"] = list(qemu_command)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        payload["runtime_receipt_sha256"] = sha256(encoded).hexdigest()
        _atomic_json(self.manifest_path, payload)
        return payload

    def start(self) -> dict[str, Any]:
        current = self.status()
        if current["running"]:
            return {
                **current,
                "transition": "START_IDEMPOTENT_ALREADY_RUNNING",
            }
        if current["stale_pid"]:
            raise GuestRuntimeError("HHS_GUEST_STALE_PID_FAIL_CLOSED")
        self.prepare_overlay()
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.qmp_socket.unlink(missing_ok=True)
        command = self.qemu_command()
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            raise GuestRuntimeError(
                "HHS_GUEST_QEMU_START_FAILED:"
                + (completed.stderr.strip() or completed.stdout.strip())
            )
        deadline = time.monotonic() + 5.0
        pid: int | None = None
        while time.monotonic() < deadline:
            pid = self._pid()
            if self._pid_alive(pid):
                break
            time.sleep(0.05)
        if not self._pid_alive(pid):
            raise GuestRuntimeError("HHS_GUEST_QEMU_PID_NOT_LIVE_AFTER_START")
        receipt = self._receipt(transition="START", qemu_command=command)
        return {**self.status(), "transition": "START", "receipt": receipt}

    def _qmp_execute(self, execute: str) -> dict[str, Any]:
        if not self.qmp_socket.exists():
            raise GuestRuntimeError("HHS_GUEST_QMP_SOCKET_MISSING")
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(2.0)
                client.connect(str(self.qmp_socket))
                stream = client.makefile("rwb", buffering=0)
                greeting = stream.readline()
                if not greeting:
                    raise GuestRuntimeError("HHS_GUEST_QMP_GREETING_MISSING")
                stream.write(b'{"execute":"qmp_capabilities"}\n')
                capabilities = stream.readline()
                if not capabilities:
                    raise GuestRuntimeError("HHS_GUEST_QMP_CAPABILITIES_FAILED")
                stream.write(
                    json.dumps({"execute": execute}, separators=(",", ":")).encode("utf-8")
                    + b"\n"
                )
                response = stream.readline()
                if not response:
                    raise GuestRuntimeError("HHS_GUEST_QMP_RESPONSE_MISSING")
                decoded = json.loads(response)
                if "error" in decoded:
                    raise GuestRuntimeError(
                        "HHS_GUEST_QMP_REJECTED:"
                        + json.dumps(decoded["error"], sort_keys=True)
                    )
                return decoded
        except (OSError, json.JSONDecodeError) as exc:
            raise GuestRuntimeError(f"HHS_GUEST_QMP_IO_FAILED:{exc}") from exc

    def stop(self, *, timeout: float = 8.0) -> dict[str, Any]:
        current = self.status()
        pid = current["pid"]
        if current["stale_pid"]:
            raise GuestRuntimeError("HHS_GUEST_STALE_PID_FAIL_CLOSED")
        if not current["running"]:
            return {**current, "transition": "STOP_IDEMPOTENT_ALREADY_STOPPED"}
        try:
            self._qmp_execute("quit")
        except GuestRuntimeError:
            assert isinstance(pid, int)
            os.kill(pid, signal.SIGTERM)
        deadline = time.monotonic() + max(0.1, timeout)
        while time.monotonic() < deadline and self._pid_alive(pid):
            time.sleep(0.05)
        if self._pid_alive(pid):
            assert isinstance(pid, int)
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.05)
        if self._pid_alive(pid):
            raise GuestRuntimeError("HHS_GUEST_QEMU_STOP_TIMEOUT")
        self.pid_file.unlink(missing_ok=True)
        self.qmp_socket.unlink(missing_ok=True)
        receipt = self._receipt(transition="STOP")
        return {**self.status(), "transition": "STOP", "receipt": receipt}

    def restart(self) -> dict[str, Any]:
        self.stop()
        result = self.start()
        return {**result, "transition": "RESTART"}

    def _transport_files(self) -> tuple[Path, Path]:
        identity = self.config.ssh_identity
        known_hosts = self.config.known_hosts
        if identity is None:
            raise GuestRuntimeError("HHS_GUEST_SSH_IDENTITY_REQUIRED")
        if known_hosts is None:
            raise GuestRuntimeError("HHS_GUEST_SSH_KNOWN_HOSTS_REQUIRED")
        if not identity.is_file() or not os.access(identity, os.R_OK):
            raise GuestRuntimeError(f"HHS_GUEST_SSH_IDENTITY_UNREADABLE:{identity}")
        if not known_hosts.is_file() or not os.access(known_hosts, os.R_OK):
            raise GuestRuntimeError(
                f"HHS_GUEST_SSH_KNOWN_HOSTS_UNREADABLE:{known_hosts}"
            )
        return identity, known_hosts

    def ssh_command(
        self,
        remote_command: Sequence[str] | str | None = None,
        *,
        allocate_tty: bool = True,
    ) -> list[str]:
        identity, known_hosts = self._transport_files()
        ssh = _tool(self.config.ssh_bin, "ssh")
        command = [
            ssh,
            "-o",
            "BatchMode=yes",
            "-o",
            "IdentitiesOnly=yes",
            "-o",
            "StrictHostKeyChecking=yes",
            "-o",
            f"UserKnownHostsFile={known_hosts}",
            "-o",
            "ConnectTimeout=10",
            "-i",
            str(identity),
            "-p",
            str(self.config.ssh_port),
        ]
        if allocate_tty:
            command.append("-tt")
        command.append(f"{self.config.ssh_user}@127.0.0.1")
        if remote_command:
            if isinstance(remote_command, str):
                command.append(remote_command)
            else:
                command.append(shlex.join([str(part) for part in remote_command]))
        return command

    def open_pty(
        self,
        remote_command: Sequence[str] | str | None = None,
        *,
        rows: int = 24,
        cols: int = 80,
        env: Mapping[str, str] | None = None,
    ) -> GuestPTYSession:
        status = self.status()
        if not status["running"]:
            raise GuestRuntimeError("HHS_GUEST_NOT_RUNNING")
        return GuestPTYSession(
            self.ssh_command(remote_command, allocate_tty=True),
            rows=rows,
            cols=cols,
            env=env,
        )


__all__ = [
    "DEFAULT_STATE_ROOT",
    "GUEST_PTY_SCHEMA",
    "GUEST_RUNTIME_SCHEMA",
    "GuestPTYSession",
    "GuestRuntimeConfig",
    "GuestRuntimeError",
    "UbuntuGuestRuntime",
    "file_sha256",
]
