"""Native-ASGI runtime graphics application factory."""
from __future__ import annotations

from pathlib import Path

from hhs_backend.runtime.hhs_native_fastapi_compat_v1 import (
    HHSNativeASGIApplication,
    NativeRouteKernel,
    native_fastapi_compatibility_contract,
)
from hhs_backend.runtime.hhs_runtime_graphics_service_v1 import (
    GRAPHICS_ROUTE_HANDLERS,
)


def build_native_runtime_graphics_app(
    library_path: str | Path,
) -> HHSNativeASGIApplication:
    kernel = NativeRouteKernel(library_path)
    app = HHSNativeASGIApplication(kernel=kernel)
    for path, handler in GRAPHICS_ROUTE_HANDLERS.items():
        app.add_api_route(path, handler, methods=("GET",))
    return app


def native_runtime_graphics_contract(library_path: str | Path) -> dict:
    app = build_native_runtime_graphics_app(library_path)
    result = native_fastapi_compatibility_contract(app.kernel)
    result.update(
        {
            "schema": "HHS_PASS_220_FASTAPI1_NATIVE_GRAPHICS_ASGI_V1",
            "route_family": "runtime_graphics",
            "route_paths": sorted(GRAPHICS_ROUTE_HANDLERS),
            "fastapi_ingress_egress_equivalence_required": True,
            "shared_service_handlers": True,
        }
    )
    return result


__all__ = [
    "build_native_runtime_graphics_app",
    "native_runtime_graphics_contract",
]
