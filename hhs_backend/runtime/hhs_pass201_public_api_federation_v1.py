"""Pass 201 public API federation and deterministic service/pass catalogs."""
from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.util
import json
import pkgutil
import re
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute, APIWebSocketRoute
from starlette.routing import BaseRoute, Mount, Route, WebSocketRoute

CONTRACT = "HHS-P201-PUBLIC-API-FEDERATION-SERVICE-PASS-ROUTER-OPENAPI"
CLASSIFICATION = "HHS_PASS_201_PUBLIC_API_FEDERATION_VERIFIED"
VERSION = "PASS_201_PUBLIC_API_FEDERATION_V1"
PASS_MODULE_PATTERN = re.compile(r"(?:^|[._-])(?:hhs_)?pass[_-]?(\d{1,4}[a-z]?)(?:[._-]|$)", re.IGNORECASE)
PUBLIC_API_PREFIX = "/api/public"


class Pass201Error(RuntimeError):
    """Raised when public API federation invariants are violated."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _route_methods(route: BaseRoute) -> Tuple[str, ...]:
    methods = getattr(route, "methods", None)
    if methods:
        return tuple(sorted(str(method) for method in methods))
    if isinstance(route, (APIWebSocketRoute, WebSocketRoute)):
        return ("WEBSOCKET",)
    if isinstance(route, Mount):
        return ("MOUNT",)
    return tuple()


def _route_signature(route: BaseRoute) -> Tuple[str, str, Tuple[str, ...]]:
    return (
        route.__class__.__name__,
        str(getattr(route, "path", "")),
        _route_methods(route),
    )


def _endpoint_module(route: BaseRoute) -> str:
    endpoint = getattr(route, "endpoint", None)
    return str(getattr(endpoint, "__module__", ""))


def _pass_identifier(*values: str) -> str | None:
    for value in values:
        match = PASS_MODULE_PATTERN.search(str(value or ""))
        if match:
            return f"pass{match.group(1).lower()}"
    return None


def _service_identifier(path: str, tags: Sequence[str]) -> str:
    parts = [part for part in path.strip("/").split("/") if part and not part.startswith("{")]
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "runtime":
        if parts[2] == "content-engine" and len(parts) >= 4:
            return f"runtime.content-engine.{parts[3]}"
        return f"runtime.{parts[2]}"
    if len(parts) >= 3 and parts[0] == "api" and parts[1].startswith("v"):
        return f"{parts[1]}.{parts[2]}"
    if len(parts) >= 2 and parts[0] == "api":
        return parts[1]
    if path.startswith("/health"):
        return "system.health"
    if path in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
        return "system.openapi"
    if tags:
        return str(tags[0]).strip().lower().replace(" ", "-") or "system"
    return "system"


def _literal_assignment(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return None


class PublicAPIFederation:
    """Discovers API routers, attaches missing routes, and publishes catalogs."""

    def __init__(self) -> None:
        self.registration_report: Dict[str, Any] = {
            "schema": "HHS_PASS_201_ROUTER_REGISTRATION_REPORT_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "closed": False,
            "registration_started": False,
        }
        self._pass_cache: List[Dict[str, Any]] | None = None

    @staticmethod
    def _iter_module_names(package_name: str) -> List[str]:
        package = importlib.import_module(package_name)
        paths = getattr(package, "__path__", None)
        if not paths:
            return []
        return sorted(
            info.name
            for info in pkgutil.walk_packages(paths, prefix=f"{package_name}.")
            if not info.name.rsplit(".", 1)[-1].startswith("_")
        )

    @staticmethod
    def _module_routers(module: ModuleType) -> List[Tuple[str, APIRouter]]:
        routers: List[Tuple[str, APIRouter]] = []
        seen: set[int] = set()
        for name, value in sorted(vars(module).items()):
            if isinstance(value, APIRouter) and id(value) not in seen:
                seen.add(id(value))
                routers.append((name, value))
        return routers

    def register_all_api_routers(self, app: FastAPI) -> Dict[str, Any]:
        module_names = self._iter_module_names("hhs_backend.api")
        existing_signatures = {_route_signature(route) for route in app.router.routes}
        module_records: List[Dict[str, Any]] = []
        import_failures: List[Dict[str, str]] = []
        router_count = 0
        discovered_route_count = 0
        attached_route_count = 0
        duplicate_route_count = 0
        discovered_signatures: set[Tuple[str, str, Tuple[str, ...]]] = set()

        for module_name in module_names:
            record: Dict[str, Any] = {
                "module": module_name,
                "imported": False,
                "routers": [],
                "error": None,
            }
            try:
                module = importlib.import_module(module_name)
                record["imported"] = True
            except Exception as exc:  # fail-closed report; production validation decides closure
                record["error"] = f"{exc.__class__.__name__}: {exc}"
                import_failures.append({"module": module_name, "error": record["error"]})
                module_records.append(record)
                continue

            for variable_name, router in self._module_routers(module):
                router_count += 1
                router_record = {
                    "variable": variable_name,
                    "prefix": str(getattr(router, "prefix", "")),
                    "route_count": len(router.routes),
                    "attached": 0,
                    "duplicates": 0,
                }
                for route in router.routes:
                    signature = _route_signature(route)
                    discovered_signatures.add(signature)
                    discovered_route_count += 1
                    if signature in existing_signatures:
                        duplicate_route_count += 1
                        router_record["duplicates"] += 1
                        continue
                    app.router.routes.append(route)
                    existing_signatures.add(signature)
                    attached_route_count += 1
                    router_record["attached"] += 1
                record["routers"].append(router_record)
            module_records.append(record)

        final_signatures = {_route_signature(route) for route in app.router.routes}
        unexposed = sorted(
            {
                "route_type": signature[0],
                "path": signature[1],
                "methods": list(signature[2]),
            }
            for signature in discovered_signatures
            if signature not in final_signatures
        )
        app.openapi_schema = None
        self.registration_report = {
            "schema": "HHS_PASS_201_ROUTER_REGISTRATION_REPORT_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "registration_started": True,
            "api_module_count": len(module_names),
            "imported_module_count": sum(1 for record in module_records if record["imported"]),
            "import_failure_count": len(import_failures),
            "router_count": router_count,
            "discovered_router_route_count": discovered_route_count,
            "attached_route_count": attached_route_count,
            "duplicate_route_count": duplicate_route_count,
            "unexposed_route_count": len(unexposed),
            "import_failures": import_failures,
            "unexposed_routes": unexposed,
            "modules": module_records,
            "closed": len(import_failures) == 0 and len(unexposed) == 0,
        }
        self.registration_report["report_sha256"] = _digest(self.registration_report)
        app.state.hhs_public_api_federation = self
        app.state.hhs_public_api_registration = self.registration_report
        return self.registration_report

    @staticmethod
    def route_catalog(app: FastAPI) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for route in app.router.routes:
            path = str(getattr(route, "path", ""))
            methods = list(_route_methods(route))
            endpoint_module = _endpoint_module(route)
            tags = sorted(str(tag) for tag in (getattr(route, "tags", None) or []))
            identity = {
                "route_type": route.__class__.__name__,
                "path": path,
                "methods": methods,
                "name": str(getattr(route, "name", "")),
                "endpoint_module": endpoint_module,
            }
            records.append(
                {
                    "route_id": _digest(identity),
                    **identity,
                    "tags": tags,
                    "include_in_schema": bool(getattr(route, "include_in_schema", False)),
                    "service_id": _service_identifier(path, tags),
                    "pass_id": _pass_identifier(endpoint_module, path, identity["name"]),
                    "public_path": path,
                }
            )
        return sorted(records, key=lambda item: (item["path"], item["methods"], item["route_type"], item["name"]))

    def service_catalog(self, app: FastAPI) -> List[Dict[str, Any]]:
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for route in self.route_catalog(app):
            grouped[route["service_id"]].append(route)
        services: List[Dict[str, Any]] = []
        for service_id, routes in sorted(grouped.items()):
            services.append(
                {
                    "service_id": service_id,
                    "display_name": service_id.replace(".", " / "),
                    "public_api_available": True,
                    "route_count": len(routes),
                    "route_ids": [route["route_id"] for route in routes],
                    "paths": sorted({route["path"] for route in routes}),
                    "methods": sorted({method for route in routes for method in route["methods"]}),
                    "endpoint_modules": sorted({route["endpoint_module"] for route in routes if route["endpoint_module"]}),
                    "pass_ids": sorted({route["pass_id"] for route in routes if route["pass_id"]}),
                    "detail_path": f"{PUBLIC_API_PREFIX}/services/{service_id}",
                }
            )
        return services

    @staticmethod
    def _module_static_metadata(module_name: str) -> Dict[str, Any]:
        record: Dict[str, Any] = {
            "module_name": module_name,
            "import_status": "NOT_IMPORTED_FOR_CATALOG",
            "contract": None,
            "classification": None,
            "version": None,
            "public_exports": [],
            "source_available": False,
        }
        spec = importlib.util.find_spec(module_name)
        origin = getattr(spec, "origin", None) if spec else None
        if not origin or not origin.endswith(".py"):
            return record
        path = Path(origin)
        if not path.is_file():
            return record
        record["source_available"] = True
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as exc:
            record["metadata_error"] = f"{exc.__class__.__name__}: {exc}"
            return record
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets: List[ast.expr]
                value_node: ast.AST | None
                if isinstance(node, ast.Assign):
                    targets = list(node.targets)
                    value_node = node.value
                else:
                    targets = [node.target]
                    value_node = node.value
                if value_node is None:
                    continue
                value = _literal_assignment(value_node)
                for target in targets:
                    if not isinstance(target, ast.Name):
                        continue
                    if target.id in {"CONTRACT", "CONTRACT_ID", "CONTRACT_IDENTIFIER"} and isinstance(value, str):
                        record["contract"] = value
                    elif target.id in {"CLASSIFICATION", "CLASSIFICATION_TARGET"} and isinstance(value, str):
                        record["classification"] = value
                    elif target.id in {"VERSION", "CONTRACT_VERSION"} and isinstance(value, (str, int)):
                        record["version"] = str(value)
                    elif target.id == "__all__" and isinstance(value, (list, tuple)):
                        record["public_exports"] = sorted(str(item) for item in value if isinstance(item, str))
        return record

    def pass_catalog(self, app: FastAPI) -> List[Dict[str, Any]]:
        if self._pass_cache is None:
            module_names: set[str] = set()
            for package_name in ("hhs_backend.runtime", "hhs_backend.api"):
                for module_name in self._iter_module_names(package_name):
                    if _pass_identifier(module_name):
                        module_names.add(module_name)
            self._pass_cache = []
            for module_name in sorted(module_names):
                metadata = self._module_static_metadata(module_name)
                metadata.update(
                    {
                        "pass_id": _pass_identifier(module_name),
                        "module_family": module_name.rsplit(".", 2)[-2] if "." in module_name else "root",
                        "detail_path": f"{PUBLIC_API_PREFIX}/passes/{module_name}",
                    }
                )
                self._pass_cache.append(metadata)
        routes = self.route_catalog(app)
        result: List[Dict[str, Any]] = []
        for cached in self._pass_cache:
            item = dict(cached)
            pass_id = item["pass_id"]
            associated = [
                route for route in routes
                if route["pass_id"] == pass_id
                or route["endpoint_module"] == item["module_name"]
                or route["endpoint_module"].startswith(f"{item['module_name']}.")
            ]
            item["associated_route_count"] = len(associated)
            item["associated_route_ids"] = [route["route_id"] for route in associated]
            item["native_public_paths"] = sorted({route["path"] for route in associated})
            item["public_api_available"] = True
            result.append(item)
        return result

    @staticmethod
    def _openapi_missing(app: FastAPI, routes: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        schema = app.openapi()
        paths = schema.get("paths", {}) if isinstance(schema, dict) else {}
        missing: List[Dict[str, Any]] = []
        for route in routes:
            if not route["include_in_schema"] or "WEBSOCKET" in route["methods"] or "MOUNT" in route["methods"]:
                continue
            schema_path = paths.get(route["path"], {})
            for method in route["methods"]:
                if method in {"HEAD", "OPTIONS"}:
                    continue
                if method.lower() not in schema_path:
                    missing.append({"route_id": route["route_id"], "path": route["path"], "method": method})
        return missing

    def catalog(self, app: FastAPI) -> Dict[str, Any]:
        routes = self.route_catalog(app)
        services = self.service_catalog(app)
        passes = self.pass_catalog(app)
        openapi_missing = self._openapi_missing(app, routes)
        registration = dict(self.registration_report)
        closed = bool(registration.get("closed")) and not openapi_missing
        payload = {
            "schema": "HHS_PASS_201_PUBLIC_API_CATALOG_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "closed": closed,
            "route_count": len(routes),
            "service_count": len(services),
            "pass_module_count": len(passes),
            "openapi_path_count": len(app.openapi().get("paths", {})),
            "openapi_missing_count": len(openapi_missing),
            "openapi_missing": openapi_missing,
            "registration": registration,
            "routes": routes,
            "services": services,
            "passes": passes,
            "documentation": {
                "openapi": "/openapi.json",
                "swagger": "/docs",
                "redoc": "/redoc",
                "federated_openapi": f"{PUBLIC_API_PREFIX}/openapi",
            },
            "claim_boundary": {
                "all_registered_routers_public": registration.get("unexposed_route_count", 1) == 0,
                "pass_metadata_public": True,
                "arbitrary_python_execution_public": False,
                "native_authority_routes_preserved": True,
            },
        }
        payload["catalog_sha256"] = _digest(payload)
        return payload

    def status(self, app: FastAPI) -> Dict[str, Any]:
        catalog = self.catalog(app)
        return {
            key: catalog[key]
            for key in (
                "schema", "contract", "classification", "closed", "route_count",
                "service_count", "pass_module_count", "openapi_path_count",
                "openapi_missing_count", "catalog_sha256", "documentation", "claim_boundary",
            )
        } | {"registration": catalog["registration"]}


PASS201_PUBLIC_API_FEDERATION = PublicAPIFederation()


def register_public_api_federation(app: FastAPI) -> Dict[str, Any]:
    return PASS201_PUBLIC_API_FEDERATION.register_all_api_routers(app)
