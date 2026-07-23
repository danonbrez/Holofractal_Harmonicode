from __future__ import annotations

import base64
import hashlib
import json
import secrets
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from hhs_runtime.pass145.canonical import canonical_json
from hhs_runtime.pass145.errors import Pass145Error
from .service import HHS146Service


class HHS146SecurityServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int], db_path: str | Path, *, token: str | None = None, identity_id: str | None = None, grant_id: str | None = None, identity_token: str | None = None):
        if address[0] not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Pass 146 security API binds to loopback only")
        super().__init__(address, HHS146SecurityHandler)
        self.db_path = Path(db_path).expanduser().resolve()
        self.token = token or secrets.token_urlsafe(32)
        self.identity_id = identity_id
        self.grant_id = grant_id
        self.identity_token = identity_token


class HHS146SecurityHandler(BaseHTTPRequestHandler):
    server: HHS146SecurityServer
    max_request_bytes = 8 * 1024 * 1024

    def log_message(self, *_: Any) -> None:
        return

    def _headers(self, status: int, length: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        self.end_headers()

    def _json(self, status: int, payload: Any) -> None:
        raw = canonical_json(payload).encode("utf-8")
        self._headers(status, len(raw))
        self.wfile.write(raw)

    def _auth(self) -> bool:
        origin = self.headers.get("Origin")
        if origin and not any(origin.startswith(x) for x in ("http://127.0.0.1", "http://localhost", "https://127.0.0.1", "https://localhost")):
            self._json(HTTPStatus.FORBIDDEN, {"ok": False, "error_code": "CROSS_ORIGIN_REJECTED"})
            return False
        if self.headers.get("Authorization", "") != f"Bearer {self.server.token}":
            self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error_code": "AUTHORITY_INSUFFICIENT"})
            return False
        return True

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > self.max_request_bytes:
            raise Pass145Error("RESOURCE_BOUNDED", "request size bound reached", "SECURITY_API")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", "request body must be an object", "SECURITY_API")
        return value

    def _bounded_cli(self, service: HHS146Service, argv: list[str], *, stdin_text: str | None = None, input_evidence: dict[str, Any] | None = None) -> Any:
        if not (self.server.identity_id and self.server.grant_id and self.server.identity_token):
            raise Pass145Error("IDENTITY_UNRESOLVED", "server knowledge API has no admitted device identity", "SECURITY_API")
        request: dict[str, Any] = {"argv": argv, "classification": "INTERNAL", "input_evidence": input_evidence or {"files": []}}
        if stdin_text is not None:
            request["stdin_text"] = stdin_text
        constructed = service.security.construct_path(self.server.identity_id, self.server.grant_id, self.server.identity_token, "RUN_CLI_COMMAND", request)
        closed = service.security.execute_path(constructed["result"]["contract_id"], self.server.identity_id, self.server.identity_token)
        return closed["result"]["result"]

    def do_OPTIONS(self) -> None:
        self._json(HTTPStatus.METHOD_NOT_ALLOWED, {"ok": False, "error_code": "CROSS_ORIGIN_REJECTED"})

    def do_GET(self) -> None:
        if not self._auth():
            return
        try:
            path = urlparse(self.path).path
            with HHS146Service(self.server.db_path) as service:
                if path in {"/api/v1/status", "/api/v1/database/status"}:
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, ["database", "status"]))
                if path.startswith("/api/v1/source/"):
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, ["source", "show", path.rsplit("/", 1)[-1], "--raw-base64"]))
                if path.startswith("/api/v1/object/"):
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, ["object", "show", path.rsplit("/", 1)[-1]]))
                if path.startswith("/api/v1/graph/"):
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, ["graph", "trace", path.rsplit("/", 1)[-1]]))
                if path.startswith("/api/v1/receipt/"):
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, ["receipt", "show", path.rsplit("/", 1)[-1]]))
                if path == "/api/v1/security/status":
                    return self._json(HTTPStatus.OK, service.security.status())
                if path.startswith("/api/v1/security/contract/"):
                    return self._json(HTTPStatus.OK, service.security.get_contract(path.rsplit("/", 1)[-1]))
                if path == "/api/v1/security/peers":
                    return self._json(HTTPStatus.OK, service.security.list_trusted_peers())
                if path.startswith("/api/v1/security/identity/") and path.endswith("/public"):
                    identity_id = path.split("/")[-2]
                    return self._json(HTTPStatus.OK, service.security.identity_public_record(identity_id))
                if path.startswith("/api/v1/security/message/"):
                    return self._json(HTTPStatus.OK, service.security.inspect_message(path.rsplit("/", 1)[-1]))
                return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
        except Pass145Error as exc:
            self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})

    def do_POST(self) -> None:
        if not self._auth():
            return
        try:
            body = self._body()
            path = urlparse(self.path).path
            with HHS146Service(self.server.db_path) as service:
                e = service.security
                if path == "/api/v1/ingest":
                    name = str(body.get("name", "api-input.txt"))
                    namespace = str(body.get("namespace", "default"))
                    mime_type = str(body.get("mime_type", "text/plain"))
                    if "text" in body:
                        argv = ["ingest", "stdin", "--name", name, "--mime-type", mime_type, "--namespace", namespace]
                        if not body.get("analyze", True): argv.append("--no-analyze")
                        return self._json(HTTPStatus.CREATED, self._bounded_cli(service, argv, stdin_text=str(body["text"])))
                    if "content_base64" in body:
                        try:
                            raw = base64.b64decode(str(body["content_base64"]), validate=True)
                        except Exception as exc:
                            raise Pass145Error("INGESTION_REJECTED", "invalid base64 source", "SECURITY_API") from exc
                        with tempfile.TemporaryDirectory(prefix="hhs146-api-") as td:
                            temp = Path(td) / name
                            temp.write_bytes(raw)
                            argv = ["ingest", "file", str(temp), "--mime-type", mime_type, "--namespace", namespace]
                            if not body.get("analyze", True): argv.append("--no-analyze")
                            evidence = {"files": [{"path": str(temp), "byte_length": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}]}
                            return self._json(HTTPStatus.CREATED, self._bounded_cli(service, argv, input_evidence=evidence))
                    raise Pass145Error("INGESTION_REJECTED", "text or content_base64 required; API filesystem paths are not accepted", "SECURITY_API")
                if path == "/api/v1/query":
                    argv = ["query", str(body.get("question", "")), "--limit", str(int(body.get("limit", 100)))]
                    if body.get("namespace"): argv += ["--namespace", str(body["namespace"])]
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, argv))
                if path == "/api/v1/search":
                    argv = ["search", str(body.get("text", "")), "--limit", str(int(body.get("limit", 100)))]
                    if body.get("symbol"): argv.append("--symbol")
                    if body.get("object_type"): argv += ["--type", str(body["object_type"])]
                    if body.get("source_id"): argv += ["--source", str(body["source_id"])]
                    if body.get("namespace"): argv += ["--namespace", str(body["namespace"])]
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, argv))
                if path == "/api/v1/validate":
                    target = str(body.get("target", "source"))
                    argv = ["validate", target]
                    if target != "database": argv.append(str(body.get("id", "")))
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, argv))
                if path == "/api/v1/replay":
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, ["replay", "ingestion", str(body["source_id"])]))
                if path == "/api/v1/backup":
                    return self._json(HTTPStatus.CREATED, self._bounded_cli(service, ["backup", "create", str(body["path"])]))
                if path == "/api/v1/restore/preview":
                    return self._json(HTTPStatus.OK, self._bounded_cli(service, ["restore", "preview", str(body["path"])]))
                if path == "/api/v1/security/bootstrap":
                    return self._json(HTTPStatus.CREATED, e.bootstrap_local_owner(str(body.get("display_name", "Local HHS Owner"))))
                if path == "/api/v1/security/peer/trust":
                    return self._json(HTTPStatus.CREATED, e.trust_peer(str(body["issuer_identity_id"]), str(body["issuer_grant_id"]), str(body["issuer_token"]), str(body["peer_id"]), str(body["public_key_b64"]), classifications=list(body.get("classifications", ["INTERNAL"])), destinations=list(body.get("destinations", ["*"]))))
                if path == "/api/v1/security/message/admit":
                    envelope = dict(body.get("envelope", {}))
                    source_peer = str(envelope.get("source_peer", body.get("source_peer", "")))
                    destination_peer = str(envelope.get("destination_peer", body.get("destination_peer", "")))
                    classification = str(envelope.get("scope", {}).get("classification", body.get("classification", "INTERNAL"))).upper()
                    request = {"envelope": envelope, "source_peer": source_peer, "destination_peer": destination_peer, "classification": classification}
                    constructed = e.construct_path(str(body["receiver_identity_id"]), str(body["receiver_grant_id"]), str(body["receiver_token"]), "RECEIVE_PROPAGATION", request, destination={"kind": "PEER", "id": destination_peer})
                    return self._json(HTTPStatus.CREATED, e.execute_path(constructed["result"]["contract_id"], str(body["receiver_identity_id"]), str(body["receiver_token"])))
                if path == "/api/v1/security/path/construct":
                    result = e.construct_path(str(body["identity_id"]), str(body["grant_id"]), str(body["identity_token"]), str(body["operation"]), dict(body.get("request", {})), destination=dict(body.get("destination", {})), parent_contract_id=body.get("parent_contract_id"), expires_after_sequences=int(body.get("expires_after_sequences", 32)))
                    return self._json(HTTPStatus.CREATED, result)
                if path == "/api/v1/security/path/execute":
                    return self._json(HTTPStatus.OK, e.execute_path(str(body["contract_id"]), str(body["identity_id"]), str(body["identity_token"])))
                if path == "/api/v1/security/path/replay":
                    return self._json(HTTPStatus.OK, e.replay_path(str(body["contract_id"])))
                if path == "/api/v1/security/message/receive":
                    return self._json(HTTPStatus.OK, e.receive_message(str(body["message_id"]), str(body["receiver_identity_id"]), str(body["receiver_grant_id"]), str(body["receiver_token"])))
                return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
        except Pass145Error as exc:
            self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})


def serve(db_path: str | Path, *, host: str = "127.0.0.1", port: int = 8876, token: str | None = None, identity_id: str | None = None, grant_id: str | None = None, identity_token: str | None = None) -> None:
    server = HHS146SecurityServer((host, port), db_path, token=token, identity_id=identity_id, grant_id=grant_id, identity_token=identity_token)
    print(canonical_json({"schema": "HHS_PASS146_SECURITY_API_START_V1", "url": f"http://{host}:{server.server_port}", "token": server.token, "loopback_only": True}))
    try:
        server.serve_forever()
    finally:
        server.server_close()
