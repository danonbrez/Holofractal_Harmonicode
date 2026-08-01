#!/usr/bin/env python3
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
repo = PROJECT if (PROJECT / "hhs_gui").exists() else Path(__file__).resolve().parents[3]
registry = (repo / "hhs_gui/runtime_os/core/RuntimeApplicationRegistry.tsx").read_text(encoding="utf-8")
surface = (repo / "hhs_gui/runtime_apps/pass190/Pass190OperationFabricSurface.tsx").read_text(encoding="utf-8")
checks = {
    "registry_id": 'id: "pass190_operation_fabric"' in registry,
    "lazy_loader": "runtime_apps/pass190/Pass190OperationFabricSurface" in registry,
    "invoke_route": "/api/pass190/invoke" in surface,
    "integrity_route": "/api/pass190/integrity" in surface,
    "websocket_route": "/api/pass190/ws?after=" in surface,
    "human_result": "Latest admitted result" in surface,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 2 GUI verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 2 GUI regression verification: PASS")
