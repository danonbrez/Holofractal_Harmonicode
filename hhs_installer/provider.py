from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping
import json
import os
import platform
import shutil
import socket
import ssl
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from .canonical import hash216, stable


class ProviderState(str, Enum):
    LOCAL_GPU_READY = "LOCAL_GPU_READY"
    LOCAL_CPU_READY = "LOCAL_CPU_READY"
    EXTERNAL_READY = "EXTERNAL_READY"
    DISABLED = "DISABLED"
    DEGRADED = "DEGRADED"
    INCOMPATIBLE = "INCOMPATIBLE"


class ProviderError(ValueError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class ProviderProbe:
    requested_mode: str
    state: ProviderState
    executable: str | None
    endpoint: str | None
    model_id: str | None
    physical_accelerator: bool
    substrate: str
    health_verified: bool
    model_registry_verified: bool
    transport_classification: str
    blocker: str | None
    probe_identity: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["state"] = self.state.value
        return stable(result)


def _physical_accelerator_visible() -> bool:
    if platform.system() == "Darwin":
        return True
    return any(Path(path).exists() for path in ("/dev/dri/renderD128", "/dev/nvidia0", "/dev/kfd"))


def _substrate() -> str:
    if platform.system() == "Darwin":
        return "Metal"
    if shutil.which("vulkaninfo"):
        return "Vulkan"
    return "absent"


def _transport_classification(url: str | None) -> str:
    if not url:
        return "NONE"
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or ""
    if parsed.scheme == "https":
        return "PROTECTED_HTTPS"
    if parsed.scheme == "http" and host in {"127.0.0.1", "localhost", "::1"}:
        return "LOOPBACK_HTTP"
    if parsed.scheme == "http" and (host.startswith("10.") or host.startswith("192.168.") or host.startswith("172.")):
        return "PRIVATE_NETWORK_HTTP_REQUIRES_EXPLICIT_AUTHORIZATION"
    return "PUBLIC_UNPROTECTED"


class ProviderResolver:
    def __init__(self, *, timeout_seconds: int = 10) -> None:
        if not 1 <= timeout_seconds <= 120:
            raise ProviderError("P172_PROVIDER_TIMEOUT_INVALID", "provider timeout is outside 1..120")
        self.timeout_seconds = timeout_seconds

    def classify(
        self,
        *,
        mode: str,
        endpoint: str | None = None,
        model_id: str | None = None,
        require_gpu: bool = False,
        authentication_configured: bool = False,
    ) -> ProviderProbe:
        if mode not in {"auto", "local", "external", "disabled"}:
            raise ProviderError("P172_PROVIDER_MODE_INVALID", "provider mode is invalid", {"mode": mode})
        executable = shutil.which("litert-lm")
        accelerator = _physical_accelerator_visible()
        substrate = _substrate()
        transport = _transport_classification(endpoint)

        if mode == "disabled":
            return self._result(mode, ProviderState.DISABLED, executable, endpoint, model_id, accelerator, substrate, False, False, transport, None)

        if mode == "external" or (mode == "auto" and endpoint):
            if not endpoint:
                return self._result(mode, ProviderState.INCOMPATIBLE, executable, endpoint, model_id, accelerator, substrate, False, False, transport, "P172_EXTERNAL_PROVIDER_URL_REQUIRED")
            if transport == "PUBLIC_UNPROTECTED" or (transport == "PRIVATE_NETWORK_HTTP_REQUIRES_EXPLICIT_AUTHORIZATION" and not authentication_configured):
                return self._result(mode, ProviderState.INCOMPATIBLE, executable, endpoint, model_id, accelerator, substrate, False, False, transport, "P172_EXTERNAL_PROVIDER_TRANSPORT_UNPROTECTED")
            health, registry, blocker = self._verify_endpoint(endpoint, model_id=model_id)
            state = ProviderState.EXTERNAL_READY if health and registry else ProviderState.DEGRADED
            return self._result(mode, state, executable, endpoint, model_id, accelerator, substrate, health, registry, transport, blocker)

        if mode in {"local", "auto"}:
            if not executable:
                state = ProviderState.DEGRADED if mode == "auto" else ProviderState.INCOMPATIBLE
                return self._result(mode, state, None, endpoint, model_id, accelerator, substrate, False, False, "LOOPBACK_HTTP", "P172_LITERT_LM_EXECUTABLE_MISSING")
            if require_gpu and (not accelerator or substrate == "absent"):
                state = ProviderState.DEGRADED if mode == "auto" else ProviderState.INCOMPATIBLE
                return self._result(mode, state, executable, endpoint, model_id, accelerator, substrate, False, False, "LOOPBACK_HTTP", "P172_LOCAL_GPU_SUBSTRATE_MISSING")
            local_endpoint = endpoint or "http://127.0.0.1:9379/v1"
            health, registry, blocker = self._verify_endpoint(local_endpoint, model_id=model_id)
            if health and registry:
                state = ProviderState.LOCAL_GPU_READY if require_gpu else ProviderState.LOCAL_CPU_READY
            else:
                state = ProviderState.DEGRADED
            return self._result(mode, state, executable, local_endpoint, model_id, accelerator, substrate, health, registry, "LOOPBACK_HTTP", blocker)

        return self._result(mode, ProviderState.INCOMPATIBLE, executable, endpoint, model_id, accelerator, substrate, False, False, transport, "P172_PROVIDER_UNRESOLVED")

    def _verify_endpoint(self, base_url: str, *, model_id: str | None) -> tuple[bool, bool, str | None]:
        parsed = urllib.parse.urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False, False, "P172_PROVIDER_URL_INVALID"
        models_url = base_url.rstrip("/") + "/models"
        request = urllib.request.Request(models_url, headers={"Accept": "application/json", "User-Agent": "HHS-P172-Provider-Probe/1"})
        try:
            context = ssl.create_default_context() if parsed.scheme == "https" else None
            with urllib.request.urlopen(request, timeout=self.timeout_seconds, context=context) as response:
                if int(getattr(response, "status", 200)) != 200:
                    return False, False, "P172_PROVIDER_HEALTH_STATUS_INVALID"
                payload = json.loads(response.read(4 * 1024 * 1024).decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            return False, False, f"P172_PROVIDER_UNREACHABLE:{type(exc).__name__}"
        data = payload.get("data", ()) if isinstance(payload, Mapping) else ()
        identifiers = {str(item.get("id")) for item in data if isinstance(item, Mapping) and item.get("id") is not None}
        registry = model_id is None or model_id in identifiers
        return True, registry, None if registry else "P172_PROVIDER_MODEL_MISMATCH"

    @staticmethod
    def _result(
        mode: str,
        state: ProviderState,
        executable: str | None,
        endpoint: str | None,
        model_id: str | None,
        accelerator: bool,
        substrate: str,
        health: bool,
        registry: bool,
        transport: str,
        blocker: str | None,
    ) -> ProviderProbe:
        payload = {
            "requested_mode": mode,
            "state": state.value,
            "executable_name": None if executable is None else Path(executable).name,
            "endpoint": endpoint,
            "model_id": model_id,
            "physical_accelerator": accelerator,
            "substrate": substrate,
            "health_verified": health,
            "model_registry_verified": registry,
            "transport_classification": transport,
            "blocker": blocker,
        }
        return ProviderProbe(
            requested_mode=mode,
            state=state,
            executable=executable,
            endpoint=endpoint,
            model_id=model_id,
            physical_accelerator=accelerator,
            substrate=substrate,
            health_verified=health,
            model_registry_verified=registry,
            transport_classification=transport,
            blocker=blocker,
            probe_identity=hash216(payload, domain="HHS-P172-PROVIDER-PROBE-V1"),
        )
