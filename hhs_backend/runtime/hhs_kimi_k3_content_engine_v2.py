"""Pass 195 I131 repair-forward Kimi K3 content engine.

V1 remains immutable provenance.  V2 narrows external-provider admission so the
provider remains proposal-only and every multimodal input/result is bound to
existing HHS capability, receipt, ingress, and native-render authority.
"""
from __future__ import annotations

import copy
import json
import re
from typing import Any, Dict, List, Mapping, Optional

from hhs_backend.runtime.hhs_capability_policy_gate_v1 import evaluate_capability_policy_gate
from hhs_backend.runtime.hhs_kimi_k3_content_engine_v1 import (
    AUTHORITY,
    PLAN_SCHEMA,
    PROVIDER_ID,
    RESULT_SCHEMA,
    STATUS_SCHEMA,
    KimiK3Config,
    KimiK3ContentEngine as KimiK3ContentEngineV1,
)
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import (
    build_provider_execution_proposal,
    validate_provider_execution_proposal,
)
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import invoke_provider_with_receipt
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import ingress_provider_result
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_PASS_195_KIMI_K3_CONTENT_ENGINE_V2"
REPAIR_SCHEMA = "HHS_PASS_195_I131_KIMI_K3_REPAIR_V2"
MAX_CONSTRAINTS = 32
MAX_CONSTRAINT_ITEM_BYTES = 4096
MAX_CONSTRAINT_TOTAL_BYTES = 32768
MAX_HANDOFF_TITLE_CHARS = 128
MAX_HANDOFF_STORY_CHARS = 16384


def _without_hash(value: Mapping[str, Any], key: str) -> Dict[str, Any]:
    return {name: item for name, item in value.items() if name != key}


def _validate_schema(value: Any, schema: Mapping[str, Any], path: str = "$") -> None:
    """Validate the strict subset of JSON Schema emitted by the V1/V2 planner."""
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(value, Mapping):
            raise RuntimeError(f"{path}:expected object")
        required = list(schema.get("required") or [])
        missing = [name for name in required if name not in value]
        if missing:
            raise RuntimeError(f"{path}:missing required {','.join(sorted(missing))}")
        properties = dict(schema.get("properties") or {})
        if schema.get("additionalProperties") is False:
            unexpected = sorted(str(name) for name in value if name not in properties)
            if unexpected:
                raise RuntimeError(f"{path}:unexpected {','.join(unexpected)}")
        for name, child in properties.items():
            if name in value:
                _validate_schema(value[name], child, f"{path}.{name}")
        return
    if kind == "array":
        if not isinstance(value, list):
            raise RuntimeError(f"{path}:expected array")
        maximum = schema.get("maxItems")
        if maximum is not None and len(value) > int(maximum):
            raise RuntimeError(f"{path}:maxItems {maximum}")
        child = schema.get("items") or {}
        for index, item in enumerate(value):
            _validate_schema(item, child, f"{path}[{index}]")
        return
    if kind == "string":
        if not isinstance(value, str):
            raise RuntimeError(f"{path}:expected string")
        minimum = schema.get("minLength")
        maximum = schema.get("maxLength")
        if minimum is not None and len(value) < int(minimum):
            raise RuntimeError(f"{path}:minLength {minimum}")
        if maximum is not None and len(value) > int(maximum):
            raise RuntimeError(f"{path}:maxLength {maximum}")
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(str(pattern), value) is None:
            raise RuntimeError(f"{path}:pattern mismatch")
        return
    if kind == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise RuntimeError(f"{path}:expected integer")
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and value < int(minimum):
            raise RuntimeError(f"{path}:minimum {minimum}")
        if maximum is not None and value > int(maximum):
            raise RuntimeError(f"{path}:maximum {maximum}")
        return
    if kind == "boolean":
        if not isinstance(value, bool):
            raise RuntimeError(f"{path}:expected boolean")
        return
    if kind is not None:
        raise RuntimeError(f"{path}:unsupported schema type {kind}")


class KimiK3ContentEngine(KimiK3ContentEngineV1):
    """Repair-forward engine preserving V1 transport and native-authority doctrine."""

    def status(self) -> Dict[str, Any]:
        status = dict(super().status())
        status.pop("status_root_hash72", None)
        status["version"] = VERSION
        status["pass195_i131_repair_schema"] = REPAIR_SCHEMA
        status["provider_plan_schema_validation_required"] = True
        status["multimodal_capability_receipt_required"] = True
        status["constraint_budget_enforced"] = True
        status["status_root_hash72"] = hash72(STATUS_SCHEMA, status)
        return status

    async def health(self) -> Dict[str, Any]:
        health = dict(await super().health())
        health.pop("status_root_hash72", None)
        health["version"] = VERSION
        health["pass195_i131_repair_schema"] = REPAIR_SCHEMA
        health["status_root_hash72"] = hash72(STATUS_SCHEMA, health)
        return health

    @staticmethod
    def _response_schema() -> Dict[str, Any]:
        response = copy.deepcopy(KimiK3ContentEngineV1._response_schema())
        schema = response["json_schema"]["schema"]
        handoff = schema["properties"]["hhs_native_handoff"]["properties"]
        # V1 intentionally reuses a single string schema object in several fields.
        # Replace these two nodes rather than mutating the shared object in place.
        handoff["title"] = {
            "type": "string",
            "minLength": 1,
            "maxLength": MAX_HANDOFF_TITLE_CHARS,
        }
        handoff["story_text"] = {
            "type": "string",
            "maxLength": MAX_HANDOFF_STORY_CHARS,
        }
        style = handoff["style_overrides"]["properties"]
        style["effect_speed"]["maximum"] = 12
        style["title_max_chars"]["minimum"] = 8
        style["caption_chars_per_line"]["minimum"] = 10
        return response

    @staticmethod
    def validate_provider_plan(plan: Mapping[str, Any]) -> None:
        try:
            schema = KimiK3ContentEngine._response_schema()["json_schema"]["schema"]
            _validate_schema(plan, schema)
        except RuntimeError as exc:
            raise RuntimeError(f"KIMI_K3_PROVIDER_PLAN_SCHEMA_REJECTED:{exc}") from exc

    def normalize_request(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        raw_constraints = payload.get("constraints") or []
        if not isinstance(raw_constraints, list):
            raise ValueError("constraints must be an array")
        if len(raw_constraints) > MAX_CONSTRAINTS:
            raise ValueError(f"constraints exceeds {MAX_CONSTRAINTS} items")
        constraints: List[str] = []
        aggregate = 0
        for index, value in enumerate(raw_constraints):
            if not isinstance(value, str):
                raise ValueError(f"constraints[{index}] must be a string")
            text = value.strip()
            if not text:
                raise ValueError(f"constraints[{index}] must not be empty")
            size = len(text.encode("utf-8"))
            if size > MAX_CONSTRAINT_ITEM_BYTES:
                raise ValueError(
                    f"constraints[{index}] exceeds {MAX_CONSTRAINT_ITEM_BYTES} UTF-8 bytes"
                )
            aggregate += size
            if aggregate > MAX_CONSTRAINT_TOTAL_BYTES:
                raise ValueError(
                    f"constraints exceeds {MAX_CONSTRAINT_TOTAL_BYTES} aggregate UTF-8 bytes"
                )
            constraints.append(text)

        bounded = dict(payload)
        bounded["constraints"] = constraints
        request = dict(super().normalize_request(bounded))
        enriched = []
        for index, item in enumerate(request.get("reference_images") or []):
            reference = dict(item)
            label = str(reference.get("label") or f"reference-{index + 1}")
            if len(label) > 160:
                raise ValueError(f"reference_images[{index}].label exceeds 160 characters")
            reference["content_root_hash72"] = hash72(
                "HHS_KIMI_K3_REFERENCE_IMAGE_CONTENT_V2",
                {
                    "index": index,
                    "mime_type": reference.get("mime_type"),
                    "label": label,
                    "data_base64": reference.get("data_base64"),
                    "size_bytes": reference.get("size_bytes"),
                },
            )
            enriched.append(reference)
        request["reference_images"] = enriched
        request["constraints_root_hash72"] = hash72(
            "HHS_KIMI_K3_CONSTRAINTS_V2", constraints
        )
        return request

    @staticmethod
    def _normalize_plan_v2(
        plan: Mapping[str, Any], request: Mapping[str, Any], model_id: str
    ) -> Dict[str, Any]:
        normalized = KimiK3ContentEngineV1._normalize_plan(plan, request)
        normalized.pop("plan_root_hash72", None)
        normalized["version"] = VERSION
        normalized["model_id"] = model_id
        handoff = dict(normalized.get("hhs_native_handoff") or {})
        handoff["title"] = str(handoff.get("title") or "")[:MAX_HANDOFF_TITLE_CHARS]
        handoff["story_text"] = str(handoff.get("story_text") or "")[:MAX_HANDOFF_STORY_CHARS]
        style = dict(handoff.get("style_overrides") or {})
        if "effect_speed" in style:
            style["effect_speed"] = max(1, min(12, int(style["effect_speed"])))
        if "title_max_chars" in style:
            style["title_max_chars"] = max(8, min(40, int(style["title_max_chars"])))
        if "caption_chars_per_line" in style:
            style["caption_chars_per_line"] = max(
                10, min(40, int(style["caption_chars_per_line"]))
            )
        handoff["style_overrides"] = style
        normalized["hhs_native_handoff"] = handoff
        normalized["plan_root_hash72"] = hash72(
            PLAN_SCHEMA, _without_hash(normalized, "plan_root_hash72")
        )
        return normalized

    @staticmethod
    def _rejection(
        *,
        status: str,
        text_proposal: Mapping[str, Any],
        text_validation: Mapping[str, Any],
        text_policy: Mapping[str, Any],
        image_proposal: Optional[Mapping[str, Any]] = None,
        image_validation: Optional[Mapping[str, Any]] = None,
        image_policy: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "schema": RESULT_SCHEMA,
            "version": VERSION,
            "ok": False,
            "status": status,
            "proposal": dict(text_proposal),
            "proposal_validation": dict(text_validation),
            "policy_gate_decision": dict(text_policy),
            "image_analysis_proposal": dict(image_proposal or {}),
            "image_analysis_proposal_validation": dict(image_validation or {}),
            "image_analysis_policy_gate_decision": dict(image_policy or {}),
            "image_analysis_admitted": False,
            "runtime_mutation_admitted": False,
            "native_asset_execution_admitted": False,
            "authority": AUTHORITY,
        }
        result["result_root_hash72"] = hash72(RESULT_SCHEMA, result)
        return result

    async def generate(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        request = self.normalize_request(payload)
        reference_hashes = [
            item["content_root_hash72"] for item in request["reference_images"]
        ]

        image_proposal: Optional[Dict[str, Any]] = None
        image_validation: Dict[str, Any] = {}
        image_policy: Dict[str, Any] = {}
        if reference_hashes:
            image_proposal = build_provider_execution_proposal(
                capability_class="IMAGE_ANALYSIS",
                project_id=request["project_id"],
                input_payload={
                    "operation": request["operation"],
                    "ordered_reference_image_root_hash72": reference_hashes,
                    "constraints_root_hash72": request["constraints_root_hash72"],
                },
                requested_operation=f"{self.requested_operation}.image_analysis",
                constraints={
                    "provider_id": self.provider_id,
                    "model_id": self.config.model_id,
                    "direct_mutation_allowed": False,
                },
            )
            image_validation = validate_provider_execution_proposal(image_proposal)
            image_policy = evaluate_capability_policy_gate(image_proposal)

        text_proposal = build_provider_execution_proposal(
            capability_class="TEXT_GENERATION",
            project_id=request["project_id"],
            input_payload={
                "operation": request["operation"],
                "title": request["title"],
                "source_text_root_hash72": hash72(
                    "HHS_KIMI_K3_SOURCE_TEXT_V2", request["source_text"]
                ),
                "art_direction_root_hash72": hash72(
                    "HHS_KIMI_K3_ART_DIRECTION_V2", request["art_direction"]
                ),
                "constraints_root_hash72": request["constraints_root_hash72"],
                "ordered_reference_image_root_hash72": reference_hashes,
                "image_analysis_proposal_root_hash72": (
                    image_proposal.get("proposal_root_hash72") if image_proposal else None
                ),
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
        text_validation = validate_provider_execution_proposal(text_proposal)
        text_policy = evaluate_capability_policy_gate(text_proposal)
        if not text_validation.get("ok") or not text_policy.get("ok"):
            return self._rejection(
                status="REJECT_KIMI_K3_PROVIDER_INVOCATION",
                text_proposal=text_proposal,
                text_validation=text_validation,
                text_policy=text_policy,
                image_proposal=image_proposal,
                image_validation=image_validation,
                image_policy=image_policy,
            )
        if image_proposal and (
            not image_validation.get("ok") or not image_policy.get("ok")
        ):
            return self._rejection(
                status="REJECT_KIMI_K3_IMAGE_ANALYSIS_AUTHORITY",
                text_proposal=text_proposal,
                text_validation=text_validation,
                text_policy=text_policy,
                image_proposal=image_proposal,
                image_validation=image_validation,
                image_policy=image_policy,
            )

        raw = await self.transport.chat_completion(
            messages=self._messages(request),
            response_format=self._response_schema(),
        )
        completion = self._extract_completion(raw)
        self.validate_provider_plan(completion["plan"])
        model_id = str(completion.get("model") or self.config.model_id)
        plan = self._normalize_plan_v2(completion["plan"], request, model_id)

        image_receipt: Dict[str, Any] = {}
        if image_proposal:
            image_receipt = invoke_provider_with_receipt(
                image_proposal,
                simulated_raw_result={
                    "schema": "HHS_KIMI_K3_IMAGE_ANALYSIS_BINDING_V2",
                    "provider_id": self.provider_id,
                    "model_id": model_id,
                    "response_id": completion.get("response_id"),
                    "text_proposal_root_hash72": text_proposal.get("proposal_root_hash72"),
                    "ordered_reference_image_root_hash72": reference_hashes,
                    "analysis_is_proposal_only": True,
                },
            )

        receipt = invoke_provider_with_receipt(
            text_proposal,
            simulated_raw_result={
                "schema": "HHS_KIMI_K3_RAW_CONTENT_PLAN_V2",
                "provider_id": self.provider_id,
                "model_id": model_id,
                "response_id": completion.get("response_id"),
                "finish_reason": completion.get("finish_reason"),
                "usage": completion.get("usage"),
                "plan": plan,
                "image_analysis_proposal_root_hash72": (
                    image_proposal.get("proposal_root_hash72") if image_proposal else None
                ),
                "image_analysis_invocation_receipt_hash72": image_receipt.get(
                    "provider_invocation_receipt_hash72"
                ),
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
        result: Dict[str, Any] = {
            "schema": RESULT_SCHEMA,
            "version": VERSION,
            "ok": ok,
            "status": (
                "KIMI_K3_CONTENT_PLAN_ADMITTED"
                if ok
                else "KIMI_K3_CONTENT_PLAN_INGRESS_REJECTED"
            ),
            "request": {
                key: value
                for key, value in request.items()
                if key not in {"reference_images"}
            },
            "reference_images": [
                {
                    "label": item["label"],
                    "mime_type": item["mime_type"],
                    "size_bytes": item["size_bytes"],
                    "content_root_hash72": item["content_root_hash72"],
                }
                for item in request["reference_images"]
            ],
            "plan": plan,
            "provider_id": self.provider_id,
            "model_id": model_id,
            "usage": completion.get("usage") or {},
            "proposal": text_proposal,
            "proposal_validation": text_validation,
            "policy_gate_decision": text_policy,
            "image_analysis_proposal": image_proposal,
            "image_analysis_proposal_validation": image_validation,
            "image_analysis_policy_gate_decision": image_policy,
            "image_analysis_invocation_receipt_hash72": image_receipt.get(
                "provider_invocation_receipt_hash72"
            ),
            "image_analysis_admitted": bool(
                not reference_hashes
                or (
                    image_validation.get("ok")
                    and image_policy.get("ok")
                    and image_receipt.get("ok")
                )
            ),
            "provider_invocation_receipt_hash72": receipt.get(
                "provider_invocation_receipt_hash72"
            ),
            "provider_result_ingress_root_hash72": ingress.get(
                "provider_result_ingress_root_hash72"
            ),
            "provider_result_ingress": ingress,
            "runtime_mutation_admitted": False,
            "native_asset_execution_admitted": False,
            "native_asset_execution_next_surface": "/api/runtime/storybook-reel/generate",
            "authority": AUTHORITY,
        }
        result["result_root_hash72"] = hash72(RESULT_SCHEMA, result)
        return result


KIMI_K3_CONTENT_ENGINE = KimiK3ContentEngine()
