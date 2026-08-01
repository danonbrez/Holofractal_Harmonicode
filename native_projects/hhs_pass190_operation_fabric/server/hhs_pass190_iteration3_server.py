#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190 import HHSOperationError  # noqa: E402
from hhs_pass190_iteration2 import PersistentAuthorityContext, PersistentStoreError  # noqa: E402
from hhs_pass190_iteration2_server import Handler as Iteration2Handler  # noqa: E402
from hhs_pass190_iteration3 import (  # noqa: E402
    DEFAULT_NATIVE_MANIFEST,
    HarmonicodeOperationCompiler,
    NativeABIError,
)


class Pass190Iteration3Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        context: PersistentAuthorityContext,
        compiler: HarmonicodeOperationCompiler,
    ):
        self.context = context
        self.compiler = compiler
        super().__init__(address, Handler)

    def server_close(self) -> None:
        super().server_close()
        self.context.close()


class Handler(Iteration2Handler):
    server_version = "HHS-P190-I3/3.0"

    @property
    def compiler(self) -> HarmonicodeOperationCompiler:
        return self.server.compiler  # type: ignore[attr-defined]

    def _manifest(self) -> dict[str, Any]:
        return json.loads(DEFAULT_NATIVE_MANIFEST.read_text(encoding="utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path == "/api/pass190/native-abi":
            self._write(200, self._manifest())
            return
        if parsed.path == "/openapi.json":
            document = self.context.openapi_document()
            document["info"]["version"] = "3.0.0"
            document["x-hhs-iteration"] = 3
            document["x-hhs-websocket"] = "/api/pass190/ws"
            document["x-hhs-native-abi"] = "/api/pass190/native-abi"
            document["paths"]["/api/pass190/compile"] = {
                "post": {
                    "operationId": "pass190.compile",
                    "summary": "Lower exact HARMONICODE constructors through CST, AST, HIR, and VMIR",
                    "responses": {"200": {"description": "Compiled operation program"}},
                }
            }
            document["paths"]["/api/pass190/compile-execute"] = {
                "post": {
                    "operationId": "pass190.compile.execute",
                    "summary": "Compile and execute through the persistent VM81 authority",
                    "responses": {"200": {"description": "Compiled program and admitted results"}},
                }
            }
            self._write(200, document)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path not in {"/api/pass190/compile", "/api/pass190/compile-execute"}:
            super().do_POST()
            return
        try:
            payload = self._body()
            source = payload["source"]
            if not isinstance(source, str):
                raise ValueError("source must be a string")
            program = self.compiler.compile_program(source)
            response: dict[str, Any] = {"program": program}
            if parsed.path.endswith("compile-execute"):
                capabilities = [
                    item.strip()
                    for item in self.headers.get("X-HHS-Capability", "").split(",")
                    if item.strip()
                ]
                response["results"] = self.compiler.execute(
                    program,
                    self.context,
                    capabilities=capabilities,
                )
            self._write(200, response)
        except (KeyError, ValueError, json.JSONDecodeError, PersistentStoreError, NativeABIError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})


def build_server(
    host: str = "127.0.0.1",
    port: int = 8190,
    *,
    database: Path | str = "pass190-authority.sqlite3",
    context: PersistentAuthorityContext | None = None,
    compiler: HarmonicodeOperationCompiler | None = None,
) -> Pass190Iteration3Server:
    return Pass190Iteration3Server(
        (host, port),
        context or PersistentAuthorityContext(database),
        compiler or HarmonicodeOperationCompiler(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8190)
    parser.add_argument("--database", default="pass190-authority.sqlite3")
    args = parser.parse_args()
    server = build_server(args.host, args.port, database=args.database)
    print(f"HHS Pass 190 iteration 3 listening on http://{args.host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
