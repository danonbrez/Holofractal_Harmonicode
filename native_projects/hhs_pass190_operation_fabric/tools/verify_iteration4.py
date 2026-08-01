#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "python/hhs_pass190_iteration4.py",
    ROOT / "server/hhs_pass190_iteration4_server.py",
    ROOT / "python/test_hhs_pass190_iteration4.py",
]
for path in required:
    if not path.exists() or path.stat().st_size == 0:
        raise SystemExit(f"missing Iteration 4 artifact: {path}")

runtime = required[0].read_text(encoding="utf-8")
server = required[1].read_text(encoding="utf-8")
checks = {
    "durable_lease_table": "CREATE TABLE IF NOT EXISTS authority_lease" in runtime,
    "fencing_witness_table": "CREATE TABLE IF NOT EXISTS authority_fences" in runtime,
    "begin_immediate": 'execute("BEGIN IMMEDIATE")' in runtime,
    "strict_fencing": "fencing tokens are not strictly increasing" in runtime,
    "stale_candidate_rejection": "candidate predecessor no longer matches durable chain head" in runtime,
    "legacy_migration": "iteration3-migration" in runtime,
    "hash72_fence": 'hash72("pass190.fence"' in runtime,
    "distributed_context": "class DistributedAuthorityContext" in runtime,
    "arbitration_endpoint": "/api/pass190/arbitration" in server,
    "iteration4_openapi": 'document["x-hhs-iteration"] = 4' in server,
    "native_compiler_inherited": "HarmonicodeOperationCompiler" in server,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 4 source verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 4 distributed singleton source verification: PASS")
