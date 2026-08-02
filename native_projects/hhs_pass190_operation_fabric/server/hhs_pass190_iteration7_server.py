#!/usr/bin/env python3
"""Pass 190 Iteration 7 durable worker execution and scheduler server."""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190 import HHSOperationError  # noqa: E402
from hhs_pass190_iteration2 import PersistentStoreError  # noqa: E402
from hhs_pass190_iteration6_server import (  # noqa: E402
    Handler as Iteration6Handler,
    Pass190Iteration6Server,
    iteration6_openapi_document,
)
from hhs_pass190_iteration7 import DurableExecutionContext  # noqa: E402
from hhs_pass190_iteration7_compiler import DurableExecutionCompiler  # noqa: E402
from hhs_pass190_iteration7_registry import ITERATION7_CLASSIFICATION, ITERATION7_CONTRACT  # noqa: E402


def iteration7_openapi_document(context: DurableExecutionContext) -> dict:
    document = iteration6_openapi_document(context)
    document["info"]["version"] = "7.0.0"
    document["x-hhs-iteration"] = 7
    document["x-hhs-contract"] = ITERATION7_CONTRACT
    document["x-hhs-classification"] = ITERATION7_CLASSIFICATION
    document["x-hhs-execution-runtime"] = "/api/pass190/execution-runtime"
    document["x-hhs-governed-operation-count"] = len(context.registry.records)
    document["x-hhs-execution-operation-count"] = int(context.registry.payload["execution_operation_count"])
    document["paths"]["/api/pass190/execution-runtime"] = {
        "get": {
            "operationId": "pass190.execution.runtime",
            "summary": "Return verified worker, scheduler, retry, cancellation, and execution status",
            "responses": {
                "200": {"description": "Verified durable execution status"},
                "503": {"description": "Persistent authority unavailable"},
            },
        }
    }
    return document


class Handler(Iteration6Handler):
    server_version = "HHS-P190-I7/7.0"

    @property
    def context(self) -> DurableExecutionContext:
        return self.server.context  # type: ignore[attr-defined]

    @property
    def compiler(self) -> DurableExecutionCompiler:
        return self.server.compiler  # type: ignore[attr-defined]

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path not in {"/api/pass190/execution-runtime", "/openapi.json"}:
            super().do_GET()
            return
        try:
            if parsed.path == "/api/pass190/execution-runtime":
                self._write(200, self.context.execution_runtime_report())
            else:
                self._write(200, iteration7_openapi_document(self.context))
        except (PersistentStoreError, sqlite3.Error, OSError) as exc:
            self._write(503, {"error": "persistent_authority_unavailable", "message": str(exc)})
        except (ValueError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})


class Pass190Iteration7Server(Pass190Iteration6Server):
    def __init__(
        self,
        address: tuple[str, int],
        context: DurableExecutionContext,
        compiler: DurableExecutionCompiler,
        capability_secret: str | bytes,
    ):
        super().__init__(address, context, compiler, capability_secret)
        self.RequestHandlerClass = Handler


def build_server(
    host: str = "127.0.0.1",
    port: int = 8190,
    *,
    database: Path | str = "pass190-authority.sqlite3",
    context: DurableExecutionContext | None = None,
    compiler: DurableExecutionCompiler | None = None,
    capability_secret: str | bytes | None = None,
) -> Pass190Iteration7Server:
    secret = capability_secret or os.environ.get("HHS_PASS190_CAPABILITY_SECRET")
    if not secret:
        raise RuntimeError("HHS_PASS190_CAPABILITY_SECRET is required")
    runtime = context or DurableExecutionContext(database)
    server = Pass190Iteration7Server(
        (host, port), runtime, compiler or DurableExecutionCompiler(), secret
    )
    server.RequestHandlerClass = Handler
    return server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8190)
    parser.add_argument("--database", default="pass190-authority.sqlite3")
    args = parser.parse_args()
    server = build_server(args.host, args.port, database=args.database)
    print(f"HHS Pass 190 iteration 7 listening on http://{args.host}:{server.server_address[1]}")
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
