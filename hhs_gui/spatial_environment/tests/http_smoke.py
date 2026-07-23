#!/usr/bin/env python3
from __future__ import annotations
import http.server
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
handler = lambda *args, **kwargs: Quiet(*args, directory=str(ROOT), **kwargs)
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
port = server.server_port
try:
    paths = [
        "/index.html", "/styles.css", "/src/main.js", "/src/spatial-renderer.js", "/src/world-model.js",
        "/src/projection-journal.js", "/src/application-registry.js", "/src/session-store.js",
        "/src/spatial-workspace-manager.js", "/src/replay-controller.js", "/src/telemetry-store.js",
        "/src/command-router.js", "/src/project-store.js", "/src/entity-scene-graph.js",
        "/src/asset-registry.js", "/src/world-router.js", "/src/simulation-engine.js",
        "/IMPLEMENTATION_MANIFEST.json"
    ]
    total = 0
    for path in paths:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=4) as response:
            data = response.read()
            assert response.status == 200 and data
            total += len(data)
    print("HTTP_SMOKE_PASSED")
    print(f"assets={len(paths)}")
    print(f"bytes={total}")
finally:
    server.shutdown(); server.server_close()
