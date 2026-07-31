from __future__ import annotations

import io
import wave
from pathlib import Path

from fastapi.testclient import TestClient

from hhs_backend.visual_server import app


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _wav_bytes(seconds: int = 1, sample_rate: int = 8000) -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        samples = bytearray()
        period = max(2, sample_rate // 220)
        for index in range(sample_rate * seconds):
            value = 1800 if index % period < period // 2 else -1800
            samples.extend(int(value).to_bytes(2, "little", signed=True))
        handle.writeframes(bytes(samples))
    return output.getvalue()


def test_storybook_reel_routes_are_registered_before_static_root():
    paths = [getattr(route, "path", None) for route in app.router.routes]
    required = {
        "/api/runtime/storybook-reel/status",
        "/api/runtime/storybook-reel/defaults",
        "/api/runtime/storybook-reel/audio",
        "/api/runtime/storybook-reel/generate",
        "/api/runtime/storybook-reel/artifacts/{artifact_id}",
        "/api/runtime/storybook-reel/artifacts/{artifact_id}/download.zip",
        "/api/runtime/storybook-reel/artifacts/{artifact_id}/video.mp4",
    }
    assert required <= set(paths)
    root_index = next(index for index, route in enumerate(app.router.routes) if getattr(route, "name", None) == "hhs-visual-home")
    for path in required:
        route_index = next(index for index, route in enumerate(app.router.routes) if getattr(route, "path", None) == path)
        assert route_index < root_index


def test_no_code_studio_and_contextual_defaults_are_reachable():
    client = TestClient(app)
    studio = client.get("/storybook-reel/")
    assert studio.status_code == 200
    assert "HHS Storybook Reel Studio" in studio.text
    assert "Upload narration audio" in studio.text
    assert "Generate 90-second reel" in studio.text
    defaults = client.post(
        "/api/runtime/storybook-reel/defaults",
        json={"text": "A hero reached the checkpoint gate in the final game level."},
    )
    assert defaults.status_code == 200
    payload = defaults.json()
    assert payload["template_id"] == "platformer_quest"
    assert payload["palette"]["phase_planes"]["z"] == (
        payload["palette"]["phase_planes"]["x"] + 36
    ) % 72


def test_audio_can_be_uploaded_without_multipart_or_backend_knowledge():
    client = TestClient(app)
    response = client.post(
        "/api/runtime/storybook-reel/audio",
        content=_wav_bytes(),
        headers={
            "Content-Type": "audio/wav",
            "X-HHS-Filename": "narration.wav",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["audio_id"].startswith("audio:")
    assert payload["size_bytes"] > 0
    assert len(payload["audio_root_hash72"]) == 72
    assert payload["codec_name"] == "pcm_s16le"


def test_static_studio_uses_no_external_frontend_dependencies():
    client = TestClient(app)
    javascript = client.get("/storybook-reel/app.js")
    stylesheet = client.get("/storybook-reel/styles.css")
    assert javascript.status_code == 200
    assert stylesheet.status_code == 200
    assert "https://" not in javascript.text
    assert "import " not in javascript.text
    assert "parallel workers" in javascript.text


def test_main_visual_ide_exposes_storybook_reel_without_route_knowledge():
    coordinator = (
        REPOSITORY_ROOT
        / "applications"
        / "holofractal_harmonizer"
        / "src"
        / "production-startup-coordinator.mjs"
    ).read_text(encoding="utf-8")
    assert "installStorybookReelLauncher" in coordinator
    assert "href = '/storybook-reel/'" in coordinator
    assert "Open the no-code 90-second storybook reel studio" in coordinator
    assert "storybook_reel_requests_never_deferred: true" in coordinator
