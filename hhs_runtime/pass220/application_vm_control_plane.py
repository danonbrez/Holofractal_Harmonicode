"""Backend-first Ubuntu application-VM control plane.

This surface deliberately contains no frontend/static mount. It composes the
already-authoritative Pass 190 shell/operation fabric and Pass 184 environment
inspection into one reusable application service for local Bash/CLI operation,
authenticated OpenAPI transport, and later GUI/frontend adapters.

It does not create another VM81 authority, Hash72 receipt clock, Hash216
persistence authority, capability-token format, or operation engine.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import platform
import shutil
import sys
from typing import Any, Iterable, Mapping

from hhs_runtime.pass184.runtime import PortableRuntimeAuthority
from hhs_runtime.pass190.completion import (
    PASS190_NATIVE_PYTHON,
    Pass190CompletionContext,
    Pass190CompletionError,
)
from hhs_runtime.pass190.shell import lower_shell_command

_native = str(PASS190_NATIVE_PYTHON)
if _native not in sys.path:
    sys.path.insert(0, _native)

from hhs_pass190_capability import (  # type: ignore  # noqa: E402
    CapabilityTokenError,
    issue_capability_token,
    parse_authorization_header,
    verify_capability_token,
)

APPLICATION_VM_SCHEMA = "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
APPLICATION_VM_VERSION = "1.0.0"
DEFAULT_STATE_ROOT = Path(".hhs_runtime_state/pass220/application-vm")
DEFAULT_DATABASE_NAME = "pass190-authority.sqlite3"


class ApplicationVMError(RuntimeError):
    """Typed application VM control-plane rejection."""


def _read_os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')
    return values


def _secret_is_admissible(secret: str | bytes | None) -> bool:
    if secret is None:
        return False
    raw = secret.encode("utf-8") if isinstance(secret, str) else bytes(secret)
    return len(raw) >= 32


@dataclass
class ApplicationVMControlPlane:
    repository_root: Path
    state_root: Path
    database_path: Path
    capability_secret: str | bytes | None
    context: Pass190CompletionContext

    @classmethod
    def create(
        cls,
        *,
        repository_root: str | os.PathLike[str],
        state_root: str | os.PathLike[str] | None = None,
        database_path: str | os.PathLike[str] | None = None,
        capability_secret: str | bytes | None = None,
        require_pinned_python: bool = True,
    ) -> "ApplicationVMControlPlane":
        repository = Path(repository_root).expanduser().resolve()
        state = Path(state_root or repository / DEFAULT_STATE_ROOT).expanduser().resolve()
        database = Path(database_path or state / DEFAULT_DATABASE_NAME).expanduser().resolve()
        if capability_secret is not None and not _secret_is_admissible(capability_secret):
            raise ApplicationVMError("HHS_APPLICATION_VM_CAPABILITY_SECRET_TOO_SHORT")
        database.parent.mkdir(parents=True, exist_ok=True)
        context = Pass190CompletionContext(
            database_path=database,
            repository_root=repository,
            hydration_state_root=state / "hydration",
            capability_secret=capability_secret,
            require_pinned_python=require_pinned_python,
        )
        return cls(repository, state, database, capability_secret, context)

    @classmethod
    def from_environment(
        cls,
        *,
        require_pinned_python: bool = True,
    ) -> "ApplicationVMControlPlane":
        repository = Path(
            os.environ.get(
                "HHS_APPLICATION_VM_REPOSITORY_ROOT",
                Path(__file__).resolve().parents[2],
            )
        )
        state = Path(
            os.environ.get(
                "HHS_APPLICATION_VM_STATE_ROOT",
                repository / DEFAULT_STATE_ROOT,
            )
        )
        database = Path(
            os.environ.get(
                "HHS_PASS190_DATABASE",
                state / DEFAULT_DATABASE_NAME,
            )
        )
        return cls.create(
            repository_root=repository,
            state_root=state,
            database_path=database,
            capability_secret=os.environ.get("HHS_PASS190_CAPABILITY_SECRET"),
            require_pinned_python=require_pinned_python,
        )

    @property
    def security_configured(self) -> bool:
        return _secret_is_admissible(self.capability_secret)

    def _desktop_snapshot(self) -> dict[str, Any]:
        os_release = _read_os_release()
        session_binaries = {
            "gnome_shell": shutil.which("gnome-shell"),
            "ubuntu_session": shutil.which("ubuntu-session"),
            "wayland_info": shutil.which("wayland-info"),
        }
        ubuntu = os_release.get("ID", "").lower() == "ubuntu"
        desktop_components = bool(
            session_binaries["gnome_shell"] or session_binaries["ubuntu_session"]
        )
        return {
            "os_release": os_release,
            "ubuntu": ubuntu,
            "ubuntu_desktop_components_present": desktop_components,
            "session_binaries": session_binaries,
            "runtime_service_requires_active_desktop_session": False,
            "frontend_attached": False,
        }

    def health(self) -> dict[str, Any]:
        desktop = self._desktop_snapshot()
        return {
            "schema": APPLICATION_VM_SCHEMA,
            "version": APPLICATION_VM_VERSION,
            "ok": True,
            "service": "HHS_UBUNTU_APPLICATION_VM_CONTROL_PLANE",
            "security_configured": self.security_configured,
            "ubuntu": desktop["ubuntu"],
            "ubuntu_desktop_components_present": desktop[
                "ubuntu_desktop_components_present"
            ],
            "frontend_attached": False,
            "public_mutation_requires_signed_capability": True,
            "new_vm81_authority": False,
            "new_hash72_mint_authority": False,
            "new_hash216_persistence_authority": False,
        }

    def status(self) -> dict[str, Any]:
        environment = PortableRuntimeAuthority().detect(
            repository_root=self.repository_root,
            writable_root=self.state_root,
        )
        return {
            "schema": APPLICATION_VM_SCHEMA,
            "version": APPLICATION_VM_VERSION,
            "mode": "BACKEND_FIRST_HEADLESS_CONTROL_PLANE",
            "repository_root": str(self.repository_root),
            "state_root": str(self.state_root),
            "database_path": str(self.database_path),
            "security_configured": self.security_configured,
            "desktop": self._desktop_snapshot(),
            "host": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python": platform.python_version(),
            },
            "portable_runtime_environment": environment,
            "pass190": self.context.status(),
            "frontend_attached": False,
            "fastapi_frontend_authority": False,
            "single_vm81_authority_preserved": True,
        }

    def doctor(self) -> dict[str, Any]:
        result = lower_shell_command(self.context, "hhs doctor")
        return {
            "schema": "HHS_PASS_220_APPLICATION_VM_DOCTOR_V1",
            "ok": bool(result.get("ok")),
            "shell": result,
            "security_configured": self.security_configured,
            "desktop": self._desktop_snapshot(),
        }

    def capabilities(self) -> dict[str, Any]:
        records = self.context.operations()
        return {
            "schema": "HHS_PASS_220_APPLICATION_VM_CAPABILITIES_V1",
            "operation_count": len(records),
            "operations": records,
            "shell_commands": lower_shell_command(self.context, "hhs completion")[
                "commands"
            ],
            "source": "INHERITED_PASS190_OPERATION_REGISTRY",
            "new_registry_authority": False,
        }

    def authenticate_header(self, authorization: str | None) -> dict[str, Any]:
        if not self.security_configured:
            raise ApplicationVMError("HHS_APPLICATION_VM_SECURITY_NOT_CONFIGURED")
        assert self.capability_secret is not None
        try:
            token = parse_authorization_header(authorization)
            principal = verify_capability_token(token, self.capability_secret)
        except CapabilityTokenError as exc:
            raise ApplicationVMError(
                f"HHS_APPLICATION_VM_CAPABILITY_INVALID:{exc}"
            ) from exc
        return {
            "token": token,
            "principal": principal.principal,
            "scopes": sorted(principal.scopes),
            "expires_at": principal.expires_at,
            "token_hash72": principal.token_hash72,
        }

    def issue_token(
        self,
        *,
        principal: str,
        scopes: Iterable[str],
        ttl_seconds: int = 900,
    ) -> str:
        if not self.security_configured:
            raise ApplicationVMError("HHS_APPLICATION_VM_SECURITY_NOT_CONFIGURED")
        assert self.capability_secret is not None
        return issue_capability_token(
            self.capability_secret,
            principal=principal,
            scopes=scopes,
            ttl_seconds=ttl_seconds,
        )

    def shell(
        self,
        command: str,
        *,
        authorization_token: str | None = None,
    ) -> dict[str, Any]:
        return lower_shell_command(
            self.context,
            command,
            authorization_token=authorization_token,
        )

    def invoke(
        self,
        operation_id: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        authorization_token: str | None = None,
        idempotency_key: str | None = None,
        expected_state: str | None = None,
    ) -> dict[str, Any]:
        return self.context.invoke(
            operation_id,
            arguments or {},
            surface="application-vm-openapi",
            authorization_token=authorization_token,
            idempotency_key=idempotency_key,
            expected_state=expected_state,
        )

    def harmonicode(
        self,
        expression: str,
        *,
        authorization_token: str | None = None,
    ) -> dict[str, Any]:
        return self.context.invoke_constructor(
            expression,
            authorization_token=authorization_token,
        )

    def receipts(self, *, after: int = 0, limit: int = 100) -> dict[str, Any]:
        if after < 0 or not 1 <= limit <= 1000:
            raise ApplicationVMError("HHS_APPLICATION_VM_RECEIPT_RANGE_INVALID")
        return {
            "schema": "HHS_PASS_220_APPLICATION_VM_RECEIPTS_V1",
            "after": after,
            "limit": limit,
            "receipts": self.context.authority.receipts_after(after, limit),
            "canonical_state_fabricated": False,
        }

    def replay(self, receipt_hash72: str) -> dict[str, Any]:
        return self.context.replay(receipt_hash72)


__all__ = [
    "APPLICATION_VM_SCHEMA",
    "APPLICATION_VM_VERSION",
    "ApplicationVMControlPlane",
    "ApplicationVMError",
    "Pass190CompletionError",
]
