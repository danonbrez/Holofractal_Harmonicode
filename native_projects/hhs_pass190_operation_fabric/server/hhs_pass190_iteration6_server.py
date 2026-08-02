#!/usr/bin/env python3
"""Pass 190 Iteration 6 unified resource-registry and job-lifecycle server."""
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

from hhs_pass190 import (  # noqa: E402
    ArgumentValidationError,
    CapabilityDeniedError,
    HHSOperationError,
    StateConflictError,
)
from hhs_pass190_capability import CapabilityTokenError  # noqa: E402
from hhs_pass190_iteration2 import PersistentStoreError  # noqa: E402
from hhs_pass190_iteration5_server import (  # noqa: E402
    Handler as Iteration5Handler,
    Pass190Iteration5Server,
    iteration5_openapi_document,
)
from hhs_pass190_iteration6_compiler import ResourceOperationCompiler  # noqa: E402
from hhs_pass190_iteration6_registry import (  # noqa: E402
    ITERATION6_CLASSIFICATION,
    ITERATION6_CONTRACT,
)
from hhs_pass190_iteration6_runtime import UnifiedResourceRegistryContext  # noqa: E402


def iteration6_openapi_document(context: UnifiedResourceRegistryContext) -> dict:
    document = iteration5_openapi_document(context)
    document["info"]["version"] = "6.0.0"
    document["x-hhs-iteration"] = 6
    document["x-hhs-contract"] = ITERATION6_CONTRACT
    document["x-hhs-classification"] = ITERATION6_CLASSIFICATION
    document["x-hhs-resource-registry"] = "/api/pass190/resource-registry"
    document["x-hhs-governed-operation-count"] = len(context.registry.records)
    document["x-hhs-native-operation-count"] = int(context.registry.payload["native_operation_count"])
    document["x-hhs-compiler-fallback"] = "vm81-exact-authority-fallback-v1"
    document["paths"]["/api/pass190/resource-registry"] = {
        "get": {
            "operationId": "pass190.resource.registry",
            "summary": "Return verified workspace, artifact, provider, capability, and job registry status",
            "responses": {
                "200": {"description": "Verified resource registry status"},
                "503": {"description": "Persistent authority unavailable"},
            },
        }
    }
    return document


class Handler(Iteration5Handler):
    server_version = "HHS-P190-I6/6.0"

    @property
    def context(self) -> UnifiedResourceRegistryContext:
        return self.server.context  # type: ignore[attr-defined]

    @property
    def compiler(self) -> ResourceOperationCompiler:
        return self.server.compiler  # type: ignore[attr-defined]

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        if parsed.path not in {"/api/pass190/resource-registry", "/openapi.json"}:
            super().do_GET()
            return
        try:
            if parsed.path == "/api/pass190/resource-registry":
                self._write(200, self.context.resource_registry_report())
            else:
                self._write(200, iteration6_openapi_document(self.context))
        except (PersistentStoreError, sqlite3.Error, OSError) as exc:
            self._write(503, {"error": "persistent_authority_unavailable", "message": str(exc)})
        except (ValueError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        prefix = "/api/pass190/operations/"
        if not parsed.path.startswith(prefix):
            super().do_POST()
            return
        try:
            operation_id = parsed.path[len(prefix):]
            record = self.context.registry.resolve(operation_id)
            if record.raw["HTTP_path"] != parsed.path:
                raise ArgumentValidationError("operation route does not match canonical registry")
            arguments = self._body()
            capabilities, principal = self._authorized_capabilities([operation_id])
            result = self.context.invoke(
                operation_id,
                arguments,
                surface=f"http-direct:{principal}",
                capabilities=capabilities,
                idempotency_key=self.headers.get("Idempotency-Key"),
                expected_state=self.headers.get("X-HHS-Expected-State"),
            )
            self._write(200, result.to_dict())
        except CapabilityTokenError as exc:
            self._write(401, {"error": type(exc).__name__, "message": str(exc)})
        except CapabilityDeniedError as exc:
            self._write(403, {"error": type(exc).__name__, "message": str(exc)})
        except StateConflictError as exc:
            self._write(409, {"error": type(exc).__name__, "message": str(exc)})
        except (PersistentStoreError, sqlite3.Error, OSError) as exc:
            self._write(503, {"error": "persistent_authority_unavailable", "message": str(exc)})
        except (KeyError, ValueError, HHSOperationError) as exc:
            self._write(400, {"error": type(exc).__name__, "message": str(exc)})


class Pass190Iteration6Server(Pass190Iteration5Server):
    def __init__(
        self,
        address: tuple[str, int],
        context: UnifiedResourceRegistryContext,
        compiler: ResourceOperationCompiler,
        capability_secret: str | bytes,
    ):
        super().__init__(address, context, compiler, capability_secret)
        self.RequestHandlerClass = Handler


def build_server(
    host: str = "127.0.0.1",
    port: int = 8190,
    *,
    database: Path | str = "pass190-authority.sqlite3",
    context: UnifiedResourceRegistryContext | None = None,
    compiler: ResourceOperationCompiler | None = None,
    capability_secret: str | bytes | None = None,
) -> Pass190Iteration6Server:
    secret = capability_secret or os.environ.get("HHS_PASS190_CAPABILITY_SECRET")
    if not secret:
        raise RuntimeError("HHS_PASS190_CAPABILITY_SECRET is required")
    runtime = context or UnifiedResourceRegistryContext(database)
    server = Pass190Iteration6Server(
        (host, port),
        runtime,
        compiler or ResourceOperationCompiler(),
        secret,
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
    print(f"HHS Pass 190 iteration 6 listening on http://{args.host}:{server.server_address[1]}")
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
