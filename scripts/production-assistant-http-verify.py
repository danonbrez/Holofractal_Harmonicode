#!/usr/bin/env python3
"""Verify a deployed HHS assistant HTTP path with bounded two-turn recall."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any


DEFAULT_TOKEN = "HHS-PRODUCTION-CHATBOT-E2E-7249"


def _post(base_url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/api/assistant/chat",
        data=body,
        headers={"content-type": "application/json", "accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        raise RuntimeError(
            f"assistant HTTP {exc.code}: {raw.decode('utf-8', 'replace')[:4000]}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"assistant request failed: {type(exc).__name__}: {exc}") from exc
    if status != 200:
        raise RuntimeError(f"assistant HTTP {status}: {raw[:4000]!r}")
    try:
        payload_out = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"assistant returned non-JSON body: {raw[:4000]!r}") from exc
    if payload_out.get("ok") is not True:
        raise RuntimeError(f"assistant returned non-ok payload: {payload_out}")
    return payload_out


def verify(base_url: str, timeout: float, token: str, label: str) -> dict[str, Any]:
    first = _post(
        base_url,
        {
            "project_id": f"project:production-http-{label}",
            "title": f"Production HTTP {label}",
            "content": f"Remember this exact token for my next message: {token}. Reply briefly.",
            "assistant_mode": "BOTH",
        },
        timeout,
    )
    thread_id = str(first.get("thread_id") or "")
    if not thread_id:
        raise RuntimeError(f"first assistant response omitted thread_id: {first}")

    second = _post(
        base_url,
        {
            "thread_id": thread_id,
            "project_id": f"project:production-http-{label}",
            "title": f"Production HTTP {label}",
            "content": (
                "What exact token did I ask you to remember in my previous message? "
                "Reply with only the token."
            ),
            "assistant_mode": "BOTH",
        },
        timeout,
    )
    recalled = str((second.get("assistant_message") or {}).get("content") or "").strip()
    if recalled != token:
        raise RuntimeError(
            f"assistant recall mismatch for {label}: expected={token!r} actual={recalled!r}"
        )
    if str(second.get("thread_id") or "") != thread_id:
        raise RuntimeError(f"assistant thread changed between turns for {label}")

    return {
        "schema": "HHS_PRODUCTION_ASSISTANT_HTTP_VERIFICATION_V1",
        "ok": True,
        "label": label,
        "base_url": base_url,
        "thread_id": thread_id,
        "token": token,
        "two_turn_exact_memory_verified": True,
        "thread_continuity_verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--token", default=DEFAULT_TOKEN)
    parser.add_argument("--label", default="backend")
    args = parser.parse_args()
    receipt = verify(
        args.base_url,
        max(1.0, args.timeout_seconds),
        str(args.token),
        str(args.label),
    )
    print(json.dumps(receipt, sort_keys=True))
    marker = "".join(
        ch if ch.isalnum() else "_" for ch in str(args.label).upper()
    ).strip("_")
    print(f"HHS_PRODUCTION_ASSISTANT_{marker}_HTTP_VERIFIED=1")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema": "HHS_PRODUCTION_ASSISTANT_HTTP_VERIFICATION_FAILURE_V1",
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise
