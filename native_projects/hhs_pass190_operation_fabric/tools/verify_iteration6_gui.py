#!/usr/bin/env python3
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
repo = PROJECT if (PROJECT / "hhs_gui").exists() else Path(__file__).resolve().parents[3]
surface = (repo / "hhs_gui/runtime_apps/pass190/Pass190OperationFabricSurface.tsx").read_text(encoding="utf-8")
checks = {
    "resource_fetch": "/api/pass190/resource-registry" in surface,
    "periodic_refresh": "setInterval" in surface and "refreshAuthority" in surface,
    "governed_operations": "governed_operation_count" in surface,
    "native_operations": "native_operation_count" in surface,
    "fallback_operations": "compiler_fallback_operation_count" in surface,
    "workspace_count": "counts.workspaces" in surface,
    "artifact_count": "counts.artifacts" in surface,
    "provider_count": "counts.providers" in surface,
    "capability_count": "counts.capabilities" in surface,
    "job_count": "counts.jobs" in surface and "active_job_count" in surface,
    "registry_hash": "resource_registry_hash72" in surface,
    "resource_integrity": "resource_registry_verified" in surface,
    "unified_action": "Invoke through unified VM81 authority" in surface,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 6 GUI verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 6 GUI verification: PASS")
