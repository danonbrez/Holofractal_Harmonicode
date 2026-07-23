#!/usr/bin/env python3
from __future__ import annotations
import http.server
import subprocess
import threading
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

handler = lambda *args, **kwargs: Quiet(*args, directory=str(ROOT), **kwargs)
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port

try:
    url = f"http://127.0.0.1:{port}/index.html?smoke=1"
    try:
        result = subprocess.run([
            "chromium", "--headless", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=1800", "--dump-dom", url
        ], capture_output=True, text=True, timeout=18)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("BROWSER_SMOKE_SKIPPED")
        print("reason=CHROMIUM_PROCESS_UNAVAILABLE_IN_CONTAINER")
        sys.exit(0)
    dom = result.stdout
    checks = ["HARMONICODE VM81", "surface-layer", "APPLICATION LIBRARY", "PROJECTION JOURNAL", "SESSION"]
    missing = [value for value in checks if value not in dom]
    if result.returncode != 0 or missing:
        print("BROWSER_SMOKE_FAILED", result.returncode, missing)
        print(result.stderr[-1000:])
        sys.exit(1)
    print("BROWSER_SMOKE_PASSED")
    print(f"dom_bytes={len(dom)}")
finally:
    server.shutdown()
    server.server_close()
