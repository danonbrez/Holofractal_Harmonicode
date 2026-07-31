"""Finite, restartable graphics hydration optimization for HHS Pass 181.

The controller admits validated native recipes, invokes one fixed native renderer
command, canonically decodes each resulting MP4, compares it with the immutable
reference timeline, and mutates the incumbent only when an exact integer score
strictly improves. Rejected proposals remain evidence and never acquire runtime
authority. No background worker or parallel candidate execution is used.
"""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from hhs_backend.runtime.hhs_graphics_mp4_decode_v1 import CanonicalMp4Decoder, Mp4DecodeError
from hhs_backend.runtime.hhs_graphics_recipe_v1 import (
    NativeRecipeError,
    NativeRecipeRuntime,
    validate_native_reconstruction_recipe,
)
from hhs_installer.canonical import canonical_bytes, hash72, hash216, stable

CONTRACT = "HHS-P181-NCSR-GHIR-VM81-H72-H216"
AUTHORITY = "HHS_VM81_SINGLETON_GRAPHICS_HYDRATION_AUTHORITY_V1"
OPTIMIZATION_REQUEST_DOMAIN = "HHS-P181-GRAPHICS-OPTIMIZATION-REQUEST-V1"
OPTIMIZATION_JOB_DOMAIN = "HHS-P181-GRAPHICS-OPTIMIZATION-JOB-V1"
NATIVE_OUTPUT_DOMAIN = "HHS-P181-NATIVE-RENDER-OUTPUT-V1"
OPTIMIZATION_RECEIPT_DOMAIN = "HHS-P181-GRAPHICS-OPTIMIZATION-RECEIPT-V1"
MAX_CANDIDATES = 72
MAX_TIMEOUT_SECONDS = 24 * 60 * 60
DEFAULT_TIMEOUT_SECONDS = 60 * 60
DEFAULT_RENDER_TIMEOUT_SECONDS = 30 * 60
FINAL_STATES = frozenset({"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT"})
TRANSIENT_STATES = frozenset({"QUEUED", "RUNNING", "CANCEL_REQUESTED"})


class GraphicsOptimizationError(ValueError):
    """Raised when optimizer authority or job-state rules reject an operation."""


class CandidateRenderError(RuntimeError):
    """A candidate-local rendering or verification failure."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _artifact_filename(canonical_identity: str) -> str:
    return hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest() + ".json"


def _renderer_environment() -> Dict[str, str]:
    environment = dict(os.environ)
    environment.update(
        {
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        }
    )
    return environment


def _integer(value: Any, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GraphicsOptimizationError(code)
    return value


def residual_score(report: Mapping[str, Any]) -> list[int]:
    """Return a deterministic lexicographic score; lower is always better."""

    if not isinstance(report, Mapping):
        raise GraphicsOptimizationError("P181_RESIDUAL_REPORT_REQUIRED")
    video = report.get("video")
    audio = report.get("audio")
    residuals = report.get("residuals")
    if not isinstance(video, Mapping) or not isinstance(audio, Mapping) or not isinstance(residuals, list):
        raise GraphicsOptimizationError("P181_RESIDUAL_REPORT_SHAPE_INVALID")

    def count(container: Mapping[str, Any], key: str) -> int:
        value = _integer(container.get(key, 0), f"P181_RESIDUAL_{key.upper()}_INVALID")
        if value < 0:
            raise GraphicsOptimizationError(f"P181_RESIDUAL_{key.upper()}_NEGATIVE")
        return value

    semantic_total = 0
    provenance_total = 0
    for residual in residuals:
        if not isinstance(residual, Mapping):
            raise GraphicsOptimizationError("P181_TYPED_RESIDUAL_INVALID")
        residual_class = str(residual.get("class") or "")
        mismatch_count = residual.get("mismatch_count", 0)
        if isinstance(mismatch_count, bool) or not isinstance(mismatch_count, int) or mismatch_count < 0:
            raise GraphicsOptimizationError("P181_TYPED_RESIDUAL_COUNT_INVALID")
        if residual_class == "UNEXPLAINED_PIXEL_PROVENANCE":
            provenance_total += mismatch_count
        elif residual_class not in {"FRAME_CONTENT_RESIDUAL", "AUDIO_CONTENT_RESIDUAL", "TIMELINE_RESIDUAL"}:
            semantic_total += mismatch_count

    missing_extra = (
        count(video, "missing_records")
        + count(video, "extra_records")
        + count(audio, "missing_records")
        + count(audio, "extra_records")
    )
    timing = count(video, "timing_mismatches") + count(audio, "timing_mismatches")
    frame_content = count(video, "content_mismatches")
    audio_content = count(audio, "content_mismatches")
    score = [
        provenance_total,
        missing_extra,
        timing,
        frame_content,
        audio_content,
        semantic_total,
    ]
    declared_exact = bool(report.get("exact_decoded_audiovisual_match"))
    if declared_exact != all(value == 0 for value in score):
        raise GraphicsOptimizationError("P181_RESIDUAL_EXACTNESS_CONTRADICTION")
    return score


def score_strictly_improves(candidate: Sequence[int], incumbent: Optional[Sequence[int]]) -> bool:
    candidate_values = tuple(int(value) for value in candidate)
    if any(value < 0 for value in candidate_values):
        raise GraphicsOptimizationError("P181_CANDIDATE_SCORE_NEGATIVE")
    if incumbent is None:
        return True
    incumbent_values = tuple(int(value) for value in incumbent)
    if len(candidate_values) != len(incumbent_values):
        raise GraphicsOptimizationError("P181_SCORE_DIMENSION_MISMATCH")
    return candidate_values < incumbent_values


def validate_native_renderer_manifest(manifest: Mapping[str, Any], recipe_hash216: str) -> Dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise CandidateRenderError("P181_NATIVE_RENDERER_MANIFEST_REQUIRED")
    required = {
        "authority": "HHS_NATIVE_ABI",
        "final_frame_authority": "HHS_NATIVE_ABI",
        "reference_passthrough": False,
        "single_threaded": True,
        "parallel_computation_logic": False,
    }
    for key, expected in required.items():
        if manifest.get(key) != expected:
            raise CandidateRenderError(f"P181_NATIVE_RENDERER_MANIFEST_REJECTED:{key}")
    if str(manifest.get("recipe_hash216") or "") != str(recipe_hash216):
        raise CandidateRenderError("P181_NATIVE_RENDERER_RECIPE_IDENTITY_MISMATCH")
    renderer = str(manifest.get("renderer") or "").strip()
    if not renderer:
        raise CandidateRenderError("P181_NATIVE_RENDERER_IDENTITY_REQUIRED")
    return stable(manifest)


class BoundedGraphicsOptimizer:
    """Serialized, one-candidate-per-step optimization authority."""

    def __init__(
        self,
        artifact_root: Path,
        *,
        renderer_command: Optional[Sequence[str]] = None,
    ) -> None:
        self.artifact_root = Path(artifact_root)
        self.job_root = self.artifact_root / "optimization_jobs"
        self.job_root.mkdir(parents=True, exist_ok=True)
        configured = os.environ.get("HHS_GRAPHICS_NATIVE_RENDERER", "").strip()
        resolved_command = list(renderer_command or (shlex.split(configured) if configured else []))
        self.renderer_command = tuple(str(item) for item in resolved_command if str(item))
        self.decode_runtime = CanonicalMp4Decoder(self.artifact_root / "optimization_decode_manifests")
        self.recipe_runtime = NativeRecipeRuntime(self.artifact_root / "optimization_native_reconstruction")
        self._authority_lock = threading.RLock()

    def status(self) -> Dict[str, Any]:
        executable = self.renderer_command[0] if self.renderer_command else ""
        renderer_available = bool(
            executable
            and (
                Path(executable).expanduser().is_file()
                or shutil.which(executable) is not None
            )
        )
        return {
            "schema": "HHS_P181_GRAPHICS_OPTIMIZER_STATUS_V1",
            "ok": True,
            "authority": AUTHORITY,
            "single_commit_authority": True,
            "parallel_candidate_execution": False,
            "background_worker": False,
            "candidate_step_model": "ONE_CANDIDATE_PER_STEP",
            "renderer_configured": bool(self.renderer_command),
            "renderer_available": renderer_available,
            "max_candidates": MAX_CANDIDATES,
            "final_states": sorted(FINAL_STATES),
        }

    def _job_directory(self, job_id: str) -> Path:
        if not isinstance(job_id, str) or not job_id.startswith("opt:"):
            raise GraphicsOptimizationError("P181_OPTIMIZATION_JOB_ID_INVALID")
        locator = hashlib.sha256(job_id.encode("utf-8")).hexdigest()
        return self.job_root / locator

    def _job_path(self, job_id: str) -> Path:
        return self._job_directory(job_id) / "job.json"

    def _write_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        identity_payload = {key: value for key, value in job.items() if key not in {"receipt_hash72", "record_path"}}
        job["job_state_hash216"] = hash216(identity_payload, domain=OPTIMIZATION_JOB_DOMAIN)
        receipt_payload = {key: value for key, value in job.items() if key != "receipt_hash72"}
        job["receipt_hash72"] = hash72(receipt_payload, domain=OPTIMIZATION_RECEIPT_DOMAIN)
        directory = self._job_directory(str(job["job_id"]))
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "job.json"
        path.write_bytes(canonical_bytes(job))
        return {**job, "record_path": str(path)}

    def _read_job(self, job_id: str) -> Dict[str, Any]:
        path = self._job_path(job_id)
        if not path.is_file():
            raise GraphicsOptimizationError("P181_OPTIMIZATION_JOB_UNKNOWN")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise GraphicsOptimizationError("P181_OPTIMIZATION_JOB_RECORD_INVALID") from error
        if payload.get("job_id") != job_id:
            raise GraphicsOptimizationError("P181_OPTIMIZATION_JOB_RECORD_IDENTITY_MISMATCH")
        return payload

    def get_job(self, job_id: str) -> Dict[str, Any]:
        with self._authority_lock:
            job = self._read_job(job_id)
            return {**job, "record_path": str(self._job_path(job_id))}

    def create_job(
        self,
        *,
        reference_manifest: Mapping[str, Any],
        candidate_recipes: Sequence[Mapping[str, Any]],
        baseline_residual_report: Optional[Mapping[str, Any]] = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        render_timeout_seconds: int = DEFAULT_RENDER_TIMEOUT_SECONDS,
        stop_on_exact: bool = True,
        parent_job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self._authority_lock:
            if not isinstance(reference_manifest, Mapping):
                raise GraphicsOptimizationError("P181_REFERENCE_MANIFEST_REQUIRED")
            reference_id = str(reference_manifest.get("reference_id") or "")
            timeline_hash216 = str(reference_manifest.get("timeline_hash216") or "")
            if not reference_id or not timeline_hash216:
                raise GraphicsOptimizationError("P181_REFERENCE_TIMELINE_IDENTITY_REQUIRED")
            if not isinstance(candidate_recipes, Sequence) or isinstance(candidate_recipes, (str, bytes)):
                raise GraphicsOptimizationError("P181_CANDIDATE_RECIPE_LIST_REQUIRED")
            if not candidate_recipes or len(candidate_recipes) > MAX_CANDIDATES:
                raise GraphicsOptimizationError("P181_CANDIDATE_COUNT_REJECTED")
            timeout_seconds = _integer(timeout_seconds, "P181_OPTIMIZATION_TIMEOUT_INVALID")
            render_timeout_seconds = _integer(render_timeout_seconds, "P181_RENDER_TIMEOUT_INVALID")
            if timeout_seconds <= 0 or timeout_seconds > MAX_TIMEOUT_SECONDS:
                raise GraphicsOptimizationError("P181_OPTIMIZATION_TIMEOUT_REJECTED")
            if render_timeout_seconds <= 0 or render_timeout_seconds > timeout_seconds:
                raise GraphicsOptimizationError("P181_RENDER_TIMEOUT_REJECTED")

            validated_candidates = []
            seen = set()
            for recipe in candidate_recipes:
                try:
                    validated = validate_native_reconstruction_recipe(recipe, reference_manifest)
                except NativeRecipeError as error:
                    raise GraphicsOptimizationError(str(error)) from error
                candidate_id = str(validated["recipe_hash216"])
                if candidate_id in seen:
                    raise GraphicsOptimizationError("P181_DUPLICATE_CANDIDATE_RECIPE")
                seen.add(candidate_id)
                validated_candidates.append(validated)

            incumbent_score = None
            incumbent_residual_hash216 = None
            if baseline_residual_report is not None:
                incumbent_score = residual_score(baseline_residual_report)
                incumbent_residual_hash216 = str(
                    baseline_residual_report.get("residual_report_hash216") or "baseline-unidentified"
                )

            request = {
                "reference_manifest": stable(reference_manifest),
                "candidate_recipes": validated_candidates,
                "baseline_residual_report": stable(baseline_residual_report) if baseline_residual_report is not None else None,
                "timeout_seconds": timeout_seconds,
                "render_timeout_seconds": render_timeout_seconds,
                "stop_on_exact": bool(stop_on_exact),
                "parent_job_id": parent_job_id,
            }
            request_hash216 = hash216(request, domain=OPTIMIZATION_REQUEST_DOMAIN)
            now_ns = time.time_ns()
            nonce = uuid.uuid4().hex
            job_id = "opt:" + hashlib.sha256(
                canonical_bytes({"request_hash216": request_hash216, "nonce": nonce, "created_unix_ns": now_ns})
            ).hexdigest()
            job = {
                "schema": "HHS_P181_GRAPHICS_OPTIMIZATION_JOB_V1",
                "job_id": job_id,
                "contract": CONTRACT,
                "authority": AUTHORITY,
                "state": "QUEUED",
                "created_unix_ns": now_ns,
                "updated_unix_ns": now_ns,
                "deadline_unix_ns": now_ns + timeout_seconds * 1_000_000_000,
                "request_hash216": request_hash216,
                "request": request,
                "next_candidate_index": 0,
                "accepted_count": 0,
                "rejected_count": 0,
                "cancel_requested": False,
                "incumbent_score": incumbent_score,
                "incumbent_recipe_hash216": None,
                "incumbent_residual_hash216": incumbent_residual_hash216,
                "incumbent_candidate_index": None,
                "history": [],
                "failure_reason": None,
                "completion_status": None,
            }
            return self._write_job(job)

    def _remaining_timeout(self, job: Mapping[str, Any]) -> int:
        remaining_ns = int(job["deadline_unix_ns"]) - time.time_ns()
        if remaining_ns <= 0:
            return 0
        remaining_seconds = max(1, remaining_ns // 1_000_000_000)
        return min(int(job["request"]["render_timeout_seconds"]), remaining_seconds)

    def _renderer_is_available(self) -> bool:
        if not self.renderer_command:
            return False
        executable = self.renderer_command[0]
        return Path(executable).expanduser().is_file() or shutil.which(executable) is not None

    def _render_candidate(
        self,
        job: Mapping[str, Any],
        candidate_index: int,
        recipe: Mapping[str, Any],
    ) -> Dict[str, Any]:
        if not self._renderer_is_available():
            raise GraphicsOptimizationError("P181_NATIVE_RENDERER_NOT_CONFIGURED_OR_UNAVAILABLE")
        timeout = self._remaining_timeout(job)
        if timeout <= 0:
            raise GraphicsOptimizationError("P181_OPTIMIZATION_DEADLINE_EXPIRED")
        job_directory = self._job_directory(str(job["job_id"]))
        candidate_directory = job_directory / f"candidate-{candidate_index:04d}"
        candidate_directory.mkdir(parents=True, exist_ok=True)
        recipe_path = candidate_directory / "recipe.json"
        output_path = candidate_directory / "native-output.mp4"
        manifest_path = candidate_directory / "native-render-manifest.json"
        recipe_path.write_bytes(canonical_bytes(recipe))
        command = [
            *self.renderer_command,
            "--recipe",
            str(recipe_path),
            "--output",
            str(output_path),
            "--manifest",
            str(manifest_path),
        ]
        started_ns = time.perf_counter_ns()
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=_renderer_environment(),
            )
        except subprocess.TimeoutExpired as error:
            raise CandidateRenderError("P181_NATIVE_RENDERER_TIMEOUT") from error
        except subprocess.CalledProcessError as error:
            detail = (error.stderr or error.stdout or "").strip().replace("\n", " ")[-600:]
            raise CandidateRenderError(f"P181_NATIVE_RENDERER_FAILED:{detail}") from error
        elapsed_ns = time.perf_counter_ns() - started_ns
        if not output_path.is_file() or output_path.stat().st_size <= 0:
            raise CandidateRenderError("P181_NATIVE_RENDERER_OUTPUT_MP4_REQUIRED")
        if not manifest_path.is_file():
            raise CandidateRenderError("P181_NATIVE_RENDERER_MANIFEST_REQUIRED")
        try:
            renderer_manifest_raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise CandidateRenderError("P181_NATIVE_RENDERER_MANIFEST_INVALID") from error
        renderer_manifest = validate_native_renderer_manifest(
            renderer_manifest_raw,
            str(recipe["recipe_hash216"]),
        )
        output_sha256 = _sha256_file(output_path)
        native_output_id = hash216(
            {
                "recipe_hash216": recipe["recipe_hash216"],
                "output_sha256": output_sha256,
                "renderer_manifest": renderer_manifest,
            },
            domain=NATIVE_OUTPUT_DOMAIN,
        )
        try:
            decode_manifest = self.decode_runtime.build(
                output_path,
                reference_id=native_output_id,
                source_sha256=output_sha256,
                logical_name=f"native-candidate-{candidate_index}",
            )
        except Mp4DecodeError as error:
            raise CandidateRenderError(str(error)) from error
        residual_report = self.recipe_runtime.compare_and_store(
            job["request"]["reference_manifest"],
            decode_manifest,
            recipe,
        )
        score = residual_score(residual_report)
        return {
            "candidate_index": candidate_index,
            "recipe_hash216": recipe["recipe_hash216"],
            "renderer_manifest": renderer_manifest,
            "native_output_id": native_output_id,
            "native_output_sha256": output_sha256,
            "native_output_path": str(output_path),
            "decode_manifest_id": decode_manifest["decode_manifest_id"],
            "timeline_hash216": decode_manifest["timeline_hash216"],
            "residual_report_hash216": residual_report["residual_report_hash216"],
            "score": score,
            "exact_decoded_audiovisual_match": residual_report["exact_decoded_audiovisual_match"],
            "elapsed_ns": elapsed_ns,
            "renderer_stdout": result.stdout.strip(),
        }

    def _finalize_after_candidates(self, job: Dict[str, Any]) -> None:
        if job.get("incumbent_recipe_hash216"):
            job["state"] = "SUCCEEDED"
            job["completion_status"] = "HHS_GRAPHICS_OPTIMIZATION_BOUNDED_CLOSURE_VERIFIED"
        elif job["request"].get("baseline_residual_report") is not None:
            job["state"] = "SUCCEEDED"
            job["completion_status"] = "HHS_GRAPHICS_OPTIMIZATION_BASELINE_PRESERVED"
        else:
            job["state"] = "FAILED"
            job["completion_status"] = "REJECT_GRAPHICS_OPTIMIZATION_NO_ADMISSIBLE_CANDIDATE"
            job["failure_reason"] = "P181_NO_ADMISSIBLE_NATIVE_CANDIDATE"

    def step_job(self, job_id: str) -> Dict[str, Any]:
        with self._authority_lock:
            job = self._read_job(job_id)
            if job["state"] in FINAL_STATES:
                return {**job, "record_path": str(self._job_path(job_id))}
            if bool(job.get("cancel_requested")) or job["state"] == "CANCEL_REQUESTED":
                job["state"] = "CANCELLED"
                job["completion_status"] = "HHS_GRAPHICS_OPTIMIZATION_CANCELLED"
                job["updated_unix_ns"] = time.time_ns()
                return self._write_job(job)
            if time.time_ns() >= int(job["deadline_unix_ns"]):
                job["state"] = "TIMED_OUT"
                job["completion_status"] = "REJECT_GRAPHICS_OPTIMIZATION_TIMED_OUT"
                job["failure_reason"] = "P181_OPTIMIZATION_DEADLINE_EXPIRED"
                job["updated_unix_ns"] = time.time_ns()
                return self._write_job(job)

            candidates = job["request"]["candidate_recipes"]
            candidate_index = int(job["next_candidate_index"])
            if candidate_index >= len(candidates):
                self._finalize_after_candidates(job)
                job["updated_unix_ns"] = time.time_ns()
                return self._write_job(job)

            job["state"] = "RUNNING"
            recipe = candidates[candidate_index]
            history_record: Dict[str, Any] = {
                "candidate_index": candidate_index,
                "recipe_hash216": recipe["recipe_hash216"],
                "started_unix_ns": time.time_ns(),
                "decision": None,
            }
            try:
                result = self._render_candidate(job, candidate_index, recipe)
                improves = score_strictly_improves(result["score"], job.get("incumbent_score"))
                if improves:
                    history_record["decision"] = "ACCEPTED_STRICT_IMPROVEMENT"
                    job["accepted_count"] = int(job["accepted_count"]) + 1
                    job["incumbent_score"] = result["score"]
                    job["incumbent_recipe_hash216"] = result["recipe_hash216"]
                    job["incumbent_residual_hash216"] = result["residual_report_hash216"]
                    job["incumbent_candidate_index"] = candidate_index
                    job["incumbent_native_output_id"] = result["native_output_id"]
                    job["incumbent_native_output_path"] = result["native_output_path"]
                    job["incumbent_decode_manifest_id"] = result["decode_manifest_id"]
                else:
                    history_record["decision"] = "REJECTED_NO_STRICT_IMPROVEMENT"
                    job["rejected_count"] = int(job["rejected_count"]) + 1
                history_record["result"] = result
            except CandidateRenderError as error:
                history_record["decision"] = "REJECTED_CANDIDATE_RENDER_FAILURE"
                history_record["reason"] = str(error)
                job["rejected_count"] = int(job["rejected_count"]) + 1
            except GraphicsOptimizationError as error:
                job["state"] = "FAILED"
                job["completion_status"] = "REJECT_GRAPHICS_OPTIMIZATION_AUTHORITY_FAILURE"
                job["failure_reason"] = str(error)
                history_record["decision"] = "JOB_FAILED_AUTHORITY_ERROR"
                history_record["reason"] = str(error)

            history_record["completed_unix_ns"] = time.time_ns()
            job["history"].append(history_record)
            if job["state"] != "FAILED":
                job["next_candidate_index"] = candidate_index + 1
                exact = (
                    history_record.get("decision") == "ACCEPTED_STRICT_IMPROVEMENT"
                    and all(value == 0 for value in job.get("incumbent_score") or [])
                )
                if exact and bool(job["request"].get("stop_on_exact")):
                    job["state"] = "SUCCEEDED"
                    job["completion_status"] = "HHS_GRAPHICS_OPTIMIZATION_EXACT_DECODED_MATCH_VERIFIED"
                elif int(job["next_candidate_index"]) >= len(candidates):
                    self._finalize_after_candidates(job)
                else:
                    job["state"] = "QUEUED"
            job["updated_unix_ns"] = time.time_ns()
            return self._write_job(job)

    def run_job(self, job_id: str, *, max_steps: Optional[int] = None) -> Dict[str, Any]:
        steps = 0
        while True:
            job = self.step_job(job_id)
            if job["state"] in FINAL_STATES:
                return job
            steps += 1
            if max_steps is not None and steps >= int(max_steps):
                return job

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        with self._authority_lock:
            job = self._read_job(job_id)
            if job["state"] in FINAL_STATES:
                return {**job, "record_path": str(self._job_path(job_id))}
            job["cancel_requested"] = True
            job["state"] = "CANCEL_REQUESTED"
            job["updated_unix_ns"] = time.time_ns()
            return self._write_job(job)

    def retry_job(self, job_id: str) -> Dict[str, Any]:
        with self._authority_lock:
            job = self._read_job(job_id)
            if job["state"] not in FINAL_STATES:
                raise GraphicsOptimizationError("P181_OPTIMIZATION_RETRY_REQUIRES_FINAL_JOB")
            request = job["request"]
            return self.create_job(
                reference_manifest=request["reference_manifest"],
                candidate_recipes=request["candidate_recipes"],
                baseline_residual_report=request.get("baseline_residual_report"),
                timeout_seconds=int(request["timeout_seconds"]),
                render_timeout_seconds=int(request["render_timeout_seconds"]),
                stop_on_exact=bool(request.get("stop_on_exact", True)),
                parent_job_id=job_id,
            )
