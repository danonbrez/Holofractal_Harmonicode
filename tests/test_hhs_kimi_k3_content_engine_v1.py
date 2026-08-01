from __future__ import annotations

import asyncio
import base64
import json
import os
import unittest
from unittest.mock import patch

from hhs_backend.runtime.hhs_kimi_k3_content_engine_v1 import (
    KimiK3Config,
    KimiK3ContentEngine,
    KimiK3Transport,
    PLAN_SCHEMA,
    PROVIDER_ID,
)


def sample_plan() -> dict:
    style = {
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
    }
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
                    "end_frame": 2699,
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
                "width": 512,
                "height": 512,
                "frame_width": 64,
                "frame_height": 64,
                "columns": 8,
                "rows": 8,
                "transparent_background": True,
                "animations": [
                    {
                        "name": "walk",
                        "first_frame": 0,
                        "frame_count": 8,
                        "fps": 12,
                        "loop": True,
                        "anchor_x": 32,
                        "anchor_y": 56,
                    }
                ],
                "collision_mask": "centered 28x48 capsule",
                "shader_channels": ["albedo", "emissive", "phase-index"],
            }
        ],
        "shader_plan": {
            "source_language": "HARMONICODE_SHADER_V1",
            "uniforms": ["phase72", "time_frame", "plane_x", "plane_z"],
            "passes": [
                {
                    "name": "reciprocal-glow",
                    "input": "emissive + phase-index",
                    "output": "native rgba",
                    "phase_rule": "z=(x+36) mod 72",
                }
            ],
            "invariants": ["integer frame authority", "no direct VM81 mutation"],
        },
        "native_mp4": {
            "duration_seconds": 1,
            "fps": 1,
            "width": 16,
            "height": 16,
            "frame_count": 1,
            "codec": "proposal",
            "pixel_format": "proposal",
            "audio_strategy": "uploaded narration normalized by HHS",
            "render_steps": ["native sprite projection", "native frame chain"],
        },
        "training_manifest": {
            "objective": "Reproduce the approved native animation deterministically.",
            "examples": [
                {
                    "input": "story + atlas + phase plan",
                    "target": "native MP4 frame and receipt chain",
                    "validation": "Hash72 frame roots and ffprobe acceptance",
                }
            ],
            "acceptance_tests": ["2700 ordered frames", "H.264 yuv420p"],
        },
        "hhs_native_handoff": {
            "title": "The Reciprocal Lantern",
            "story_text": "The lantern follows four phase planes home.",
            "style_overrides": style,
            "asset_actions": ["rasterize atlas natively", "render and encode through HHS"],
            "external_model_is_proposal": False,
            "hhs_native_renderer_is_authority": False,
        },
    }


class FakeTransport:
    provider_id = PROVIDER_ID
    requested_operation = "moonshot.kimi_k3.multimodal_content_plan"

    def __init__(self) -> None:
        self.messages = None
        self.response_format = None

    async def list_models(self) -> dict:
        return {"data": [{"id": "kimi-k3"}]}

    async def chat_completion(self, *, messages, response_format) -> dict:
        self.messages = messages
        self.response_format = response_format
        return {
            "id": "response:test",
            "model": "kimi-k3",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps(sample_plan()),
                        "reasoning_content": "private reasoning is not an artifact",
                    },
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 200},
        }


class KimiK3ContentEngineTests(unittest.TestCase):
    def test_status_never_exposes_secret(self) -> None:
        status = KimiK3ContentEngine(
            config=KimiK3Config(api_key="super-secret"),
            transport=FakeTransport(),
        ).status()
        self.assertTrue(status["configured"])
        self.assertFalse(status["api_key_exposed"])
        self.assertNotIn("super-secret", json.dumps(status))

    def test_environment_accepts_dedicated_or_moonshot_key(self) -> None:
        with patch.dict(
            os.environ,
            {"HHS_KIMI_K3_API_KEY": "dedicated", "MOONSHOT_API_KEY": "fallback"},
            clear=False,
        ):
            self.assertEqual(KimiK3Config.from_env().api_key, "dedicated")
        with patch.dict(
            os.environ,
            {"HHS_KIMI_K3_API_KEY": "", "MOONSHOT_API_KEY": "fallback"},
            clear=False,
        ):
            self.assertEqual(KimiK3Config.from_env().api_key, "fallback")

    def test_transport_uses_kimi_completion_controls_only(self) -> None:
        captured = {}
        transport = KimiK3Transport(
            KimiK3Config(api_key="test", max_completion_tokens=4096, reasoning_effort="high")
        )

        def fake_request(method, path, payload=None):
            captured.update({"method": method, "path": path, "payload": payload})
            return {"choices": [{"message": {"content": "{}"}}]}

        transport._request_sync = fake_request  # type: ignore[method-assign]
        asyncio.run(
            transport.chat_completion(
                messages=[{"role": "user", "content": "plan"}],
                response_format={"type": "json_schema", "json_schema": {}},
            )
        )
        payload = captured["payload"]
        self.assertEqual(payload["max_completion_tokens"], 4096)
        self.assertEqual(payload["reasoning_effort"], "high")
        for forbidden in ("temperature", "top_p", "top_k", "seed", "frequency_penalty"):
            self.assertNotIn(forbidden, payload)

    def test_reference_images_are_base64_only(self) -> None:
        engine = KimiK3ContentEngine(config=KimiK3Config(api_key="test"), transport=FakeTransport())
        with self.assertRaisesRegex(ValueError, "public image URLs"):
            engine.normalize_request(
                {
                    "source_text": "brief",
                    "reference_images": [
                        {"mime_type": "image/png", "data_base64": "https://example.com/a.png"}
                    ],
                }
            )
        normalized = engine.normalize_request(
            {
                "source_text": "brief",
                "reference_images": [
                    {
                        "mime_type": "image/png",
                        "data_base64": base64.b64encode(b"png").decode("ascii"),
                    }
                ],
            }
        )
        self.assertEqual(normalized["reference_images"][0]["size_bytes"], 3)

    def test_generation_preserves_hhs_native_authority(self) -> None:
        transport = FakeTransport()
        engine = KimiK3ContentEngine(config=KimiK3Config(api_key="test"), transport=transport)
        admitted_ingress = {"ok": True, "provider_result_ingress_root_hash72": "ingress-hash72"}
        with patch(
            "hhs_backend.runtime.hhs_kimi_k3_content_engine_v1.ingress_provider_result",
            return_value=admitted_ingress,
        ):
            result = asyncio.run(
                engine.generate(
                    {
                        "operation": "complete_pipeline",
                        "project_id": "project:test",
                        "title": "Reciprocal Lantern",
                        "source_text": "A lantern follows four phase planes home.",
                        "duration_seconds": 90,
                        "fps": 30,
                        "width": 1080,
                        "height": 1920,
                    }
                )
            )
        plan = result["plan"]
        self.assertTrue(result["ok"])
        self.assertEqual(plan["schema"], PLAN_SCHEMA)
        self.assertEqual(plan["native_mp4"]["frame_count"], 2700)
        self.assertEqual(plan["native_mp4"]["codec"], "h264")
        self.assertEqual(plan["native_mp4"]["pixel_format"], "yuv420p")
        self.assertTrue(plan["hhs_native_handoff"]["external_model_is_proposal"])
        self.assertTrue(plan["hhs_native_handoff"]["hhs_native_renderer_is_authority"])
        self.assertFalse(plan["direct_vm81_mutation_allowed"])
        self.assertFalse(result["native_asset_execution_admitted"])
        self.assertTrue(plan["plan_root_hash72"])
        self.assertNotIn("reasoning_content", json.dumps(result))
        self.assertEqual(
            transport.response_format["json_schema"]["name"],
            "hhs_kimi_k3_content_plan",
        )


if __name__ == "__main__":
    unittest.main()
