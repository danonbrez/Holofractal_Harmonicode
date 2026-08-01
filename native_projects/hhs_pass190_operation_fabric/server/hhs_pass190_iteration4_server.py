#!/usr/bin/env python3
"""Pass 190 Iteration 4 distributed singleton authority server."""
from __future__ import annotations

import argparse
import os
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Type
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190_iteration3 import HarmonicodeOperationCompiler  # noqa: E402
from hhs_pass190_iteration3_server import (  # noqa: E402
    Handler as Iteration3Handler,
    iteration3_openapi_document,
)
from hhs_pass190_iteration4 import (  # noqa: E402
    ITERATION4_CLASSIFICATION,
    DistributedAuthorityContext,
)


class Pass190Iteration4Server(ThreadingHTTPServer):
    daemon_threads = False
    block_on_close = True

    def __init__(
        self,
        address: tuple[str, int],
        context: DistributedAuthorityContext,
        compiler: HarmonicodeOperationCompiler,
        capability_secret: str | bytes,
        handler_class: Type[Iteration3Handler] | None = None,
    ):
        self.context = context
        self.compiler = compiler
        self.capability_secret = capability_secret
        self.closing = threading.Event()
        super().__init__(address, handler_class or Handler)

    def server_close(self) -> None:
        self.closing.set()
        super().server_close()
        self.context.close()


class Handler(Iteration3Handler):
    server_version = "HHS-P190-I4/4.0"

    @property
    def context(self) -> DistributedAuthorityContext:
        return self.server.context  # type: ignore[attr-defined]

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path == "/api/pass190/arbitration":
            self._write(200, self.context.arbitration_report())
            return
        if parsed.path == "/openapi.json":
            document = iteration3_openapi_document(self.context)
            document["info"]["version"] = "4.0.0"
            document["x-hhs-iteration"] = 4
            document["x-hhs-classification"] = ITERATION4_CLASSIFICATION
            document["x-hhs-arbitration"] = "/api/pass190/arbitration"
            document["paths"]["/api/pass190/arbitration"] = {
                "get": {
                    "operationId": "pass190.arbitration",
                    "summary": "Return distributed singleton lease and fencing status",
                    "responses": {"200": {"description": "Arbitration status"}},
                }
            }
            self._write(200, document)
            return
        super().do_GET()


def build_server(
    host: str = "127.0.0.1",
    port: int = 8190,
    *,
    database: Path | str = "pass190-authority.sqlite3",
    context: DistributedAuthorityContext | None = None,
    compiler: HarmonicodeOperationCompiler | None = None,
    capability_secret: str | bytes | None = None,
) -> Pass190Iteration4Server:
    secret = capability_secret or os.environ.get("HHS_PASS190_CAPABILITY_SECRET")
    if not secret:
        raise RuntimeError("HHS_PASS190_CAPABILITY_SECRET is required")
    return Pass190Iteration4Server(
        (host, port),
        context or DistributedAuthorityContext(database),
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
    print(f"HHS Pass 190 iteration 4 listening on http://{args.host}:{server.server_address[1]}")
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
