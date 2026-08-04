"""Durable repository-native AGI learning and optimization observer for Pass 209.

The observer consumes admitted or rejected assistant-turn evidence after the
user-facing provider hierarchy completes. It may derive optimization proposals
through the repository-native HHS language provider, but those proposals are
noncanonical, cannot mutate VM81, cannot write repository content, and require a
separate authorized admission path before use.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
    HHSNativeLiteRTLMTransport,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_PASS_209_NATIVE_AGI_OPTIMIZER_V1"
OBSERVATION_SCHEMA = "HHS_PASS_209_NATIVE_AGI_TURN_OBSERVATION_V1"
PROPOSAL_SCHEMA = "HHS_PASS_209_NATIVE_AGI_OPTIMIZATION_PROPOSAL_V1"
STATUS_SCHEMA = "HHS_PASS_209_NATIVE_AGI_OPTIMIZER_STATUS_V1"
DEFAULT_DB = "/var/lib/hhs/pass209/native_agi_optimizer.sqlite3"

OPTIMIZER_SYSTEM_INSTRUCTION = """You are the repository-native HHS backend
learning and optimization agent. Analyze the witnessed assistant-turn record
and return a concise optimization proposal. Identify reusable semantic,
tooling, routing, cache, retrieval, hydration, or validation improvements.
Preserve exact user propositions. Do not generate a user-facing answer. Do not
claim repository mutation, VM81 mutation, Hash72 or Hash216 commit, deployment,
or training completion. Every recommendation is a noncanonical proposal that
requires separate HHS admission."""


def _now_ms() -> int:
    return int(time.time() * 1000)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _bounded_text(value: Any, maximum: int = 32768) -> str:
    text = str(value or "")
    encoded = text.encode("utf-8")
    if len(encoded) <= maximum:
        return text
    return encoded[:maximum].decode("utf-8", errors="ignore")


def _assistant_message(turn: Mapping[str, Any]) -> Mapping[str, Any]:
    value = turn.get("assistant_message")
    return value if isinstance(value, Mapping) else {}


def _user_message(turn: Mapping[str, Any]) -> Mapping[str, Any]:
    value = turn.get("user_message")
    return value if isinstance(value, Mapping) else {}


class NativeAGIOptimizer:
    """SQLite-backed observation queue and noncanonical proposal producer."""

    def __init__(
        self,
        db_path: Optional[str | Path] = None,
        transport: Optional[Any] = None,
    ) -> None:
        self.db_path = Path(
            db_path
            or os.getenv("HHS_PASS209_OPTIMIZER_DB")
            or DEFAULT_DB
        )
        self.transport = transport or HHSNativeLiteRTLMTransport()
        self._lock = threading.RLock()
        self._initialized = False

    def _connect(self) -> sqlite3.Connection:
        if not self._initialized:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(self.db_path), timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        if not self._initialized:
            with self._lock:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS observations (
                        observation_root_hash72 TEXT PRIMARY KEY,
                        thread_id TEXT NOT NULL,
                        turn_root_hash72 TEXT NOT NULL,
                        selected_provider_id TEXT,
                        effective_mode TEXT,
                        fallback_used INTEGER NOT NULL,
                        turn_ok INTEGER NOT NULL,
                        payload_json TEXT NOT NULL,
                        status TEXT NOT NULL,
                        attempts INTEGER NOT NULL DEFAULT 0,
                        last_error TEXT,
                        created_at_unix_ms INTEGER NOT NULL,
                        updated_at_unix_ms INTEGER NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS observations_status_created
                    ON observations(status, created_at_unix_ms, observation_root_hash72);
                    CREATE TABLE IF NOT EXISTS proposals (
                        proposal_root_hash72 TEXT PRIMARY KEY,
                        observation_root_hash72 TEXT NOT NULL UNIQUE,
                        proposal_json TEXT NOT NULL,
                        provider_id TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        created_at_unix_ms INTEGER NOT NULL,
                        FOREIGN KEY(observation_root_hash72)
                          REFERENCES observations(observation_root_hash72)
                    );
                    """
                )
                connection.commit()
                self._initialized = True
        return connection

    def installation_status(self) -> Dict[str, Any]:
        installation = getattr(self.transport, "installation_status", None)
        if callable(installation):
            try:
                return dict(installation())
            except Exception as exc:
                return {
                    "ready": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
        return {
            "ready": False,
            "error": "native optimizer transport exposes no installation status",
        }

    def enqueue_turn(
        self,
        turn: Mapping[str, Any],
        *,
        selected_provider_id: Optional[str],
        effective_mode: str,
        fallback_used: bool,
    ) -> Dict[str, Any]:
        user = _user_message(turn)
        assistant = _assistant_message(turn)
        reasoning = str(assistant.get("reasoning_content") or "")
        tool_trace = turn.get("hhs_api_tool_trace")
        trace = list(tool_trace) if isinstance(tool_trace, list) else []
        payload: Dict[str, Any] = {
            "schema": OBSERVATION_SCHEMA,
            "version": VERSION,
            "thread_id": str(turn.get("thread_id") or user.get("thread_id") or ""),
            "turn_root_hash72": str(turn.get("turn_root_hash72") or ""),
            "selected_provider_id": str(selected_provider_id or ""),
            "effective_mode": str(effective_mode),
            "fallback_used": bool(fallback_used),
            "turn_ok": bool(turn.get("ok")),
            "turn_status": str(turn.get("status") or ""),
            "user_message": _bounded_text(user.get("content")),
            "assistant_message": _bounded_text(assistant.get("content")),
            "assistant_reasoning_present": bool(reasoning),
            "assistant_reasoning_root_hash72": (
                hash72("HHS_PASS_209_PROVIDER_REASONING_WITNESS_V1", reasoning)
                if reasoning
                else None
            ),
            "tool_trace": trace[:128],
            "tool_trace_count": len(trace),
            "provider_invocation_receipt_hash72": str(
                (turn.get("provider_invocation_receipt") or {}).get(
                    "provider_invocation_receipt_hash72"
                )
                or ""
            ),
            "provider_result_ingress_root_hash72": str(
                (turn.get("provider_result_ingress") or {}).get(
                    "provider_result_ingress_root_hash72"
                )
                or ""
            ),
            "runtime_mutation_admitted": False,
            "optimization_proposal_requires_separate_admission": True,
        }
        payload["observation_root_hash72"] = hash72(OBSERVATION_SCHEMA, payload)
        now = _now_ms()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO observations (
                    observation_root_hash72,thread_id,turn_root_hash72,
                    selected_provider_id,effective_mode,fallback_used,turn_ok,
                    payload_json,status,attempts,last_error,
                    created_at_unix_ms,updated_at_unix_ms
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    payload["observation_root_hash72"],
                    payload["thread_id"],
                    payload["turn_root_hash72"],
                    payload["selected_provider_id"],
                    payload["effective_mode"],
                    int(payload["fallback_used"]),
                    int(payload["turn_ok"]),
                    _canonical_json(payload),
                    "PENDING",
                    0,
                    None,
                    now,
                    now,
                ),
            )
            connection.commit()
        return {
            "schema": "HHS_PASS_209_NATIVE_AGI_OBSERVATION_ENQUEUE_V1",
            "ok": True,
            "observation_root_hash72": payload["observation_root_hash72"],
            "status": "PENDING",
            "native_agi_is_user_facing_provider": False,
            "runtime_mutation_admitted": False,
        }

    def _pending(self, limit: int) -> List[sqlite3.Row]:
        with self._connect() as connection:
            return list(
                connection.execute(
                    """
                    SELECT * FROM observations
                    WHERE status='PENDING'
                    ORDER BY created_at_unix_ms, observation_root_hash72
                    LIMIT ?
                    """,
                    (max(1, int(limit)),),
                ).fetchall()
            )

    @staticmethod
    def _extract_completion(raw: Mapping[str, Any]) -> Dict[str, Any]:
        choices = list(raw.get("choices") or [])
        if not choices:
            raise RuntimeError("native optimizer response contained no choices")
        message = dict((choices[0] or {}).get("message") or {})
        content = str(message.get("content") or "").strip()
        if not content:
            raise RuntimeError("native optimizer response was empty")
        return {
            "content": content,
            "model": str(raw.get("model") or getattr(raw, "model_id", "hhs-native-language-v1")),
            "usage": dict(raw.get("usage") or {}),
            "finish_reason": (choices[0] or {}).get("finish_reason"),
        }

    async def _process_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        payload = json.loads(str(row["payload_json"]))
        messages = [
            {"role": "system", "content": OPTIMIZER_SYSTEM_INSTRUCTION},
            {
                "role": "user",
                "content": _canonical_json({
                    "observation": payload,
                    "requested_output": {
                        "summary": "string",
                        "reusable_patterns": ["string"],
                        "optimization_proposals": ["string"],
                        "validation_requirements": ["string"],
                        "admission_required": True,
                    },
                }),
            },
        ]
        try:
            raw = await self.transport.chat_completion(
                messages=messages,
                tools=None,
                response_format=None,
            )
            completion = self._extract_completion(raw)
            proposal: Dict[str, Any] = {
                "schema": PROPOSAL_SCHEMA,
                "version": VERSION,
                "observation_root_hash72": str(row["observation_root_hash72"]),
                "provider_id": str(getattr(self.transport, "provider_id", "provider:hhs.local.text")),
                "model_id": str(completion.get("model") or "hhs-native-language-v1"),
                "proposal_text": completion["content"],
                "usage": completion["usage"],
                "finish_reason": completion["finish_reason"],
                "user_facing_response": False,
                "canonical_authority": False,
                "runtime_mutation_admitted": False,
                "repository_mutation_admitted": False,
                "separate_admission_required": True,
                "created_at_unix_ms": _now_ms(),
            }
            proposal["proposal_root_hash72"] = hash72(PROPOSAL_SCHEMA, proposal)
            now = _now_ms()
            with self._lock, self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO proposals (
                        proposal_root_hash72,observation_root_hash72,proposal_json,
                        provider_id,model_id,created_at_unix_ms
                    ) VALUES (?,?,?,?,?,?)
                    """,
                    (
                        proposal["proposal_root_hash72"],
                        proposal["observation_root_hash72"],
                        _canonical_json(proposal),
                        proposal["provider_id"],
                        proposal["model_id"],
                        now,
                    ),
                )
                connection.execute(
                    """
                    UPDATE observations
                    SET status='COMPLETE', attempts=attempts+1,
                        last_error=NULL, updated_at_unix_ms=?
                    WHERE observation_root_hash72=?
                    """,
                    (now, proposal["observation_root_hash72"]),
                )
                connection.commit()
            return {
                "ok": True,
                "observation_root_hash72": proposal["observation_root_hash72"],
                "proposal_root_hash72": proposal["proposal_root_hash72"],
            }
        except Exception as exc:
            now = _now_ms()
            error = f"{type(exc).__name__}: {exc}"
            with self._lock, self._connect() as connection:
                connection.execute(
                    """
                    UPDATE observations
                    SET attempts=attempts+1,last_error=?,updated_at_unix_ms=?
                    WHERE observation_root_hash72=?
                    """,
                    (error[:4096], now, str(row["observation_root_hash72"])),
                )
                connection.commit()
            return {
                "ok": False,
                "observation_root_hash72": str(row["observation_root_hash72"]),
                "error": error,
                "retryable": True,
            }

    async def process_pending(self, limit: int = 8) -> Dict[str, Any]:
        rows = self._pending(limit)
        results = []
        for row in rows:
            results.append(await self._process_row(row))
        return {
            "schema": "HHS_PASS_209_NATIVE_AGI_OPTIMIZER_BATCH_V1",
            "version": VERSION,
            "ok": all(item.get("ok") for item in results) if results else True,
            "selected_count": len(rows),
            "completed_count": sum(1 for item in results if item.get("ok")),
            "deferred_count": sum(1 for item in results if not item.get("ok")),
            "results": results,
            "runtime_mutation_admitted": False,
        }

    def observations(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json,status,attempts,last_error,updated_at_unix_ms
                FROM observations
                ORDER BY created_at_unix_ms DESC, observation_root_hash72 DESC
                LIMIT ?
                """,
                (max(1, min(int(limit), 1000)),),
            ).fetchall()
        result = []
        for row in rows:
            payload = json.loads(str(row["payload_json"]))
            payload.update({
                "optimizer_status": str(row["status"]),
                "optimizer_attempts": int(row["attempts"]),
                "optimizer_last_error": row["last_error"],
                "optimizer_updated_at_unix_ms": int(row["updated_at_unix_ms"]),
            })
            result.append(payload)
        return result

    def proposals(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT proposal_json FROM proposals
                ORDER BY created_at_unix_ms DESC, proposal_root_hash72 DESC
                LIMIT ?
                """,
                (max(1, min(int(limit), 1000)),),
            ).fetchall()
        return [json.loads(str(row["proposal_json"])) for row in rows]

    def status(self) -> Dict[str, Any]:
        counts = {"PENDING": 0, "COMPLETE": 0}
        proposal_count = 0
        database_error = None
        try:
            with self._connect() as connection:
                for row in connection.execute(
                    "SELECT status,COUNT(*) AS count FROM observations GROUP BY status"
                ).fetchall():
                    counts[str(row["status"])] = int(row["count"])
                proposal_count = int(
                    connection.execute("SELECT COUNT(*) FROM proposals").fetchone()[0]
                )
        except Exception as exc:
            database_error = f"{type(exc).__name__}: {exc}"
        installation = self.installation_status()
        status: Dict[str, Any] = {
            "schema": STATUS_SCHEMA,
            "version": VERSION,
            "ok": database_error is None,
            "ready": bool(database_error is None and installation.get("ready")),
            "provider_id": str(getattr(self.transport, "provider_id", "provider:hhs.local.text")),
            "model_id": str(getattr(self.transport, "model_id", "hhs-native-language-v1")),
            "role": "BACKEND_LEARNING_AND_OPTIMIZATION_AGENT",
            "native_agi_is_user_facing_provider": False,
            "database": str(self.db_path),
            "database_error": database_error,
            "pending_observations": counts.get("PENDING", 0),
            "completed_observations": counts.get("COMPLETE", 0),
            "proposal_count": proposal_count,
            "installation": installation,
            "runtime_mutation_admitted": False,
            "repository_mutation_admitted": False,
            "separate_admission_required": True,
        }
        status["status_root_hash72"] = hash72(STATUS_SCHEMA, status)
        return status


DEFAULT_PASS209_NATIVE_AGI_OPTIMIZER = NativeAGIOptimizer()
