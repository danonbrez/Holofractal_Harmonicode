"""Durable, deduplicated background jobs for the bounded Pass 196 deep scan."""
from __future__ import annotations

import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Mapping

SCHEMA = "HHS_PASS_196_INTEGRATION_SCAN_JOB_V1"
TERMINAL = frozenset({"SUCCEEDED", "FAILED", "INTERRUPTED"})
ACTIVE = frozenset({"QUEUED", "RUNNING"})


def _unix_ms() -> int:
    return time.time_ns() // 1_000_000


def _stable(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str))


def _job_order(job: Mapping[str, Any]) -> tuple[int, str]:
    return (
        int(job.get("created_at_unix_ms") or 0),
        str(job.get("job_id") or ""),
    )


class Pass196ScanJobError(RuntimeError):
    pass


class Pass196ScanJobManager:
    """Own one serialized deep-scan worker while the scan itself remains parallel."""

    def __init__(
        self,
        runner: Callable[..., Mapping[str, Any]],
        *,
        state_root: str | Path | None = None,
    ) -> None:
        default_root = Path(
            os.getenv("HHS_PASS196_STATE_ROOT", ".hhs/pass196")
        ).resolve()
        self.state_root = Path(state_root or default_root).resolve() / "scan-jobs"
        self._runner = runner
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="hhs-pass196-scan-job",
        )
        self._jobs: dict[str, dict[str, Any]] = {}
        self._latest_job_id: str | None = None
        self._load_restart_state()

    def _path(self, job_id: str) -> Path:
        return self.state_root / f"{job_id}.json"

    def _persist(self, job: Mapping[str, Any]) -> None:
        self.state_root.mkdir(parents=True, exist_ok=True)
        path = self._path(str(job["job_id"]))
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(job, sort_keys=True, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(path)

    def _load_restart_state(self) -> None:
        if not self.state_root.is_dir():
            return
        loaded: list[dict[str, Any]] = []
        for path in sorted(self.state_root.glob("*.json")):
            try:
                job = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            job_id = job.get("job_id")
            if not isinstance(job_id, str) or not job_id:
                continue
            if job.get("state") in ACTIVE:
                job["state"] = "INTERRUPTED"
                job["finished_at_unix_ms"] = _unix_ms()
                job["error"] = {
                    "type": "ProcessRestart",
                    "message": "scan job did not reach a terminal state before process restart",
                }
                self._persist(job)
            loaded.append(job)

        for job in sorted(loaded, key=_job_order):
            job_id = str(job["job_id"])
            self._jobs[job_id] = job
        if loaded:
            self._latest_job_id = str(max(loaded, key=_job_order)["job_id"])

    @staticmethod
    def _summary(result: Mapping[str, Any]) -> dict[str, Any]:
        return {
            key: _stable(result.get(key))
            for key in (
                "schema",
                "version",
                "phase",
                "scanned",
                "operational",
                "integration_closed",
                "ok",
                "manifest_hash72",
                "manifest_hash216",
                "file_count",
                "byte_count",
                "maximum_discovered_pass",
                "pass_state_counts",
                "surface_matrix",
                "gap_scope",
                "vector",
                "vm81_authorized_tick",
            )
            if key in result
        }

    def _active_job(self) -> dict[str, Any] | None:
        active = [job for job in self._jobs.values() if job.get("state") in ACTIVE]
        return max(active, key=_job_order) if active else None

    def submit(
        self,
        *,
        persist_vector: bool,
        source: str,
        vm81_receipt_hash72: str | None = None,
        authorization_factory: Callable[[], Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Submit one scan or return the existing active job.

        The authorization factory is evaluated only after the singleton active-job
        check and while the manager lock is held. A deduplicated request therefore
        creates no extra canonical tick and always returns the original job-bound
        witness.
        """
        with self._lock:
            active = self._active_job()
            if active is not None:
                response = _stable(active)
                response["deduplicated"] = True
                return response

            authorization: dict[str, Any] | None = None
            receipt_hash72 = vm81_receipt_hash72
            if authorization_factory is not None:
                produced = authorization_factory()
                if not isinstance(produced, Mapping):
                    raise Pass196ScanJobError(
                        "scan authorization factory must return a mapping"
                    )
                authorization = _stable(dict(produced))
                factory_receipt = authorization.get("receipt_hash72")
                if factory_receipt is not None and not isinstance(factory_receipt, str):
                    raise Pass196ScanJobError(
                        "scan authorization receipt_hash72 must be a string or null"
                    )
                if receipt_hash72 and factory_receipt and receipt_hash72 != factory_receipt:
                    raise Pass196ScanJobError(
                        "explicit and factory scan authorization receipts disagree"
                    )
                receipt_hash72 = receipt_hash72 or factory_receipt

            job_id = f"pass196-scan:{uuid.uuid4().hex}"
            job = {
                "schema": SCHEMA,
                "job_id": job_id,
                "state": "QUEUED",
                "created_at_unix_ms": _unix_ms(),
                "started_at_unix_ms": None,
                "finished_at_unix_ms": None,
                "persist_vector": bool(persist_vector),
                "source": source,
                "vm81_receipt_hash72": receipt_hash72,
                "vm81_authorized_tick": authorization,
                "result": None,
                "error": None,
                "deduplicated": False,
            }
            self._jobs[job_id] = job
            self._latest_job_id = job_id
            self._persist(job)
            self._executor.submit(self._execute, job_id)
            return _stable(job)

    def _execute(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job["state"] = "RUNNING"
            job["started_at_unix_ms"] = _unix_ms()
            self._persist(job)
            persist_vector = bool(job["persist_vector"])
            receipt = job.get("vm81_receipt_hash72")

        try:
            result = self._runner(
                vm81_receipt_hash72=receipt,
                persist_vector=persist_vector,
            )
        except Exception as exc:  # boundary converts every failure to evidence
            with self._lock:
                job = self._jobs[job_id]
                job["state"] = "FAILED"
                job["finished_at_unix_ms"] = _unix_ms()
                job["error"] = {
                    "type": type(exc).__name__,
                    "message": str(exc),
                }
                self._persist(job)
            return

        with self._lock:
            job = self._jobs[job_id]
            job["state"] = "SUCCEEDED"
            job["finished_at_unix_ms"] = _unix_ms()
            job["result"] = self._summary(result)
            self._persist(job)

    def get(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise Pass196ScanJobError(f"unknown Pass 196 scan job: {job_id}")
            return _stable(job)

    def latest(self) -> dict[str, Any] | None:
        with self._lock:
            if self._latest_job_id is None:
                return None
            return _stable(self._jobs[self._latest_job_id])

    def wait(self, job_id: str, timeout_seconds: float = 10.0) -> dict[str, Any]:
        deadline = time.monotonic() + max(0.0, timeout_seconds)
        while True:
            job = self.get(job_id)
            if job["state"] in TERMINAL:
                return job
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Pass 196 scan job did not finish: {job_id}")
            time.sleep(0.01)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=False)
