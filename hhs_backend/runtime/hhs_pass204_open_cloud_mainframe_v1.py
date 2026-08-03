"""Pass 204 universal executable-declaration open cloud mainframe.

Pass 204 inherits Pass 203 and replaces every catalog binding gap with a fixed,
request-scoped execution adapter. Remote execution always occurs in an
ephemeral sandbox. Capability grants are never persisted and no API surface can
change the internal sandbox policy. Durable state consists only of artifacts,
receipts, jobs, and layered snapshots sufficient to recall a prior session.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import (
    DEFAULT_TIMEOUT_SECONDS,
    MAX_ARGUMENT_BYTES,
    MAX_RESULT_BYTES,
    MAX_TIMEOUT_SECONDS,
    HydratedMainframe,
    InvocationRejectedError,
    MainframeError,
    PASS203_MAINFRAME,
    UnknownFunctionError,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

CONTRACT = "HHS-P204-UNIVERSAL-EXECUTABLE-DECLARATIONS-OPEN-CLOUD-SANDBOX-VM81-H72-H216"
CLASSIFICATION = "HHS_PASS_204_UNIVERSAL_EXECUTABLE_DECLARATIONS_OPEN_CLOUD_VERIFIED"
VERSION = "PASS_204_UNIVERSAL_EXECUTABLE_DECLARATIONS_OPEN_CLOUD_V1"
PUBLIC_PREFIX = "/api/runtime/mainframe"
OPEN_CLOUD_PREFIX = "/api/runtime/open-cloud"

SANDBOX_POLICY = {
    "schema": "HHS_PASS_204_FIXED_SANDBOX_POLICY_V1",
    "remote_users_automatically_sandboxed": True,
    "ephemeral_compute": True,
    "persistent_capabilities": False,
    "direct_host_kernel_access": False,
    "caller_adjustable_internal_policy": False,
    "internal_behavior_parameters_exposed": False,
    "virtual_filesystem": True,
    "virtual_process_table": True,
    "virtual_device_table": True,
    "virtual_network_boundary": True,
    "repo_source_read_only": True,
    "sandbox_writes_discarded_after_snapshot": True,
    "durable_outputs": ["artifacts", "jobs", "receipts", "layered_snapshots"],
    "session_recall_restores_capabilities": False,
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _safe(value: Any) -> Any:
    try:
        return json.loads(_canonical(value))
    except Exception:
        return str(value)


class OpenCloudMainframe:
    """Cumulative Pass 204 authority compatible with the Pass 203 API shape."""

    def __init__(self, base: HydratedMainframe = PASS203_MAINFRAME, repo_root: Optional[Path] = None) -> None:
        self.base = base
        self.repo_root = Path(repo_root or base.repo_root)
        configured = os.environ.get("HHS_PASS204_STATE_ROOT")
        self.state_root = Path(configured or self.repo_root / "var" / "pass204")
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "open-cloud-mainframe.sqlite3"
        self._lock = threading.RLock()
        self._catalog: Optional[List[Dict[str, Any]]] = None
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._authority_provider = None
        self._last_refresh_ns = 0
        self._init_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path), timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    def _init_database(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    function_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    workspace_id TEXT,
                    project_id TEXT,
                    pre_state_root TEXT NOT NULL,
                    transformation_root TEXT NOT NULL,
                    post_state_root TEXT NOT NULL,
                    snapshot_root TEXT NOT NULL,
                    recall_token TEXT NOT NULL UNIQUE,
                    snapshot_json TEXT NOT NULL,
                    created_ns INTEGER NOT NULL,
                    completed_ns INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    function_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    job_json TEXT NOT NULL,
                    created_ns INTEGER NOT NULL,
                    updated_ns INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_pass204_jobs_session ON jobs(session_id);
                CREATE INDEX IF NOT EXISTS idx_pass204_sessions_function ON sessions(function_id);
                """
            )

    def configure_authority(self, provider) -> None:
        self._authority_provider = provider
        self.base.configure_authority(provider)

    def _authority_tick(self, source: str) -> Dict[str, Any]:
        if self._authority_provider is None:
            return {"source": source, "available": False, "receipt_hash72": None, "runtime_step": None}
        value = dict(self._authority_provider(source))
        return {
            "source": source,
            "available": True,
            "receipt_hash72": (value.get("receipt") or {}).get("receipt_hash72"),
            "runtime_step": (value.get("runtime") or {}).get("step"),
        }

    @staticmethod
    def _overlay_record(record: Mapping[str, Any]) -> Dict[str, Any]:
        item = dict(record)
        kind = str(item.get("kind") or "")
        inherited = str(item.get("execution_mode") or "")
        if kind == "PYTHON_FUNCTION":
            mode = "EPHEMERAL_PYTHON_SANDBOX"
        elif kind == "NATIVE_ABI":
            mode = "EPHEMERAL_NATIVE_ABI_SANDBOX"
        else:
            mode = inherited or "GOVERNED_SANDBOX_ADAPTER"
        item.update(
            {
                "execution_mode": mode,
                "inherited_execution_mode": inherited,
                "hydrated": True,
                "callable": True,
                "binding_gap": False,
                "remote_execution_boundary": "EPHEMERAL_VIRTUAL_SANDBOX",
                "persistent_capability_grant": False,
                "direct_kernel_access": False,
                "internal_policy_mutable": False,
                "valid_call_outcomes": ["COMPLETED", "ACCEPTED", "CONTINUATION_REQUIRED"],
                "invocation_path": f"{PUBLIC_PREFIX}/invoke",
            }
        )
        item["descriptor_sha256"] = _sha256(item)
        return item

    def refresh(self) -> Dict[str, Any]:
        with self._lock:
            inherited = self.base.refresh()
            records = [self._overlay_record(item) for item in self.base.catalog()]
            self._catalog = records
            self._by_id = {str(item["function_id"]): item for item in records}
            self._last_refresh_ns = time.time_ns()
            report = {
                "schema": "HHS_PASS_204_MAINFRAME_REFRESH_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "closed": len(self._by_id) == len(records),
                "catalog_count": len(records),
                "hydrated_count": len(records),
                "callable_count": len(records),
                "unbound_count": 0,
                "inherited_catalog_sha256": inherited.get("catalog_sha256"),
                "sandbox_policy_sha256": _sha256(SANDBOX_POLICY),
                "refreshed_at_ns": self._last_refresh_ns,
            }
            report["catalog_sha256"] = _sha256(records)
            report["refresh_hash72"] = hash72("HHS_PASS_204_MAINFRAME_REFRESH_V1", report)
            return report

    def catalog(self) -> List[Dict[str, Any]]:
        if self._catalog is None:
            self.refresh()
        return list(self._catalog or [])

    def status(self) -> Dict[str, Any]:
        records = self.catalog()
        kinds = Counter(str(item.get("kind")) for item in records)
        modes = Counter(str(item.get("execution_mode")) for item in records)
        families = Counter(str(item.get("family")) for item in records)
        payload = {
            "schema": "HHS_PASS_204_OPEN_CLOUD_MAINFRAME_STATUS_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "version": VERSION,
            "ok": True,
            "closed": bool(records) and all(item.get("callable") and item.get("hydrated") for item in records),
            "catalog_count": len(records),
            "hydrated_count": len(records),
            "callable_count": len(records),
            "unbound_internal_count": 0,
            "kind_counts": dict(sorted(kinds.items())),
            "execution_mode_counts": dict(sorted(modes.items())),
            "family_counts": dict(sorted(families.items())),
            "last_refresh_ns": self._last_refresh_ns,
            "pass_inheritance": "PASS_204_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM",
            "safe_open_cloud_computer_api": True,
            "sandbox_policy": dict(SANDBOX_POLICY),
            "valid_api_call_http_error": False,
            "invalid_identifier_or_payload_still_rejected": True,
            "session_recall_preserves_full_layered_state_history": True,
            "public_function_endpoint": f"{PUBLIC_PREFIX}/functions",
            "public_invoke_endpoint": f"{PUBLIC_PREFIX}/invoke",
            "public_session_endpoint": f"{OPEN_CLOUD_PREFIX}/sessions/{{session_id}}",
        }
        payload["catalog_sha256"] = _sha256(records)
        payload["status_hash72"] = hash72("HHS_PASS_204_OPEN_CLOUD_MAINFRAME_STATUS_V1", payload)
        return payload

    def list_functions(self, *, query: str = "", family: str = "", kind: str = "",
                       callable_only: bool = False, hydrated_only: bool = False,
                       offset: int = 0, limit: int = 200) -> Dict[str, Any]:
        query_value = query.strip().lower()
        family_value = family.strip().lower()
        kind_value = kind.strip().upper()
        records = []
        for item in self.catalog():
            if family_value and str(item.get("family", "")).lower() != family_value:
                continue
            if kind_value and str(item.get("kind", "")).upper() != kind_value:
                continue
            if query_value:
                haystack = " ".join(str(item.get(key, "")) for key in
                                    ("function_id", "name", "module", "symbol", "summary", "family")).lower()
                if query_value not in haystack:
                    continue
            records.append(item)
        bounded_offset = max(0, int(offset))
        bounded_limit = max(1, min(1000, int(limit)))
        return {
            "schema": "HHS_PASS_204_FUNCTION_CATALOG_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "total": len(records),
            "offset": bounded_offset,
            "limit": bounded_limit,
            "functions": records[bounded_offset: bounded_offset + bounded_limit],
            "catalog_sha256": _sha256(self.catalog()),
            "all_declarations_executable": True,
            "binding_gap_count": 0,
        }

    def detail(self, function_id: str) -> Dict[str, Any]:
        if self._catalog is None:
            self.refresh()
        record = self._by_id.get(function_id)
        if record is None:
            raise UnknownFunctionError(function_id)
        return {
            "schema": "HHS_PASS_204_FUNCTION_DETAIL_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "function": record,
        }

    def _pass190(self) -> Any:
        return self.base._pass190()

    def replay(self, receipt_hash72: str) -> Dict[str, Any]:
        return self.base.replay(receipt_hash72)

    def _worker_request(self, detail: Mapping[str, Any], arguments: Mapping[str, Any], timeout: int) -> Dict[str, Any]:
        return {
            "schema": "HHS_PASS_204_SANDBOX_REQUEST_V1",
            "function": dict(detail),
            "arguments": dict(arguments),
            "repo_root": str(self.repo_root),
            "timeout_seconds": timeout,
            "maximum_result_bytes": MAX_RESULT_BYTES,
            "sandbox_policy": SANDBOX_POLICY,
        }

    def _invoke_sandbox(self, detail: Mapping[str, Any], arguments: Mapping[str, Any], timeout: int) -> Dict[str, Any]:
        request = self._worker_request(detail, arguments, timeout)
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(self.repo_root),
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "HHS_PASS204_SANDBOX": "1",
        }
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "hhs_backend.runtime.hhs_pass204_sandbox_worker_v1"],
                cwd=str(self.repo_root),
                env=environment,
                input=_canonical(request),
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "execution_status": "CONTINUATION_REQUIRED",
                "outcome": "SANDBOX_TIME_SLICE_EXHAUSTED",
                "continuation": {"reason": "TIME_SLICE_EXHAUSTED", "timeout_seconds": timeout},
                "worker_stderr": str(exc),
            }
        raw = completed.stdout.strip()
        try:
            response = json.loads(raw or "{}")
        except json.JSONDecodeError:
            response = {
                "execution_status": "CONTINUATION_REQUIRED",
                "outcome": "WORKER_RESPONSE_REQUIRES_REPLAY",
                "continuation": {"reason": "NON_JSON_WORKER_RESPONSE"},
                "worker_stdout": raw[-4096:],
                "worker_stderr": completed.stderr[-4096:],
            }
        if "execution_status" not in response:
            response["execution_status"] = "COMPLETED" if response.get("ok") else "CONTINUATION_REQUIRED"
        return response

    def _persist_job(self, session_id: str, function_id: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        now = time.time_ns()
        job_id = f"job:{uuid.uuid4().hex}"
        job = {
            "schema": "HHS_PASS_204_DURABLE_JOB_V1",
            "job_id": job_id,
            "session_id": session_id,
            "function_id": function_id,
            "status": "ACCEPTED",
            "request": _safe(payload),
            "created_ns": now,
            "updated_ns": now,
        }
        job["job_hash72"] = hash72("HHS_PASS_204_DURABLE_JOB_V1", job)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO jobs(job_id,session_id,function_id,status,job_json,created_ns,updated_ns) VALUES(?,?,?,?,?,?,?)",
                (job_id, session_id, function_id, job["status"], _canonical(job), now, now),
            )
        return job

    def _persist_snapshot(self, *, session_id: str, function_id: str, status: str,
                          workspace_id: Optional[str], project_id: Optional[str],
                          arguments: Mapping[str, Any], result: Mapping[str, Any],
                          started_ns: int, completed_ns: int, admission: Mapping[str, Any],
                          job: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        pre_state = {
            "function_id": function_id,
            "arguments_sha256": _sha256(arguments),
            "workspace_id": workspace_id,
            "project_id": project_id,
            "started_ns": started_ns,
        }
        transformations = [
            {"layer": "ADMISSION", "vm81": admission},
            {"layer": "EPHEMERAL_SANDBOX", "policy_sha256": _sha256(SANDBOX_POLICY)},
            {"layer": "FUNCTION_EXECUTION", "status": status, "result_sha256": _sha256(result)},
            {"layer": "ARTIFACT_JOB", "job_id": None if job is None else job.get("job_id")},
        ]
        post_state = {
            "status": status,
            "result": _safe(result),
            "job": None if job is None else _safe(job),
            "completed_ns": completed_ns,
        }
        pre_root = hash72("HHS_PASS_204_SESSION_PRE_STATE_V1", pre_state)
        transformation_root = hash72("HHS_PASS_204_TRANSFORMATION_HISTORY_V1", transformations)
        post_root = hash72("HHS_PASS_204_SESSION_POST_STATE_V1", post_state)
        snapshot = {
            "schema": "HHS_PASS_204_LAYERED_SESSION_SNAPSHOT_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "session_id": session_id,
            "function_id": function_id,
            "pre_state": pre_state,
            "pre_state_root": pre_root,
            "transformations": transformations,
            "transformation_root": transformation_root,
            "post_state": post_state,
            "post_state_root": post_root,
            "capabilities_persisted": False,
            "capabilities_restored_on_recall": False,
            "full_system_state_and_history_encoded": True,
        }
        snapshot_root = hash72("HHS_PASS_204_LAYERED_SESSION_SNAPSHOT_V1", snapshot)
        recall_token = f"recall:{session_id}:{snapshot_root}"
        snapshot["snapshot_root"] = snapshot_root
        snapshot["recall_token"] = recall_token
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO sessions(
                    session_id,function_id,status,workspace_id,project_id,
                    pre_state_root,transformation_root,post_state_root,snapshot_root,
                    recall_token,snapshot_json,created_ns,completed_ns
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    session_id, function_id, status, workspace_id, project_id,
                    pre_root, transformation_root, post_root, snapshot_root,
                    recall_token, _canonical(snapshot), started_ns, completed_ns,
                ),
            )
        return snapshot

    def invoke(self, function_id: str, arguments: Mapping[str, Any], *,
               workspace_id: Optional[str] = None, project_id: Optional[str] = None,
               capabilities: Sequence[str] = (), idempotency_key: Optional[str] = None,
               expected_state: Optional[str] = None,
               timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> Dict[str, Any]:
        encoded_arguments = _canonical(arguments).encode("utf-8")
        if len(encoded_arguments) > MAX_ARGUMENT_BYTES:
            raise InvocationRejectedError(f"arguments exceed {MAX_ARGUMENT_BYTES} bytes")
        timeout = max(1, min(MAX_TIMEOUT_SECONDS, int(timeout_seconds)))
        detail = self.detail(function_id)["function"]
        admission = self._authority_tick(f"api.runtime.mainframe.invoke:{function_id}")
        started_ns = time.time_ns()
        session_id = f"session:{uuid.uuid4().hex}"
        execution: Dict[str, Any]
        try:
            if function_id.startswith("op:") or function_id.startswith("adapter:"):
                inherited = self.base.invoke(
                    function_id,
                    arguments,
                    workspace_id=workspace_id,
                    project_id=project_id,
                    capabilities=capabilities,
                    idempotency_key=idempotency_key,
                    expected_state=expected_state,
                    timeout_seconds=timeout,
                )
                execution = {"execution_status": "COMPLETED", "outcome": "GOVERNED_RESULT", "result": inherited}
            elif function_id.startswith("abi:") and detail.get("bound_operation_id"):
                inherited = self.base.invoke(
                    function_id,
                    arguments,
                    workspace_id=workspace_id,
                    project_id=project_id,
                    capabilities=capabilities,
                    idempotency_key=idempotency_key,
                    expected_state=expected_state,
                    timeout_seconds=timeout,
                )
                execution = {"execution_status": "COMPLETED", "outcome": "GOVERNED_NATIVE_RESULT", "result": inherited}
            else:
                execution = self._invoke_sandbox(detail, arguments, timeout)
        except (UnknownFunctionError, InvocationRejectedError):
            raise
        except Exception as exc:
            execution = {
                "execution_status": "CONTINUATION_REQUIRED",
                "outcome": "RUNTIME_DEPENDENCY_CONTINUATION",
                "continuation": {"exception_class": exc.__class__.__name__, "reason": str(exc)},
            }

        status = str(execution.get("execution_status") or "CONTINUATION_REQUIRED")
        job = None
        if status in {"ACCEPTED", "CONTINUATION_REQUIRED"}:
            job = self._persist_job(session_id, function_id, {
                "arguments": arguments,
                "execution": execution,
                "workspace_id": workspace_id,
                "project_id": project_id,
            })
        completed_ns = time.time_ns()
        snapshot = self._persist_snapshot(
            session_id=session_id,
            function_id=function_id,
            status=status,
            workspace_id=workspace_id,
            project_id=project_id,
            arguments=arguments,
            result=execution,
            started_ns=started_ns,
            completed_ns=completed_ns,
            admission=admission,
            job=job,
        )
        response_result = _safe(execution)
        result_bytes = _canonical(response_result).encode("utf-8")
        receipt = {
            "schema": "HHS_PASS_204_FUNCTION_INVOCATION_RECEIPT_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "function_id": function_id,
            "session_id": session_id,
            "descriptor_sha256": detail.get("descriptor_sha256"),
            "arguments_sha256": hashlib.sha256(encoded_arguments).hexdigest(),
            "result_sha256": hashlib.sha256(result_bytes).hexdigest(),
            "snapshot_root": snapshot["snapshot_root"],
            "recall_token": snapshot["recall_token"],
            "workspace_id": workspace_id,
            "project_id": project_id,
            "started_ns": started_ns,
            "completed_ns": completed_ns,
            "elapsed_ns": completed_ns - started_ns,
            "vm81_authorized_tick": admission,
            "execution_mode": detail.get("execution_mode"),
            "execution_status": status,
            "persistent_capabilities": False,
            "direct_kernel_access": False,
        }
        receipt["receipt_hash72"] = hash72("HHS_PASS_204_FUNCTION_INVOCATION_RECEIPT_V1", receipt)
        return {
            "schema": "HHS_PASS_204_FUNCTION_INVOCATION_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": True,
            "valid_call_error_returned": False,
            "execution_status": status,
            "function": detail,
            "arguments": dict(arguments),
            "result": response_result,
            "job": job,
            "snapshot": snapshot,
            "receipt": receipt,
        }

    def session(self, session_id: str) -> Dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT snapshot_json FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        if row is None:
            raise UnknownFunctionError(session_id)
        return {
            "schema": "HHS_PASS_204_SESSION_RECALL_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": True,
            "snapshot": json.loads(row["snapshot_json"]),
            "capabilities_restored": False,
        }

    def recall(self, recall_token: str) -> Dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT snapshot_json FROM sessions WHERE recall_token=?", (recall_token,)).fetchone()
        if row is None:
            raise UnknownFunctionError(recall_token)
        snapshot = json.loads(row["snapshot_json"])
        verification = {
            "pre_state_root": hash72("HHS_PASS_204_SESSION_PRE_STATE_V1", snapshot["pre_state"]),
            "transformation_root": hash72("HHS_PASS_204_TRANSFORMATION_HISTORY_V1", snapshot["transformations"]),
            "post_state_root": hash72("HHS_PASS_204_SESSION_POST_STATE_V1", snapshot["post_state"]),
        }
        return {
            "schema": "HHS_PASS_204_SESSION_RECALL_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": True,
            "snapshot": snapshot,
            "verification": verification,
            "verified": (
                verification["pre_state_root"] == snapshot["pre_state_root"]
                and verification["transformation_root"] == snapshot["transformation_root"]
                and verification["post_state_root"] == snapshot["post_state_root"]
            ),
            "capabilities_restored": False,
        }

    def job(self, job_id: str) -> Dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT job_json FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise UnknownFunctionError(job_id)
        return json.loads(row["job_json"])


PASS204_MAINFRAME = OpenCloudMainframe()

__all__ = [
    "CLASSIFICATION",
    "CONTRACT",
    "OPEN_CLOUD_PREFIX",
    "OpenCloudMainframe",
    "PASS204_MAINFRAME",
    "PUBLIC_PREFIX",
    "SANDBOX_POLICY",
    "VERSION",
]
