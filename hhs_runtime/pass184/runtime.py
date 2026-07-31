"""Deterministic package, verification, readiness, and service supervision for Pass 184."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import time
from typing import Any, Iterable, Mapping, Sequence

CONTRACT_ID = "HHS-P184-PHRP-PSRA-VM81-H72-H216"
RUNTIME_VERSION = "1.0.0"
APP_IMPORT = "hhs_backend.application_ide_server:app"
HEALTH_PATH = "/health"
ZERO_SHA256 = "0" * 64

COMPONENT_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "vm81": (),
    "hash72": ("vm81",),
    "hash216": ("hash72",),
    "configuration": (),
    "manifests": ("hash216",),
    "receipts": ("hash72", "hash216", "manifests"),
    "api": ("vm81", "hash216"),
    "websocket": ("api",),
    "health": ("api",),
    "service": ("configuration", "manifests", "health"),
    "text": ("api",),
    "audio": ("api",),
    "graphics": ("api",),
    "video": ("audio", "graphics"),
    "games": ("graphics", "audio", "websocket"),
    "documents": ("text",),
    "applications": ("documents", "websocket"),
    "multimodal": ("text", "audio", "graphics", "video", "documents", "applications"),
    "assistant": ("text", "websocket"),
    "workspace": ("applications",),
    "application_ide": ("workspace", "assistant", "multimodal", "service", "receipts"),
}

COMPONENT_ORDER = tuple(COMPONENT_DEPENDENCIES)

PROFILE_SEEDS: dict[str, tuple[str, ...]] = {
    "minimal": ("service", "receipts"),
    "text": ("text", "service", "receipts"),
    "audio": ("audio", "service", "receipts"),
    "graphics": ("graphics", "service", "receipts"),
    "video": ("video", "service", "receipts"),
    "games": ("games", "service", "receipts"),
    "documents": ("documents", "service", "receipts"),
    "applications": ("applications", "service", "receipts"),
    "multimodal": ("multimodal", "service", "receipts"),
    "full": ("application_ide",),
}

TOOL_NAMES = (
    "cc",
    "make",
    "node",
    "ffmpeg",
    "ffprobe",
    "systemctl",
    "docker",
    "podman",
)

REQUIRED_PACKAGE_DIRS = (
    "bin",
    "configuration",
    "profiles",
    "manifests",
    "service",
    "installation-evidence",
)


class Pass184Error(RuntimeError):
    """Typed Pass 184 failure carrying a stable status classification."""

    def __init__(self, status: str, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_184_ERROR_V1",
            "contract": CONTRACT_ID,
            "status": self.status,
            "message": self.message,
            "details": self.details,
        }


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _file_digest(path: Path) -> str:
    hasher = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _atomic_write(path: Path, content: str, *, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.pass184.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.chmod(temporary, mode)
    os.replace(temporary, path)


def _safe_text(value: str, field: str) -> str:
    if not value or any(character in value for character in ("\n", "\r", "\0")):
        raise Pass184Error("P184_REJECT_UNSAFE_TEXT", f"invalid {field}", details={field: value})
    return value


def _systemd_quote(value: str) -> str:
    safe = _safe_text(value, "systemd_value")
    return '"' + safe.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _env_quote(value: str) -> str:
    safe = _safe_text(value, "environment_value")
    return '"' + safe.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _validate_port(port: int) -> int:
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise Pass184Error("P184_REJECT_INVALID_PORT", "port must be an integer from 1 through 65535", details={"port": port})
    return port


def resolve_profile_components(profile: str) -> tuple[str, ...]:
    if profile not in PROFILE_SEEDS:
        raise Pass184Error(
            "P184_REJECT_UNKNOWN_PROFILE",
            f"unknown profile {profile!r}",
            details={"profile": profile, "available_profiles": sorted(PROFILE_SEEDS)},
        )
    resolved: set[str] = set()
    active: set[str] = set()

    def visit(component: str) -> None:
        if component in resolved:
            return
        if component in active:
            raise Pass184Error("P184_REJECT_COMPONENT_CYCLE", "component dependency cycle detected", details={"component": component})
        if component not in COMPONENT_DEPENDENCIES:
            raise Pass184Error("P184_REJECT_UNKNOWN_COMPONENT", "unknown package component", details={"component": component})
        active.add(component)
        for dependency in COMPONENT_DEPENDENCIES[component]:
            visit(dependency)
        active.remove(component)
        resolved.add(component)

    for seed in PROFILE_SEEDS[profile]:
        visit(seed)
    return tuple(component for component in COMPONENT_ORDER if component in resolved)


@dataclass(frozen=True)
class PackagePlan:
    profile: str
    components: tuple[str, ...]
    repository_root: str
    install_root: str
    app_import: str
    host: str
    port: int
    health_path: str
    environment_identity: str
    plan_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_184_PACKAGE_PLAN_V1",
            "contract": CONTRACT_ID,
            "runtime_version": RUNTIME_VERSION,
            "profile": self.profile,
            "components": list(self.components),
            "repository_root": self.repository_root,
            "install_root": self.install_root,
            "app_import": self.app_import,
            "host": self.host,
            "port": self.port,
            "health_path": self.health_path,
            "environment_identity": self.environment_identity,
            "plan_identity": self.plan_identity,
        }


class PortableRuntimeAuthority:
    """Singleton-compatible package and supervised-service authority."""

    authority = "HHS_VM81_SINGLETON_PORTABLE_RUNTIME_SERVICE_AUTHORITY_V1"

    def detect(
        self,
        *,
        repository_root: str | os.PathLike[str] | None = None,
        writable_root: str | os.PathLike[str] | None = None,
    ) -> dict[str, Any]:
        repository = Path(repository_root or os.environ.get("HHS_REPOSITORY_ROOT") or Path.cwd()).expanduser().resolve()
        writable = Path(writable_root or os.environ.get("HHS_PASS184_PACKAGE_ROOT") or repository / ".hhs" / "pass184" / "packages").expanduser().resolve()
        binaries = {name: shutil.which(name) for name in TOOL_NAMES}
        snapshot: dict[str, Any] = {
            "schema": "HHS_PASS_184_ENVIRONMENT_SNAPSHOT_V1",
            "contract": CONTRACT_ID,
            "authority": self.authority,
            "os": platform.system(),
            "kernel_release": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "python_executable": str(Path(sys.executable).resolve()),
            "cpu_count": os.cpu_count() or 1,
            "repository_root": str(repository),
            "writable_root": str(writable),
            "binaries": binaries,
            "service_managers": {
                "systemd": bool(binaries.get("systemctl")),
                "docker": bool(binaries.get("docker")),
                "podman": bool(binaries.get("podman")),
            },
        }
        snapshot["environment_identity"] = _digest(snapshot)
        return snapshot

    def plan(
        self,
        *,
        profile: str,
        install_root: str | os.PathLike[str],
        repository_root: str | os.PathLike[str] | None = None,
        host: str = "0.0.0.0",
        port: int = 8080,
        environment: Mapping[str, Any] | None = None,
    ) -> PackagePlan:
        _validate_port(port)
        host = _safe_text(str(host), "host")
        repository = Path(repository_root or os.environ.get("HHS_REPOSITORY_ROOT") or Path.cwd()).expanduser().resolve()
        install = Path(install_root).expanduser().resolve()
        components = resolve_profile_components(profile)
        environment_snapshot = dict(environment or self.detect(repository_root=repository, writable_root=install.parent))
        environment_identity = str(environment_snapshot.get("environment_identity") or _digest(environment_snapshot))
        body = {
            "contract": CONTRACT_ID,
            "runtime_version": RUNTIME_VERSION,
            "profile": profile,
            "components": list(components),
            "repository_root": str(repository),
            "install_root": str(install),
            "app_import": APP_IMPORT,
            "host": host,
            "port": port,
            "health_path": HEALTH_PATH,
            "environment_identity": environment_identity,
        }
        return PackagePlan(
            profile=profile,
            components=components,
            repository_root=str(repository),
            install_root=str(install),
            app_import=APP_IMPORT,
            host=host,
            port=port,
            health_path=HEALTH_PATH,
            environment_identity=environment_identity,
            plan_identity=_digest(body),
        )

    @staticmethod
    def _launcher(plan: PackagePlan) -> str:
        return f'''#!/usr/bin/env bash
set -euo pipefail
PACKAGE_ROOT="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/.." && pwd)"
ENV_FILE="${{HHS_ENV_FILE:-${{PACKAGE_ROOT}}/configuration/hhs.env}}"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "HHS Pass 184 environment file missing: $ENV_FILE" >&2
  exit 66
fi
set -a
# Generated by the repository-owned Pass 184 compiler.
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
exec "${{PYTHON_BIN:-python3}}" -m hhs_runtime.pass184.cli serve \
  --repository-root "$HHS_REPOSITORY_ROOT" \
  --host "${{HOST:-{plan.host}}}" \
  --port "${{PORT:-{plan.port}}}" \
  --timeout "${{HHS_STARTUP_TIMEOUT_SECONDS:-60}}"
'''

    @staticmethod
    def _environment_file(plan: PackagePlan) -> str:
        values = {
            "HHS_REPOSITORY_ROOT": plan.repository_root,
            "HHS_PASS184_INSTALL_ROOT": plan.install_root,
            "HHS_PASS184_PROFILE": plan.profile,
            "HHS_APPLICATION_IMPORT": plan.app_import,
            "HOST": plan.host,
            "PORT": str(plan.port),
            "HHS_HEALTH_PATH": plan.health_path,
            "HHS_STARTUP_TIMEOUT_SECONDS": "60",
            "PYTHONUNBUFFERED": "1",
        }
        return "\n".join(f"{key}={_env_quote(value)}" for key, value in values.items()) + "\n"

    @staticmethod
    def _systemd_unit(plan: PackagePlan) -> str:
        launcher = str(Path(plan.install_root) / "bin" / "hhs-runtime")
        environment = str(Path(plan.install_root) / "configuration" / "hhs.env")
        return f'''[Unit]
Description=HHS Pass 184 Full Application IDE
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={_systemd_quote(plan.repository_root)}
EnvironmentFile={_systemd_quote(environment)}
ExecStart={_systemd_quote(launcher)}
Restart=on-failure
RestartSec=3
TimeoutStartSec=75
TimeoutStopSec=20
KillSignal=SIGTERM
KillMode=mixed
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
'''

    def build(self, plan: PackagePlan, *, clean: bool = False) -> dict[str, Any]:
        root = Path(plan.install_root)
        if root.exists() and clean:
            shutil.rmtree(root)
        if root.exists() and root.is_symlink():
            raise Pass184Error("P184_REJECT_INSTALL_ROOT_SYMLINK", "installation root may not be a symlink", details={"install_root": str(root)})
        root.mkdir(parents=True, exist_ok=True)
        for directory in REQUIRED_PACKAGE_DIRS:
            (root / directory).mkdir(parents=True, exist_ok=True)

        profile_payload = {
            "schema": "HHS_PASS_184_PROFILE_V1",
            "contract": CONTRACT_ID,
            "profile": plan.profile,
            "components": list(plan.components),
            "plan_identity": plan.plan_identity,
        }
        receipt_payload = {
            "schema": "HHS_PASS_184_PACKAGE_BUILD_RECEIPT_V1",
            "classification": "HHS_PASS_184_PORTABLE_RUNTIME_PACKAGE_BUILT",
            "contract": CONTRACT_ID,
            "authority": self.authority,
            "profile": plan.profile,
            "plan_identity": plan.plan_identity,
            "environment_identity": plan.environment_identity,
            "public_application": plan.app_import,
            "host": plan.host,
            "port": plan.port,
            "health_path": plan.health_path,
        }

        generated: dict[str, tuple[str, int, str]] = {
            "bin/hhs-runtime": (self._launcher(plan), 0o755, "foreground_launcher"),
            "configuration/hhs.env": (self._environment_file(plan), 0o640, "environment_configuration"),
            f"profiles/{plan.profile}.json": (json.dumps(profile_payload, indent=2, sort_keys=True) + "\n", 0o644, "profile_closure"),
            "service/hhs.service": (self._systemd_unit(plan), 0o644, "systemd_service"),
            "installation-evidence/build-receipt.json": (json.dumps(receipt_payload, indent=2, sort_keys=True) + "\n", 0o644, "build_receipt"),
        }
        for relative, (content, mode, _role) in generated.items():
            destination = root / relative
            if destination.exists() and destination.is_symlink():
                raise Pass184Error("P184_REJECT_PACKAGE_FILE_SYMLINK", "generated package file may not be a symlink", details={"path": relative})
            _atomic_write(destination, content, mode=mode)

        files: list[dict[str, Any]] = []
        for relative, (_content, _mode, role) in sorted(generated.items()):
            path = root / relative
            files.append({
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": _file_digest(path),
                "role": role,
            })
        manifest_payload = {
            "schema": "HHS_PASS_184_RUNTIME_PACKAGE_MANIFEST_V1",
            "classification": "HHS_PASS_184_PACKAGE_MANIFEST_VERIFIED",
            "contract": CONTRACT_ID,
            "runtime_version": RUNTIME_VERSION,
            "authority": self.authority,
            "plan": plan.to_dict(),
            "files": files,
        }
        manifest_payload["manifest_identity"] = _digest(manifest_payload)
        manifest_path = root / "manifests" / "runtime-package.json"
        _atomic_write(manifest_path, json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n")
        verification = self.verify(root)
        return {
            "schema": "HHS_PASS_184_BUILD_RESULT_V1",
            "classification": "HHS_PASS_184_PORTABLE_RUNTIME_PACKAGE_BUILT_AND_VERIFIED",
            "contract": CONTRACT_ID,
            "install_root": str(root),
            "profile": plan.profile,
            "plan_identity": plan.plan_identity,
            "manifest_identity": manifest_payload["manifest_identity"],
            "manifest_sha256": _file_digest(manifest_path),
            "verification": verification,
        }

    def verify(self, install_root: str | os.PathLike[str]) -> dict[str, Any]:
        root = Path(install_root).expanduser().resolve()
        manifest_path = root / "manifests" / "runtime-package.json"
        if not manifest_path.is_file() or manifest_path.is_symlink():
            raise Pass184Error("P184_REJECT_MANIFEST_MISSING", "runtime package manifest is missing or unsafe", details={"path": str(manifest_path)})
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise Pass184Error("P184_REJECT_MANIFEST_PARSE", "runtime package manifest cannot be parsed", details={"error": str(error)}) from error
        if manifest.get("contract") != CONTRACT_ID:
            raise Pass184Error("P184_REJECT_MANIFEST_CONTRACT", "runtime package manifest contract mismatch")
        claimed_identity = manifest.get("manifest_identity")
        identity_body = dict(manifest)
        identity_body.pop("manifest_identity", None)
        actual_identity = _digest(identity_body)
        if claimed_identity != actual_identity:
            raise Pass184Error(
                "P184_REJECT_MANIFEST_IDENTITY",
                "runtime package manifest identity mismatch",
                details={"claimed": claimed_identity, "actual": actual_identity},
            )
        expected_paths = {"manifests/runtime-package.json"}
        verified: list[dict[str, Any]] = []
        for record in manifest.get("files") or []:
            relative = str(record.get("path") or "")
            if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise Pass184Error("P184_REJECT_MANIFEST_PATH", "unsafe manifest path", details={"path": relative})
            expected_paths.add(relative)
            path = root / relative
            if not path.is_file() or path.is_symlink():
                raise Pass184Error("P184_REJECT_PACKAGE_FILE", "required package file is missing or unsafe", details={"path": relative})
            actual_sha = _file_digest(path)
            actual_bytes = path.stat().st_size
            if actual_sha != record.get("sha256") or actual_bytes != record.get("bytes"):
                raise Pass184Error(
                    "P184_REJECT_PACKAGE_TAMPER",
                    "package file digest or length mismatch",
                    details={
                        "path": relative,
                        "claimed_sha256": record.get("sha256"),
                        "actual_sha256": actual_sha,
                        "claimed_bytes": record.get("bytes"),
                        "actual_bytes": actual_bytes,
                    },
                )
            verified.append({"path": relative, "sha256": actual_sha, "bytes": actual_bytes})
        actual_paths = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        }
        unexpected = sorted(actual_paths - expected_paths)
        missing = sorted(expected_paths - actual_paths)
        if unexpected or missing:
            raise Pass184Error(
                "P184_REJECT_PACKAGE_FILE_SET",
                "runtime package file set differs from the manifest",
                details={"unexpected": unexpected, "missing": missing},
            )
        return {
            "schema": "HHS_PASS_184_PACKAGE_VERIFICATION_V1",
            "classification": "HHS_PASS_184_PORTABLE_RUNTIME_PACKAGE_VERIFIED",
            "contract": CONTRACT_ID,
            "install_root": str(root),
            "manifest_identity": claimed_identity,
            "verified_file_count": len(verified),
            "files": verified,
        }

    @staticmethod
    def _probe_host(host: str) -> str:
        return "127.0.0.1" if host in {"0.0.0.0", "::", "[::]", "localhost"} else host

    def port_available(self, host: str, port: int) -> bool:
        _validate_port(port)
        bind_host = "" if host in {"0.0.0.0", "::", "[::]"} else host
        family = socket.AF_INET6 if ":" in bind_host and bind_host else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                listener.bind((bind_host, port))
            except OSError:
                return False
        return True

    def probe(
        self,
        *,
        host: str,
        port: int,
        health_path: str = HEALTH_PATH,
        timeout: float = 2.0,
    ) -> dict[str, Any]:
        _validate_port(port)
        if timeout <= 0 or timeout > 300:
            raise Pass184Error("P184_REJECT_INVALID_TIMEOUT", "timeout must be greater than zero and at most 300 seconds")
        probe_host = self._probe_host(_safe_text(host, "host"))
        started = time.monotonic()
        try:
            with socket.create_connection((probe_host, port), timeout=timeout):
                pass
        except OSError as error:
            return {
                "schema": "HHS_PASS_184_READINESS_PROBE_V1",
                "classification": "HHS_PASS_184_PROCESS_RUNNING_NO_LISTENER",
                "ready": False,
                "tcp_listener": False,
                "http_health": False,
                "host": probe_host,
                "port": port,
                "health_path": health_path,
                "error": str(error),
                "elapsed_ms": int((time.monotonic() - started) * 1000),
            }
        try:
            connection = HTTPConnection(probe_host, port, timeout=timeout)
            connection.request("GET", health_path, headers={"Accept": "application/json", "Connection": "close"})
            response = connection.getresponse()
            body = response.read(1024 * 1024)
            connection.close()
        except OSError as error:
            return {
                "schema": "HHS_PASS_184_READINESS_PROBE_V1",
                "classification": "HHS_PASS_184_TCP_LISTENER_READY_HTTP_NOT_READY",
                "ready": False,
                "tcp_listener": True,
                "http_health": False,
                "host": probe_host,
                "port": port,
                "health_path": health_path,
                "error": str(error),
                "elapsed_ms": int((time.monotonic() - started) * 1000),
            }
        ready = 200 <= response.status < 300
        return {
            "schema": "HHS_PASS_184_READINESS_PROBE_V1",
            "classification": "HHS_PASS_184_HTTP_HEALTH_READY" if ready else "HHS_PASS_184_TCP_LISTENER_READY_HTTP_NOT_READY",
            "ready": ready,
            "tcp_listener": True,
            "http_health": ready,
            "host": probe_host,
            "port": port,
            "health_path": health_path,
            "http_status": response.status,
            "body_sha256": sha256(body).hexdigest(),
            "elapsed_ms": int((time.monotonic() - started) * 1000),
        }

    def supervised_command(
        self,
        *,
        repository_root: str | os.PathLike[str],
        host: str,
        port: int,
        python_bin: str | None = None,
        app_import: str = APP_IMPORT,
    ) -> list[str]:
        repository = Path(repository_root).expanduser().resolve()
        module_path = repository / "hhs_backend" / "application_ide_server.py"
        if not module_path.is_file():
            raise Pass184Error(
                "P184_REJECT_APPLICATION_MODULE_MISSING",
                "full application IDE module is missing",
                details={"expected_path": str(module_path)},
            )
        if not self.port_available(host, port):
            raise Pass184Error(
                "P184_REJECT_PORT_OCCUPIED",
                "selected port is already occupied",
                details={"host": host, "port": port},
            )
        return [
            python_bin or sys.executable,
            "-m",
            "uvicorn",
            app_import,
            "--host",
            host,
            "--port",
            str(port),
            "--workers",
            "1",
            "--timeout-keep-alive",
            "5",
            "--log-level",
            os.environ.get("HHS_LOG_LEVEL", "info"),
        ]

    def serve(
        self,
        *,
        repository_root: str | os.PathLike[str],
        host: str = "0.0.0.0",
        port: int = 8080,
        timeout: float = 60.0,
        python_bin: str | None = None,
        extra_environment: Mapping[str, str] | None = None,
    ) -> int:
        if timeout <= 0 or timeout > 900:
            raise Pass184Error("P184_REJECT_INVALID_TIMEOUT", "startup timeout must be greater than zero and at most 900 seconds")
        repository = Path(repository_root).expanduser().resolve()
        command = self.supervised_command(
            repository_root=repository,
            host=host,
            port=port,
            python_bin=python_bin,
        )
        environment = os.environ.copy()
        environment.update({key: str(value) for key, value in dict(extra_environment or {}).items()})
        environment["HHS_REPOSITORY_ROOT"] = str(repository)
        existing_pythonpath = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = str(repository) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
        process = subprocess.Popen(command, cwd=repository, env=environment)
        deadline = time.monotonic() + timeout
        try:
            while time.monotonic() < deadline:
                return_code = process.poll()
                if return_code is not None:
                    raise Pass184Error(
                        "P184_PROCESS_EXITED_BEFORE_LISTEN",
                        "Uvicorn exited before the HHS health endpoint became ready",
                        details={"return_code": return_code, "command": command},
                    )
                result = self.probe(host=host, port=port, timeout=min(1.0, max(0.1, deadline - time.monotonic())))
                if result["ready"]:
                    print(json.dumps({
                        "classification": "HHS_PASS_184_SUPERVISED_SERVICE_READY",
                        "pid": process.pid,
                        "host": host,
                        "port": port,
                        "health_path": HEALTH_PATH,
                    }, sort_keys=True), flush=True)
                    return process.wait()
                time.sleep(0.2)
            raise Pass184Error(
                "P184_STARTUP_TIMEOUT",
                "HHS service did not expose a healthy listener before the startup deadline",
                details={"host": host, "port": port, "timeout": timeout},
            )
        except BaseException:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            raise

    def status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_184_STATUS_V1",
            "classification": "HHS_PASS_184_PORTABLE_RUNTIME_AUTHORITY_AVAILABLE",
            "contract": CONTRACT_ID,
            "runtime_version": RUNTIME_VERSION,
            "authority": self.authority,
            "public_application": APP_IMPORT,
            "health_path": HEALTH_PATH,
            "profiles": {profile: list(resolve_profile_components(profile)) for profile in PROFILE_SEEDS},
        }


def ensure_within(root: str | os.PathLike[str], candidate: str | os.PathLike[str]) -> Path:
    resolved_root = Path(root).expanduser().resolve()
    resolved_candidate = Path(candidate).expanduser().resolve()
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as error:
        raise Pass184Error(
            "P184_REJECT_PACKAGE_ROOT_ESCAPE",
            "package output must remain under the configured Pass 184 package root",
            details={"root": str(resolved_root), "candidate": str(resolved_candidate)},
        ) from error
    return resolved_candidate


def write_completion_receipt(path: str | os.PathLike[str], checks: Mapping[str, bool]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "HHS_PASS_184_COMPLETION_RECEIPT_V1",
        "classification": "HHS_PASS_184_PORTABLE_HYDRATION_RUNTIME_PACKAGE_AND_SUPERVISED_SERVICE_AUTHORITY_VERIFIED",
        "contract": CONTRACT_ID,
        "authority": PortableRuntimeAuthority.authority,
        "checks": dict(sorted(checks.items())),
    }
    if not payload["checks"] or not all(payload["checks"].values()):
        raise Pass184Error("P184_REJECT_INCOMPLETE_ACCEPTANCE", "all Pass 184 completion checks must be true")
    payload["receipt_sha256"] = _digest(payload)
    destination = Path(path)
    _atomic_write(destination, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload
