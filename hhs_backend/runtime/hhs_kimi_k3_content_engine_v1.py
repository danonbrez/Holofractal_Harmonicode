"""Governed Kimi K3 multimodal content-planning engine for HHS.

Kimi K3 is an external proposal and visual-analysis provider. HHS VM81,
Hash72/Hash216, native sprite/shader/game/storybook runtimes, and their
admission gates remain the only canonical execution authority.
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence

from hhs_backend.runtime.hhs_capability_policy_gate_v1 import evaluate_capability_policy_gate
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import (
    build_provider_execution_proposal,
    validate_provider_execution_proposal,
)
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import invoke_provider_with_receipt
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import ingress_provider_result
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_PASS_195_KIMI_K3_CONTENT_ENGINE_V1"
AUTHORITY = "HHS_VM81_KIMI_K3_CONTENT_PROPOSAL_AUTHORITY_V1"
PROVIDER_ID = "provider:hhs.moonshot.kimi_k3"
STATUS_SCHEMA = "HHS_KIMI_K3_CONTENT_ENGINE_STATUS_V1"
PLAN_SCHEMA = "HHS_KIMI_K3_MULTIMODAL_CONTENT_PLAN_V1"
RESULT_SCHEMA = "HHS_KIMI_K3_CONTENT_ENGINE_RESULT_V1"
ALLOWED_OPERATIONS = {"sprite_map", "storyboard", "native_mp4_training", "complete_pipeline"}
ALLOWED_REASONING_EFFORT = {"low", "high", "max"}
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SOURCE_TEXT_BYTES = 128 * 1024
MAX_ART_DIRECTION_BYTES = 32 * 1024
MAX_REFERENCE_IMAGES = 4
MAX_REFERENCE_IMAGE_BYTES = 8 * 1024 * 1024

SYSTEM_INSTRUCTION = """You are the governed visual-development planning engine
for the Holofractal Harmonicode System (HHS). Return only the requested strict
JSON object. Preserve the user's source meaning. Produce implementable visual
specifications for HHS native sprite-map, shader, game-engine, and storybook
MP4 surfaces. Your output is a proposal only: HHS VM81, Hash72/Hash216, native
renderers, and their admission gates remain authoritative. Never claim that an
asset was rasterized, a shader executed, an MP4 encoded, a training example
validated, or a repository mutation completed. Use integer frame indices,
explicit atlas geometry and anchors, deterministic transitions, and exact
x/y/z/w phase-plane values from 0 through 71."""


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() not in {"0", "false", "no", "off", "disabled"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _clean_json_text(value: str) -> str:
    text = str(value or "").strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else text


def _bounded_text(value: Any, *, field: str, maximum_bytes: int, required: bool = False) -> str:
    text = str(value or "")
    if required and not text.strip():
        raise ValueError(f"{field} is required")
    if len(text.encode("utf-8")) > maximum_bytes:
        raise ValueError(f"{field} exceeds {maximum_bytes} UTF-8 bytes")
    return text


def _integer(value: Any, *, field: str, minimum: int, maximum: int) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if result < minimum or result > maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return result


def _object(properties: Mapping[str, Any], required: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": dict(properties),
        "required": list(required or properties.keys()),
    }


def _array(items: Mapping[str, Any], maximum: Optional[int] = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {"type": "array", "items": dict(items)}
    if maximum is not None:
        result["maxItems"] = maximum
    return result


@dataclass(frozen=True)
class KimiK3Config:
    enabled: bool = True
    base_url: str = "https://api.moonshot.ai/v1"
    model_id: str = "kimi-k3"
    api_key: str = ""
    timeout_seconds: float = 300.0
    max_completion_tokens: int = 8192
    reasoning_effort: str = "max"
    max_reference_images: int = MAX_REFERENCE_IMAGES
    max_reference_image_bytes: int = MAX_REFERENCE_IMAGE_BYTES

    @classmethod
    def from_env(cls) -> "KimiK3Config":
        effort = os.getenv("HHS_KIMI_K3_REASONING_EFFORT", cls.reasoning_effort).strip().lower()
        if effort not in ALLOWED_REASONING_EFFORT:
            effort = cls.reasoning_effort
        return cls(
            enabled=_env_bool("HHS_KIMI_K3_ENABLED", True),
            base_url=os.getenv("HHS_KIMI_K3_BASE_URL", cls.base_url).rstrip("/"),
            model_id=os.getenv("HHS_KIMI_K3_MODEL", cls.model_id).strip() or cls.model_id,
            api_key=(os.getenv("HHS_KIMI_K3_API_KEY") or os.getenv("MOONSHOT_API_KEY") or "").strip(),
            timeout_seconds=float(os.getenv("HHS_KIMI_K3_TIMEOUT_SECONDS", str(cls.timeout_seconds))),
            max_completion_tokens=int(os.getenv("HHS_KIMI_K3_MAX_COMPLETION_TOKENS", str(cls.max_completion_tokens))),
            reasoning_effort=effort,
            max_reference_images=int(os.getenv("HHS_KIMI_K3_MAX_REFERENCE_IMAGES", str(cls.max_reference_images))),
            max_reference_image_bytes=int(os.getenv("HHS_KIMI_K3_MAX_REFERENCE_IMAGE_BYTES", str(cls.max_reference_image_bytes))),
        )


class KimiK3Transport:
    provider_id = PROVIDER_ID
    requested_operation = "moonshot.kimi_k3.multimodal_content_plan"

    def __init__(self, config: KimiK3Config):
        self.config = config
        self.model_id = config.model_id

    def _request_sync(self, method: str, path: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        if not self.config.enabled:
            raise RuntimeError("Kimi K3 content engine is disabled")
        if not self.config.api_key:
            raise RuntimeError("Kimi K3 API key is not configured; set HHS_KIMI_K3_API_KEY or MOONSHOT_API_KEY")
        body = None
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": "HHS-Pass195-KimiK3/1.0",
        }
        if payload is not None:
            body = _canonical_json(dict(payload)).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(f"{self.config.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                decoded = response.read().decode("utf-8")
                return json.loads(decoded) if decoded else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Kimi K3 HTTP {exc.code} for {path}: {detail[:2048]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Kimi K3 unavailable at {self.config.base_url}: {exc.reason}") from exc

    async def list_models(self) -> Dict[str, Any]:
        return await asyncio.to_thread(self._request_sync, "GET", "/models")

    async def chat_completion(self, *, messages: Sequence[Mapping[str, Any]], response_format: Mapping[str, Any]) -> Dict[str, Any]:
        payload = {
            "model": self.config.model_id,
            "messages": [dict(message) for message in messages],
            "stream": False,
            "max_completion_tokens": self.config.max_completion_tokens,
            "reasoning_effort": self.config.reasoning_effort,
            "response_format": dict(response_format),
        }
        return await asyncio.to_thread(self._request_sync, "POST", "/chat/completions", payload)


class KimiK3ContentEngine:
    def __init__(self, config: Optional[KimiK3Config] = None, transport: Optional[Any] = None) -> None:
        self.config = config or KimiK3Config.from_env()
        self.transport = transport or KimiK3Transport(self.config)
        self.provider_id = str(getattr(self.transport, "provider_id", None) or PROVIDER_ID)
        self.requested_operation = str(
            getattr(self.transport, "requested_operation", None)
            or "moonshot.kimi_k3.multimodal_content_plan"
        )

    def status(self) -> Dict[str, Any]:
        status = {
            "schema": STATUS_SCHEMA,
            "version": VERSION,
            "ok": bool(self.config.enabled),
            "status": (
                "KIMI_K3_READY_FOR_PROVIDER_PROBE"
                if self.config.enabled and self.config.api_key
                else "KIMI_K3_CONFIGURATION_REQUIRED"
                if self.config.enabled
                else "KIMI_K3_DISABLED"
            ),
            "enabled": self.config.enabled,
            "configured": bool(self.config.api_key),
            "provider_id": self.provider_id,
            "model_id": self.config.model_id,
            "base_url": self.config.base_url,
            "reasoning_effort": self.config.reasoning_effort,
            "max_completion_tokens": self.config.max_completion_tokens,
            "supported_operations": sorted(ALLOWED_OPERATIONS),
            "supported_reference_image_mime_types": sorted(ALLOWED_IMAGE_MIME_TYPES),
            "max_reference_images": self.config.max_reference_images,
            "max_reference_image_bytes": self.config.max_reference_image_bytes,
            "api_key_exposed": False,
            "external_model_generates_canonical_pixels": False,
            "external_model_executes_hhs_shaders": False,
            "external_model_encodes_native_mp4": False,
            "direct_vm81_mutation_allowed": False,
            "provider_result_ingress_required": True,
            "hhs_native_renderer_is_authority": True,
            "studio_path": "/storybook-reel/",
            "authority": AUTHORITY,
        }
        status["status_root_hash72"] = hash72(STATUS_SCHEMA, status)
        return status

    async def health(self) -> Dict[str, Any]:
        base = self.status()
        if not self.config.enabled or not self.config.api_key:
            return {
                **base,
                "ok": False,
                "online": False,
                "configured_model_registered": False,
                "error": "Kimi K3 is disabled" if not self.config.enabled else "API key is not configured",
            }
        try:
            models = await self.transport.list_models()
            model_ids = {
                str(item.get("id"))
                for item in (models.get("data") or [])
                if isinstance(item, Mapping) and item.get("id")
            }
            ready = self.config.model_id in model_ids
            return {
                **base,
                "ok": ready,
                "online": True,
                "configured_model_registered": ready,
                "registered_model_ids": sorted(model_ids),
                "models": models,
                "status": "KIMI_K3_MODEL_READY" if ready else "KIMI_K3_MODEL_NOT_REGISTERED",
                "error": None if ready else "configured model is not listed",
            }
        except Exception as exc:
            return {
                **base,
                "ok": False,
                "online": False,
                "configured_model_registered": False,
                "status": "KIMI_K3_PROVIDER_OFFLINE",
                "error": str(exc),
            }

    @staticmethod
    def _response_schema() -> Dict[str, Any]:
        string = {"type": "string"}
        integer = {"type": "integer"}
        boolean = {"type": "boolean"}
        phase = _object({plane: {"type": "integer", "minimum": 0, "maximum": 71} for plane in "xyzw"})
        palette = _object({plane: {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"} for plane in "xyzw"})
        scene = _object({
            "scene_id": string,
            "start_frame": {"type": "integer", "minimum": 0},
            "end_frame": {"type": "integer", "minimum": 0},
            "purpose": string,
            "narration": string,
            "camera": string,
            "action": string,
            "transition": string,
            "phase_planes": phase,
            "palette": palette,
        })
        animation = _object({
            "name": string,
            "first_frame": {"type": "integer", "minimum": 0},
            "frame_count": {"type": "integer", "minimum": 1},
            "fps": {"type": "integer", "minimum": 1, "maximum": 120},
            "loop": boolean,
            "anchor_x": integer,
            "anchor_y": integer,
        })
        atlas = _object({
            "atlas_id": string,
            "purpose": string,
            "width": {"type": "integer", "minimum": 1, "maximum": 8192},
            "height": {"type": "integer", "minimum": 1, "maximum": 8192},
            "frame_width": {"type": "integer", "minimum": 1, "maximum": 2048},
            "frame_height": {"type": "integer", "minimum": 1, "maximum": 2048},
            "columns": {"type": "integer", "minimum": 1, "maximum": 128},
            "rows": {"type": "integer", "minimum": 1, "maximum": 128},
            "transparent_background": boolean,
            "animations": _array(animation),
            "collision_mask": string,
            "shader_channels": _array(string),
        })
        shader_pass = _object({"name": string, "input": string, "output": string, "phase_rule": string})
        example = _object({"input": string, "target": string, "validation": string})
        style = {
            "template_id": string,
            "font_face": {"type": "integer", "minimum": 0, "maximum": 4},
            "font_effect": {"type": "integer", "minimum": 0, "maximum": 4},
            "font_scale": {"type": "integer", "minimum": 1, "maximum": 4},
            "letter_spacing": {"type": "integer", "minimum": 0, "maximum": 8},
            "effect_depth": {"type": "integer", "minimum": 0, "maximum": 12},
            "effect_speed": {"type": "integer", "minimum": 1, "maximum": 72},
            "effect_amplitude": {"type": "integer", "minimum": 0, "maximum": 24},
            "phase_origin": {"type": "integer", "minimum": 0, "maximum": 4294967295},
            "phase_scene_stride": {"type": "integer", "minimum": 1, "maximum": 71},
            "title_x": {"type": "integer", "minimum": 0, "maximum": 150},
            "title_y": {"type": "integer", "minimum": 0, "maximum": 136},
            "caption_x": {"type": "integer", "minimum": 0, "maximum": 150},
            "caption_y": {"type": "integer", "minimum": 0, "maximum": 136},
            "title_max_chars": {"type": "integer", "minimum": 1, "maximum": 40},
            "caption_chars_per_line": {"type": "integer", "minimum": 1, "maximum": 40},
            "caption_lines": {"type": "integer", "minimum": 1, "maximum": 4},
            "panel_opacity": {"type": "integer", "minimum": 0, "maximum": 255},
        }
        schema = _object({
            "project": _object({"title": string, "creative_intent": string, "art_direction": string}),
            "storyboard": _object({"logline": string, "visual_arc": string, "scenes": _array(scene, 48)}),
            "sprite_maps": _array(atlas, 24),
            "shader_plan": _object({
                "source_language": string,
                "uniforms": _array(string),
                "passes": _array(shader_pass),
                "invariants": _array(string),
            }),
            "native_mp4": _object({
                "duration_seconds": {"type": "integer", "minimum": 1, "maximum": 3600},
                "fps": {"type": "integer", "minimum": 1, "maximum": 120},
                "width": {"type": "integer", "minimum": 16, "maximum": 8192},
                "height": {"type": "integer", "minimum": 16, "maximum": 8192},
                "frame_count": {"type": "integer", "minimum": 1},
                "codec": string,
                "pixel_format": string,
                "audio_strategy": string,
                "render_steps": _array(string),
            }),
            "training_manifest": _object({
                "objective": string,
                "examples": _array(example),
                "acceptance_tests": _array(string),
            }),
            "hhs_native_handoff": _object({
                "title": string,
                "story_text": string,
                "style_overrides": _object(style),
                "asset_actions": _array(string),
                "external_model_is_proposal": boolean,
                "hhs_native_renderer_is_authority": boolean,
            }),
        })
        return {
            "type": "json_schema",
            "json_schema": {"name": "hhs_kimi_k3_content_plan", "strict": True, "schema": schema},
        }

    def _normalize_reference_images(self, values: Any) -> List[Dict[str, Any]]:
        if values is None:
            return []
        if not isinstance(values, list):
            raise ValueError("reference_images must be an array")
        if len(values) > self.config.max_reference_images:
            raise ValueError(f"reference_images exceeds {self.config.max_reference_images} items")
        normalized = []
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                raise ValueError(f"reference_images[{index}] must be an object")
            mime_type = str(item.get("mime_type") or "").lower()
            if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
                raise ValueError(f"reference_images[{index}].mime_type is unsupported")
            encoded = str(item.get("data_base64") or "")
            if encoded.startswith(("http://", "https://")):
                raise ValueError("public image URLs are not accepted; send base64 data")
            try:
                raw = base64.b64decode(encoded, validate=True)
            except Exception as exc:
                raise ValueError(f"reference_images[{index}].data_base64 is invalid") from exc
            if not raw:
                raise ValueError(f"reference_images[{index}] is empty")
            if len(raw) > self.config.max_reference_image_bytes:
                raise ValueError(f"reference_images[{index}] exceeds {self.config.max_reference_image_bytes} bytes")
            normalized.append({
                "mime_type": mime_type,
                "data_base64": encoded,
                "label": str(item.get("label") or f"reference-{index + 1}"),
                "size_bytes": len(raw),
            })
        return normalized

    def normalize_request(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        operation = str(payload.get("operation") or "complete_pipeline").strip().lower()
        if operation not in ALLOWED_OPERATIONS:
            raise ValueError(f"operation must be one of {', '.join(sorted(ALLOWED_OPERATIONS))}")
        duration = _integer(payload.get("duration_seconds", 90), field="duration_seconds", minimum=1, maximum=3600)
        fps = _integer(payload.get("fps", 30), field="fps", minimum=1, maximum=120)
        width = _integer(payload.get("width", 1080), field="width", minimum=16, maximum=8192)
        height = _integer(payload.get("height", 1920), field="height", minimum=16, maximum=8192)
        return {
            "operation": operation,
            "project_id": str(payload.get("project_id") or "project:graphics-content"),
            "title": _bounded_text(payload.get("title") or "HHS KIMI K3 CONTENT PLAN", field="title", maximum_bytes=1024, required=True),
            "source_text": _bounded_text(payload.get("source_text"), field="source_text", maximum_bytes=MAX_SOURCE_TEXT_BYTES, required=True),
            "art_direction": _bounded_text(payload.get("art_direction"), field="art_direction", maximum_bytes=MAX_ART_DIRECTION_BYTES),
            "duration_seconds": duration,
            "fps": fps,
            "width": width,
            "height": height,
            "frame_count": duration * fps,
            "reference_images": self._normalize_reference_images(payload.get("reference_images")),
            "constraints": [str(value) for value in (payload.get("constraints") or []) if str(value).strip()][:128],
        }

    @staticmethod
    def _request_prompt(request: Mapping[str, Any]) -> str:
        visible = {key: value for key, value in request.items() if key != "reference_images"}
        visible["reference_images"] = [
            {"label": item["label"], "mime_type": item["mime_type"], "size_bytes": item["size_bytes"]}
            for item in request.get("reference_images") or []
        ]
        return (
            "Build the strict HHS multimodal content plan for this request. The native handoff must be usable by the existing HHS storybook, sprite-map, shader, and game-engine surfaces. Keep scene ranges within frame_count and atlas geometry internally consistent.\n\nREQUEST:\n"
            + json.dumps(visible, indent=2, ensure_ascii=False, sort_keys=True)
        )

    def _messages(self, request: Mapping[str, Any]) -> List[Dict[str, Any]]:
        prompt = self._request_prompt(request)
        references = list(request.get("reference_images") or [])
        content: Any = prompt
        if references:
            content = [{"type": "text", "text": prompt}]
            content.extend({
                "type": "image_url",
                "image_url": {"url": f"data:{item['mime_type']};base64,{item['data_base64']}"},
            } for item in references)
        return [{"role": "system", "content": SYSTEM_INSTRUCTION}, {"role": "user", "content": content}]

    @staticmethod
    def _extract_completion(raw: Mapping[str, Any]) -> Dict[str, Any]:
        choices = list(raw.get("choices") or [])
        if not choices:
            raise RuntimeError("Kimi K3 response contained no choices")
        message = dict((choices[0] or {}).get("message") or {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Kimi K3 response contained no final JSON content")
        try:
            plan = json.loads(_clean_json_text(content))
        except json.JSONDecodeError as exc:
            raise RuntimeError("Kimi K3 final content was not valid JSON") from exc
        if not isinstance(plan, dict):
            raise RuntimeError("Kimi K3 final content must be a JSON object")
        return {
            "plan": plan,
            "finish_reason": (choices[0] or {}).get("finish_reason"),
            "usage": dict(raw.get("usage") or {}),
            "model": raw.get("model"),
            "response_id": raw.get("id"),
            "reasoning_content_used_as_plan": False,
        }

    @staticmethod
    def _normalize_plan(plan: Mapping[str, Any], request: Mapping[str, Any]) -> Dict[str, Any]:
        normalized = json.loads(json.dumps(dict(plan), ensure_ascii=False, default=str))
        mp4 = dict(normalized.get("native_mp4") or {})
        mp4.update({
            "duration_seconds": request["duration_seconds"],
            "fps": request["fps"],
            "width": request["width"],
            "height": request["height"],
            "frame_count": request["frame_count"],
            "codec": "h264",
            "pixel_format": "yuv420p",
        })
        normalized["native_mp4"] = mp4
        handoff = dict(normalized.get("hhs_native_handoff") or {})
        handoff["external_model_is_proposal"] = True
        handoff["hhs_native_renderer_is_authority"] = True
        normalized["hhs_native_handoff"] = handoff
        storyboard = dict(normalized.get("storyboard") or {})
        scenes = list(storyboard.get("scenes") or [])
        previous_end = -1
        for index, value in enumerate(scenes):
            scene = dict(value or {})
            start = max(0, min(request["frame_count"] - 1, int(scene.get("start_frame", 0))))
            end = max(start, min(request["frame_count"] - 1, int(scene.get("end_frame", start))))
            if start <= previous_end:
                start = min(request["frame_count"] - 1, previous_end + 1)
                end = max(start, end)
            scene["start_frame"] = start
            scene["end_frame"] = end
            scenes[index] = scene
            previous_end = end
        if scenes:
            scenes[-1]["end_frame"] = request["frame_count"] - 1
        storyboard["scenes"] = scenes
        normalized["storyboard"] = storyboard
        normalized.update({
            "schema": PLAN_SCHEMA,
            "version": VERSION,
            "operation": request["operation"],
            "project_id": request["project_id"],
            "provider_id": PROVIDER_ID,
            "model_id": "kimi-k3",
            "external_model_generates_canonical_pixels": False,
            "external_model_executes_hhs_shaders": False,
            "external_model_encodes_native_mp4": False,
            "direct_vm81_mutation_allowed": False,
            "requires_hhs_native_execution": True,
            "authority": AUTHORITY,
        })
        normalized["plan_root_hash72"] = hash72(
            PLAN_SCHEMA,
            {key: value for key, value in normalized.items() if key != "plan_root_hash72"},
        )
        return normalized

    async def generate(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        request = self.normalize_request(payload)
        proposal = build_provider_execution_proposal(
            capability_class="TEXT_GENERATION",
            project_id=request["project_id"],
            input_payload={
                "operation": request["operation"],
                "title": request["title"],
                "source_text_root_hash72": hash72("HHS_KIMI_K3_SOURCE_TEXT_V1", request["source_text"]),
                "art_direction_root_hash72": hash72("HHS_KIMI_K3_ART_DIRECTION_V1", request["art_direction"]),
                "reference_image_count": len(request["reference_images"]),
                "duration_seconds": request["duration_seconds"],
                "fps": request["fps"],
                "width": request["width"],
                "height": request["height"],
            },
            requested_operation=self.requested_operation,
            constraints={
                "provider_id": self.provider_id,
                "model_id": self.config.model_id,
                "direct_mutation_allowed": False,
                "native_renderer_authority_required": True,
            },
        )
        validation = validate_provider_execution_proposal(proposal)
        policy = evaluate_capability_policy_gate(proposal)
        if not validation.get("ok") or not policy.get("ok"):
            result = {
                "schema": RESULT_SCHEMA,
                "version": VERSION,
                "ok": False,
                "status": "REJECT_KIMI_K3_PROVIDER_INVOCATION",
                "proposal": proposal,
                "proposal_validation": validation,
                "policy_gate_decision": policy,
                "runtime_mutation_admitted": False,
                "authority": AUTHORITY,
            }
            result["result_root_hash72"] = hash72(RESULT_SCHEMA, result)
            return result
        raw = await self.transport.chat_completion(
            messages=self._messages(request),
            response_format=self._response_schema(),
        )
        completion = self._extract_completion(raw)
        plan = self._normalize_plan(completion["plan"], request)
        receipt = invoke_provider_with_receipt(
            proposal,
            simulated_raw_result={
                "schema": "HHS_KIMI_K3_RAW_CONTENT_PLAN_V1",
                "provider_id": self.provider_id,
                "model_id": completion.get("model") or self.config.model_id,
                "response_id": completion.get("response_id"),
                "finish_reason": completion.get("finish_reason"),
                "usage": completion.get("usage"),
                "plan": plan,
                "reasoning_content_used_as_plan": False,
            },
        )
        ingress = ingress_provider_result(
            receipt,
            project_id=request["project_id"],
            output_modality="TEXT",
            target_artifact_type="KIMI_K3_MULTIMODAL_CONTENT_PLAN",
        )
        ok = bool(receipt.get("ok") and ingress.get("ok"))
        result = {
            "schema": RESULT_SCHEMA,
            "version": VERSION,
            "ok": ok,
            "status": "KIMI_K3_CONTENT_PLAN_ADMITTED" if ok else "KIMI_K3_CONTENT_PLAN_INGRESS_REJECTED",
            "request": {key: value for key, value in request.items() if key != "reference_images"},
            "reference_images": [
                {"label": item["label"], "mime_type": item["mime_type"], "size_bytes": item["size_bytes"]}
                for item in request["reference_images"]
            ],
            "plan": plan,
            "provider_id": self.provider_id,
            "model_id": completion.get("model") or self.config.model_id,
            "usage": completion.get("usage") or {},
            "proposal": proposal,
            "proposal_validation": validation,
            "policy_gate_decision": policy,
            "provider_invocation_receipt_hash72": receipt.get("provider_invocation_receipt_hash72"),
            "provider_result_ingress_root_hash72": ingress.get("provider_result_ingress_root_hash72"),
            "provider_result_ingress": ingress,
            "runtime_mutation_admitted": False,
            "native_asset_execution_admitted": False,
            "native_asset_execution_next_surface": "/api/runtime/storybook-reel/generate",
            "authority": AUTHORITY,
        }
        result["result_root_hash72"] = hash72(RESULT_SCHEMA, result)
        return result


KIMI_K3_CONTENT_ENGINE = KimiK3ContentEngine()
