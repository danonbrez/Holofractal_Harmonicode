#!/usr/bin/env python3
"""Durable single-host Pass 190 Iteration 7 worker process."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from hhs_pass190 import ArgumentValidationError
from hhs_pass190_iteration3_hardening import DEFAULT_DATABASE
from hhs_pass190_iteration7 import DurableExecutionContext

CONTROL_CAPABILITIES = frozenset({"worker:admin", "worker:read", "worker:execute", "scheduler:write"})


class DurableWorker:
    def __init__(
        self,
        context: DurableExecutionContext,
        worker_id: str,
        *,
        capabilities: Iterable[str] = (),
        labels: Iterable[str] = (),
        lease_timeout_ns: int = 30_000_000_000,
        clock_ns: Callable[[], int] = time.time_ns,
    ):
        self.context = context
        self.worker_id = worker_id
        self.capabilities = tuple(sorted(set(capabilities)))
        self.labels = tuple(sorted(set(labels)))
        self.lease_timeout_ns = lease_timeout_ns
        self.clock_ns = clock_ns

    def ensure_registered(self, now_ns: int | None = None) -> dict[str, Any]:
        observed = self.clock_ns() if now_ns is None else now_ns
        try:
            return self.context.invoke(
                "worker.get", {"worker_id": self.worker_id},
                surface="worker-process", capabilities=CONTROL_CAPABILITIES,
            ).result
        except ArgumentValidationError:
            return self.context.invoke(
                "worker.register",
                {
                    "worker_id": self.worker_id,
                    "capabilities": list(self.capabilities),
                    "labels": list(self.labels),
                    "lease_timeout_ns": self.lease_timeout_ns,
                    "now_ns": observed,
                },
                surface="worker-process",
                capabilities=CONTROL_CAPABILITIES,
                idempotency_key=f"worker-register:{self.worker_id}",
            ).result

    def run_once(self, now_ns: int | None = None) -> dict[str, Any]:
        observed = self.clock_ns() if now_ns is None else now_ns
        self.ensure_registered(observed)
        heartbeat = self.context.invoke(
            "worker.heartbeat", {"worker_id": self.worker_id, "now_ns": observed},
            surface="worker-process", capabilities=CONTROL_CAPABILITIES,
        ).result
        scheduler = self.context.invoke(
            "scheduler.tick", {"now_ns": observed, "limit": 1000},
            surface="worker-process", capabilities=CONTROL_CAPABILITIES,
        ).result
        claim = self.context.invoke(
            "job.claim_next", {"worker_id": self.worker_id, "now_ns": observed},
            surface="worker-process", capabilities=CONTROL_CAPABILITIES,
        ).result
        execution = None
        if claim["claimed"]:
            execution = self.context.invoke(
                "job.execute_claimed",
                {
                    "job_id": claim["job"]["job_id"],
                    "worker_id": self.worker_id,
                    "claim_token_hash72": claim["claim_token_hash72"],
                    "now_ns": observed,
                },
                surface="worker-process",
                capabilities=CONTROL_CAPABILITIES,
            ).result
        return {
            "worker": heartbeat,
            "scheduler": scheduler,
            "claim": claim,
            "execution": execution,
            "state_root": self.context.state_root,
        }


def _csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default=str(DEFAULT_DATABASE))
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--capabilities", default="")
    parser.add_argument("--labels", default="local,digitalocean")
    parser.add_argument("--lease-timeout-ns", type=int, default=30_000_000_000)
    parser.add_argument("--poll-ms", type=int, default=250)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if args.poll_ms < 10 or args.poll_ms > 60_000:
        parser.error("--poll-ms must be between 10 and 60000")
    context = DurableExecutionContext(Path(args.database))
    worker = DurableWorker(
        context,
        args.worker_id,
        capabilities=_csv(args.capabilities),
        labels=_csv(args.labels),
        lease_timeout_ns=args.lease_timeout_ns,
    )
    try:
        while True:
            result = worker.run_once()
            if args.as_json:
                print(json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)
            if args.once:
                return 0
            time.sleep(args.poll_ms / 1000)
    except KeyboardInterrupt:
        return 0
    finally:
        context.close()


if __name__ == "__main__":
    raise SystemExit(main())
