from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from hhs_backend.runtime.hhs_vulkan_loader_runtime_v1 import (
    AUTHORITY,
    SCHEMA,
    inspect_vulkan_loader,
)

router = APIRouter(
    prefix="/api/runtime/graphics",
    tags=["runtime", "graphics", "vulkan"],
)


@router.get("/status")
def runtime_graphics_status() -> Dict[str, Any]:
    vulkan = inspect_vulkan_loader()
    return {
        "schema": "HHS_RUNTIME_GRAPHICS_STATUS_V1",
        "ok": bool(vulkan.get("loader_ready")),
        "render_authority": "PROJECTION_ONLY",
        "canonical_state_mutation_allowed": False,
        "native_accelerator_api": "vulkan",
        "vulkan": vulkan,
        "authority": AUTHORITY,
    }


@router.get("/vulkan")
def runtime_graphics_vulkan_status() -> Dict[str, Any]:
    return inspect_vulkan_loader()


@router.get("/capabilities")
def runtime_graphics_capabilities() -> Dict[str, Any]:
    return {
        "schema": "HHS_RUNTIME_GRAPHICS_CAPABILITIES_V1",
        "vulkan_loader_schema": SCHEMA,
        "loader_role": "APPLICATION_TO_ICD_DISPATCH",
        "driver_bundled_by_hhs": False,
        "gpu_device_authority": "HOST_DRIVER_ONLY",
        "hhs_runtime_authority": "PROJECTION_ACCELERATION_ONLY",
        "selective_projection": {
            "schema": "HHS_PASS219B_SELECTIVE_PROJECTION_1_0",
            "selector": "EXACT_RATIONAL_PRECOMPUTED_IDS_AND_CELL_RANGES",
            "gpu_id_buffer": "STATIC_UINT32_PROJECTION_IDENTITY",
            "measured_hot_path_division": False,
            "measured_hot_path_modulo": False,
            "canonical_state_mutation_allowed": False,
            "canonical_persistence_allowed": False,
            "canonical_hash72_commit_allowed": False,
        },
        "sparse_dirty_projection": {
            "schema": "HHS_PASS219B_SPARSE_DIRTY_PROJECTION_1_0",
            "input": "I7_PRECOMPUTED_CELL_RANGES_PLUS_SORTED_UNIQUE_DIRTY_CELL_IDS",
            "output": "COALESCED_SELECTED_INDEX_SPANS",
            "full_selected_rebuild_required_per_tick": False,
            "selected_count_must_match_inherited_i7_plan": True,
            "dirty_set_completeness_required": True,
            "incomplete_dirty_set_fallback": "FULL_DERIVED_PROJECTION_PATH",
            "measured_hot_path_division": False,
            "measured_hot_path_modulo": False,
            "canonical_state_mutation_allowed": False,
            "canonical_persistence_allowed": False,
            "canonical_hash72_commit_allowed": False,
        },
        "routes": [
            "GET /api/runtime/graphics/status",
            "GET /api/runtime/graphics/vulkan",
            "GET /api/runtime/graphics/capabilities",
        ],
        "authority": AUTHORITY,
    }
