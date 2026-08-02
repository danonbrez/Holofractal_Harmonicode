#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-http://127.0.0.1:8190}"

health="$(curl --fail --silent --show-error "$BASE_URL/api/pass190/health")"
integrity="$(curl --fail --silent --show-error "$BASE_URL/api/pass190/integrity")"
arbitration="$(curl --fail --silent --show-error "$BASE_URL/api/pass190/arbitration")"
resources="$(curl --fail --silent --show-error "$BASE_URL/api/pass190/resource-registry")"
lease_receipts="$(curl --fail --silent --show-error "$BASE_URL/api/pass190/lease-receipts?after=0&limit=1000")"
native="$(curl --fail --silent --show-error "$BASE_URL/api/pass190/native-abi")"
openapi="$(curl --fail --silent --show-error "$BASE_URL/openapi.json")"

python3 - "$health" "$integrity" "$arbitration" "$resources" "$lease_receipts" "$native" "$openapi" <<'PY'
import json
import sys
health, integrity, arbitration, resources, lease_receipts, native, openapi = map(json.loads, sys.argv[1:])
assert health["result"]["status"] == "ok"
assert health["result"]["operations"] == 31
assert health["result"]["native_operations"] == 10
assert integrity["status"] == "ok"
assert integrity["metadata_complete"] is True
assert integrity["events_verified"] is True
assert integrity["distributed_singleton_verified"] is True
assert integrity["atomic_snapshot_verified"] is True
assert integrity["lease_receipts_verified"] is True
assert integrity["kernel_authority_verified"] is True
assert integrity["resource_registry_verified"] is True
assert integrity["governed_operation_count"] == 31
assert integrity["native_operation_count"] == 10
assert integrity["compiler_fallback_operation_count"] == 21
assert resources["governed_operation_count"] == 31
assert resources["native_operation_count"] == 10
assert resources["compiler_fallback_operation_count"] == 21
assert resources["counts"] == {"workspaces": 0, "artifacts": 0, "providers": 0, "capabilities": 0, "jobs": 0}
assert resources["active_job_count"] == 0
assert len(resources["resource_registry_hash72"]) == 72
assert arbitration["lease_receipt_chain_verified"] is True
assert arbitration["lease_state"] in {"absent", "active", "released"}
if arbitration["active"]:
    assert arbitration["lease_state"] == "active"
    assert arbitration["holder_id"]
    assert arbitration["lease_expires_ns"] > 0
    assert arbitration["last_transition"] == "ACQUIRED"
else:
    assert arbitration["lease_state"] in {"absent", "released"}
assert arbitration["fence_count"] == integrity["receipt_count"]
assert arbitration["highest_committed_fence"] >= arbitration["fence_count"]
assert arbitration["lease_transition_count"] == len(lease_receipts["lease_receipts"])
assert native["operation_count"] == 10
assert openapi["x-hhs-iteration"] == 6
assert openapi["x-hhs-governed-operation-count"] == 31
assert openapi["x-hhs-native-operation-count"] == 10
required = {
    "/api/pass190/integrity",
    "/api/pass190/arbitration",
    "/api/pass190/resource-registry",
    "/api/pass190/lease-receipts",
    "/api/pass190/events",
    "/api/pass190/receipts",
    "/api/pass190/native-abi",
    "/api/pass190/invoke",
    "/api/pass190/replay",
    "/api/pass190/compile",
    "/api/pass190/compile-execute",
    "/api/pass190/operations/workspace.create",
    "/api/pass190/operations/job.submit",
}
assert required.issubset(openapi["paths"])
PY

printf 'Pass 190 iteration 6 unified resource authority verification: PASS\n'
