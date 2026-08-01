#!/usr/bin/env python3
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
repo = PROJECT if (PROJECT / "hhs_gui").exists() else Path(__file__).resolve().parents[3]
registry = (repo / "hhs_gui/runtime_os/core/RuntimeApplicationRegistry.tsx").read_text(encoding="utf-8")
manager = (repo / "hhs_gui/runtime_os/core/RuntimeWindowManager.ts").read_text(encoding="utf-8")
surface = (repo / "hhs_gui/runtime_apps/pass190/Pass190OperationFabricSurface.tsx").read_text(encoding="utf-8")
vite = (repo / "hhs_gui/vite.config.ts").read_text(encoding="utf-8")
checks = {
    "registry_singleton": 'id: "pass190_operation_fabric"' in registry and "singleton: true" in registry,
    "manager_enforces_singleton": "application?.singleton" in manager and "reuse singleton" in manager,
    "configurable_service_base": "VITE_PASS190_BASE_URL" in surface,
    "signed_authorization": "HHS-Capability" in surface and "headers.Authorization" in surface,
    "unsigned_scope_absent": "X-HHS-Capability" not in surface,
    "sequence_resume": "lastSequenceRef.current" in surface and "wsUrl(lastSequenceRef.current)" in surface,
    "reconnect_on_close": "socket.onclose" in surface and "EVENT CHANNEL RECOVERING" in surface,
    "pass190_proxy": '"/api/pass190"' in vite and 'target: "http://127.0.0.1:8190"' in vite,
    "websocket_proxy": '"/api/pass190"' in vite and "ws: true" in vite,
    "openapi_proxy": '"/openapi.json"' in vite,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 3 GUI verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 3 authenticated GUI verification: PASS")
