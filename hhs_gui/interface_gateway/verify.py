#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATEWAY = ROOT / "hhs_gui/interface_gateway/ubuntu_pty_gateway.py"
PAGE = ROOT / "hhs_gui/public/interface-proof.html"
VITE = ROOT / "hhs_gui/vite.config.ts"
UNIT = ROOT / "hhs_gui/interface_gateway/hhs-interface-pty.service"
NGINX = ROOT / "hhs_gui/interface_gateway/nginx-interface-pty.conf"

for path in (GATEWAY, PAGE, VITE, UNIT, NGINX):
    if not path.is_file():
        raise SystemExit(f"MISSING:{path.relative_to(ROOT)}")

py_compile.compile(str(GATEWAY), doraise=True)

gateway = GATEWAY.read_text("utf-8")
page = PAGE.read_text("utf-8")
vite = VITE.read_text("utf-8")
unit = UNIT.read_text("utf-8")
nginx = NGINX.read_text("utf-8")

required_gateway = [
    'GUEST_CLI = ROOT / "bin" / "hhs-guest"',
    'HHS_INTERFACE_PTY_ENABLED',
    'HHS_INTERFACE_PTY_TOKEN',
    'secrets.compare_digest',
    'asyncio.create_subprocess_exec',
    '"pty-exec"',
    '"bash", "-lc", command',
    '@app.websocket("/api/interface/ubuntu/pty/ws")',
]
for token in required_gateway:
    if token not in gateway:
        raise SystemExit(f"GATEWAY_INVARIANT_MISSING:{token}")

for forbidden in (
    "from hhs_runtime",
    "import hhs_runtime",
    "os.system(",
    "subprocess.run(",
    "shell=True",
):
    if forbidden in gateway:
        raise SystemExit(f"GATEWAY_BYPASS_FORBIDDEN:{forbidden}")

required_page = [
    "/api/interface/ubuntu/pty/ws",
    "HHS_INTERFACE_UBUNTU_PTY_GATEWAY_V1",
    'type="password"',
    "ubuntuAuthenticated",
    'action: "exec"',
]
for token in required_page:
    if token not in page:
        raise SystemExit(f"PAGE_INVARIANT_MISSING:{token}")

for forbidden in ("localStorage", "sessionStorage", "indexedDB", "WebAssembly"):
    if forbidden in page:
        raise SystemExit(f"CLIENT_COMPUTE_OR_STORAGE_FORBIDDEN:{forbidden}")

if '"/api/interface/ubuntu/pty"' not in vite or "127.0.0.1:8787" not in vite:
    raise SystemExit("VITE_GATEWAY_PROXY_MISSING")
if "127.0.0.1:8787" not in unit:
    raise SystemExit("SYSTEMD_LOOPBACK_BIND_MISSING")
if "/var/lib/hhs/ubuntu-guest/current/runtime.env" not in unit:
    raise SystemExit("PROMOTED_GUEST_ENV_MISSING")
if "127.0.0.1:8787" not in nginx or "proxy_set_header Upgrade $http_upgrade" not in nginx:
    raise SystemExit("NGINX_WEBSOCKET_ROUTE_MISSING")

print("HHS_INTERFACE_UBUNTU_PTY_GATEWAY_SOURCE_VERIFY:PASS")
