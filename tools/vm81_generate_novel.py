#!/usr/bin/env python3
"""Generate a novel through the VM81 runtime API, never a direct model endpoint."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict


def _post_json(url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"VM81 runtime API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"VM81 runtime API unavailable: {exc.reason}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runtime-url",
        default=os.getenv("HHS_RUNTIME_URL", "http://127.0.0.1:8000"),
    )
    parser.add_argument("--title", default="The Ninth Archive")
    parser.add_argument(
        "--premise",
        default=(
            "In a city where every public action must be sealed into an immutable "
            "receipt, a maintenance archivist discovers a ninth archive containing "
            "events that have not happened yet."
        ),
    )
    parser.add_argument("--chapters", type=int, default=9)
    parser.add_argument("--target-words", type=int, default=9000)
    parser.add_argument("--filename", default="THE_NINTH_ARCHIVE.md")
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=1800.0)
    parser.add_argument("--no-persist", action="store_true")
    args = parser.parse_args()

    endpoint = args.runtime_url.rstrip("/") + "/api/runtime/creative/novel"
    payload = {
        "title": args.title,
        "premise": args.premise,
        "chapter_count": args.chapters,
        "target_words": args.target_words,
        "filename": args.filename,
        "max_concurrency": args.max_concurrency,
        "persist": not args.no_persist,
        "request_class": "canonical_full_witness_chain",
    }
    result = _post_json(endpoint, payload, args.timeout)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    response = result.get("payload", result)
    return 0 if response.get("ok") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
