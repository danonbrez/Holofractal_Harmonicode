"""Append-only graphics constraint and style-profile registry for Pass 181.

Only support-counted vector candidates with a complete external validation chain
may be frozen. Hard runtime constraints and style profiles use separate active
frontiers. Immutable freeze records are activated, superseded, and rolled back
through chained journal events; the active frontier is atomically replaced and
verified from the journal after cold restart.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from hhs_installer.canonical import canonical_bytes, hash72, hash216, stable

CONTRACT = "HHS-P181-NCSR-GHIR-VM81-H72-H216"
AUTHORITY = "HHS_VM81_SINGLETON_GRAPHICS_HYDRATION_AUTHORITY_V1"
REGISTRY_SCHEMA = "HHS_P181_GRAPHICS_CONSTRAINT_REGISTRY_V1"
JOURNAL_SCHEMA = "HHS_P181_GRAPHICS_CONSTRAINT_EVENT_ENVELOPE_V1"
FRONTIER_SCHEMA = "HHS_P181_GRAPHICS_CONSTRAINT_FRONTIER_V1"
HARD_RECORD_SCHEMA = "HHS_GRAPHICS_RUNTIME_CONSTRAINT_V1"
STYLE_RECORD_SCHEMA = "HHS_GRAPHICS_STYLE_PROFILE_V1"
CONSTRAINT_RECORD_DOMAIN = "HHS-P181-GRAPHICS-CONSTRAINT-RECORD-V1"
CONSTRAINT_EVENT_DOMAIN = "HHS-P181-GRAPHICS-CONSTRAINT-EVENT-V1"
CONSTRAINT_FRONTIER_DOMAIN = "HHS-P181-GRAPHICS-CONSTRAINT-FRONTIER-V1"
CONSTRAINT_RECEIPT_DOMAIN = "HHS-P181-GRAPHICS-CONSTRAINT-RECEIPT-V1"
PROMOTION_STAGES: Sequence[str] = (
    "reproduced",
    "cross_sample_verified",
    "positive_tested",
    "negative_tested",
    "adversarial_tested",
    "replay_verified",
    "calibrated",
    "contradiction_scan_passed",
)
RECORD_KINDS = frozenset({"RUNTIME_CONSTRAINT", "STYLE_PROFILE"})


class GraphicsConstraintRegistryError(ValueError):
    """Raised when constraint promotion, activation, or replay fails closed."""


def _artifact_filename(canonical_identity: str) -> str:
    return hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest() + ".json"


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _event_envelope(event: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema": JOURNAL_SCHEMA,
        "event": stable(event),
        "event_sha256": hashlib.sha256(canonical_bytes(event)).hexdigest(),
    }


def _validate_stage_evidence(promotion_evidence: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(promotion_evidence, Mapping):
        raise GraphicsConstraintRegistryError("P181_PROMOTION_EVIDENCE_REQUIRED")
    stages = promotion_evidence.get("stages")
    stage_evidence = promotion_evidence.get("stage_evidence")
    if not isinstance(stages, Mapping) or not isinstance(stage_evidence, Mapping):
        raise GraphicsConstraintRegistryError("P181_PROMOTION_STAGE_EVIDENCE_REQUIRED")
    missing = [stage for stage in PROMOTION_STAGES if stages.get(stage) is not True]
    if missing:
        raise GraphicsConstraintRegistryError(
            "P181_PROMOTION_STAGES_INCOMPLETE:" + ",".join(missing)
        )
    normalized_evidence: Dict[str, list[str]] = {}
    for stage in PROMOTION_STAGES:
        values = stage_evidence.get(stage)
        if not isinstance(values, list) or not values:
            raise GraphicsConstraintRegistryError(
                f"P181_PROMOTION_STAGE_EVIDENCE_EMPTY:{stage}"
            )
        normalized = []
        for value in values:
            lexical = str(value).strip()
            if not lexical:
                raise GraphicsConstraintRegistryError(
                    f"P181_PROMOTION_STAGE_EVIDENCE_INVALID:{stage}"
                )
            normalized.append(lexical)
        normalized_evidence[stage] = sorted(set(normalized))
    if str(promotion_evidence.get("contradiction_scan_result") or "") != "PASSED":
        raise GraphicsConstraintRegistryError("P181_CONTRADICTION_SCAN_NOT_PASSED")
    return {
        "stages": {stage: True for stage in PROMOTION_STAGES},
        "stage_evidence": normalized_evidence,
        "contradiction_scan_result": "PASSED",
        "calibration_profile": stable(promotion_evidence.get("calibration_profile") or {}),
        "validator_versions": stable(promotion_evidence.get("validator_versions") or {}),
        "operator": str(promotion_evidence.get("operator") or "HHS_VM81_PROMOTION_AUTHORITY"),
    }


def validate_freeze_candidate(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(candidate, Mapping):
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_REQUIRED")
    if candidate.get("schema") != "HHS_P181_GRAPHICS_INVARIANT_CANDIDATE_V1":
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_SCHEMA_INVALID")
    if candidate.get("authority") != AUTHORITY:
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_AUTHORITY_INVALID")
    if candidate.get("validation_state") != "CANDIDATE":
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_STATE_INVALID")
    if candidate.get("eligible_for_promotion") is not True:
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_NOT_ELIGIBLE")
    if candidate.get("runtime_constraint_authority") is not False or candidate.get("frozen") is not False:
        raise GraphicsConstraintRegistryError("P181_VECTOR_CANDIDATE_AUTHORITY_BOUNDARY_INVALID")
    if candidate.get("counterexample_record_hash216"):
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_HAS_COUNTEREXAMPLES")
    support = candidate.get("supporting_record_hash216")
    jobs = candidate.get("supporting_job_ids")
    if not isinstance(support, list) or not support or not isinstance(jobs, list) or not jobs:
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_SUPPORT_REQUIRED")
    if int(candidate.get("support_count", -1)) != len(support):
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_SUPPORT_COUNT_MISMATCH")
    if int(candidate.get("distinct_job_count", -1)) != len(jobs):
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_JOB_COUNT_MISMATCH")
    track = str(candidate.get("promotion_track") or "")
    if track not in RECORD_KINDS:
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_PROMOTION_TRACK_INVALID")
    predicate_id = str(candidate.get("predicate_id") or "").strip()
    candidate_hash216 = str(candidate.get("candidate_hash216") or "").strip()
    if not predicate_id or not candidate_hash216:
        raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_IDENTITY_REQUIRED")
    return stable(candidate)


class GraphicsConstraintRegistry:
    """Immutable freeze records plus atomic active constraint frontiers."""

    def __init__(self, storage_root: Path | str) -> None:
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.record_root = self.storage_root / "records"
        self.record_root.mkdir(parents=True, exist_ok=True)
        self.journal_path = self.storage_root / "constraint-events.jsonl"
        self.frontier_path = self.storage_root / "active-frontier.json"
        self.frontier_temp_path = self.storage_root / "active-frontier.json.tmp"
        self._lock = RLock()
        self._events: list[Dict[str, Any]] = []
        self._records: Dict[str, Dict[str, Any]] = {}
        self._active_constraints: Dict[str, str] = {}
        self._active_style_profiles: Dict[str, str] = {}
        self._load_and_verify()

    def _load_and_verify(self) -> None:
        if self.journal_path.exists():
            raw = self.journal_path.read_bytes()
            if raw and not raw.endswith(b"\n"):
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_JOURNAL_INCOMPLETE_TAIL")
            previous_hash = "GENESIS"
            expected_sequence = 1
            for line_number, line in enumerate(raw.splitlines(), start=1):
                try:
                    envelope = json.loads(line)
                except json.JSONDecodeError as error:
                    raise GraphicsConstraintRegistryError(
                        f"P181_CONSTRAINT_JOURNAL_JSON_INVALID:{line_number}"
                    ) from error
                if envelope.get("schema") != JOURNAL_SCHEMA or not isinstance(envelope.get("event"), dict):
                    raise GraphicsConstraintRegistryError(
                        f"P181_CONSTRAINT_JOURNAL_SCHEMA_INVALID:{line_number}"
                    )
                event = envelope["event"]
                expected_sha = hashlib.sha256(canonical_bytes(event)).hexdigest()
                if envelope.get("event_sha256") != expected_sha:
                    raise GraphicsConstraintRegistryError(
                        f"P181_CONSTRAINT_JOURNAL_DIGEST_MISMATCH:{line_number}"
                    )
                if event.get("sequence") != expected_sequence:
                    raise GraphicsConstraintRegistryError("P181_CONSTRAINT_EVENT_SEQUENCE_INVALID")
                if event.get("previous_event_hash216") != previous_hash:
                    raise GraphicsConstraintRegistryError("P181_CONSTRAINT_EVENT_CHAIN_INVALID")
                event_body = {key: value for key, value in event.items() if key != "event_hash216"}
                computed_hash = hash216(event_body, domain=CONSTRAINT_EVENT_DOMAIN)
                if event.get("event_hash216") != computed_hash:
                    raise GraphicsConstraintRegistryError("P181_CONSTRAINT_EVENT_IDENTITY_INVALID")
                self._apply_event(event, persist_record=True)
                self._events.append(event)
                previous_hash = computed_hash
                expected_sequence += 1
        expected_frontier = self._frontier_payload()
        if self.frontier_path.exists():
            try:
                observed = json.loads(self.frontier_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_FRONTIER_INVALID") from error
            if observed != expected_frontier:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_FRONTIER_REPLAY_MISMATCH")
        else:
            self._write_frontier_atomic()

    def _apply_event(self, event: Mapping[str, Any], *, persist_record: bool) -> None:
        event_type = str(event.get("event_type") or "")
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            raise GraphicsConstraintRegistryError("P181_CONSTRAINT_EVENT_PAYLOAD_INVALID")
        if event_type == "FREEZE":
            record = payload.get("record")
            if not isinstance(record, Mapping):
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_FREEZE_RECORD_INVALID")
            record_id = str(record.get("record_hash216") or "")
            if not record_id:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_RECORD_IDENTITY_REQUIRED")
            prior = self._records.get(record_id)
            normalized = stable(record)
            if prior is not None and prior != normalized:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_RECORD_COLLISION")
            self._records[record_id] = normalized
            if persist_record:
                path = self.record_root / _artifact_filename(record_id)
                if path.exists() and path.read_bytes() != canonical_bytes(normalized):
                    raise GraphicsConstraintRegistryError("P181_CONSTRAINT_RECORD_FILE_MISMATCH")
                if not path.exists():
                    path.write_bytes(canonical_bytes(normalized))
        elif event_type in {"ACTIVATE", "SUPERSEDE", "ROLLBACK"}:
            predicate_id = str(payload.get("predicate_id") or "")
            target_id = str(payload.get("target_record_hash216") or "")
            record_kind = str(payload.get("record_kind") or "")
            if record_kind not in RECORD_KINDS or target_id not in self._records:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_ACTIVATION_TARGET_INVALID")
            if self._records[target_id].get("predicate_id") != predicate_id:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_ACTIVATION_PREDICATE_MISMATCH")
            active = (
                self._active_constraints
                if record_kind == "RUNTIME_CONSTRAINT"
                else self._active_style_profiles
            )
            if event_type in {"SUPERSEDE", "ROLLBACK"}:
                from_id = str(payload.get("from_record_hash216") or "")
                if active.get(predicate_id) != from_id:
                    raise GraphicsConstraintRegistryError("P181_CONSTRAINT_ACTIVE_FRONTIER_MISMATCH")
            active[predicate_id] = target_id
        else:
            raise GraphicsConstraintRegistryError(f"P181_CONSTRAINT_EVENT_TYPE_INVALID:{event_type}")

    def _journal_sha256(self) -> str:
        raw = self.journal_path.read_bytes() if self.journal_path.exists() else b""
        return hashlib.sha256(raw).hexdigest()

    def _frontier_payload(self) -> Dict[str, Any]:
        payload = {
            "schema": FRONTIER_SCHEMA,
            "contract": CONTRACT,
            "authority": AUTHORITY,
            "event_count": len(self._events),
            "last_event_hash216": self._events[-1]["event_hash216"] if self._events else "GENESIS",
            "journal_sha256": self._journal_sha256(),
            "active_runtime_constraints": dict(sorted(self._active_constraints.items())),
            "active_style_profiles": dict(sorted(self._active_style_profiles.items())),
            "record_hash216": sorted(self._records),
        }
        payload["frontier_hash216"] = hash216(payload, domain=CONSTRAINT_FRONTIER_DOMAIN)
        payload["receipt_hash72"] = hash72(payload, domain=CONSTRAINT_RECEIPT_DOMAIN)
        return payload

    def _write_frontier_atomic(self) -> Dict[str, Any]:
        payload = self._frontier_payload()
        with self.frontier_temp_path.open("wb") as handle:
            handle.write(canonical_bytes(payload) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(self.frontier_temp_path, self.frontier_path)
        _fsync_directory(self.storage_root)
        return payload

    def _append_event(self, event_type: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        sequence = len(self._events) + 1
        event_body = {
            "schema": "HHS_P181_GRAPHICS_CONSTRAINT_EVENT_V1",
            "sequence": sequence,
            "event_type": event_type,
            "created_unix_ns": time.time_ns(),
            "previous_event_hash216": self._events[-1]["event_hash216"] if self._events else "GENESIS",
            "payload": stable(payload),
        }
        event = {
            **event_body,
            "event_hash216": hash216(event_body, domain=CONSTRAINT_EVENT_DOMAIN),
        }
        line = canonical_bytes(_event_envelope(event)) + b"\n"
        with self.journal_path.open("ab") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        self._apply_event(event, persist_record=True)
        self._events.append(event)
        self._write_frontier_atomic()
        return event

    def status(self) -> Dict[str, Any]:
        frontier = self._frontier_payload()
        return {
            "schema": REGISTRY_SCHEMA,
            "ok": True,
            "authority": AUTHORITY,
            "append_only_events": True,
            "atomic_frontier": True,
            "runtime_constraint_count": sum(
                record["record_kind"] == "RUNTIME_CONSTRAINT"
                for record in self._records.values()
            ),
            "style_profile_count": sum(
                record["record_kind"] == "STYLE_PROFILE"
                for record in self._records.values()
            ),
            "active_runtime_constraint_count": len(self._active_constraints),
            "active_style_profile_count": len(self._active_style_profiles),
            "event_count": len(self._events),
            "frontier_hash216": frontier["frontier_hash216"],
            "legacy_direct_promotion_exposed": False,
        }

    def _next_version(self, predicate_id: str, record_kind: str) -> int:
        versions = [
            int(record["version"])
            for record in self._records.values()
            if record["predicate_id"] == predicate_id and record["record_kind"] == record_kind
        ]
        return max(versions, default=0) + 1

    def freeze_candidate(
        self,
        candidate: Mapping[str, Any],
        promotion_evidence: Mapping[str, Any],
        *,
        activate: bool = True,
        supersedes: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self._lock:
            normalized_candidate = validate_freeze_candidate(candidate)
            normalized_evidence = _validate_stage_evidence(promotion_evidence)
            predicate_id = normalized_candidate["predicate_id"]
            record_kind = normalized_candidate["promotion_track"]
            active = (
                self._active_constraints
                if record_kind == "RUNTIME_CONSTRAINT"
                else self._active_style_profiles
            )
            current_active = active.get(predicate_id)
            if supersedes is not None:
                if not current_active or str(supersedes) != current_active:
                    raise GraphicsConstraintRegistryError("P181_CONSTRAINT_SUPERSESSION_TARGET_INVALID")
            elif current_active is not None and activate:
                raise GraphicsConstraintRegistryError("P181_ACTIVE_CONSTRAINT_REQUIRES_EXPLICIT_SUPERSESSION")

            record_base = {
                "schema": HARD_RECORD_SCHEMA if record_kind == "RUNTIME_CONSTRAINT" else STYLE_RECORD_SCHEMA,
                "contract": CONTRACT,
                "authority": AUTHORITY,
                "record_kind": record_kind,
                "predicate_id": predicate_id,
                "candidate_hash216": normalized_candidate["candidate_hash216"],
                "candidate_class": normalized_candidate["candidate_class"],
                "proposition": normalized_candidate["proposition"],
                "domain": normalized_candidate["domain"],
                "version": self._next_version(predicate_id, record_kind),
                "support_count": normalized_candidate["support_count"],
                "distinct_job_count": normalized_candidate["distinct_job_count"],
                "supporting_record_hash216": normalized_candidate["supporting_record_hash216"],
                "supporting_job_ids": normalized_candidate["supporting_job_ids"],
                "counterexample_record_hash216": [],
                "evidence_root_hash216": normalized_candidate["evidence_root_hash216"],
                "promotion_evidence": normalized_evidence,
                "supersedes": supersedes,
                "state": "FROZEN_IMMUTABLE",
                "runtime_constraint_authority": record_kind == "RUNTIME_CONSTRAINT",
                "style_profile_authority": record_kind == "STYLE_PROFILE",
            }
            record_hash216 = hash216(record_base, domain=CONSTRAINT_RECORD_DOMAIN)
            prior = self._records.get(record_hash216)
            if prior is not None:
                return {
                    "schema": "HHS_P181_GRAPHICS_CONSTRAINT_FREEZE_RESULT_V1",
                    "ok": True,
                    "status": "HHS_GRAPHICS_CONSTRAINT_FREEZE_REUSED",
                    "record": prior,
                    "frontier": self._frontier_payload(),
                    "reused": True,
                }
            record = {**record_base, "record_hash216": record_hash216}
            record["receipt_hash72"] = hash72(record, domain=CONSTRAINT_RECEIPT_DOMAIN)
            freeze_event = self._append_event("FREEZE", {"record": record})
            activation_event = None
            if activate:
                if supersedes is not None:
                    activation_event = self._append_event(
                        "SUPERSEDE",
                        {
                            "predicate_id": predicate_id,
                            "record_kind": record_kind,
                            "from_record_hash216": supersedes,
                            "target_record_hash216": record_hash216,
                        },
                    )
                else:
                    activation_event = self._append_event(
                        "ACTIVATE",
                        {
                            "predicate_id": predicate_id,
                            "record_kind": record_kind,
                            "target_record_hash216": record_hash216,
                        },
                    )
            return {
                "schema": "HHS_P181_GRAPHICS_CONSTRAINT_FREEZE_RESULT_V1",
                "ok": True,
                "status": (
                    "HHS_GRAPHICS_RUNTIME_CONSTRAINT_FROZEN"
                    if record_kind == "RUNTIME_CONSTRAINT"
                    else "HHS_GRAPHICS_STYLE_PROFILE_FROZEN"
                ),
                "record": record,
                "freeze_event_hash216": freeze_event["event_hash216"],
                "activation_event_hash216": (
                    activation_event["event_hash216"] if activation_event else None
                ),
                "frontier": self._frontier_payload(),
                "reused": False,
            }

    def rollback(
        self,
        predicate_id: str,
        *,
        record_kind: str = "RUNTIME_CONSTRAINT",
        target_record_hash216: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self._lock:
            if record_kind not in RECORD_KINDS:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_RECORD_KIND_INVALID")
            active = (
                self._active_constraints
                if record_kind == "RUNTIME_CONSTRAINT"
                else self._active_style_profiles
            )
            current = active.get(predicate_id)
            if current is None:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_ACTIVE_RECORD_NOT_FOUND")
            candidates = sorted(
                (
                    record
                    for record in self._records.values()
                    if record["predicate_id"] == predicate_id
                    and record["record_kind"] == record_kind
                    and record["record_hash216"] != current
                ),
                key=lambda record: int(record["version"]),
                reverse=True,
            )
            if target_record_hash216 is None:
                target = next(
                    (
                        record
                        for record in candidates
                        if int(record["version"]) < int(self._records[current]["version"])
                    ),
                    None,
                )
            else:
                target = self._records.get(str(target_record_hash216))
                if target is not None and (
                    target["predicate_id"] != predicate_id
                    or target["record_kind"] != record_kind
                    or target["record_hash216"] == current
                ):
                    target = None
            if target is None:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_ROLLBACK_TARGET_NOT_FOUND")
            event = self._append_event(
                "ROLLBACK",
                {
                    "predicate_id": predicate_id,
                    "record_kind": record_kind,
                    "from_record_hash216": current,
                    "target_record_hash216": target["record_hash216"],
                },
            )
            return {
                "schema": "HHS_P181_GRAPHICS_CONSTRAINT_ROLLBACK_RESULT_V1",
                "ok": True,
                "status": "HHS_GRAPHICS_CONSTRAINT_ROLLBACK_VERIFIED",
                "event_hash216": event["event_hash216"],
                "from_record_hash216": current,
                "target_record_hash216": target["record_hash216"],
                "frontier": self._frontier_payload(),
            }

    def active_frontier(self) -> Dict[str, Any]:
        with self._lock:
            return self._frontier_payload()

    def list_records(
        self,
        *,
        record_kind: Optional[str] = None,
        predicate_id: Optional[str] = None,
    ) -> list[Dict[str, Any]]:
        values: Iterable[Dict[str, Any]] = self._records.values()
        if record_kind:
            values = (record for record in values if record["record_kind"] == record_kind)
        if predicate_id:
            values = (record for record in values if record["predicate_id"] == predicate_id)
        return [
            stable(record)
            for record in sorted(
                values,
                key=lambda record: (
                    record["record_kind"],
                    record["predicate_id"],
                    int(record["version"]),
                ),
            )
        ]

    def verify_replay(self) -> Dict[str, Any]:
        with self._lock:
            observed = self._frontier_payload()
            replay_records: Dict[str, Dict[str, Any]] = {}
            active_constraints: Dict[str, str] = {}
            active_styles: Dict[str, str] = {}
            for event in self._events:
                payload = event["payload"]
                event_type = event["event_type"]
                if event_type == "FREEZE":
                    record = payload["record"]
                    replay_records[record["record_hash216"]] = record
                else:
                    active = (
                        active_constraints
                        if payload["record_kind"] == "RUNTIME_CONSTRAINT"
                        else active_styles
                    )
                    if event_type in {"SUPERSEDE", "ROLLBACK"}:
                        if active.get(payload["predicate_id"]) != payload["from_record_hash216"]:
                            raise GraphicsConstraintRegistryError("P181_CONSTRAINT_REPLAY_ACTIVE_MISMATCH")
                    active[payload["predicate_id"]] = payload["target_record_hash216"]
            if replay_records != self._records:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_REPLAY_RECORD_MISMATCH")
            if active_constraints != self._active_constraints:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_REPLAY_RUNTIME_FRONTIER_MISMATCH")
            if active_styles != self._active_style_profiles:
                raise GraphicsConstraintRegistryError("P181_CONSTRAINT_REPLAY_STYLE_FRONTIER_MISMATCH")
            return {
                "schema": "HHS_P181_GRAPHICS_CONSTRAINT_REPLAY_RESULT_V1",
                "ok": True,
                "status": "HHS_GRAPHICS_CONSTRAINT_COLD_RESTART_REPLAY_VERIFIED",
                "event_count": len(self._events),
                "record_count": len(self._records),
                "frontier_hash216": observed["frontier_hash216"],
                "active_runtime_constraints": observed["active_runtime_constraints"],
                "active_style_profiles": observed["active_style_profiles"],
            }
