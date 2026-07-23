from __future__ import annotations

import secrets
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from hhs_runtime.pass145.canonical import canonical_json
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass146.api import HHS146SecurityHandler
from .service import HHS147Service


class HHS147PublicServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int], db_path: str | Path, *, token: str | None = None, identity_id: str | None = None, grant_id: str | None = None, identity_token: str | None = None):
        if address[0] not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Pass 147 public API binds to loopback only")
        super().__init__(address, HHS147PublicHandler)
        self.db_path = Path(db_path).expanduser().resolve()
        self.token = token or secrets.token_urlsafe(32)
        self.identity_id = identity_id
        self.grant_id = grant_id
        self.identity_token = identity_token


class HHS147PublicHandler(HHS146SecurityHandler):
    server: HHS147PublicServer

    def _public_discover(self, service: HHS147Service, request: dict[str, Any]) -> Any:
        if not (self.server.identity_id and self.server.grant_id and self.server.identity_token):
            raise Pass145Error("IDENTITY_UNRESOLVED", "server has no admitted device identity", "PUBLIC_API")
        built = service.security.construct_path(self.server.identity_id, self.server.grant_id, self.server.identity_token, "PUBLIC_DISCOVER", request, destination={"kind": "LOCAL_RESULT", "id": "LOCAL_RESULT"})
        closed = service.security.execute_path(built["result"]["contract_id"], self.server.identity_id, self.server.identity_token)
        return closed["result"]["result"]

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if not path.startswith("/api/v1/public/"):
            return super().do_GET()
        if not self._auth():
            return
        try:
            with HHS147Service(self.server.db_path) as service:
                if path == "/api/v1/public/capabilities":
                    query = parse_qs(parsed.query)
                    return self._json(HTTPStatus.OK, self._public_discover(service, {"action": "list", "filter_classification": (query.get("classification") or [None])[0], "surface_type": (query.get("surface_type") or [None])[0]}))
                if path.startswith("/api/v1/public/capability/"):
                    return self._json(HTTPStatus.OK, self._public_discover(service, {"action": "describe", "identifier": path.rsplit("/", 1)[-1]}))
                if path == "/api/v1/public/graph":
                    return self._json(HTTPStatus.OK, self._public_discover(service, {"action": "graph"}))
                if path == "/api/v1/public/audit":
                    return self._json(HTTPStatus.OK, self._public_discover(service, {"action": "audit"}))
                if path == "/api/v1/public/schemas":
                    return self._json(HTTPStatus.OK, self._public_discover(service, {"action": "schema"}))
                if path == "/api/v1/public/runtime/types":
                    return self._json(HTTPStatus.OK, self._public_discover(service, {"action": "runtime_types"}))
                if path == "/api/v1/public/examples":
                    return self._json(HTTPStatus.OK, self._public_discover(service, {"action": "examples"}))
                return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
        except Pass145Error as exc:
            self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/v1/public/"):
            return super().do_POST()
        if not self._auth():
            return
        try:
            body = self._body()
            with HHS147Service(self.server.db_path) as service:
                if path == "/api/v1/public/docs/query":
                    built = service.security.construct_path(self.server.identity_id, self.server.grant_id, self.server.identity_token, "PUBLIC_DOC_QUERY", {"question": str(body.get("question", "")), "limit": int(body.get("limit", 50))})
                    closed = service.security.execute_path(built["result"]["contract_id"], self.server.identity_id, self.server.identity_token)
                    return self._json(HTTPStatus.OK, closed["result"]["result"])
                if path == "/api/v1/public/agent/execute":
                    result = service.external_execute(str(body["identity_id"]), str(body["grant_id"]), str(body["identity_token"]), [str(x) for x in body.get("argv", [])], stdin_text=body.get("stdin_text"))
                    return self._json(HTTPStatus.OK, result)
                return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
        except Pass145Error as exc:
            self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})


def serve(db_path: str | Path, *, host: str = "127.0.0.1", port: int = 8877, token: str | None = None, identity_id: str | None = None, grant_id: str | None = None, identity_token: str | None = None) -> None:
    server = HHS147PublicServer((host, port), db_path, token=token, identity_id=identity_id, grant_id=grant_id, identity_token=identity_token)
    print(canonical_json({"schema": "HHS_PASS147_PUBLIC_API_START_V1", "url": f"http://{host}:{server.server_port}", "token": server.token, "loopback_only": True, "privileged_internal_access": 0}))
    try:
        server.serve_forever()
    finally:
        server.server_close()
