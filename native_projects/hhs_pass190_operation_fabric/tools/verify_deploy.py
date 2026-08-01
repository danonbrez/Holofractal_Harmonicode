#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
service = (ROOT / "deploy/hhs-pass190.service").read_text(encoding="utf-8")
nginx = (ROOT / "deploy/nginx-hhs-pass190.conf").read_text(encoding="utf-8")
install = (ROOT / "deploy/install.sh").read_text(encoding="utf-8")
verify = (ROOT / "deploy/verify.sh").read_text(encoding="utf-8")
checks = {
    "persistent_database": "/var/lib/hhs/pass190-authority.sqlite3" in service,
    "iteration4_server": "hhs_pass190_iteration4_server.py" in service,
    "installed_working_directory": "WorkingDirectory=/opt/hhs/pass190-operation-fabric" in service,
    "capability_environment": "EnvironmentFile=/etc/hhs/pass190.env" in service,
    "service_source_copy": 'sudo cp -a "$ROOT/." "$STAGE/"' in install,
    "atomic_swap": 'sudo mv -T "$STAGE" "$TARGET"' in install,
    "rollback_path": "rollback()" in install and "trap rollback ERR" in install,
    "secret_generation": "HHS_PASS190_CAPABILITY_SECRET" in install,
    "validation_before_install": "make validate" in install,
    "websocket_upgrade": "proxy_set_header Upgrade" in nginx,
    "authorization_forwarding": "proxy_set_header Authorization $http_authorization" in nginx,
    "unsigned_scope_removed": 'proxy_set_header X-HHS-Capability ""' in nginx,
    "integrity_probe": "/api/pass190/integrity" in verify,
    "arbitration_probe": "/api/pass190/arbitration" in verify,
    "native_manifest_probe": "/api/pass190/native-abi" in verify,
    "compiler_probe": '"/api/pass190/compile-execute"' in verify,
    "distributed_assertion": "distributed_singleton_verified" in verify,
}
failed = [key for key, value in checks.items() if not value]
if failed:
    raise SystemExit("deployment verification failed: " + ", ".join(failed))
print("Pass 190 iteration 4 distributed deployment verification: PASS")
