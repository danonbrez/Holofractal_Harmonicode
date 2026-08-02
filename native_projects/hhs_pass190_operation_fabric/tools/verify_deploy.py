#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
service = (ROOT / "deploy/hhs-pass190.service").read_text(encoding="utf-8")
worker_service = (ROOT / "deploy/hhs-pass190-worker.service").read_text(encoding="utf-8")
nginx = (ROOT / "deploy/nginx-hhs-pass190.conf").read_text(encoding="utf-8")
install = (ROOT / "deploy/install.sh").read_text(encoding="utf-8")
verify = (ROOT / "deploy/verify.sh").read_text(encoding="utf-8")
checks = {
    "persistent_database": "/var/lib/hhs/pass190-authority.sqlite3" in service and "/var/lib/hhs/pass190-authority.sqlite3" in worker_service,
    "iteration7_server": "hhs_pass190_iteration7_server.py" in service,
    "iteration7_worker": "hhs_pass190_iteration7_worker.py" in worker_service,
    "worker_requires_api": "Requires=hhs-pass190.service" in worker_service,
    "worker_restart": "Restart=on-failure" in worker_service,
    "installed_working_directory": "WorkingDirectory=/opt/hhs/pass190-operation-fabric" in service and "WorkingDirectory=/opt/hhs/pass190-operation-fabric" in worker_service,
    "capability_environment": "EnvironmentFile=/etc/hhs/pass190.env" in service and "EnvironmentFile=/etc/hhs/pass190.env" in worker_service,
    "service_source_copy": 'sudo cp -a "$ROOT/." "$STAGE/"' in install,
    "atomic_swap": 'sudo mv -T "$STAGE" "$TARGET"' in install,
    "rollback_path": "rollback()" in install and "trap rollback ERR" in install,
    "worker_rollback": "hhs-pass190-worker.service" in install,
    "secret_generation": "HHS_PASS190_CAPABILITY_SECRET" in install,
    "validation_before_install": "make validate" in install,
    "websocket_upgrade": "proxy_set_header Upgrade" in nginx,
    "authorization_forwarding": "proxy_set_header Authorization $http_authorization" in nginx,
    "unsigned_scope_removed": 'proxy_set_header X-HHS-Capability ""' in nginx,
    "integrity_probe": "/api/pass190/integrity" in verify,
    "arbitration_probe": "/api/pass190/arbitration" in verify,
    "resource_registry_probe": "/api/pass190/resource-registry" in verify,
    "execution_runtime_probe": "/api/pass190/execution-runtime" in verify,
    "lease_receipt_probe": "/api/pass190/lease-receipts" in verify,
    "native_manifest_probe": "/api/pass190/native-abi" in verify,
    "compiler_probe": '"/api/pass190/compile-execute"' in verify,
    "resource_assertion": "resource_registry_verified" in verify,
    "execution_assertion": "execution_runtime_verified" in verify,
    "governed_count": 'governed_operation_count"] == 42' in verify,
    "native_count": 'native_operation_count"] == 10' in verify,
    "fallback_count": 'compiler_fallback_operation_count"] == 32' in verify,
    "worker_count": 'worker_count"] >= 1' in verify,
    "active_lease_tolerated": 'arbitration["active"]' in verify and 'lease_state"] == "active"' in verify,
}
failed = [key for key, value in checks.items() if not value]
if failed:
    raise SystemExit("deployment verification failed: " + ", ".join(failed))
print("Pass 190 iteration 7 durable execution deployment verification: PASS")
