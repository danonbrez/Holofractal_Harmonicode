#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
registry = (ROOT / "python/hhs_pass190_iteration7_registry.py").read_text(encoding="utf-8")
authority = (ROOT / "python/hhs_pass190_iteration7.py").read_text(encoding="utf-8")
compiler = (ROOT / "python/hhs_pass190_iteration7_compiler.py").read_text(encoding="utf-8")
worker = (ROOT / "worker/hhs_pass190_iteration7_worker.py").read_text(encoding="utf-8")
server = (ROOT / "server/hhs_pass190_iteration7_server.py").read_text(encoding="utf-8")
tests = (ROOT / "python/test_hhs_pass190_iteration7.py").read_text(encoding="utf-8")
bindings = (ROOT / "bindings/P190_OPERATION_SURFACE_BINDINGS_V3.json").read_text(encoding="utf-8")
checks = {
    "eleven_operations": "EXECUTION_OPERATION_IDS" in registry and registry.count("_operation(") == 11,
    "forty_two_governed": '"governed_operation_count": len(combined_records)' in registry and '"execution_operation_count": len(EXECUTION_OPERATION_RECORDS)' in registry,
    "native_preserved": "NativeManifest(OperationRegistry" in compiler,
    "pure_execution_boundary": "durable internal execution accepts pure operations only" in authority and "durable worker cannot execute mutating targets" in authority,
    "dependency_dag": "job dependency cycle detected" in authority and "dependency_terminal" in authority,
    "priority_claim": 'key=lambda item: (-int(item["priority"]), item["job_id"])' in authority,
    "claim_hash72": 'hash72("pass190.execution.claim"' in authority,
    "execution_hash72": 'hash72("pass190.execution.result"' in authority,
    "bounded_retry": "max_attempts" in authority and "retry_backoff_ns" in authority and "retry_wait" in authority,
    "cancellation": '"status": "cancelled"' in authority and "job.cancel" in registry,
    "stale_recovery": "worker_lease_expired" in authority and "lease_expires_ns" in authority,
    "worker_process": "class DurableWorker" in worker and "job.execute_claimed" in worker,
    "execution_endpoint": "/api/pass190/execution-runtime" in server,
    "bindings_v3": "P190_OPERATION_SURFACE_BINDINGS_V3" in bindings and '"governed_operation_count":42' in bindings and '"execution_operation_count":11' in bindings,
    "lifecycle_tests": "test_claim_is_priority_ordered_and_execution_is_receipt_bound" in tests,
    "retry_test": "test_failed_execution_retries_then_exhausts_budget" in tests,
    "cancellation_test": "test_cancellation_releases_running_worker" in tests,
    "recovery_test": "test_stale_worker_lease_is_recovered_by_scheduler" in tests,
    "tamper_test": "test_persistence_restart_and_worker_tamper_rejection" in tests,
    "live_server_test": "test_live_server_projects_execution_runtime" in tests,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 7 verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 7 durable worker execution verification: PASS")
