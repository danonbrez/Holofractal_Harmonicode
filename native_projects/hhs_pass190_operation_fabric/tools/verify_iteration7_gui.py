#!/usr/bin/env python3
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
repo = PROJECT if (PROJECT / "hhs_gui").exists() else Path(__file__).resolve().parents[3]
surface = (repo / "hhs_gui/runtime_apps/pass190/Pass190OperationFabricSurface.tsx").read_text(encoding="utf-8")
checks = {
    "execution_fetch": "/api/pass190/execution-runtime" in surface,
    "periodic_refresh": "setInterval" in surface and "refreshAuthority" in surface,
    "durable_execution": "Durable execution" in surface,
    "worker_count": "worker_count" in surface and "enabled_worker_count" in surface,
    "queued_jobs": "queued_job_count" in surface,
    "scheduled_jobs": "scheduled_job_count" in surface,
    "running_jobs": "running_job_count" in surface,
    "execution_operations": "execution_operation_count" in surface,
    "execution_hash": "execution_runtime_hash72" in surface,
    "execution_integrity": "execution_runtime_verified" in surface,
    "inherited_kernel_action": "Invoke through kernel authority" in surface,
    "inherited_resource_action": "Invoke through unified VM81 authority" in surface,
    "inherited_distributed_authority": "distributed_singleton_verified" in surface,
    "inherited_event_fence": "event.fencing_token" in surface,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 7 GUI verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 7 durable execution GUI verification: PASS")
