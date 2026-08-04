#!/usr/bin/env python3
"""Process the Pass 209 native-AGI optimization observation queue."""
from __future__ import annotations

import argparse
import asyncio
import json
import signal
import time
from typing import Any

from hhs_backend.runtime.hhs_pass209_native_agi_optimizer_v1 import (
    DEFAULT_PASS209_NATIVE_AGI_OPTIMIZER,
)

_STOP = False


def _stop(*_: Any) -> None:
    global _STOP
    _STOP = True


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--limit", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    interval = max(1.0, float(args.interval))
    limit = max(1, int(args.limit))

    while not _STOP:
        result = asyncio.run(
            DEFAULT_PASS209_NATIVE_AGI_OPTIMIZER.process_pending(limit=limit)
        )
        print(json.dumps(result, sort_keys=True, default=str), flush=True)
        if args.once:
            return 0 if result.get("ok") else 1
        time.sleep(interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
