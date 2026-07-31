"""Durable Pass 181 graphics evidence hydration over the Pass 165 vector store.

Final optimization jobs are decomposed into immutable typed packets and admitted
through the existing singleton VM81-governed 5,184-bit Pass 165 ingestion path.
Support-counted candidate invariants are extracted into a separate candidate
registry. Vector observations never possess runtime-constraint freeze authority.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from hhs_installer.canonical import canonical_bytes, hash72, hash216, stable
from hhs_runtime.pass165.durability import DurableMultimodalLearningService
from hhs_runtime.pass165.ingestion import IngestionError

CONTRACT = "HHS-P181-NCSR-GHIR-VM81-H72-H216"
AUTHORITY = "HHS_VM81_SINGLETON_GRAPHICS_HYDRATION_AUTHORITY_V1"
VECTOR_RECORD_DOMAIN = "HHS-P181-GRAPHICS-HYDRATION-VECTOR-RECORD-V1"
VECTOR_FRONTIER_DOMAIN = "HHS-P181-GRAPHICS-HYDRATION-VECTOR-FRONTIER-V1"
INVARIANT_CANDIDATE_DOMAIN = "HHS-P181-GRAPHICS-INVARIANT-CANDIDATE-V1"
VECTOR_RECEIPT_DOMAIN = "HHS-P181-GRAPHICS-HYDRATION-VECTOR-RECEIPT-V1"
CATALOG_SCHEMA = "HHS_P181_GRAPHICS_VECTOR_CATALOG_RECORD_V1"
PACKET_SCHEMA = "HHS_P181_GRAPHICS_HYDRATION_VECTOR_PACKET_V1"
CANDIDATE_SCHEMA = "HHS_P181_GRAPHICS_INVARIANT_CANDIDATE_V1"
MAX_PACKET_BYTES = 16 * 1024 * 1024
ALLOWED_JOB_FINAL_STATES = frozenset({"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT"})
FORBIDDEN_REFERENCE_VALUES = frozenset(
    {
        "reference_frame",
        "reference_texture",
        "reference_audio",
        "encoded_packet",
        "decoded_packet",
        "passthrough",
        "copied_frame",
        "copied_audio",
    }
)


class GraphicsVectorHydrationError(ValueError):
    """Raised when evidence admission or candidate extraction fails closed."""


def _artifact_filename(canonical_identity: str) -> str:
    return hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest() + ".json"


def _contains_forbidden_reference_source(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key).lower() in FORBIDDEN_REFERENCE_VALUES
            or _contains_forbidden_reference_source(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_reference_source(item) for item in value)
    return isinstance(value, str) and value.lower() in FORBIDDEN_REFERENCE_VALUES


def _catalog_envelope(record: Mapping[str, Any]) -> Dict[str, Any]:
    canonical = canonical_bytes(record)
    return {
        "schema": CATALOG_SCHEMA,
        "record": stable(record),
        "record_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def _score_tuple(value: Any) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise GraphicsVectorHydrationError("P181_OPTIMIZATION_SCORE_REQUIRED")
    output = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int) or item < 0:
            raise GraphicsVectorHydrationError("P181_OPTIMIZATION_SCORE_INVALID")
        output.append(item)
    return tuple(output)


class GraphicsVectorHydrationStore:
    """Append-only typed evidence catalog backed by durable Pass 165 ingestion."""

    def __init__(self, storage_root: Path | str) -> None:
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.catalog_path = self.storage_root / "graphics-vector-catalog.jsonl"
        self.candidate_root = self.storage_root / "invariant_candidates"
        self.candidate_root.mkdir(parents=True, exist_ok=True)
        self.pass165 = DurableMultimodalLearningService(self.storage_root / "pass165")
        self._authority_lock = threading.RLock()
        self._records: Dict[str, Dict[str, Any]] = {}
        self._candidates: Dict[str, Dict[str, Any]] = {}
        self._load_catalog()
        self._load_candidates()

    def _load_catalog(self) -> None:
        if not self.catalog_path.exists():
            return
        raw = self.catalog_path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            raise GraphicsVectorHydrationError("P181_GRAPHICS_VECTOR_CATALOG_INCOMPLETE_TAIL")
        for line_number, line in enumerate(raw.splitlines(), start=1):
            try:
                envelope = json.loads(line)
            except json.JSONDecodeError as error:
                raise GraphicsVectorHydrationError(
                    f"P181_GRAPHICS_VECTOR_CATALOG_JSON_INVALID:{line_number}"
                ) from error
            if envelope.get("schema") != CATALOG_SCHEMA or not isinstance(envelope.get("record"), dict):
                raise GraphicsVectorHydrationError(
                    f"P181_GRAPHICS_VECTOR_CATALOG_SCHEMA_INVALID:{line_number}"
                )
            record = envelope["record"]
            expected = hashlib.sha256(canonical_bytes(record)).hexdigest()
            if envelope.get("record_sha256") != expected:
                raise GraphicsVectorHydrationError(
                    f"P181_GRAPHICS_VECTOR_CATALOG_DIGEST_MISMATCH:{line_number}"
                )
            record_id = str(record.get("record_hash216") or "")
            if not record_id:
                raise GraphicsVectorHydrationError(
                    f"P181_GRAPHICS_VECTOR_RECORD_IDENTITY_MISSING:{line_number}"
                )
            prior = self._records.get(record_id)
            if prior is not None and prior != record:
                raise GraphicsVectorHydrationError("P181_GRAPHICS_VECTOR_RECORD_COLLISION")
            self._records[record_id] = record

    def _load_candidates(self) -> None:
        for path in sorted(self.candidate_root.glob("*.json")):
            try:
                candidate = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise GraphicsVectorHydrationError("P181_INVARIANT_CANDIDATE_RECORD_INVALID") from error
            candidate_id = str(candidate.get("candidate_hash216") or "")
            if not candidate_id:
                raise GraphicsVectorHydrationError("P181_INVARIANT_CANDIDATE_IDENTITY_MISSING")
            self._candidates[candidate_id] = candidate

    def _append_catalog(self, record: Dict[str, Any]) -> None:
        envelope = _catalog_envelope(record)
        line = canonical_bytes(envelope) + b"\n"
        with self.catalog_path.open("ab") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        self._records[str(record["record_hash216"])] = record

    def status(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_P181_GRAPHICS_VECTOR_HYDRATION_STATUS_V1",
            "ok": True,
            "contract": CONTRACT,
            "authority": AUTHORITY,
            "append_only_catalog": True,
            "runtime_constraint_freeze_authority": False,
            "vector_record_count": len(self._records),
            "candidate_invariant_count": len(self._candidates),
            "pass165": self.pass165.status(),
            "catalog_path": str(self.catalog_path),
        }

    @staticmethod
    def _validate_job(job: Mapping[str, Any]) -> None:
        if not isinstance(job, Mapping):
            raise GraphicsVectorHydrationError("P181_OPTIMIZATION_JOB_REQUIRED")
        if job.get("schema") != "HHS_P181_GRAPHICS_OPTIMIZATION_JOB_V1":
            raise GraphicsVectorHydrationError("P181_OPTIMIZATION_JOB_SCHEMA_INVALID")
        if job.get("authority") != AUTHORITY:
            raise GraphicsVectorHydrationError("P181_OPTIMIZATION_JOB_AUTHORITY_INVALID")
        if job.get("state") not in ALLOWED_JOB_FINAL_STATES:
            raise GraphicsVectorHydrationError("P181_VECTOR_HYDRATION_REQUIRES_FINAL_JOB")
        request = job.get("request")
        if not isinstance(request, Mapping):
            raise GraphicsVectorHydrationError("P181_OPTIMIZATION_JOB_REQUEST_INVALID")
        reference = request.get("reference_manifest")
        recipes = request.get("candidate_recipes")
        history = job.get("history")
        if not isinstance(reference, Mapping) or not isinstance(recipes, list) or not isinstance(history, list):
            raise GraphicsVectorHydrationError("P181_OPTIMIZATION_JOB_EVIDENCE_INVALID")
        if not reference.get("reference_id") or not reference.get("timeline_hash216"):
            raise GraphicsVectorHydrationError("P181_REFERENCE_TIMELINE_IDENTITY_REQUIRED")

    @staticmethod
    def _packets_from_job(job: Mapping[str, Any]) -> list[Dict[str, Any]]:
        request = job["request"]
        job_id = str(job["job_id"])
        packets: list[Dict[str, Any]] = []

        def packet(record_class: str, authority_class: str, payload: Mapping[str, Any]) -> None:
            packets.append(
                {
                    "schema": PACKET_SCHEMA,
                    "contract": CONTRACT,
                    "source_job_id": job_id,
                    "record_class": record_class,
                    "authority_class": authority_class,
                    "runtime_constraint_authority": False,
                    "frozen": False,
                    "payload": stable(payload),
                }
            )

        packet(
            "OPTIMIZATION_JOB_SUMMARY",
            "ADMITTED_JOB_EVIDENCE" if job["state"] == "SUCCEEDED" else "FINAL_FAILURE_EVIDENCE",
            {
                "job_id": job_id,
                "state": job["state"],
                "completion_status": job.get("completion_status"),
                "request_hash216": job.get("request_hash216"),
                "accepted_count": job.get("accepted_count", 0),
                "rejected_count": job.get("rejected_count", 0),
                "incumbent_score": job.get("incumbent_score"),
                "incumbent_recipe_hash216": job.get("incumbent_recipe_hash216"),
                "incumbent_residual_hash216": job.get("incumbent_residual_hash216"),
                "history": job["history"],
            },
        )
        packet(
            "REFERENCE_TIMELINE",
            "IMMUTABLE_REFERENCE_EVIDENCE",
            request["reference_manifest"],
        )
        accepted_hashes = {
            str(item.get("recipe_hash216"))
            for item in job["history"]
            if isinstance(item, Mapping)
            and item.get("decision") == "ACCEPTED_STRICT_IMPROVEMENT"
        }
        rejected_hashes = {
            str(item.get("recipe_hash216"))
            for item in job["history"]
            if isinstance(item, Mapping)
            and str(item.get("decision") or "").startswith("REJECTED_")
        }
        for index, recipe in enumerate(request["candidate_recipes"]):
            recipe_hash = str(recipe.get("recipe_hash216") or "")
            if recipe_hash in accepted_hashes:
                authority_class = "ADMITTED_OPTIMIZATION_RECIPE_EVIDENCE"
            elif recipe_hash in rejected_hashes:
                authority_class = "REJECTED_OPTIMIZATION_RECIPE_EVIDENCE"
            else:
                authority_class = "UNEXECUTED_CANDIDATE_RECIPE_EVIDENCE"
            packet(
                "NATIVE_RECIPE",
                authority_class,
                {"candidate_index": index, "recipe": recipe},
            )
        for index, decision in enumerate(job["history"]):
            decision_name = str(decision.get("decision") or "") if isinstance(decision, Mapping) else ""
            authority_class = (
                "ADMITTED_OPTIMIZATION_DECISION_EVIDENCE"
                if decision_name == "ACCEPTED_STRICT_IMPROVEMENT"
                else "REJECTED_OPTIMIZATION_DECISION_EVIDENCE"
            )
            packet(
                "OPTIMIZATION_DECISION",
                authority_class,
                {"history_index": index, "decision": decision},
            )
        if job.get("incumbent_recipe_hash216"):
            packet(
                "INCUMBENT_RESULT",
                "ADMITTED_INCUMBENT_EVIDENCE",
                {
                    "recipe_hash216": job.get("incumbent_recipe_hash216"),
                    "residual_report_hash216": job.get("incumbent_residual_hash216"),
                    "score": job.get("incumbent_score"),
                    "candidate_index": job.get("incumbent_candidate_index"),
                    "native_output_id": job.get("incumbent_native_output_id"),
                    "decode_manifest_id": job.get("incumbent_decode_manifest_id"),
                },
            )
        return packets

    def _admit_packet(self, packet: Mapping[str, Any]) -> Dict[str, Any]:
        canonical_packet = stable(packet)
        raw = canonical_bytes(canonical_packet)
        if not raw or len(raw) > MAX_PACKET_BYTES:
            raise GraphicsVectorHydrationError("P181_GRAPHICS_VECTOR_PACKET_SIZE_REJECTED")
        record_hash216 = hash216(canonical_packet, domain=VECTOR_RECORD_DOMAIN)
        prior = self._records.get(record_hash216)
        if prior is not None:
            return {**prior, "reused": True}
        try:
            pass165_result = self.pass165.ingest_source(
                raw,
                declared_media_type="HHS_VECTOR_PACKET",
                provenance=f"P181:{packet['source_job_id']}:{record_hash216}",
                authorization_scope="P181_GRAPHICS_HYDRATION_VECTOR_ADMISSION",
            )
        except IngestionError as error:
            raise GraphicsVectorHydrationError(str(error)) from error
        record = {
            "schema": "HHS_P181_GRAPHICS_VECTOR_RECORD_V1",
            "record_hash216": record_hash216,
            "record_sha256": hashlib.sha256(raw).hexdigest(),
            "record_class": packet["record_class"],
            "authority_class": packet["authority_class"],
            "source_job_id": packet["source_job_id"],
            "runtime_constraint_authority": False,
            "frozen": False,
            "packet": canonical_packet,
            "pass165": stable(pass165_result),
        }
        record["receipt_hash72"] = hash72(record, domain=VECTOR_RECEIPT_DOMAIN)
        self._append_catalog(record)
        return {**record, "reused": False}

    def hydrate_optimization_job(self, job: Mapping[str, Any]) -> Dict[str, Any]:
        with self._authority_lock:
            self._validate_job(job)
            packets = self._packets_from_job(job)
            records = [self._admit_packet(packet) for packet in packets]
            new_count = sum(not record["reused"] for record in records)
            reused_count = len(records) - new_count
            frontier_payload = {
                "record_hashes": sorted(self._records),
                "pass165_weight_root": self.pass165.weight_root,
                "pass165_vm81_state_hash72": self.pass165.status()["vm81"]["state_hash72"],
            }
            return {
                "schema": "HHS_P181_GRAPHICS_VECTOR_HYDRATION_RESULT_V1",
                "ok": True,
                "status": "HHS_GRAPHICS_OPTIMIZATION_EVIDENCE_HYDRATED",
                "source_job_id": job["job_id"],
                "packet_count": len(records),
                "new_record_count": new_count,
                "reused_record_count": reused_count,
                "record_hash216": [record["record_hash216"] for record in records],
                "vector_frontier_hash216": hash216(frontier_payload, domain=VECTOR_FRONTIER_DOMAIN),
                "pass165_weight_root": self.pass165.weight_root,
                "runtime_constraint_authority": False,
            }

    def list_records(
        self,
        *,
        record_class: Optional[str] = None,
        source_job_id: Optional[str] = None,
    ) -> list[Dict[str, Any]]:
        values: Iterable[Dict[str, Any]] = self._records.values()
        if record_class:
            values = (item for item in values if item["record_class"] == record_class)
        if source_job_id:
            values = (item for item in values if item["source_job_id"] == source_job_id)
        return [stable(item) for item in sorted(values, key=lambda item: item["record_hash216"])]

    @staticmethod
    def _recipe_observations(record: Mapping[str, Any]) -> Dict[str, bool]:
        recipe = record["packet"]["payload"]["recipe"]
        scenes = recipe.get("scenes") if isinstance(recipe, Mapping) else None
        if not isinstance(scenes, list) or not scenes:
            return {
                "ALL_LAYERS_NATIVE": False,
                "NO_REFERENCE_PASSTHROUGH": False,
                "RECIPROCAL_PALETTE": False,
                "SINGLE_COMMIT_AUTHORITY": False,
            }
        all_layers_native = True
        reciprocal = True
        for scene in scenes:
            if not isinstance(scene, Mapping):
                all_layers_native = False
                reciprocal = False
                continue
            palette = scene.get("palette")
            if not isinstance(palette, Mapping):
                reciprocal = False
            else:
                try:
                    x = int(palette.get("x"))
                    z = int(palette.get("z"))
                except (TypeError, ValueError):
                    reciprocal = False
                else:
                    reciprocal = reciprocal and 0 <= x < 72 and 0 <= z < 72 and z == (x + 36) % 72
            layers = scene.get("layers")
            if not isinstance(layers, list) or not layers:
                all_layers_native = False
            else:
                all_layers_native = all_layers_native and all(
                    isinstance(layer, Mapping) and layer.get("authority") == "HHS_NATIVE_ABI"
                    for layer in layers
                )
        return {
            "ALL_LAYERS_NATIVE": all_layers_native,
            "NO_REFERENCE_PASSTHROUGH": not _contains_forbidden_reference_source(recipe),
            "RECIPROCAL_PALETTE": reciprocal,
            "SINGLE_COMMIT_AUTHORITY": recipe.get("single_commit_authority") is True,
        }

    @staticmethod
    def _job_observations(record: Mapping[str, Any]) -> Dict[str, bool]:
        payload = record["packet"]["payload"]
        history = payload.get("history")
        strict = True
        prior_score: Optional[tuple[int, ...]] = None
        rejected_never_incumbent = True
        incumbent_hash = str(payload.get("incumbent_recipe_hash216") or "")
        if not isinstance(history, list):
            strict = False
            rejected_never_incumbent = False
        else:
            for item in history:
                if not isinstance(item, Mapping):
                    strict = False
                    rejected_never_incumbent = False
                    continue
                decision = str(item.get("decision") or "")
                recipe_hash = str(item.get("recipe_hash216") or "")
                result = item.get("result")
                if decision == "ACCEPTED_STRICT_IMPROVEMENT":
                    if not isinstance(result, Mapping):
                        strict = False
                        continue
                    try:
                        score = _score_tuple(result.get("score"))
                    except GraphicsVectorHydrationError:
                        strict = False
                        continue
                    if prior_score is not None and not score < prior_score:
                        strict = False
                    prior_score = score
                elif decision.startswith("REJECTED_") and recipe_hash == incumbent_hash:
                    rejected_never_incumbent = False
        return {
            "STRICT_IMPROVEMENT_ADMISSION": strict,
            "REJECTED_CANDIDATES_LACK_AUTHORITY": rejected_never_incumbent,
        }

    def extract_invariant_candidates(
        self,
        *,
        minimum_support: int = 2,
        minimum_distinct_jobs: int = 2,
    ) -> Dict[str, Any]:
        with self._authority_lock:
            if minimum_support < 1 or minimum_distinct_jobs < 1:
                raise GraphicsVectorHydrationError("P181_INVARIANT_SUPPORT_BOUND_INVALID")
            accumulator: Dict[str, Dict[str, Any]] = {}

            def observe(
                predicate_id: str,
                candidate_class: str,
                proposition: str,
                domain: str,
                record: Mapping[str, Any],
                satisfied: bool,
                promotion_track: str = "RUNTIME_CONSTRAINT",
            ) -> None:
                entry = accumulator.setdefault(
                    predicate_id,
                    {
                        "predicate_id": predicate_id,
                        "candidate_class": candidate_class,
                        "proposition": proposition,
                        "domain": domain,
                        "promotion_track": promotion_track,
                        "support": set(),
                        "counterexamples": set(),
                        "jobs": set(),
                    },
                )
                target = entry["support"] if satisfied else entry["counterexamples"]
                target.add(str(record["record_hash216"]))
                entry["jobs"].add(str(record["source_job_id"]))

            for record in self._records.values():
                if record["record_class"] == "NATIVE_RECIPE":
                    observations = self._recipe_observations(record)
                    definitions = {
                        "ALL_LAYERS_NATIVE": (
                            "HARD_INVARIANT",
                            "every authoritative recipe layer uses HHS_NATIVE_ABI",
                            "NATIVE_FRAME_PROVENANCE",
                        ),
                        "NO_REFERENCE_PASSTHROUGH": (
                            "HARD_INVARIANT",
                            "native reconstruction recipes contain no reference-frame, texture, audio, or packet passthrough",
                            "REFERENCE_PROVENANCE",
                        ),
                        "RECIPROCAL_PALETTE": (
                            "HARD_INVARIANT",
                            "every scene satisfies z=(x+36) mod 72",
                            "RECIPROCAL_PALETTE",
                        ),
                        "SINGLE_COMMIT_AUTHORITY": (
                            "HARD_INVARIANT",
                            "every reconstruction recipe declares one serialized commit authority",
                            "VM81_AUTHORITY",
                        ),
                    }
                    for predicate_id, satisfied in observations.items():
                        cls, proposition, domain = definitions[predicate_id]
                        observe(predicate_id, cls, proposition, domain, record, satisfied)

                    if record["authority_class"] == "ADMITTED_OPTIMIZATION_RECIPE_EVIDENCE":
                        recipe = record["packet"]["payload"]["recipe"]
                        for scene in recipe.get("scenes", []):
                            if not isinstance(scene, Mapping):
                                continue
                            camera = scene.get("camera")
                            if isinstance(camera, Mapping) and camera.get("mode"):
                                mode = str(camera["mode"])
                                observe(
                                    f"STYLE_CAMERA_MODE:{mode}",
                                    "STYLE_PROFILE",
                                    f"camera mode {mode} appears in admitted native reconstruction recipes",
                                    "CAMERA_STYLE",
                                    record,
                                    True,
                                    "STYLE_PROFILE",
                                )
                            for layer in scene.get("layers", []):
                                if isinstance(layer, Mapping) and layer.get("type"):
                                    layer_type = str(layer["type"])
                                    observe(
                                        f"STYLE_LAYER_TYPE:{layer_type}",
                                        "STYLE_PROFILE",
                                        f"layer type {layer_type} appears in admitted native reconstruction recipes",
                                        "LAYER_STYLE",
                                        record,
                                        True,
                                        "STYLE_PROFILE",
                                    )
                elif record["record_class"] == "OPTIMIZATION_JOB_SUMMARY":
                    observations = self._job_observations(record)
                    definitions = {
                        "STRICT_IMPROVEMENT_ADMISSION": (
                            "HARD_INVARIANT",
                            "accepted optimization candidates form a strictly decreasing exact residual-score sequence",
                            "OPTIMIZATION_ADMISSION",
                        ),
                        "REJECTED_CANDIDATES_LACK_AUTHORITY": (
                            "HARD_INVARIANT",
                            "rejected optimization candidates never become the authoritative incumbent",
                            "OPTIMIZATION_AUTHORITY",
                        ),
                    }
                    for predicate_id, satisfied in observations.items():
                        cls, proposition, domain = definitions[predicate_id]
                        observe(predicate_id, cls, proposition, domain, record, satisfied)

            candidates = []
            for predicate_id in sorted(accumulator):
                item = accumulator[predicate_id]
                support = sorted(item["support"])
                counterexamples = sorted(item["counterexamples"])
                jobs = sorted(item["jobs"])
                evidence_payload = {
                    "predicate_id": predicate_id,
                    "support": support,
                    "counterexamples": counterexamples,
                    "jobs": jobs,
                }
                candidate = {
                    "schema": CANDIDATE_SCHEMA,
                    "contract": CONTRACT,
                    "authority": AUTHORITY,
                    "predicate_id": predicate_id,
                    "candidate_class": item["candidate_class"],
                    "proposition": item["proposition"],
                    "domain": item["domain"],
                    "promotion_track": item["promotion_track"],
                    "support_count": len(support),
                    "distinct_job_count": len(jobs),
                    "supporting_record_hash216": support,
                    "supporting_job_ids": jobs,
                    "counterexample_record_hash216": counterexamples,
                    "minimum_support": minimum_support,
                    "minimum_distinct_jobs": minimum_distinct_jobs,
                    "eligible_for_promotion": (
                        len(support) >= minimum_support
                        and len(jobs) >= minimum_distinct_jobs
                        and not counterexamples
                    ),
                    "validation_state": "CANDIDATE",
                    "runtime_constraint_authority": False,
                    "frozen": False,
                    "evidence_root_hash216": hash216(
                        evidence_payload,
                        domain=INVARIANT_CANDIDATE_DOMAIN,
                    ),
                }
                candidate["candidate_hash216"] = hash216(
                    candidate,
                    domain=INVARIANT_CANDIDATE_DOMAIN,
                )
                candidate["receipt_hash72"] = hash72(
                    candidate,
                    domain=VECTOR_RECEIPT_DOMAIN,
                )
                path = self.candidate_root / _artifact_filename(candidate["candidate_hash216"])
                path.write_bytes(canonical_bytes(candidate))
                self._candidates[candidate["candidate_hash216"]] = candidate
                candidates.append(candidate)
            return {
                "schema": "HHS_P181_GRAPHICS_INVARIANT_EXTRACTION_RESULT_V1",
                "ok": True,
                "status": "HHS_GRAPHICS_SUPPORT_COUNTED_INVARIANTS_EXTRACTED",
                "candidate_count": len(candidates),
                "eligible_count": sum(candidate["eligible_for_promotion"] for candidate in candidates),
                "runtime_constraints_frozen": 0,
                "candidates": candidates,
            }

    def list_invariant_candidates(
        self,
        *,
        candidate_class: Optional[str] = None,
        eligible_only: bool = False,
    ) -> list[Dict[str, Any]]:
        values: Iterable[Dict[str, Any]] = self._candidates.values()
        if candidate_class:
            values = (item for item in values if item["candidate_class"] == candidate_class)
        if eligible_only:
            values = (item for item in values if item["eligible_for_promotion"])
        return [stable(item) for item in sorted(values, key=lambda item: item["candidate_hash216"])]

    def build_promotion_proposal(self, candidate_hash216: str) -> Dict[str, Any]:
        candidate = self._candidates.get(str(candidate_hash216))
        if candidate is None:
            raise GraphicsVectorHydrationError("P181_INVARIANT_CANDIDATE_UNKNOWN")
        if not candidate["eligible_for_promotion"]:
            raise GraphicsVectorHydrationError("P181_INVARIANT_CANDIDATE_SUPPORT_INSUFFICIENT")
        return {
            "schema": "HHS_P181_GRAPHICS_CONSTRAINT_PROMOTION_PROPOSAL_V1",
            "candidate_hash216": candidate_hash216,
            "family": candidate["domain"],
            "predicate": candidate["predicate_id"],
            "scope": "ALL_AUTHORITATIVE_STORY_REEL_FRAMES",
            "arithmetic": "EXACT_INTEGER_OR_RATIONAL",
            "severity": "HARD_REJECTION" if candidate["candidate_class"] == "HARD_INVARIANT" else "PROFILE_DEFAULT",
            "evidence": candidate["supporting_record_hash216"],
            "stages": {
                "reproduced": False,
                "cross_sample_verified": False,
                "positive_tested": False,
                "negative_tested": False,
                "adversarial_tested": False,
                "replay_verified": False,
                "calibrated": False,
                "contradiction_scan_passed": False,
            },
            "runtime_constraint_authority": False,
            "frozen": False,
        }

    def freeze_candidate(self, candidate_hash216: str) -> None:
        raise GraphicsVectorHydrationError(
            "P181_VECTOR_OBSERVATION_CANNOT_FREEZE_RUNTIME_CONSTRAINT"
        )

    def replay(self) -> Dict[str, Any]:
        with self._authority_lock:
            replay = self.pass165.replay_ingestion()
            frontier_payload = {
                "record_hashes": sorted(self._records),
                "pass165_weight_root": self.pass165.weight_root,
                "pass165_vm81_state_hash72": self.pass165.status()["vm81"]["state_hash72"],
            }
            return {
                "schema": "HHS_P181_GRAPHICS_VECTOR_HYDRATION_REPLAY_V1",
                "ok": True,
                "status": "HHS_GRAPHICS_VECTOR_HYDRATION_REPLAY_VERIFIED",
                "catalog_records": len(self._records),
                "vector_frontier_hash216": hash216(
                    frontier_payload,
                    domain=VECTOR_FRONTIER_DOMAIN,
                ),
                "pass165_replay": replay,
                "runtime_constraints_frozen": 0,
            }
