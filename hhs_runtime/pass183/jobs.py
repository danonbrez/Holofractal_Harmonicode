"""Durable finite-state Pass 183 job storage."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path
import json
import os
import time
from typing import Any, Mapping

from .core import GLOBAL_MODULUS, Pass183Error, _canonical
from .runtime import ProbabilityHydrationRuntime


@dataclass
class ProbabilityHydrationJob:
    job_id: str
    state: str
    request: dict[str, Any]
    created_ns: int
    updated_ns: int
    deadline_ns: int
    checkpoint: str = "CREATED"
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    attempt: int = 1
    events: list[dict[str, Any]] = field(default_factory=list)


class ProbabilityHydrationJobStore:
    """Durable finite-state Pass 183 job manager."""

    TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT"}

    def __init__(self, runtime: ProbabilityHydrationRuntime, root: str | Path) -> None:
        self.runtime = runtime
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, ProbabilityHydrationJob] = {}
        for path in sorted(self.root.glob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                raw.setdefault("events", [])
                self._jobs[path.stem] = ProbabilityHydrationJob(**raw)
            except Exception as exc:
                raise Pass183Error("P183_REJECT_REPLAY", f"job_file:{path.name}") from exc

    def _persist(self, job: ProbabilityHydrationJob) -> None:
        target = self.root / f"{job.job_id}.json"
        temporary = target.with_suffix(".json.tmp")
        temporary.write_bytes(_canonical(asdict(job)) + b"\n")
        os.replace(temporary, target)

    @staticmethod
    def _event(job: ProbabilityHydrationJob, state: str, detail: str) -> None:
        job.events.append(
            {
                "sequence": len(job.events),
                "state": state,
                "detail": detail,
                "timestamp_ns": time.time_ns(),
            }
        )

    def create(self, request: Mapping[str, Any], *, timeout_ms: int = 30_000) -> ProbabilityHydrationJob:
        if not isinstance(timeout_ms, int) or isinstance(timeout_ms, bool) or not 1 <= timeout_ms <= 300_000:
            raise Pass183Error("P183_TIMEOUT", "timeout_ms")
        now = time.time_ns()
        identity = sha256(b"P183-JOB\0" + _canonical(request) + now.to_bytes(16, "big")).hexdigest()
        job = ProbabilityHydrationJob(
            job_id=identity,
            state="QUEUED",
            request=json.loads(_canonical(request)),
            created_ns=now,
            updated_ns=now,
            deadline_ns=now + timeout_ms * 1_000_000,
        )
        self._event(job, "QUEUED", "job created")
        self._jobs[job.job_id] = job
        self._persist(job)
        return job

    def get(self, job_id: str) -> ProbabilityHydrationJob:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise Pass183Error("P183_REJECT_PARSE", "job_not_found") from exc

    def run(self, job_id: str) -> ProbabilityHydrationJob:
        job = self.get(job_id)
        if job.state == "CANCELLED":
            return job
        if job.state not in {"QUEUED", "FAILED", "TIMED_OUT"}:
            raise Pass183Error("P183_REJECT_REPLAY", f"job_state:{job.state}")
        now = time.time_ns()
        if now > job.deadline_ns:
            job.state = "TIMED_OUT"
            job.updated_ns = now
            job.checkpoint = "DEADLINE"
            job.error = {"classification": "P183_TIMEOUT", "detail": "deadline"}
            self._event(job, "TIMED_OUT", "deadline reached before execution")
            self._persist(job)
            return job
        job.state = "RUNNING"
        job.updated_ns = now
        job.checkpoint = "VALIDATING"
        self._event(job, "RUNNING", "exact hydration execution started")
        self._persist(job)
        try:
            request = dict(job.request)
            job.result = self.runtime.execute(
                adapter=request["adapter"],
                equation=request["equation"],
                manifest=request["manifest"],
                seed_class=request.get("seed_class", "DETERMINISTIC_ENUMERATION"),
                seed=request.get("seed"),
                modulus=request.get("modulus", GLOBAL_MODULUS),
            )
            job.state = "SUCCEEDED"
            job.checkpoint = "RECEIPT_COMMITTED"
            job.error = None
            self._event(job, "SUCCEEDED", "VM81 receipt committed")
        except Pass183Error as exc:
            job.state = "FAILED"
            job.checkpoint = "REJECTED"
            job.error = {"classification": exc.classification, "detail": exc.detail}
            self._event(job, "FAILED", exc.classification)
        job.updated_ns = time.time_ns()
        self._persist(job)
        return job

    def cancel(self, job_id: str) -> ProbabilityHydrationJob:
        job = self.get(job_id)
        if job.state in self.TERMINAL:
            return job
        job.state = "CANCELLED"
        job.updated_ns = time.time_ns()
        job.checkpoint = "CANCELLED"
        job.error = {"classification": "P183_CANCELLED", "detail": "operator"}
        self._event(job, "CANCELLED", "cancelled by operator")
        self._persist(job)
        return job

    def retry(self, job_id: str, *, timeout_ms: int = 30_000) -> ProbabilityHydrationJob:
        prior = self.get(job_id)
        if prior.state not in {"FAILED", "CANCELLED", "TIMED_OUT"}:
            raise Pass183Error("P183_REJECT_REPLAY", "retry_nonterminal")
        retried = self.create(prior.request, timeout_ms=timeout_ms)
        retried.attempt = prior.attempt + 1
        self._event(retried, "QUEUED", f"retry_of:{prior.job_id}")
        self._persist(retried)
        return retried
