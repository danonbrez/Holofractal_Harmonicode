#!/usr/bin/env python3
"""Pass 190 Iteration 5 atomic kernel-authority server."""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190 import HHSOperationError  # noqa: E402
from hhs_pass190_iteration2 import PersistentStoreError  # noqa: E402
from hhs_pass190_iteration3 import HarmonicodeOperationCompiler  # noqa: E402
from hhs_pass190_iteration3_server import iteration3_openapi_document  # noqa: E402
from hhs_pass190_iteration4_server import (  # noqa: E402
    Handler as Iteration4Handler,
    Pass190Iteration4Server,
)
from hhs_pass190_iteration5 import (  # noqa: E402
    ITERATION5_CLASSIFICATION,
    CorrectedAuthorityContext,
)


def iteration5_openapi_document(context: CorrectedAuthorityContext) -> dict:
    document = iteration3_openapi_document(context)
    document["info"]["version"] = "5.0.0"
    document["x-hhs-iteration"] = 5
    document["x-hhs-classification"] = ITERATION5_CLASSIFICATION
    document["x-hhs-arbitration"] = "/api/pass190/arbitration"
    document["x-hhs-lease-receipts"] = "/api/pass190/lease-receipts"
    document["paths"]["/api/pass190/arbitration"] = {
        "get": {
            "operationId": "pass190.arbitration",
            "summary": "Return refreshed singleton lease, transition, and fencing status",
            "responses": {
                "200": {"description": "Verified arbitration status"},
                "503": {"description": "Persistent authority unavailable"},
            },
        }
    }
    document["paths"]["/api/pass190/lease-receipts"] = {
        "get": {
            "operationId": "pass190.lease.receipts",
            "summary": "Return the Hash72 lease-transition receipt chain",
            "parameters": [
                {"name": "after", "in": "query", "schema": {"type": "integer", "minimum": 0}},
                {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 1000}},
            ],
            "responses": {
                "200": {"description": "Verified lease-transition receipt page"},
                "503": {"description": "Persistent authority unavailable"},
            },
        }
    }
    return document


class Handler(Iteration4Handler):
    server_version = "HHS-P190-I5/5.0"

    @property
    def context(self) -> CorrectedAuthorityContext:
        return self.server.context  # type: ignore[attr-defined]

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path not in {
            "/api/pass190/arbitration",
            "/api/pass190/lease-receipts",
            "/openapi.json",
        }:
            super().do_GET()
            return
        try:
            if parsed.path == "/api/pass190/arbitration":
                self._write(200, self.context.arbitration_report())
                return
            if parsed.path == "/api/pass190/lease-receipts":
                query = parse_qs(parsed.query, keep_blank_values=True)
                after, limit = self._range(query)
                self._write(200, {"lease_receipts": self.context.lease_receipts_after(after, limit)})
                return
            self._write(200, iteration5_openapi_document(self.context))
        except (PersistentStoreError, sqlite3.Error, OSError) as exc:
            self._write(503, {"error": "persistent_authority_unavailable", "message": str(exc)})
        except (ValueError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})


class Pass190Iteration5Server(Pass190Iteration4Server):
    def __init__(
        self,
        address: tuple[str, int],
        context: CorrectedAuthorityContext,
        compiler: HarmonicodeOperationCompiler,
        capability_secret: str | bytes,
    ):
        super().__init__(address, context, compiler, capability_secret, Handler)


def build_server(
    host: str = "127.0.0.1",
    port: int = 8190,
    *,
    database: Path | str = "pass190-authority.sqlite3",
    context: CorrectedAuthorityContext | None = None,
    compiler: HarmonicodeOperationCompiler | None = None,
    capability_secret: str | bytes | None = None,
) -> Pass190Iteration5Server:
    secret = capability_secret or os.environ.get("HHS_PASS190_CAPABILITY_SECRET")
    if not secret:
        raise RuntimeError("HHS_PASS190_CAPABILITY_SECRET is required")
    return Pass190Iteration5Server(
        (host, port),
        context or CorrectedAuthorityContext(database),
        compiler or HarmonicodeOperationCompiler(),
        secret,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8190)
    parser.add_argument("--database", default="pass190-authority.sqlite3")
    args = parser.parse_args()
    server = build_server(args.host, args.port, database=args.database)
    print(f"HHS Pass 190 iteration 5 listening on http://{args.host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
