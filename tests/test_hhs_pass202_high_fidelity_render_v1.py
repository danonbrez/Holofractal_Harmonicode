from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.storybook_reel_routes import router
from hhs_backend.runtime.hhs_storybook_reel_v2 import (
    CLASSIFICATION,
    CONTRACT,
    QUALITY_PRESETS,
    SPRITE_OVERLAY_BITS,
    TEXTURE_LAYER_BITS,
    HighFidelityStorybookReelRuntime,
)


class Pass202HighFidelityRenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = HighFidelityStorybookReelRuntime(Path(self.temp.name))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_parameter_catalog_exposes_complete_mutable_and_locked_surface(self) -> None:
        catalog = self.runtime.parameter_catalog()
        self.assertEqual(catalog["contract"], CONTRACT)
        self.assertEqual(catalog["classification"], CLASSIFICATION)
        self.assertTrue(catalog["all_parameters_publicly_enumerated"])
        self.assertTrue(catalog["compiled_constants_are_read_only"])
        style_names = {field["name"] for field in catalog["style_fields"]}
        self.assertIn("font_effect", style_names)
        self.assertIn("effect_amplitude", style_names)
        for plane in "xyzw":
            for component in ("r", "g", "b"):
                self.assertIn(f"manual_{plane}.{component}", style_names)
        native_names = {field["name"] for field in catalog["native_layer_fields"]}
        self.assertEqual(native_names, set(TEXTURE_LAYER_BITS) | set(SPRITE_OVERLAY_BITS))
        locked = {field["name"]: field for field in catalog["authority_locked_fields"]}
        self.assertEqual(locked["logical_width"]["value"], 160)
        self.assertEqual(locked["logical_height"]["value"], 144)
        self.assertFalse(locked["logical_width"]["mutable"])
        self.assertGreater(catalog["parameter_count"], 60)

    def test_contextual_defaults_return_three_scored_candidates_and_production_profile(self) -> None:
        defaults = self.runtime.contextual_defaults(
            "A clockmaker frees a silent bell from a candle in an old town fable."
        )
        self.assertEqual(defaults["quality_profile"], "production_vertical_1080")
        self.assertEqual(defaults["candidate_count"], 3)
        self.assertEqual(len(defaults["template_candidates"]), 3)
        scores = [candidate["score"] for candidate in defaults["template_candidates"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(defaults["reason_trace_public"])
        self.assertEqual(defaults["template_candidates"][0]["template_id"], "serif_fable")

    def test_all_quality_presets_resolve_deterministically(self) -> None:
        for profile_id, preset in QUALITY_PRESETS.items():
            first = self.runtime.resolve_parameters({"text": "A story", "quality_profile": profile_id})
            second = self.runtime.resolve_parameters({"text": "A story", "quality_profile": profile_id})
            self.assertEqual(first, second)
            self.assertEqual(first["quality_profile"], profile_id)
            self.assertEqual(first["render"]["output_width"], preset["output_width"])
            self.assertEqual(first["render"]["output_height"], preset["output_height"])
            self.assertEqual(first["native_layers"]["texture_flags"], 31)
            self.assertEqual(first["native_layers"]["sprite_overlay_flags"], 31)
            self.assertEqual(len(first["resolution_hash72"]), 72)

    def test_native_layer_masks_are_effective_and_exact(self) -> None:
        resolved = self.runtime.resolve_parameters(
            {
                "text": "Layer test",
                "native_layers": {
                    "texture": {
                        "field": True,
                        "midground": False,
                        "materials": True,
                        "semantic": False,
                        "player": True,
                    },
                    "sprite": {
                        "atmosphere": False,
                        "phase": True,
                        "glows": False,
                        "vignette": True,
                        "hud": False,
                    },
                },
            }
        )
        self.assertEqual(resolved["native_layers"]["texture_flags"], 1 | 4 | 16)
        self.assertEqual(resolved["native_layers"]["sprite_overlay_flags"], 2 | 8)

    def test_production_filter_is_high_fidelity_not_fixed_neighbor_black_padding(self) -> None:
        resolved = self.runtime.resolve_parameters({"text": "High fidelity"})
        graph = self.runtime.video_filter_graph(resolved["render"])
        self.assertIn("split=2", graph)
        self.assertIn("gblur=sigma=30", graph)
        self.assertIn("flags=lanczos", graph)
        self.assertIn("overlay=(W-w)/2:(H-h)/2", graph)
        self.assertNotIn("scale=1080:972:flags=neighbor,pad=1080:1920:0:474", graph)
        self.assertNotIn("color=0x0b0910[v]", graph)

    def test_integer_native_mode_remains_intentional_option(self) -> None:
        resolved = self.runtime.resolve_parameters(
            {"text": "Crisp pixels", "quality_profile": "native_integer_1080"}
        )
        graph = self.runtime.video_filter_graph(resolved["render"])
        self.assertIn("flags=neighbor", graph)
        self.assertIn("pad=1080:1920", graph)
        self.assertEqual(resolved["render"]["fit_mode"], "native_integer")

    def test_invalid_parameters_fail_closed(self) -> None:
        invalid_payloads = (
            {"render": {"output_width": 1079}},
            {"render": {"fit_mode": "demo_low_res"}},
            {"render": {"scale_filter": "unknown"}},
            {"render": {"background_color": "black"}},
            {"render": {"contrast": "99"}},
            {"render": {"video_codec": "arbitrary"}},
            {"render": {"audio_bitrate": "lossless"}},
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    self.runtime.resolve_parameters({"text": "Reject", **payload})

    def test_pass202_resolution_is_bound_into_style_evidence(self) -> None:
        resolved = self.runtime.resolve_parameters(
            {"text": "Evidence", "quality_profile": "production_vertical_1440"}
        )
        self.runtime._active_pass202_resolution = resolved
        try:
            style = self.runtime._style("Evidence", None, {})
            args = self.runtime._style_cli_arguments(style)
        finally:
            self.runtime._active_pass202_resolution = None
        self.assertEqual(
            style["values"]["pass202_resolution_hash72"],
            resolved["resolution_hash72"],
        )
        self.assertIn("--texture-flags", args)
        self.assertIn("--sprite-overlay-flags", args)
        self.assertIn("31", args)

    def test_api_parameter_surfaces_are_public_and_machine_correctable(self) -> None:
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        for path in (
            "/api/runtime/storybook-reel/status",
            "/api/runtime/storybook-reel/parameters",
            "/api/runtime/storybook-reel/presets",
        ):
            response = client.get(path)
            self.assertEqual(response.status_code, 200, response.text)
        candidates = client.post(
            "/api/runtime/storybook-reel/defaults/candidates",
            json={"text": "A candle and bell fable"},
        )
        self.assertEqual(candidates.status_code, 200, candidates.text)
        self.assertEqual(candidates.json()["candidate_count"], 3)
        resolved = client.post(
            "/api/runtime/storybook-reel/parameters/resolve",
            json={"text": "A candle", "quality_profile": "production_vertical_2160"},
        )
        self.assertEqual(resolved.status_code, 200, resolved.text)
        self.assertEqual(resolved.json()["render"]["output_height"], 3840)
        rejected = client.post(
            "/api/runtime/storybook-reel/parameters/resolve",
            json={"text": "A candle", "render": {"output_width": 1079}},
        )
        self.assertEqual(rejected.status_code, 422, rejected.text)
        detail = rejected.json()["detail"]
        self.assertFalse(detail["retryable"])
        self.assertIn("remediation", detail)
        self.assertFalse(detail["frontend_result_fabricated"])


if __name__ == "__main__":
    unittest.main()
