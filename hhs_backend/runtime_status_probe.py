"""Isolated status producer used by the deployment bootstrap gateway.

The probe imports the authoritative visual server in a child process, invokes status
routes sequentially, and emits one JSON record per completed route. It never mutates
canonical runtime state and never serves user traffic.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from typing import Any
from urllib.parse import urlsplit


async def invoke_get(app: Any, path: str) -> tuple[int, dict[str, Any]]:
    parsed = urlsplit(path)
    messages: list[dict[str, Any]] = []
    delivered = False

    async def receive() -> dict[str, Any]:
        nonlocal delivered
        if delivered:
            await asyncio.sleep(0)
            return {"type": "http.disconnect"}
        delivered = True
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": parsed.path,
        "raw_path": parsed.path.encode("utf-8"),
        "query_string": parsed.query.encode("utf-8"),
        "root_path": "",
        "headers": [(b"accept", b"application/json")],
        "client": ("127.0.0.1", 0),
        "server": ("127.0.0.1", 8080),
    }
    await app(scope, receive, send)
    status_code = 500
    body = bytearray()
    for message in messages:
        if message["type"] == "http.response.start":
            status_code = int(message["status"])
        elif message["type"] == "http.response.body":
            body.extend(message.get("body", b""))
    try:
        payload = json.loads(bytes(body).decode("utf-8"))
        if not isinstance(payload, dict):
            payload = {"value": payload}
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = {
            "ok": False,
            "error": "NON_JSON_STATUS_RESPONSE",
            "body_preview": bytes(body[:256]).decode("utf-8", errors="replace"),
        }
    return status_code, payload


async def run(paths: list[str]) -> int:
    from hhs_backend.visual_server import app

    for path in paths:
        started = time.perf_counter()
        try:
            status_code, payload = await invoke_get(app, path)
            record = {
                "schema": "HHS_RUNTIME_STATUS_PROBE_RECORD_V1",
                "path": path,
                "status_code": status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000),
                "payload": payload,
            }
        except Exception as exc:  # the probe must report and continue
            record = {
                "schema": "HHS_RUNTIME_STATUS_PROBE_RECORD_V1",
                "path": path,
                "status_code": 503,
                "duration_ms": round((time.perf_counter() - started) * 1000),
                "payload": {
                    "ok": False,
                    "phase": "PROBE_FAILED",
                    "error": f"{type(exc).__name__}: {exc}",
                },
            }
        print(json.dumps(record, sort_keys=True, ensure_ascii=False), flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-json", required=True)
    args = parser.parse_args()
    paths = json.loads(args.paths_json)
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise SystemExit("--paths-json must encode a list of strings")
    return asyncio.run(run(paths))


if __name__ == "__main__":
    raise SystemExit(main())
