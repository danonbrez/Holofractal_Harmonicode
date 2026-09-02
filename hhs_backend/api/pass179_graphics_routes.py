"""Governed HTTP projection for the Pass 179 native exact graphics nucleus."""
from __future__ import annotations

import base64
from typing import Any, Dict

from fastapi import APIRouter, Response

from hhs_runtime.pass179.backends import BackendProjectionError, project_backend
from hhs_runtime.pass179.golden import golden_scene_manifest, lattice_run_scene, motion_5184_scene
from hhs_runtime.pass179.runtime import (
    PASS179_GRAPHICS,
    GraphicsError,
    command_stream,
    scene_from_payload,
)
from hhs_runtime.pass179.shader_ir import ShaderIRError, compile_shader_ir, validate_shader_ir
from hhs_runtime.pass179.software import SoftwareRenderError, png_from_rgba16

router = APIRouter(
    prefix="/api/runtime/pass179-graphics",
    tags=["pass179", "graphics", "vm81", "software-renderer", "shader-ir"],
)


def _reject(error: Exception) -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS_179_GRAPHICS_ROUTE_RESULT_V1",
        "ok": False,
        "status": "REJECT_PASS179_GRAPHICS_REQUEST",
        "reason": str(error),
    }


@router.get("/status")
def status() -> Dict[str, Any]:
    result = PASS179_GRAPHICS.status()
    result["golden_scenes"] = golden_scene_manifest()
    result["graphics_studio"] = "/graphics-studio/"
    return result


@router.post("/scene/commit")
def commit_scene(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        record = PASS179_GRAPHICS.commit_scene(scene_from_payload(payload))
        return {
            "schema": "HHS_PASS_179_SCENE_COMMIT_ROUTE_V1",
            "ok": True,
            "scene_id": record["scene"]["scene_id"],
            "scene_hash216": record["scene_hash216"],
            "post_vm81_hash72_evidence": record["post_vm81_hash72_evidence"],
            "vm81_admission": record["vm81_admission"],
            "command_stream_sha256": record["command_stream"]["command_stream_sha256"],
        }
    except (GraphicsError, ValueError) as error:
        return _reject(error)


@router.get("/scene/{scene_id}/render")
def render_scene(scene_id: str) -> Dict[str, Any]:
    try:
        result = PASS179_GRAPHICS.render_scene(scene_id)
        frame = result["frame"]
        return {
            "schema": "HHS_PASS_179_RENDER_ROUTE_V1",
            "ok": True,
            "scene_hash216": result["scene_hash216"],
            "frame_hash216": result["frame_hash216"],
            "frame_hash72_evidence": result["frame_hash72_evidence"],
            "width": frame["width"],
            "height": frame["height"],
            "frame_sha256": frame["frame_sha256"],
            "rgba16_bytes": len(frame["rgba16"]),
            "projection_only": True,
        }
    except (GraphicsError, SoftwareRenderError) as error:
        return _reject(error)


@router.get("/scene/{scene_id}/png")
def render_png(scene_id: str) -> Response:
    try:
        result = PASS179_GRAPHICS.render_scene(scene_id)
        frame = result["frame"]
        png = png_from_rgba16(frame["width"], frame["height"], frame["rgba16"])
        return Response(
            content=png,
            media_type="image/png",
            headers={
                "X-HHS-Frame-SHA256": frame["frame_sha256"],
                "X-HHS-Projection-Only": "true",
            },
        )
    except (GraphicsError, SoftwareRenderError) as error:
        return Response(content=str(error), media_type="text/plain", status_code=400)


@router.post("/shader/validate")
def shader_validate(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return validate_shader_ir(payload)
    except ShaderIRError as error:
        return _reject(error)


@router.post("/shader/project/{target}")
def shader_project(target: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return compile_shader_ir(payload, target)
    except ShaderIRError as error:
        return _reject(error)


@router.post("/backend/project/{backend}")
def backend_project(backend: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        scene = scene_from_payload(payload)
        return project_backend(command_stream(scene), backend)
    except (BackendProjectionError, GraphicsError, ValueError) as error:
        return _reject(error)


def _golden(name: str):
    if name == "lattice-run":
        return lattice_run_scene()
    if name == "motion-5184":
        return motion_5184_scene()
    raise GraphicsError("P179_GOLDEN_SCENE_UNKNOWN")


@router.post("/golden/{name}/commit")
def commit_golden(name: str) -> Dict[str, Any]:
    try:
        scene = _golden(name)
        record = PASS179_GRAPHICS.commit_scene(scene)
        return {
            "schema": "HHS_PASS_179_GOLDEN_COMMIT_V1",
            "ok": True,
            "name": name,
            "scene_id": scene.scene_id,
            "node_count": len(scene.nodes),
            "scene_hash216": record["scene_hash216"],
            "classification": golden_scene_manifest()[
                "lattice_run" if name == "lattice-run" else "motion_5184"
            ]["classification"],
            "terminal_golden_scene_parity": False,
        }
    except GraphicsError as error:
        return _reject(error)
