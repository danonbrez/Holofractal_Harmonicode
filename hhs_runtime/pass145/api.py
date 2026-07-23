from __future__ import annotations

import base64
import json
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .canonical import canonical_json
from .errors import Pass145Error
from .service import HHS145Service
from .workbench import EnvironmentManager, LVMEngine, ScriptWorkbench


class HHS145APIServer(ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], db_path: str | Path, token: str | None = None, static_root: str | Path | None = None):
        host = address[0]
        if host not in {"127.0.0.1", "localhost", "::1"}:
            raise Pass145Error("DISCLOSURE_PATH_INVALID", "Pass 145 API binds to loopback only by default", "API_BIND")
        super().__init__(address, HHS145APIHandler)
        self.db_path = str(Path(db_path).expanduser().resolve())
        self.token = token or secrets.token_urlsafe(32)
        self.static_root = Path(static_root).resolve() if static_root else None


class HHS145APIHandler(BaseHTTPRequestHandler):
    server: HHS145APIServer
    protocol_version = "HTTP/1.1"
    max_request_bytes = 16 * 1024 * 1024

    def log_message(self, fmt: str, *args: Any) -> None:
        # Avoid secrets or document content in default logs.
        print(f"HHS145_API {self.client_address[0]} {fmt % args}")

    def _headers(self, status: int, length: int, content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()

    def _json(self, status: int, payload: Any) -> None:
        data = canonical_json(payload).encode("utf-8")
        self._headers(status, len(data))
        self.wfile.write(data)

    def _auth(self) -> bool:
        origin = self.headers.get("Origin")
        if origin and not (origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost") or origin.startswith("https://127.0.0.1") or origin.startswith("https://localhost")):
            self._json(HTTPStatus.FORBIDDEN, {"ok": False, "error_code": "CROSS_ORIGIN_REJECTED"})
            return False
        auth = self.headers.get("Authorization", "")
        if auth != f"Bearer {self.server.token}":
            self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error_code": "AUTHORITY_INSUFFICIENT"})
            return False
        return True

    def _body(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise Pass145Error("INGESTION_REJECTED", "invalid Content-Length", "API_REQUEST") from exc
        if length < 0 or length > self.max_request_bytes:
            raise Pass145Error("RESOURCE_BOUNDED", "API request size bound reached", "API_REQUEST")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise Pass145Error("INGESTION_REJECTED", f"invalid JSON request: {exc}", "API_REQUEST") from exc
        if not isinstance(value, dict):
            raise Pass145Error("INGESTION_REJECTED", "request body must be an object", "API_REQUEST")
        return value

    def _service(self) -> HHS145Service:
        return HHS145Service(self.server.db_path)

    def do_OPTIONS(self) -> None:
        self._json(HTTPStatus.METHOD_NOT_ALLOWED, {"ok": False, "error_code": "CROSS_ORIGIN_REJECTED"})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"} and self.server.static_root:
            return self._static("index.html")
        if parsed.path.startswith("/static/") and self.server.static_root:
            return self._static(parsed.path.removeprefix("/static/"))
        if not self._auth():
            return
        try:
            with self._service() as service:
                if parsed.path == "/api/v1/status" or parsed.path == "/api/v1/database/status":
                    return self._json(HTTPStatus.OK, service.status())
                if parsed.path.startswith("/api/v1/source/"):
                    obj = service.db.get_source(parsed.path.rsplit("/", 1)[-1])
                    return self._json(HTTPStatus.OK if obj else HTTPStatus.NOT_FOUND, obj or {"ok": False, "error_code": "NOT_FOUND"})
                if parsed.path.startswith("/api/v1/object/"):
                    obj = service.db.get_object(parsed.path.rsplit("/", 1)[-1])
                    return self._json(HTTPStatus.OK if obj else HTTPStatus.NOT_FOUND, obj or {"ok": False, "error_code": "NOT_FOUND"})
                if parsed.path.startswith("/api/v1/graph/"):
                    return self._json(HTTPStatus.OK, service.graph_trace(parsed.path.rsplit("/", 1)[-1]))
                if parsed.path.startswith("/api/v1/receipt/"):
                    obj = service.db.get_receipt(parsed.path.rsplit("/", 1)[-1])
                    return self._json(HTTPStatus.OK if obj else HTTPStatus.NOT_FOUND, obj or {"ok": False, "error_code": "NOT_FOUND"})
                if parsed.path.startswith("/api/v1/ingest/"):
                    obj = service.db.get_source(parsed.path.rsplit("/", 1)[-1])
                    return self._json(HTTPStatus.OK if obj else HTTPStatus.NOT_FOUND, obj or {"ok": False, "error_code": "NOT_FOUND"})
                return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
        except Pass145Error as exc:
            return self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
        except Exception as exc:
            return self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})

    def do_POST(self) -> None:
        if not self._auth():
            return
        try:
            body = self._body()
            parsed = urlparse(self.path)
            with self._service() as service:
                if parsed.path == "/api/v1/ingest":
                    if "path" in body:
                        result = service.ingest_path(body["path"], mime_type=body.get("mime_type"), namespace=body.get("namespace", "default"), analyze=body.get("analyze", True))
                    elif "content_base64" in body:
                        try:
                            raw = base64.b64decode(body["content_base64"], validate=True)
                        except Exception as exc:
                            raise Pass145Error("INGESTION_REJECTED", "invalid base64 source", "API_INGEST") from exc
                        result = service.ingest_bytes(raw, name=body.get("name", "api-input.txt"), mime_type=body.get("mime_type"), namespace=body.get("namespace", "default"), source_kind="LOCAL_API", acquisition={"method": "LOCAL_API"}, analyze=body.get("analyze", True))
                    elif "text" in body:
                        result = service.ingest_bytes(str(body["text"]).encode("utf-8"), name=body.get("name", "api-input.txt"), mime_type=body.get("mime_type", "text/plain"), namespace=body.get("namespace", "default"), source_kind="LOCAL_API", acquisition={"method": "LOCAL_API"}, analyze=body.get("analyze", True))
                    else:
                        raise Pass145Error("INGESTION_REJECTED", "path, text, or content_base64 required", "API_INGEST")
                    return self._json(HTTPStatus.CREATED, result)
                if parsed.path == "/api/v1/query":
                    return self._json(HTTPStatus.OK, service.query(str(body.get("question", "")), namespace=body.get("namespace"), limit=int(body.get("limit", 100))))
                if parsed.path == "/api/v1/search":
                    return self._json(HTTPStatus.OK, service.search(str(body.get("text", "")), symbol=bool(body.get("symbol", False)), object_type=body.get("object_type"), source_id=body.get("source_id"), namespace=body.get("namespace"), limit=int(body.get("limit", 100))))
                if parsed.path == "/api/v1/analyze":
                    op = body.get("operation")
                    if op == "changes":
                        result = service.analyze_changes(body["source_a"], body["source_b"])
                    elif op == "graph":
                        result = service.graph_trace(body["object_id"], max_depth=int(body.get("max_depth", 16)))
                    else:
                        raise Pass145Error("QUERY_PLAN_FAILED", "unsupported analysis operation", "API_ANALYZE")
                    return self._json(HTTPStatus.OK, result)
                if parsed.path == "/api/v1/validate":
                    target = body.get("target", "source")
                    if target == "source":
                        result = service.validate_source(body["id"])
                    elif target == "database":
                        result = service.db.integrity_check()
                    elif target == "receipt":
                        result = service.db.verify_receipt_chain()
                    else:
                        raise Pass145Error("QUERY_PLAN_FAILED", "unsupported validation target", "API_VALIDATE")
                    return self._json(HTTPStatus.OK, result)
                if parsed.path == "/api/v1/replay":
                    return self._json(HTTPStatus.OK, service.replay_ingestion(body["source_id"]))
                if parsed.path == "/api/v1/backup":
                    return self._json(HTTPStatus.CREATED, service.backup_create(body["path"]))
                if parsed.path == "/api/v1/restore/preview":
                    return self._json(HTTPStatus.OK, service.restore_preview(body["path"]))
                return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
        except Pass145Error as exc:
            return self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
        except Exception as exc:
            return self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})

    def _static(self, name: str) -> None:
        root = self.server.static_root
        assert root is not None
        path = (root / name).resolve()
        if root not in path.parents and path != root:
            return self._json(HTTPStatus.FORBIDDEN, {"ok": False, "error_code": "PATH_TRAVERSAL_REJECTED"})
        if not path.is_file():
            return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
        mime = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}.get(path.suffix, "application/octet-stream")
        data = path.read_bytes()
        self._headers(HTTPStatus.OK, len(data), mime)
        self.wfile.write(data)


def serve(db_path: str | Path, *, host: str = "127.0.0.1", port: int = 8765, token: str | None = None, static_root: str | Path | None = None) -> None:
    server = HHS145APIServer((host, port), db_path, token=token, static_root=static_root)
    print(canonical_json({"schema": "HHS_PASS145_API_START_V1", "url": f"http://{host}:{server.server_port}", "token": server.token, "loopback_only": True}))
    try:
        server.serve_forever()
    finally:
        server.server_close()
