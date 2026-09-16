"""Isolated status producer used by the deployment bootstrap gateway.

The probe imports the authoritative visual server in a child process, invokes
status routes sequentially, and emits one JSON record per completed route.  It
must never mutate canonical runtime state.  In particular, the child inherits
the production runtime-output directory, so unified Hash72 ledger appends are
replaced with a fail-closed read-only projection *before* the authoritative app
is imported.  The probe still reads the real ledger and all normal status
state; it simply cannot become a competing append writer.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


def install_read_only_unified_ledger_projection() -> dict[str, Any]:
    """Prevent this synthetic probe process from appending canonical receipts.

    ``append_payload`` normally returns the materialized unified-ledger state.
    The read-only replacement returns that same state shape after a full
    transition validation, so status-only consumers retain their read surface
    without creating an alternate authority or racing the live Uvicorn worker.
    """

    from hhs_runtime import hhs_unified_hash72_ledger_v1 as ledger

    def read_only_append_payload(
        _kind: str,
        _source: str,
        _payload: dict[str, Any],
        *,
        ledger_path: str | Path | None = None,
    ) -> dict[str, Any]:
        path = Path(ledger_path) if ledger_path is not None else ledger.default_unified_ledger_path()
        data, invalid = ledger._load_with_errors(path, force_reload=True)
        if invalid:
            raise RuntimeError(
                f"status probe refuses invalid unified ledger projection: {invalid[:3]}"
            )
        projected = dict(data)
        projected["probe_read_only"] = True
        projected["canonical_ledger_mutated"] = False
        return projected

    ledger.append_payload = read_only_append_payload
    return {
        "schema": "HHS_RUNTIME_STATUS_PROBE_LEDGER_ISOLATION_V1",
        "mode": "READ_ONLY_UNIFIED_LEDGER",
        "canonical_ledger_mutated": False,
    }


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
    isolation = install_read_only_unified_ledger_projection()
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
                "ledger_isolation": isolation,
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
                "ledger_isolation": isolation,
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
