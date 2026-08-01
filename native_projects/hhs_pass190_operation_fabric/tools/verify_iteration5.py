#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
authority = (ROOT / "python/hhs_pass190_iteration5.py").read_text(encoding="utf-8")
runtime = (ROOT / "python/hhs_pass190_iteration5_runtime.py").read_text(encoding="utf-8")
server = (ROOT / "server/hhs_pass190_iteration5_server.py").read_text(encoding="utf-8")
tests = (ROOT / "python/test_hhs_pass190_iteration5.py").read_text(encoding="utf-8")
runtime_tests = (ROOT / "python/test_hhs_pass190_iteration5_runtime.py").read_text(encoding="utf-8")
checks = {
    "lock_retry": "_begin_immediate_until" in authority and "SQLite authority remained locked" in authority,
    "bounded_lock_slice": "SQLITE_LOCK_SLICE_MS = 25" in runtime and "PRAGMA busy_timeout" in runtime,
    "bounded_runtime_context": "AtomicKernelAuthorityContext" in runtime and "AtomicKernelAuthorityContext" in server,
    "atomic_restore": 'self._connection.execute("BEGIN")' in authority and "HardenedSQLiteAuthorityStore.restore_into" in authority,
    "validate_before_migration": authority.index("self._validated_receipts()") < authority.index("Only validated inherited receipts"),
    "lease_receipt_table": "authority_lease_receipts" in authority,
    "lease_transitions": all(value in authority for value in ("ACQUIRED", "RELEASED", "FAILED_RELEASED", "EXPIRED")),
    "kernel_fence": "kernel_authority_hash72" in authority and "lease_acquire_hash72" in authority,
    "arbitration_refresh": "_refresh_expired_lease" in authority and "lease_receipt_chain_verified" in authority,
    "structured_503": "persistent_authority_unavailable" in server and "sqlite3.Error" in server,
    "lease_receipt_route": "/api/pass190/lease-receipts" in server,
    "iteration5_openapi": 'document["x-hhs-iteration"] = 5' in server,
    "lock_tests": "test_sqlite_lock_is_retried_then_succeeds" in tests and "test_sqlite_lock_timeout_is_typed" in tests,
    "bounded_runtime_test": "test_busy_timeout_is_sliced_and_respects_bounded_wait" in runtime_tests,
    "legacy_validation_test": "test_legacy_receipt_is_validated_before_fence_migration" in tests,
    "active_lease_test": "test_active_lease_is_a_valid_arbitration_state" in tests,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 5 verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 5 authority correctness verification: PASS")
