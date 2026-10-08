"""Production assistant stage timing and synchronous-stall watchdogs."""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import traceback
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

TIMING_SCHEMA = "HHS_PRODUCTION_ASSISTANT_STAGE_TIMING_V1"
WATCHDOG_SCHEMA = "HHS_PRODUCTION_ASSISTANT_STAGE_WATCHDOG_V1"

_TRACE_ID: ContextVar[str] = ContextVar("hhs_production_assistant_trace_id", default="")


def current_trace_id() -> str:
    return _TRACE_ID.get() or "unscoped"


@contextmanager
def assistant_trace(trace_id: str | None = None) -> Iterator[str]:
    resolved = str(trace_id or f"assistant-{uuid.uuid4().hex[:16]}")
    token = _TRACE_ID.set(resolved)
    try:
        yield resolved
    finally:
        _TRACE_ID.reset(token)


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str), flush=True)


def _watchdog_seconds() -> float:
    return max(
        1.0,
        float(os.getenv("HHS_ASSISTANT_STAGE_WATCHDOG_SECONDS", "10")),
    )


def _dump_stacks(stage: str, trace_id: str, started: float) -> None:
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    frames = sys._current_frames()
    threads = {thread.ident: thread for thread in threading.enumerate()}
    snapshots: list[dict[str, Any]] = []
    for ident, frame in frames.items():
        thread = threads.get(ident)
        stack = "".join(traceback.format_stack(frame, limit=40))
        snapshots.append(
            {
                "thread_id": ident,
                "thread_name": getattr(thread, "name", None),
                "daemon": getattr(thread, "daemon", None),
                "stack": stack,
            }
        )
    _emit(
        {
            "schema": WATCHDOG_SCHEMA,
            "trace_id": trace_id,
            "stage": stage,
            "elapsed_ms": elapsed_ms,
            "thread_count": len(snapshots),
            "threads": snapshots,
        }
    )


@contextmanager
def timed_stage(stage: str, **metadata: Any) -> Iterator[None]:
    started = time.perf_counter()
    trace_id = current_trace_id()
    timer = threading.Timer(
        _watchdog_seconds(),
        _dump_stacks,
        args=(stage, trace_id, started),
    )
    timer.daemon = True
    timer.start()
    error: BaseException | None = None
    try:
        yield
    except BaseException as exc:
        error = exc
        raise
    finally:
        timer.cancel()
        _emit(
            {
                "schema": TIMING_SCHEMA,
                "trace_id": trace_id,
                "stage": stage,
                "elapsed_ms": int((time.perf_counter() - started) * 1000),
                "ok": error is None,
                "error_type": type(error).__name__ if error is not None else None,
                **metadata,
            }
        )


__all__ = [
    "TIMING_SCHEMA",
    "WATCHDOG_SCHEMA",
    "assistant_trace",
    "current_trace_id",
    "timed_stage",
]
