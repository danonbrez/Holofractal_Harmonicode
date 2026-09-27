from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from hhs_backend.runtime.hhs_runtime_graphics_service_v1 import (
    runtime_graphics_capabilities_payload,
    runtime_graphics_status_payload,
    runtime_graphics_vulkan_status_payload,
)

router = APIRouter(
    prefix="/api/runtime/graphics",
    tags=["runtime", "graphics", "vulkan"],
)


@router.get("/status")
def runtime_graphics_status() -> Dict[str, Any]:
    return runtime_graphics_status_payload()


@router.get("/vulkan")
def runtime_graphics_vulkan_status() -> Dict[str, Any]:
    return runtime_graphics_vulkan_status_payload()


@router.get("/capabilities")
def runtime_graphics_capabilities() -> Dict[str, Any]:
    return runtime_graphics_capabilities_payload()
