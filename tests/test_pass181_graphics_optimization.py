from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_graphics_hydration_v1 import GraphicsHydrationRuntime
from hhs_backend.runtime.hhs_graphics_optimization_v1 import (
    BoundedGraphicsOptimizer,
    CandidateRenderError,
    GraphicsOptimizationError,
    residual_score,
    score_strictly_improves,
    validate_native_renderer_manifest,
)


def _require_media_tools() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("Pass 181 optimization acceptance requires ffmpeg and ffprobe")


def _encode_fixture(path: Path, *, color: str = "black", with_audio: bool = True) -> None:
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-nostdin",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s=64x48:r=4:d=1",
    ]
    if with_audio:
        command.extend(
            [
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:sample_rate=8000:duration=1",
                "-shortest",
            ]
        )
    command.extend(
        [
            "-c:v",
            "mpeg4",
            "-q:v",
            "2",
            "-pix_fmt",
            "yuv420p",
        ]
    )
    if with_audio:
        command.extend(["-c:a", "aac", "-ar", "8000", "-ac", "1"])
    else:
        command.append("-an")
    command.extend(["-movflags", "+faststart", "-y", str(path)])
    subprocess.run(command, check=True, capture_output=True, text=True, timeout=120)


def _renderer_script(path: Path) -> Path:
    script = path / "fake_native_renderer.py"
    script.write_text(
        """from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--recipe', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--manifest', required=True)
args = parser.parse_args()
recipe = json.loads(Path(args.recipe).read_text(encoding='utf-8'))
parameters = recipe['scenes'][0]['layers'][0]['parameters']
color = str(parameters.get('render_color', 'black'))
with_audio = recipe['audio']['mode'] != 'silence'
command = [
    'ffmpeg', '-v', 'error', '-nostdin',
    '-f', 'lavfi', '-i', f'color=c={color}:s=64x48:r=4:d=1',
]
if with_audio:
    command.extend([
        '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=8000:duration=1',
        '-shortest',
    ])
command.extend(['-c:v', 'mpeg4', '-q:v', '2', '-pix_fmt', 'yuv420p'])
if with_audio:
    command.extend(['-c:a', 'aac', '-ar', '8000', '-ac', '1'])
else:
    command.append('-an')
command.extend(['-movflags', '+faststart', '-y', args.output])
subprocess.run(command, check=True, capture_output=True, text=True, timeout=120)
manifest = {
    'schema': 'HHS_P181_NATIVE_RENDER_RESULT_V1',
    'renderer': 'TEST_NATIVE_RENDERER_PROTOCOL_V1',
    'recipe_hash216': recipe['recipe_hash216'],
    'authority': 'HHS_NATIVE_ABI',
    'final_frame_authority': 'HHS_NATIVE_ABI',
    'reference_passthrough': False,
    'single_threaded': True,
    'parallel_computation_logic': False,
}
Path(args.manifest).write_text(json.dumps(manifest, sort_keys=True) + '\\n', encoding='utf-8')
""",
        encoding="utf-8",
    )
    return script


def _recipe(reference: dict, *, color: str, audio_mode: str, variant: int) -> dict:
    video = next(
        timeline
        for timeline in reference["decoded_timelines"]
        if timeline["canonical_projection"]["media_type"] == "video"
    )
    frame_count = int(video["record_count"])
    return {
        "reference_id": reference["reference_id"],
        "target_timeline_hash216": reference["timeline_hash216"],
        "scenes": [
            {
                "scene_id": f"candidate-{variant}",
                "start_frame": 0,
                "end_frame": frame_count,
                "palette": {"x": 5, "y": 17, "z": 41, "w": 53},
                "layers": [
                    {
                        "layer_id": f"native-background-{variant}",
                        "type": "background",
                        "source_type": "native_sprite_map",
                        "authority": "HHS_NATIVE_ABI",
                        "parameters": {
                            "render_color": color,
                            "render_variant": variant,
                        },
                    }
                ],
                "captions": [],
                "camera": {"mode": "static"},
                "lighting": {"mode": "native_flat"},
                "transition": {"mode": "cut", "duration_frames": 0},
            }
        ],
        "audio": {
            "mode": audio_mode,
            "parameters": {"frequency": 440, "sample_rate": 8000},
        },
    }


def _residual_report(*, frame: int, audio: int, timing: int, missing: int, provenance: int = 0) -> dict:
    residuals = []
    if frame:
        residuals.append({"class": "FRAME_CONTENT_RESIDUAL"})
    if audio:
        residuals.append({"class": "AUDIO_CONTENT_RESIDUAL"})
    if timing:
        residuals.append({"class": "TIMELINE_RESIDUAL"})
    if provenance:
        residuals.append({"class": "UNEXPLAINED_PIXEL_PROVENANCE", "mismatch_count": provenance})
    return {
        "video": {
            "content_mismatches": frame,
            "timing_mismatches": timing,
            "missing_records": missing,
            "extra_records": 0,
        },
        "audio": {
            "content_mismatches": audio,
            "timing_mismatches": 0,
            "missing_records": 0,
            "extra_records": 0,
        },
        "residuals": residuals,
        "exact_decoded_audiovisual_match": not any((frame, audio, timing, missing, provenance)),
        "residual_report_hash216": "synthetic-residual-root",
    }


def test_residual_score_is_exact_and_lexicographic() -> None:
    weak = residual_score(_residual_report(frame=4, audio=2, timing=1, missing=3))
    strong = residual_score(_residual_report(frame=1, audio=0, timing=0, missing=0))
    exact = residual_score(_residual_report(frame=0, audio=0, timing=0, missing=0))
    provenance_failure = residual_score(
        _residual_report(frame=0, audio=0, timing=0, missing=0, provenance=1)
    )
    assert score_strictly_improves(strong, weak)
    assert score_strictly_improves(exact, strong)
    assert not score_strictly_improves(weak, strong)
    assert provenance_failure[0] == 1
    assert exact == [0, 0, 0, 0, 0, 0]


def test_renderer_manifest_requires_native_no_passthrough_authority() -> None:
    valid = {
        "renderer": "native-test",
        "recipe_hash216": "recipe-root",
        "authority": "HHS_NATIVE_ABI",
        "final_frame_authority": "HHS_NATIVE_ABI",
        "reference_passthrough": False,
        "single_threaded": True,
        "parallel_computation_logic": False,
    }
    assert validate_native_renderer_manifest(valid, "recipe-root")["renderer"] == "native-test"
    invalid = dict(valid)
    invalid["reference_passthrough"] = True
    with pytest.raises(CandidateRenderError, match="reference_passthrough"):
        validate_native_renderer_manifest(invalid, "recipe-root")


def test_optimizer_accepts_only_strict_improvements_and_persists_closure(tmp_path: Path) -> None:
    _require_media_tools()
    reference_mp4 = tmp_path / "reference.mp4"
    _encode_fixture(reference_mp4, color="black", with_audio=True)
    hydration = GraphicsHydrationRuntime(tmp_path / "hydration")
    reference = hydration.build_decode_manifest(reference_mp4, logical_name="optimization-reference")
    renderer = _renderer_script(tmp_path)
    optimizer = BoundedGraphicsOptimizer(
        tmp_path / "optimizer",
        renderer_command=[sys.executable, str(renderer)],
    )
    candidates = [
        _recipe(reference, color="white", audio_mode="silence", variant=1),
        _recipe(reference, color="black", audio_mode="native_synthesis", variant=2),
        _recipe(reference, color="white", audio_mode="silence", variant=3),
    ]
    created = optimizer.create_job(
        reference_manifest=reference,
        candidate_recipes=candidates,
        timeout_seconds=300,
        render_timeout_seconds=120,
        stop_on_exact=False,
    )
    assert created["state"] == "QUEUED"
    final = optimizer.run_job(created["job_id"])
    assert final["state"] == "SUCCEEDED"
    assert final["completion_status"] == "HHS_GRAPHICS_OPTIMIZATION_BOUNDED_CLOSURE_VERIFIED"
    assert final["accepted_count"] == 2
    assert final["rejected_count"] == 1
    assert final["incumbent_candidate_index"] == 1
    assert final["incumbent_score"] == [0, 0, 0, 0, 0, 0]
    assert [entry["decision"] for entry in final["history"]] == [
        "ACCEPTED_STRICT_IMPROVEMENT",
        "ACCEPTED_STRICT_IMPROVEMENT",
        "REJECTED_NO_STRICT_IMPROVEMENT",
    ]
    assert Path(final["record_path"]).is_file()
    replayed = optimizer.get_job(created["job_id"])
    assert replayed["job_state_hash216"] == final["job_state_hash216"]
    retry = optimizer.retry_job(created["job_id"])
    assert retry["state"] == "QUEUED"
    assert retry["request"]["parent_job_id"] == created["job_id"]


def test_optimizer_cancellation_and_unconfigured_renderer_fail_closed(tmp_path: Path) -> None:
    reference = {
        "reference_id": "reference-root",
        "timeline_hash216": "timeline-root",
        "decoded_timelines": [
            {
                "source_stream_index": 0,
                "canonical_projection": {"media_type": "video"},
                "record_count": 1,
                "records": [
                    {"stream": 0, "dts": 0, "pts": 0, "duration": 1, "size_bytes": 4, "sha256": "frame"}
                ],
            }
        ],
    }
    candidate = {
        "reference_id": "reference-root",
        "target_timeline_hash216": "timeline-root",
        "scenes": [
            {
                "start_frame": 0,
                "end_frame": 1,
                "palette": {"x": 0, "y": 12, "z": 36, "w": 48},
                "layers": [
                    {
                        "layer_id": "layer",
                        "type": "background",
                        "source_type": "native_sprite_map",
                        "authority": "HHS_NATIVE_ABI",
                        "parameters": {},
                    }
                ],
                "captions": [],
                "camera": {"mode": "static"},
                "lighting": {},
                "transition": {},
            }
        ],
        "audio": {"mode": "silence", "parameters": {}},
    }
    optimizer = BoundedGraphicsOptimizer(tmp_path / "optimizer", renderer_command=[])
    cancelled = optimizer.create_job(
        reference_manifest=reference,
        candidate_recipes=[candidate],
        timeout_seconds=60,
        render_timeout_seconds=30,
    )
    optimizer.cancel_job(cancelled["job_id"])
    cancelled_final = optimizer.step_job(cancelled["job_id"])
    assert cancelled_final["state"] == "CANCELLED"

    failed = optimizer.create_job(
        reference_manifest=reference,
        candidate_recipes=[candidate],
        timeout_seconds=60,
        render_timeout_seconds=30,
    )
    failed_final = optimizer.step_job(failed["job_id"])
    assert failed_final["state"] == "FAILED"
    assert failed_final["failure_reason"] == "P181_NATIVE_RENDERER_NOT_CONFIGURED_OR_UNAVAILABLE"


def test_retry_requires_final_job(tmp_path: Path) -> None:
    optimizer = BoundedGraphicsOptimizer(tmp_path / "optimizer", renderer_command=[])
    reference = {
        "reference_id": "reference-root",
        "timeline_hash216": "timeline-root",
        "decoded_timelines": [
            {
                "source_stream_index": 0,
                "canonical_projection": {"media_type": "video"},
                "record_count": 1,
                "records": [
                    {"stream": 0, "dts": 0, "pts": 0, "duration": 1, "size_bytes": 4, "sha256": "frame"}
                ],
            }
        ],
    }
    candidate = {
        "reference_id": "reference-root",
        "target_timeline_hash216": "timeline-root",
        "scenes": [
            {
                "start_frame": 0,
                "end_frame": 1,
                "palette": {"x": 0, "y": 12, "z": 36, "w": 48},
                "layers": [
                    {
                        "layer_id": "layer",
                        "type": "background",
                        "source_type": "native_sprite_map",
                        "authority": "HHS_NATIVE_ABI",
                        "parameters": {},
                    }
                ],
                "captions": [],
                "camera": {"mode": "static"},
                "lighting": {},
                "transition": {},
            }
        ],
        "audio": {"mode": "silence", "parameters": {}},
    }
    job = optimizer.create_job(
        reference_manifest=reference,
        candidate_recipes=[candidate],
        timeout_seconds=60,
        render_timeout_seconds=30,
    )
    with pytest.raises(GraphicsOptimizationError, match="RETRY_REQUIRES_FINAL_JOB"):
        optimizer.retry_job(job["job_id"])
