"""Pass 220 FastAPI1 native C11 route-kernel ASGI compatibility membrane."""
from __future__ import annotations

import ctypes
import inspect
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Mapping

SCHEMA = "HHS_PASS_220_FASTAPI1_NATIVE_ASGI_COMPAT_V1"
MAX_ROUTES = 512
MAX_PATH_BYTES = 384
MAX_CAPTURE_BYTES = 1024

METHOD_CODE = {
    "GET": 1,
    "POST": 2,
    "PUT": 3,
    "PATCH": 4,
    "DELETE": 5,
    "OPTIONS": 6,
    "HEAD": 7,
    "WEBSOCKET": 8,
}

OK = 0
ERR_NOT_FOUND = 5


class NativeFastAPICompatibilityError(RuntimeError):
    pass


class _Route(ctypes.Structure):
    _fields_ = [
        ("method", ctypes.c_uint32),
        ("handler_id", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
        ("path", ctypes.c_char * MAX_PATH_BYTES),
    ]


class _Registry(ctypes.Structure):
    _fields_ = [
        ("version", ctypes.c_uint32),
        ("route_count", ctypes.c_uint32),
        ("routes", _Route * MAX_ROUTES),
    ]


class _Resolution(ctypes.Structure):
    _fields_ = [
        ("matched", ctypes.c_uint32),
        ("route_index", ctypes.c_uint32),
        ("handler_id", ctypes.c_uint32),
        ("capture_bytes", ctypes.c_uint32),
        ("captures", ctypes.c_char * MAX_CAPTURE_BYTES),
    ]


@dataclass(frozen=True)
class NativeRouteResolution:
    handler_id: int
    route_index: int
    captures: Mapping[str, str]


class NativeRouteKernel:
    def __init__(self, library_path: str | Path):
        self.library_path = str(Path(library_path))
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.hhs_fastapi_native_route_kernel_version.restype = ctypes.c_uint32
        self._lib.hhs_fastapi_native_registry_init.argtypes = [
            ctypes.POINTER(_Registry)
        ]
        self._lib.hhs_fastapi_native_registry_init.restype = ctypes.c_int
        self._lib.hhs_fastapi_native_register.argtypes = [
            ctypes.POINTER(_Registry),
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self._lib.hhs_fastapi_native_register.restype = ctypes.c_int
        self._lib.hhs_fastapi_native_resolve.argtypes = [
            ctypes.POINTER(_Registry),
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.POINTER(_Resolution),
        ]
        self._lib.hhs_fastapi_native_resolve.restype = ctypes.c_int
        self._lib.hhs_fastapi_native_registry_fingerprint.argtypes = [
            ctypes.POINTER(_Registry)
        ]
        self._lib.hhs_fastapi_native_registry_fingerprint.restype = ctypes.c_uint64

        if int(self._lib.hhs_fastapi_native_route_kernel_version()) != 1:
            raise NativeFastAPICompatibilityError(
                "HHS_FASTAPI_NATIVE_ROUTE_KERNEL_VERSION_MISMATCH"
            )
        self._registry = _Registry()
        status = int(
            self._lib.hhs_fastapi_native_registry_init(
                ctypes.byref(self._registry)
            )
        )
        if status != OK:
            raise NativeFastAPICompatibilityError(
                f"HHS_FASTAPI_NATIVE_REGISTRY_INIT_FAILED:{status}"
            )

    @property
    def route_count(self) -> int:
        return int(self._registry.route_count)

    @property
    def fingerprint(self) -> int:
        return int(
            self._lib.hhs_fastapi_native_registry_fingerprint(
                ctypes.byref(self._registry)
            )
        )

    def register(
        self,
        method: str,
        path: str,
        handler_id: int,
        *,
        flags: int = 0,
    ) -> None:
        method_name = str(method).upper()
        if method_name not in METHOD_CODE:
            raise NativeFastAPICompatibilityError(
                f"HHS_FASTAPI_NATIVE_METHOD_UNSUPPORTED:{method_name}"
            )
        status = int(
            self._lib.hhs_fastapi_native_register(
                ctypes.byref(self._registry),
                METHOD_CODE[method_name],
                path.encode("utf-8"),
                int(handler_id),
                int(flags),
            )
        )
        if status != OK:
            raise NativeFastAPICompatibilityError(
                f"HHS_FASTAPI_NATIVE_ROUTE_REGISTER_FAILED:{status}:{method_name}:{path}"
            )

    def resolve(self, method: str, path: str) -> NativeRouteResolution | None:
        method_name = str(method).upper()
        code = METHOD_CODE.get(method_name)
        if code is None:
            return None
        out = _Resolution()
        status = int(
            self._lib.hhs_fastapi_native_resolve(
                ctypes.byref(self._registry),
                code,
                str(path).encode("utf-8"),
                ctypes.byref(out),
            )
        )
        if status == ERR_NOT_FOUND:
            return None
        if status != OK or not out.matched:
            raise NativeFastAPICompatibilityError(
                f"HHS_FASTAPI_NATIVE_ROUTE_RESOLVE_FAILED:{status}:{method_name}:{path}"
            )
        captures: Dict[str, str] = {}
        raw = bytes(out.captures[: int(out.capture_bytes)]).decode(
            "utf-8", errors="strict"
        )
        for row in raw.splitlines():
            if "=" in row:
                key, value = row.split("=", 1)
                captures[key] = value
        return NativeRouteResolution(
            handler_id=int(out.handler_id),
            route_index=int(out.route_index),
            captures=captures,
        )


Handler = Callable[..., Any] | Callable[..., Awaitable[Any]]


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


class HHSNativeASGIApplication:
    """Minimal FastAPI-compatible ASGI ingress/egress around native routing."""

    def __init__(self, *, kernel: NativeRouteKernel):
        self.kernel = kernel
        self._handlers: Dict[int, Handler] = {}
        self._next_handler_id = 1

    def add_api_route(
        self,
        path: str,
        handler: Handler,
        *,
        methods: tuple[str, ...] = ("GET",),
    ) -> int:
        handler_id = self._next_handler_id
        self._next_handler_id += 1
        self._handlers[handler_id] = handler
        for method in methods:
            self.kernel.register(method, path, handler_id)
        return handler_id

    def route(
        self,
        path: str,
        *,
        methods: tuple[str, ...],
    ):
        def decorator(handler: Handler) -> Handler:
            self.add_api_route(path, handler, methods=methods)
            return handler
        return decorator

    def get(self, path: str):
        return self.route(path, methods=("GET",))

    def post(self, path: str):
        return self.route(path, methods=("POST",))

    def put(self, path: str):
        return self.route(path, methods=("PUT",))

    def patch(self, path: str):
        return self.route(path, methods=("PATCH",))

    def delete(self, path: str):
        return self.route(path, methods=("DELETE",))

    async def _invoke(
        self,
        handler: Handler,
        captures: Mapping[str, str],
    ) -> Any:
        value = handler(**dict(captures))
        if inspect.isawaitable(value):
            return await value
        return value

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") != "http":
            raise NativeFastAPICompatibilityError(
                "HHS_FASTAPI_NATIVE_ASGI_HTTP_ONLY_V1"
            )

        method = str(scope.get("method") or "GET").upper()
        path = str(scope.get("path") or "/")
        resolution = self.kernel.resolve(method, path)

        if resolution is None:
            allowed: list[str] = []
            for candidate in (
                "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"
            ):
                if candidate == method:
                    continue
                if self.kernel.resolve(candidate, path) is not None:
                    allowed.append(candidate)
            if allowed:
                body = _json_bytes({"detail": "Method Not Allowed"})
                headers = [
                    (b"allow", ", ".join(allowed).encode("ascii")),
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"content-type", b"application/json"),
                ]
                await send(
                    {
                        "type": "http.response.start",
                        "status": 405,
                        "headers": headers,
                    }
                )
                await send({"type": "http.response.body", "body": body})
                return

            body = _json_bytes({"detail": "Not Found"})
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [
                        (b"content-length", str(len(body)).encode("ascii")),
                        (b"content-type", b"application/json"),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        handler = self._handlers.get(resolution.handler_id)
        if handler is None:
            raise NativeFastAPICompatibilityError(
                "HHS_FASTAPI_NATIVE_HANDLER_BINDING_MISSING"
            )

        try:
            value = await self._invoke(handler, resolution.captures)
            status = 200
        except Exception as exc:
            value = {"detail": "Internal Server Error"}
            status = 500
            # The compatibility membrane does not expose exception internals.
            _ = exc

        body = _json_bytes(value)
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"content-type", b"application/json"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


@dataclass(frozen=True)
class NativeAPIRoute:
    """Deferred FastAPI-compatible route declaration for native-first imports."""

    path: str
    endpoint: Handler
    methods: frozenset[str]
    name: str
    tags: tuple[str, ...]
    include_in_schema: bool = True

    @property
    def route_type(self) -> str:
        return "WEBSOCKET" if "WEBSOCKET" in self.methods else "HTTP"


class NativeAPIRouter:
    """Minimal APIRouter-compatible declaration surface.

    This object is intentionally a registration membrane, not an execution
    authority. Native execution remains owned by NativeRouteKernel /
    HHSNativeASGIApplication when a route family is bound for ASGI service.
    """

    def __init__(
        self,
        *,
        prefix: str = "",
        tags: list[str] | tuple[str, ...] | None = None,
        **_: Any,
    ) -> None:
        self.prefix = str(prefix)
        self.tags = tuple(tags or ())
        self.routes: list[NativeAPIRoute] = []

    def _path(self, path: str) -> str:
        path_value = str(path)
        if not self.prefix:
            return path_value
        if not path_value:
            return self.prefix
        return self.prefix.rstrip("/") + "/" + path_value.lstrip("/")

    def add_api_route(
        self,
        path: str,
        endpoint: Handler,
        *,
        methods: list[str] | tuple[str, ...] | set[str] | frozenset[str] | None = None,
        name: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        include_in_schema: bool = True,
        **_: Any,
    ) -> None:
        method_set = frozenset(
            str(method).upper() for method in (methods or ("GET",))
        )
        self.routes.append(
            NativeAPIRoute(
                path=self._path(path),
                endpoint=endpoint,
                methods=method_set,
                name=str(name or getattr(endpoint, "__name__", "native_route")),
                tags=tuple(self.tags) + tuple(tags or ()),
                include_in_schema=bool(include_in_schema),
            )
        )

    def api_route(
        self,
        path: str,
        *,
        methods: list[str] | tuple[str, ...] | set[str] | frozenset[str] | None = None,
        **kwargs: Any,
    ):
        def decorator(endpoint: Handler) -> Handler:
            self.add_api_route(path, endpoint, methods=methods, **kwargs)
            return endpoint
        return decorator

    def get(self, path: str, **kwargs: Any):
        return self.api_route(path, methods=("GET",), **kwargs)

    def post(self, path: str, **kwargs: Any):
        return self.api_route(path, methods=("POST",), **kwargs)

    def put(self, path: str, **kwargs: Any):
        return self.api_route(path, methods=("PUT",), **kwargs)

    def patch(self, path: str, **kwargs: Any):
        return self.api_route(path, methods=("PATCH",), **kwargs)

    def delete(self, path: str, **kwargs: Any):
        return self.api_route(path, methods=("DELETE",), **kwargs)

    def options(self, path: str, **kwargs: Any):
        return self.api_route(path, methods=("OPTIONS",), **kwargs)

    def head(self, path: str, **kwargs: Any):
        return self.api_route(path, methods=("HEAD",), **kwargs)

    def websocket(self, path: str, **kwargs: Any):
        return self.api_route(
            path,
            methods=("WEBSOCKET",),
            include_in_schema=False,
            **kwargs,
        )

    def include_router(
        self,
        router: "NativeAPIRouter",
        *,
        prefix: str = "",
        tags: list[str] | tuple[str, ...] | None = None,
        **_: Any,
    ) -> None:
        extra_prefix = str(prefix)
        extra_tags = tuple(tags or ())
        for route in router.routes:
            path = route.path
            if extra_prefix:
                path = extra_prefix.rstrip("/") + "/" + path.lstrip("/")
            self.routes.append(
                NativeAPIRoute(
                    path=self._path(path),
                    endpoint=route.endpoint,
                    methods=route.methods,
                    name=route.name,
                    tags=tuple(self.tags) + extra_tags + tuple(route.tags),
                    include_in_schema=route.include_in_schema,
                )
            )


def bind_native_router_to_external_app(\n    app: Any,\n    router: NativeAPIRouter,\n    *,\n    external_websocket_type: Any = None,\n) -> int:
    """Project deferred native route declarations into an external ASGI app.

    The native router remains the declaration authority. This boundary adapter
    is used only when the canonical external FastAPI server composes routes
    after the Lane 5 provider module has already been resolved in native mode.
    """

    if not isinstance(router, NativeAPIRouter):
        raise NativeFastAPICompatibilityError(
            "HHS_FASTAPI_NATIVE_ROUTER_BINDING_TYPE_MISMATCH"
        )

    bound = 0
    for route in router.routes:
        if route.route_type == "WEBSOCKET":
            add_websocket = getattr(app, "add_api_websocket_route", None)
            if add_websocket is None:
                raise NativeFastAPICompatibilityError(
                    "HHS_FASTAPI_EXTERNAL_WEBSOCKET_BINDING_UNAVAILABLE"
                )

            projected_endpoint = route.endpoint
            # External framework types are supplied by the canonical server
            # boundary; native compatibility code remains dependency-free.
            ExternalWebSocket = external_websocket_type

            if ExternalWebSocket is not None:
                endpoint = route.endpoint

                async def projected_endpoint(*args: Any, __endpoint=endpoint, **kwargs: Any):
                    value = __endpoint(*args, **kwargs)
                    if inspect.isawaitable(value):
                        return await value
                    return value

                signature = inspect.signature(endpoint)
                projected_parameters = []
                for parameter in signature.parameters.values():
                    annotation = parameter.annotation
                    if (
                        annotation is NativeWebSocket
                        or annotation == "WebSocket"
                        or annotation == "NativeWebSocket"
                    ):
                        annotation = ExternalWebSocket
                    projected_parameters.append(
                        parameter.replace(annotation=annotation)
                    )
                projected_endpoint.__signature__ = signature.replace(
                    parameters=projected_parameters
                )
                projected_endpoint.__name__ = getattr(
                    endpoint, "__name__", route.name
                )
                projected_endpoint.__qualname__ = getattr(
                    endpoint, "__qualname__", projected_endpoint.__name__
                )

            add_websocket(route.path, projected_endpoint, name=route.name)
        else:
            add_http = getattr(app, "add_api_route", None)
            if add_http is None:
                raise NativeFastAPICompatibilityError(
                    "HHS_FASTAPI_EXTERNAL_HTTP_BINDING_UNAVAILABLE"
                )
            add_http(
                route.path,
                route.endpoint,
                methods=sorted(route.methods),
                name=route.name,
                tags=list(route.tags),
                include_in_schema=route.include_in_schema,
            )
        bound += 1
    return bound


class NativeHTTPException(Exception):
    """FastAPI HTTPException-compatible data carrier for native-only imports."""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(str(detail))
        self.status_code = int(status_code)
        self.detail = detail
        self.headers = dict(headers or {})


class NativeBaseModel:
    """Minimal Pydantic BaseModel-compatible constructor for native-only paths."""

    def __init__(self, **data: Any) -> None:
        annotations: dict[str, Any] = {}
        for cls in reversed(type(self).__mro__):
            annotations.update(getattr(cls, "__annotations__", {}))
        for field_name in annotations:
            if field_name in data:
                value = data[field_name]
            elif hasattr(type(self), field_name):
                value = getattr(type(self), field_name)
            else:
                raise TypeError(f"missing required field: {field_name}")
            setattr(self, field_name, value)
        unknown = set(data) - set(annotations)
        if unknown:
            raise TypeError(f"unexpected fields: {sorted(unknown)!r}")

    def model_dump(self) -> dict[str, Any]:
        annotations: dict[str, Any] = {}
        for cls in reversed(type(self).__mro__):
            annotations.update(getattr(cls, "__annotations__", {}))
        return {name: getattr(self, name) for name in annotations}


class NativeWebSocket:
    """Structural WebSocket compatibility type for native-first route modules."""

    async def accept(self, *args: Any, **kwargs: Any) -> None:
        raise NativeFastAPICompatibilityError(
            "HHS_NATIVE_WEBSOCKET_TRANSPORT_NOT_BOUND"
        )

    async def receive_text(self) -> str:
        raise NativeFastAPICompatibilityError(
            "HHS_NATIVE_WEBSOCKET_TRANSPORT_NOT_BOUND"
        )

    async def send_text(self, data: str) -> None:
        _ = data
        raise NativeFastAPICompatibilityError(
            "HHS_NATIVE_WEBSOCKET_TRANSPORT_NOT_BOUND"
        )

    async def close(self, *args: Any, **kwargs: Any) -> None:
        raise NativeFastAPICompatibilityError(
            "HHS_NATIVE_WEBSOCKET_TRANSPORT_NOT_BOUND"
        )


class NativeWebSocketDisconnect(Exception):
    def __init__(self, code: int = 1000, reason: str | None = None) -> None:
        super().__init__(reason or f"WebSocket disconnected ({code})")
        self.code = int(code)
        self.reason = reason


def native_fastapi_compatibility_contract(kernel: NativeRouteKernel) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "native_route_kernel_version": 1,
        "route_count": kernel.route_count,
        "route_registry_fingerprint": kernel.fingerprint,
        "fastapi_external_contract_target": True,
        "starlette_internal_dependency_required": False,
        "pydantic_internal_dependency_required": False,
        "native_route_resolution": True,
        "python_asgi_projection_only": True,
        "canonical_state_mutation_authority": False,
        "vm81_admission_authority": False,
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "HHSNativeASGIApplication",
    "NativeAPIRoute",
    "NativeAPIRouter",
    "NativeBaseModel",
    "NativeFastAPICompatibilityError",
    "NativeHTTPException",
    "NativeRouteKernel",
    "NativeRouteResolution",
    "NativeWebSocket",
    "NativeWebSocketDisconnect",
    "bind_native_router_to_external_app",
    "native_fastapi_compatibility_contract",
]
