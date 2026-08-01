#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
service = (ROOT / "deploy/hhs-pass190.service").read_text()
nginx = (ROOT / "deploy/nginx-hhs-pass190.conf").read_text()
install = (ROOT / "deploy/install.sh").read_text()
verify = (ROOT / "deploy/verify.sh").read_text()
checks = {
    "persistent_database": "/var/lib/hhs/pass190-authority.sqlite3" in service,
    "single_server": "hhs_pass190_iteration2_server.py" in service,
    "websocket_upgrade": "proxy_set_header Upgrade" in nginx,
    "validation_before_install": "make validate" in install,
    "integrity_probe": "/api/pass190/integrity" in verify,
}
failed = [key for key, value in checks.items() if not value]
if failed:
    raise SystemExit("deployment verification failed: " + ", ".join(failed))
print("Pass 190 iteration 2 deployment verification: PASS")
