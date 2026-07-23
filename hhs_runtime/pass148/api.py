from __future__ import annotations

import secrets
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from hhs_runtime.pass145.canonical import canonical_json
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass147.api import HHS147PublicHandler
from .service import HHS148Service


class HHS148SemanticServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int], db_path: str | Path, *, token: str | None = None, identity_id: str | None = None, grant_id: str | None = None, identity_token: str | None = None):
        if address[0] not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Pass 148 semantic API binds to loopback only")
        super().__init__(address, HHS148SemanticHandler)
        self.db_path = Path(db_path).expanduser().resolve()
        self.token = token or secrets.token_urlsafe(32)
        self.identity_id = identity_id
        self.grant_id = grant_id
        self.identity_token = identity_token


class HHS148SemanticHandler(HHS147PublicHandler):
    server: HHS148SemanticServer

    def _semantic(self, service: HHS148Service, operation: str, request: dict[str, Any], *, explicit_credentials: bool = False) -> Any:
        if explicit_credentials:
            identity = str(request.pop("identity_id", "")); grant = str(request.pop("grant_id", "")); token = str(request.pop("identity_token", ""))
        else:
            identity = str(self.server.identity_id or ""); grant = str(self.server.grant_id or ""); token = str(self.server.identity_token or "")
        if not (identity and grant and token):
            raise Pass145Error("IDENTITY_UNRESOLVED", "semantic API has no admitted identity", "SEMANTIC_API")
        built = service.security.construct_path(identity, grant, token, operation, request)
        closed = service.security.execute_path(built["result"]["contract_id"], identity, token)
        return closed["result"]["result"]

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        prefix = "/api/v1/semantic-membrane/"
        if not path.startswith(prefix):
            return super().do_GET()
        if not self._auth(): return
        try:
            with HHS148Service(self.server.db_path) as service:
                if path.startswith(prefix + "propositions/"):
                    return self._json(HTTPStatus.OK, self._semantic(service, "SEMANTIC_RETRIEVE", {"kind": "proposition", "target_id": path.rsplit("/", 1)[-1]}))
                if path.startswith(prefix + "derivations/"):
                    return self._json(HTTPStatus.OK, self._semantic(service, "SEMANTIC_RETRIEVE", {"kind": "derivation", "target_id": path.rsplit("/", 1)[-1]}))
                if path.startswith(prefix + "rules/"):
                    return self._json(HTTPStatus.OK, self._semantic(service, "SEMANTIC_RULE_READ", {"rule_id": path.rsplit("/", 1)[-1]}))
                if path == prefix + "audit":
                    return self._json(HTTPStatus.OK, self._semantic(service, "SEMANTIC_AUDIT", {"dependency_scope": "pass148"}))
                return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
        except Pass145Error as exc:
            self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        prefix = "/api/v1/semantic-membrane/"
        if path == "/api/v1/public/agent/execute":
            if not self._auth(): return
            try:
                body = self._body()
                with HHS148Service(self.server.db_path) as service:
                    result = service.external_execute(str(body["identity_id"]), str(body["grant_id"]), str(body["identity_token"]), [str(x) for x in body.get("argv", [])], stdin_text=body.get("stdin_text"))
                    return self._json(HTTPStatus.OK, result)
            except Pass145Error as exc:
                return self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
            except Exception as exc:
                return self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})
        if not path.startswith(prefix):
            return super().do_POST()
        if not self._auth(): return
        try:
            body = self._body()
            with HHS148Service(self.server.db_path) as service:
                if path == prefix + "analyze": operation = "SEMANTIC_ANALYZE"; request = {"expression": str(body.get("expression", "")), "source_type": str(body.get("source_type", "model_output")), "source_reference": str(body.get("source_reference", "API_SUBMISSION")), "profile_id": str(body.get("requested_operator_profile", body.get("profile_id", "HHS_NATIVE_TYPED_V1"))), "declared_scope": dict(body.get("declared_scope", {})), "governing_contracts": list(body.get("governing_contracts", []))}
                elif path == prefix + "documents/analyze": operation = "SEMANTIC_DOCUMENT_ANALYZE"; request = {"text": str(body.get("text", "")), "name": str(body.get("name", "semantic-document.md")), "source_type": str(body.get("source_type", "documentation")), "source_reference": str(body.get("source_reference", "API_DOCUMENT")), "profile_id": str(body.get("profile_id", "HHS_NATIVE_TYPED_V1")), "governing_contracts": list(body.get("governing_contracts", []))}
                elif path == prefix + "derive": operation = "SEMANTIC_DERIVE"; request = {"proposition_ids": list(body.get("proposition_ids", [])), "rule_id": str(body.get("rule_id", "")), "substitutions": dict(body.get("substitutions", {}))}
                elif path == prefix + "project": operation = "SEMANTIC_PROJECT"; request = {"expression": str(body.get("expression", "")), "profile_id": str(body.get("profile_id", "")), "assumptions": list(body.get("assumptions", []))}
                elif path == prefix + "promotions/request": operation = "SEMANTIC_PROMOTION_REQUEST"; request = {"proposition_id": str(body.get("source_proposition_id", "")), "target_class": str(body.get("target_class", "")), "governing_rule": str(body.get("governing_rule", "")), "dependency_set": list(body.get("dependency_set", [])), "scope": dict(body.get("scope", {}))}
                elif path == prefix + "promotions/evaluate":
                    operation = "SEMANTIC_PROMOTION_EVALUATE"; request = dict(body)
                    return self._json(HTTPStatus.OK, self._semantic(service, operation, request, explicit_credentials=True))
                elif path == prefix + "replay": operation = "SEMANTIC_REPLAY"; request = {"target_id": str(body.get("target_id", body.get("receipt_id", "")))}
                elif path == prefix + "registry/sync":
                    operation = "SEMANTIC_REGISTRY_SYNC"; request = dict(body)
                    return self._json(HTTPStatus.OK, self._semantic(service, operation, request, explicit_credentials=True))
                else: return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error_code": "NOT_FOUND"})
                return self._json(HTTPStatus.OK, self._semantic(service, operation, request))
        except Pass145Error as exc:
            self._json(HTTPStatus.BAD_REQUEST, exc.to_dict())
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error_code": "API_INTERNAL_ERROR", "description": str(exc)})


def serve(db_path: str | Path, *, host: str = "127.0.0.1", port: int = 8878, token: str | None = None, identity_id: str | None = None, grant_id: str | None = None, identity_token: str | None = None) -> None:
    server = HHS148SemanticServer((host, port), db_path, token=token, identity_id=identity_id, grant_id=grant_id, identity_token=identity_token)
    print(canonical_json({"schema": "HHS_PASS148_SEMANTIC_API_START_V1", "url": f"http://{host}:{server.server_port}", "token": server.token, "loopback_only": True, "privileged_semantic_authority": 0}))
    try: server.serve_forever()
    finally: server.server_close()
