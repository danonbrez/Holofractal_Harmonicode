#!/usr/bin/env python3
"""Production-oriented validation for the Pass 203 high-fidelity native renderer."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def unwrap(value: Any) -> Any:
    if isinstance(value, Mapping) and isinstance(value.get("payload"), Mapping):
        return value["payload"]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    native = repo / "native_projects" / "hhs_storybook_reel"

    with tempfile.TemporaryDirectory(prefix="hhs-pass203-render-") as directory:
        from fastapi.testclient import TestClient
        from hhs_backend.application_ide_server import app
        from hhs_backend.runtime.hhs_storybook_reel_v3 import STORYBOOK_REEL_RUNTIME

        catalog = STORYBOOK_REEL_RUNTIME.parameter_catalog()
        presets = STORYBOOK_REEL_RUNTIME.presets()
        status = STORYBOOK_REEL_RUNTIME.status()
        resolved = STORYBOOK_REEL_RUNTIME.resolve_parameters(
            {
                "text": "The sixth candle waited beside the silent clock.",
                "quality_profile": "production_vertical_1440",
                "render": {
                    "contrast": "1.12",
                    "saturation": "1.22",
                    "background_blur": 38,
                    "sharpen_luma": "0.58",
                },
                "native_layers": {
                    "texture": {name: True for name in ("field", "midground", "materials", "semantic", "player")},
                    "sprite": {name: True for name in ("atmosphere", "phase", "glows", "vignette", "hud")},
                },
            }
        )
        filter_graph = STORYBOOK_REEL_RUNTIME.video_filter_graph(resolved["render"])

        layout = subprocess.run(
            ["make", "-C", str(native), "print-source-layout"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        build = subprocess.run(
            ["make", "-C", str(native), "test-projection"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            timeout=900,
        )
        assert "HHS_PASS_203_NATIVE_PROJECTION_BRIDGE_VERIFIED" in build.stdout
        assert "GAME_SRC_DIR=" in layout.stdout
        assert status["cumulative_system_version"] == 203
        assert status["logical_frame_is_output_quality_ceiling"] is False
        assert catalog["all_parameters_publicly_enumerated"] is True
        assert catalog["compiled_constants_are_read_only"] is True
        assert catalog["parameter_count"] > 50
        assert len(catalog["native_layer_fields"]) == 10
        assert len(presets["quality_profiles"]) >= 5
        assert resolved["render"]["output_width"] == 1440
        assert resolved["render"]["output_height"] == 2560
        assert resolved["native_layers"]["texture_flags"] == 31
        assert resolved["native_layers"]["sprite_overlay_flags"] == 31
        assert "flags=lanczos" in filter_graph
        assert "gblur=sigma=38" in filter_graph
        assert "unsharp=" in filter_graph
        assert "pad=1080:1920:0:474" not in filter_graph

        with TestClient(app) as client:
            response = client.get("/api/runtime/storybook-reel/parameters")
            assert response.status_code == 200
            hosted_catalog = unwrap(response.json())
            assert hosted_catalog["catalog_hash72"] == catalog["catalog_hash72"]

            response = client.post(
                "/api/runtime/storybook-reel/resolve",
                json={
                    "text": "The sixth candle waited beside the silent clock.",
                    "quality_profile": "production_vertical_2160",
                    "render": {"video_preset": "slower", "crf": 14},
                },
            )
            assert response.status_code == 200
            hosted_resolution = unwrap(response.json())
            assert hosted_resolution["render"]["output_width"] == 2160
            assert hosted_resolution["render"]["output_height"] == 3840

        evidence = {
            "schema": "HHS_PASS_203_HIGH_FIDELITY_RENDER_VALIDATION_RECEIPT_V1",
            "contract": catalog["contract"],
            "classification": catalog["classification"],
            "closed": True,
            "cumulative_system_version": 203,
            "all_prior_passes_inherited": True,
            "summary": {
                "parameter_count": catalog["parameter_count"],
                "style_parameter_count": len(catalog["style_fields"]),
                "native_layer_parameter_count": len(catalog["native_layer_fields"]),
                "render_parameter_count": len(catalog["render_fields"]),
                "compiled_native_constant_record_count": len(catalog["compiled_native_constants"]),
                "quality_profile_count": len(presets["quality_profiles"]),
                "validated_output_width": resolved["render"]["output_width"],
                "validated_output_height": resolved["render"]["output_height"],
                "texture_flags": resolved["native_layers"]["texture_flags"],
                "sprite_overlay_flags": resolved["native_layers"]["sprite_overlay_flags"],
            },
            "catalog_hash72": catalog["catalog_hash72"],
            "resolution_hash72": resolved["resolution_hash72"],
            "filter_graph_sha256": hashlib.sha256(filter_graph.encode("utf-8")).hexdigest(),
            "source_layout": layout.stdout.strip(),
            "native_projection_test": build.stdout.strip(),
            "claim_boundary": {
                "logical_frame_is_output_quality_ceiling": False,
                "native_frame_identity_preserved": True,
                "all_mutable_parameters_publicly_enumerated": True,
                "compiled_constants_public_and_read_only": True,
                "native_layers_publicly_selectable": True,
                "frontend_is_authority": False,
                "parallel_computation_used": False,
            },
        }
        evidence["receipt_sha256"] = sha256(evidence)

    output = Path(args.evidence)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
