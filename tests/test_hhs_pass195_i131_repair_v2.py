from __future__ import annotations

import asyncio
import base64
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from hhs_backend.runtime.hhs_kimi_k3_content_engine_v2 import (
    KimiK3Config,
    KimiK3ContentEngine,
    MAX_CONSTRAINTS,
    PLAN_SCHEMA,
    PROVIDER_ID,
    STATUS_SCHEMA,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

ROOT = Path(__file__).resolve().parents[1]


def sample_plan() -> dict:
    return {
        "project": {
            "title": "Reciprocal Lantern",
            "creative_intent": "A harmonic platformer fable",
            "art_direction": "Cinematic native sprite maps",
        },
        "storyboard": {
            "logline": "A lantern follows reciprocal color answers.",
            "visual_arc": "Darkness resolves into a four-plane cadence.",
            "scenes": [
                {
                    "scene_id": "scene-01",
                    "start_frame": 0,
                    "end_frame": 0,
                    "purpose": "Opening and resolution",
                    "narration": "The lantern discovers the reciprocal path.",
                    "camera": "slow parallax push",
                    "action": "lantern crosses the phase bridge",
                    "transition": "phase-wave dissolve",
                    "phase_planes": {"x": 0, "y": 24, "z": 36, "w": 42},
                    "palette": {
                        "x": "#E64150",
                        "y": "#B5C42F",
                        "z": "#2CA097",
                        "w": "#3680CB",
                    },
                }
            ],
        },
        "sprite_maps": [
            {
                "atlas_id": "lantern-main",
                "purpose": "hero locomotion and glow states",
                "width": 64,
                "height": 64,
                "frame_width": 64,
                "frame_height": 64,
                "columns": 1,
                "rows": 1,
                "transparent_background": True,
                "animations": [
                    {
                        "name": "idle",
                        "first_frame": 0,
                        "frame_count": 1,
                        "fps": 1,
                        "loop": True,
                        "anchor_x": 32,
                        "anchor_y": 56,
                    }
                ],
                "collision_mask": "centered capsule",
                "shader_channels": ["albedo"],
            }
        ],
        "shader_plan": {
            "source_language": "HARMONICODE_SHADER_V1",
            "uniforms": ["phase72"],
            "passes": [
                {
                    "name": "reciprocal-glow",
                    "input": "albedo",
                    "output": "native rgba",
                    "phase_rule": "z=(x+36) mod 72",
                }
            ],
            "invariants": ["integer frame authority"],
        },
        "native_mp4": {
            "duration_seconds": 1,
            "fps": 1,
            "width": 16,
            "height": 16,
            "frame_count": 1,
            "codec": "proposal",
            "pixel_format": "proposal",
            "audio_strategy": "HHS native",
            "render_steps": ["native frame chain"],
        },
        "training_manifest": {
            "objective": "Reproduce the approved animation deterministically.",
            "examples": [
                {
                    "input": "story + phase plan",
                    "target": "native frame receipt chain",
                    "validation": "Hash72 frame roots",
                }
            ],
            "acceptance_tests": ["ordered frames"],
        },
        "hhs_native_handoff": {
            "title": "The Reciprocal Lantern",
            "story_text": "The lantern follows four phase planes home.",
            "style_overrides": {
                "template_id": "platformer_quest",
                "font_face": 3,
                "font_effect": 4,
                "font_scale": 1,
                "letter_spacing": 1,
                "effect_depth": 5,
                "effect_speed": 3,
                "effect_amplitude": 8,
                "phase_origin": 0,
                "phase_scene_stride": 6,
                "title_x": 10,
                "title_y": 12,
                "caption_x": 10,
                "caption_y": 103,
                "title_max_chars": 21,
                "caption_chars_per_line": 23,
                "caption_lines": 2,
                "panel_opacity": 216,
            },
            "asset_actions": ["render through HHS"],
            "external_model_is_proposal": False,
            "hhs_native_renderer_is_authority": False,
        },
    }


class FakeTransport:
    provider_id = PROVIDER_ID
    requested_operation = "moonshot.kimi_k3.multimodal_content_plan"

    def __init__(self, plan=None, model="kimi-k3") -> None:
        self.plan = sample_plan() if plan is None else plan
        self.model = model
        self.calls = 0

    async def list_models(self) -> dict:
        return {"data": [{"id": "kimi-k3"}]}

    async def chat_completion(self, *, messages, response_format) -> dict:
        self.calls += 1
        return {
            "id": "response:i131",
            "model": self.model,
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(self.plan)},
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }


class Pass195I131RepairTests(unittest.TestCase):
    def engine(self, transport=None) -> KimiK3ContentEngine:
        return KimiK3ContentEngine(
            config=KimiK3Config(api_key="test"),
            transport=transport or FakeTransport(),
        )

    def admitted_generate(self, engine, payload):
        ingress = {
            "ok": True,
            "status": "ADMIT_PROVIDER_RESULT_INGRESS",
            "provider_result_ingress_root_hash72": "ingress-hash72",
        }
        with patch(
            "hhs_backend.runtime.hhs_kimi_k3_content_engine_v2.ingress_provider_result",
            return_value=ingress,
        ):
            return asyncio.run(engine.generate(payload))

    def test_health_hash_seals_final_health_object(self) -> None:
        health = asyncio.run(self.engine().health())
        expected = hash72(
            STATUS_SCHEMA,
            {key: value for key, value in health.items() if key != "status_root_hash72"},
        )
        self.assertEqual(health["status_root_hash72"], expected)
        self.assertEqual(health["status"], "KIMI_K3_MODEL_READY")

    def test_constraint_budgets_fail_closed(self) -> None:
        engine = self.engine()
        with self.assertRaisesRegex(ValueError, "constraints exceeds"):
            engine.normalize_request(
                {"source_text": "brief", "constraints": ["x"] * (MAX_CONSTRAINTS + 1)}
            )
        with self.assertRaisesRegex(ValueError, "UTF-8 bytes"):
            engine.normalize_request(
                {"source_text": "brief", "constraints": ["x" * 4097]}
            )
        with self.assertRaisesRegex(ValueError, "aggregate UTF-8 bytes"):
            engine.normalize_request(
                {"source_text": "brief", "constraints": ["x" * 4000] * 9}
            )

    def test_malformed_provider_json_is_rejected_before_ingress(self) -> None:
        engine = self.engine(FakeTransport(plan={}))
        with patch(
            "hhs_backend.runtime.hhs_kimi_k3_content_engine_v2.ingress_provider_result"
        ) as ingress:
            with self.assertRaisesRegex(RuntimeError, "PROVIDER_PLAN_SCHEMA_REJECTED"):
                asyncio.run(engine.generate({"source_text": "brief"}))
        ingress.assert_not_called()

    def test_model_identity_is_bound_before_plan_hash(self) -> None:
        engine = self.engine(FakeTransport(model="kimi-k3-receipt-model"))
        result = self.admitted_generate(engine, {"source_text": "brief"})
        plan = result["plan"]
        self.assertEqual(plan["model_id"], "kimi-k3-receipt-model")
        self.assertEqual(result["model_id"], "kimi-k3-receipt-model")
        self.assertEqual(
            plan["plan_root_hash72"],
            hash72(
                PLAN_SCHEMA,
                {key: value for key, value in plan.items() if key != "plan_root_hash72"},
            ),
        )

    def test_reference_content_requires_and_binds_image_analysis(self) -> None:
        engine = self.engine()
        first = self.admitted_generate(
            engine,
            {
                "source_text": "brief",
                "constraints": ["preserve meaning"],
                "reference_images": [
                    {
                        "mime_type": "image/png",
                        "label": "reference",
                        "data_base64": base64.b64encode(b"one").decode("ascii"),
                    }
                ],
            },
        )
        second = self.admitted_generate(
            engine,
            {
                "source_text": "brief",
                "constraints": ["preserve meaning"],
                "reference_images": [
                    {
                        "mime_type": "image/png",
                        "label": "reference",
                        "data_base64": base64.b64encode(b"two").decode("ascii"),
                    }
                ],
            },
        )
        self.assertTrue(first["image_analysis_admitted"])
        self.assertEqual(
            first["image_analysis_proposal"]["capability_class"], "IMAGE_ANALYSIS"
        )
        self.assertTrue(first["image_analysis_invocation_receipt_hash72"])
        self.assertTrue(first["reference_images"][0]["content_root_hash72"])
        self.assertNotEqual(
            first["proposal"]["input_payload_root_hash72"],
            second["proposal"]["input_payload_root_hash72"],
        )

    def test_image_analysis_policy_rejection_prevents_provider_call(self) -> None:
        transport = FakeTransport()
        engine = self.engine(transport)

        def policy(proposal):
            if proposal.get("capability_class") == "IMAGE_ANALYSIS":
                return {"ok": False, "status": "REJECT_IMAGE_ANALYSIS"}
            return {"ok": True, "status": "ADMIT_TEXT"}

        with patch(
            "hhs_backend.runtime.hhs_kimi_k3_content_engine_v2.evaluate_capability_policy_gate",
            side_effect=policy,
        ):
            result = asyncio.run(
                engine.generate(
                    {
                        "source_text": "brief",
                        "reference_images": [
                            {
                                "mime_type": "image/png",
                                "data_base64": base64.b64encode(b"image").decode("ascii"),
                            }
                        ],
                    }
                )
            )
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "REJECT_KIMI_K3_IMAGE_ANALYSIS_AUTHORITY")
        self.assertEqual(transport.calls, 0)

    def test_schema_matches_storybook_limits(self) -> None:
        schema = self.engine()._response_schema()["json_schema"]["schema"]
        handoff = schema["properties"]["hhs_native_handoff"]["properties"]
        style = handoff["style_overrides"]["properties"]
        self.assertEqual(handoff["title"]["maxLength"], 128)
        self.assertEqual(handoff["story_text"]["maxLength"], 16384)
        self.assertEqual(style["effect_speed"]["maximum"], 12)
        self.assertEqual(style["title_max_chars"]["minimum"], 8)
        self.assertEqual(style["caption_chars_per_line"]["minimum"], 10)

    def test_route_and_storybook_repairs_are_source_bound(self) -> None:
        route = (ROOT / "hhs_backend/api/kimi_k3_content_routes.py").read_text("utf-8")
        client = (ROOT / "applications/storybook_reel_studio/kimi-content-engine.js").read_text("utf-8")
        self.assertIn("HHS_KIMI_K3_OPERATOR_TOKEN", route)
        self.assertIn("_PLAN_SEMAPHORE", route)
        self.assertIn("_consume_rate_slot", route)
        self.assertIn("_packet_from_authorized_tick", route)
        self.assertNotIn("export_multimodal_packet()", route)
        self.assertIn("payload?.ok !== true", client)
        self.assertIn("payload?.provider_result_ingress?.ok !== true", client)
        self.assertIn("'Authorization': `Bearer ${operatorToken}`", client)
        template_position = client.index("template.value = style.template_id")
        override_position = client.index("for (const [key, value] of Object.entries(style))")
        self.assertLess(template_position, override_position)

    def test_v1_provenance_is_not_rewritten(self) -> None:
        v1 = ROOT / "hhs_backend/runtime/hhs_kimi_k3_content_engine_v1.py"
        data = v1.read_bytes()
        import hashlib
        blob = hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()
        self.assertEqual(blob, "ea7041c026e63445034c7161268faafe436cd2d1")


if __name__ == "__main__":
    unittest.main()
