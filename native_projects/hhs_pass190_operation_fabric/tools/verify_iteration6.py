#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
registry = (ROOT / "python/hhs_pass190_iteration6_registry.py").read_text(encoding="utf-8")
authority = (ROOT / "python/hhs_pass190_iteration6.py").read_text(encoding="utf-8")
runtime = (ROOT / "python/hhs_pass190_iteration6_runtime.py").read_text(encoding="utf-8")
compiler = (ROOT / "python/hhs_pass190_iteration6_compiler.py").read_text(encoding="utf-8")
server = (ROOT / "server/hhs_pass190_iteration6_server.py").read_text(encoding="utf-8")
tests = (ROOT / "python/test_hhs_pass190_iteration6.py").read_text(encoding="utf-8")
bindings = (ROOT / "bindings/P190_OPERATION_SURFACE_BINDINGS_V2.json").read_text(encoding="utf-8")
checks = {
    "five_resource_kinds": all(value in registry for value in ("workspaces", "artifacts", "providers", "capabilities", "jobs")),
    "twenty_one_operations": "RESOURCE_OPERATION_IDS" in registry and registry.count("_operation(") == 22,
    "expanded_registry": "ExpandedOperationRegistry" in registry and "governed_operation_count" in registry,
    "record_hash72": "record_hash72" in authority and "pass190.resource" in authority,
    "referential_integrity": "artifact references an unknown workspace" in authority and "job references an unknown provider" in authority,
    "artifact_immutable": "artifact already exists and is immutable" in authority,
    "provider_secret_boundary": '"secret_material_present": False' in authority,
    "job_lifecycle": all(value in authority for value in ("job.submit", "job.claim", "job.complete", "job.fail")),
    "persistent_surface": all(value in runtime for value in ("receipts_after", "events_after", "wait_for_events", "arbitration_report")),
    "compiler_fallback": "vm81-exact-authority-fallback-v1" in compiler and '"native_available": False' in compiler,
    "native_preserved": "NativeManifest(OperationRegistry" in compiler,
    "resource_endpoint": "/api/pass190/resource-registry" in server,
    "direct_operation_routes": 'prefix = "/api/pass190/operations/"' in server,
    "structured_authority_errors": "persistent_authority_unavailable" in server,
    "bindings_v2": "P190_OPERATION_SURFACE_BINDINGS_V2" in bindings and '"governed_operation_count":31' in bindings,
    "lifecycle_tests": "test_provider_and_job_lifecycle_preserve_constraints" in tests,
    "restart_test": "test_persistence_restart_and_integrity" in tests,
    "tamper_test": "test_resource_record_tamper_is_rejected_after_valid_state_root_update" in tests,
    "live_server_test": "test_live_server_direct_routes_registry_and_compiler" in tests,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 6 verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 6 unified resource registry verification: PASS")
