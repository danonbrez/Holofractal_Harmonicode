#!/usr/bin/env python3
"""Direct command-line acceptance for native HHS general-chat generation.

This intentionally bypasses FastAPI, nginx, Lane 5, and the Runtime OS UI.  A
strict acceptance run passes only when arbitrary ordinary prompts are answered
through the real native serialized causal-generation path.
"""
from __future__ import annotations

import argparse
import asyncio
from hashlib import sha256
import json
import os
import sys
from typing import Any, Mapping, Sequence

ROOT_MODE = "GENERAL_CHAT"
EXPECTED_GENERATION_PATH = "NATIVE_CAUSAL_LM_SERIALIZED_BLOCK_STREAM"
CANNED_GENERAL_CHAT_FALLBACK = (
    "I can continue this as a general natural-language conversation. "
    "Tell me what you want to understand, create, compare, or reason "
    "through, and I’ll respond directly without forcing a developer workflow."
)
EMERGENCY_CONVERSATION_FALLBACK_FRAGMENT = (
    "The native causal generator is temporarily slow"
)
ACCEPTANCE_PROMPTS = (
    "Explain in two concise sentences why ice floats on liquid water.",
    "Compare Baroque counterpoint with modern jazz harmony in a short paragraph.",
    "Write a three-sentence story about a clock that loses track of time.",
    "Explain what causes a lunar eclipse without using mathematical notation.",
)


def _stable_sha256(text: str) -> str:
    return sha256(text.strip().encode("utf-8")).hexdigest()


def _trace_record(prompt: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    choices = list(payload.get("choices") or [])
    message = dict(choices[0].get("message") or {}) if choices else {}
    answer = str(message.get("content") or "").strip()
    trace = dict(payload.get("hhs_native_trace") or {})
    return {
        "schema": "HHS_NATIVE_CHAT_CLI_TURN_V1",
        "prompt": prompt,
        "response": answer,
        "response_sha256": _stable_sha256(answer) if answer else None,
        "generation_path": trace.get("generation_path"),
        "causal_generation_failure": trace.get("causal_generation_failure"),
        "response_block_count": trace.get("response_block_count"),
        "assistant_mode": trace.get("assistant_mode"),
        "runtime_mutation_admitted": trace.get("runtime_mutation_admitted"),
        "trace_root_hash72": trace.get("trace_root_hash72"),
    }


def _strict_failures(record: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    answer = str(record.get("response") or "").strip()
    if not answer:
        failures.append("EMPTY_RESPONSE")
    if record.get("generation_path") != EXPECTED_GENERATION_PATH:
        failures.append(
            "GENERATION_PATH="
            + str(record.get("generation_path") or "MISSING")
        )
    if record.get("causal_generation_failure"):
        failures.append(
            "CAUSAL_GENERATION_FAILURE="
            + str(record.get("causal_generation_failure"))
        )
    if answer == CANNED_GENERAL_CHAT_FALLBACK:
        failures.append("CANNED_GENERAL_CHAT_FALLBACK")
    if EMERGENCY_CONVERSATION_FALLBACK_FRAGMENT in answer:
        failures.append("EMERGENCY_CONVERSATION_FALLBACK")
    blocks = record.get("response_block_count")
    if not isinstance(blocks, int) or blocks < 1:
        failures.append("NO_SERIALIZED_RESPONSE_BLOCKS")
    if record.get("runtime_mutation_admitted") is not False:
        failures.append("RUNTIME_MUTATION_AUTHORITY_CHANGED")
    return failures


async def _direct_turn(
    provider: Any,
    prompt: str,
    *,
    mode: str,
    history: Sequence[Mapping[str, str]] = (),
) -> dict[str, Any]:
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are the native HHS natural-language assistant. "
                f"HHS_ASSISTANT_MODE={mode}. "
                "Answer the user's ordinary natural-language request directly."
            ),
        },
        *[dict(item) for item in history],
        {"role": "user", "content": prompt},
    ]
    payload = await provider.chat_completion(messages=messages, tools=[])
    return _trace_record(prompt, payload)


def _print_record(record: Mapping[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(dict(record), sort_keys=True, ensure_ascii=False))
        return
    print(f"prompt: {record.get('prompt')}")
    print(f"generation_path: {record.get('generation_path')}")
    print(f"causal_generation_failure: {record.get('causal_generation_failure')}")
    print(f"response_block_count: {record.get('response_block_count')}")
    print(f"response: {record.get('response')}")
    print()


async def run_acceptance(
    provider: Any,
    *,
    prompts: Sequence[str] = ACCEPTANCE_PROMPTS,
    mode: str = ROOT_MODE,
    as_json: bool = False,
) -> tuple[int, dict[str, Any]]:
    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for prompt in prompts:
        record = await _direct_turn(provider, prompt, mode=mode)
        record["strict_failures"] = _strict_failures(record)
        records.append(record)
        _print_record(record, as_json=as_json)
        if record["strict_failures"]:
            failures.append({
                "prompt": prompt,
                "failures": list(record["strict_failures"]),
            })

    hashes = [str(item.get("response_sha256") or "") for item in records]
    if len(set(hashes)) != len(hashes):
        failures.append({
            "prompt": "<cross-prompt>",
            "failures": ["NON_DISTINCT_PROMPT_RESPONSES"],
        })

    report = {
        "schema": "HHS_NATIVE_CHAT_CLI_ACCEPTANCE_V1",
        "ok": not failures,
        "expected_generation_path": EXPECTED_GENERATION_PATH,
        "prompt_count": len(records),
        "distinct_response_count": len(set(hashes)),
        "failures": failures,
        "turns": records,
    }
    print(json.dumps(report, sort_keys=True, ensure_ascii=False))
    return (0 if report["ok"] else 2), report


async def run_prompts(
    provider: Any,
    prompts: Sequence[str],
    *,
    mode: str,
    strict_generation: bool,
    as_json: bool,
) -> int:
    exit_code = 0
    for prompt in prompts:
        record = await _direct_turn(provider, prompt, mode=mode)
        record["strict_failures"] = (
            _strict_failures(record) if strict_generation else []
        )
        _print_record(record, as_json=as_json)
        if record["strict_failures"]:
            exit_code = 2
    return exit_code


async def run_interactive(
    provider: Any,
    *,
    mode: str,
    strict_generation: bool,
    as_json: bool,
) -> int:
    history: list[dict[str, str]] = []
    print(
        "HHS native chat CLI. Type /quit to exit. "
        f"mode={mode} strict_generation={strict_generation}"
    )
    while True:
        try:
            prompt = input("you> ").strip()
        except EOFError:
            print()
            return 0
        if prompt in {"/quit", "/exit"}:
            return 0
        if not prompt:
            continue
        record = await _direct_turn(
            provider,
            prompt,
            mode=mode,
            history=history,
        )
        record["strict_failures"] = (
            _strict_failures(record) if strict_generation else []
        )
        _print_record(record, as_json=as_json)
        answer = str(record.get("response") or "")
        history.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": answer},
        ])
        if record["strict_failures"]:
            print(
                "strict generation failure: "
                + ", ".join(record["strict_failures"]),
                file=sys.stderr,
            )
            return 2


def _provider() -> Any:
    os.environ.setdefault("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC", "0")
    from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
        HHSNativeLiteRTLMTransport,
    )

    return HHSNativeLiteRTLMTransport(require_word2vec=False)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Direct native HHS command-line chat and generative acceptance"
    )
    parser.add_argument("--prompt", action="append", default=[])
    parser.add_argument("--mode", default=ROOT_MODE)
    parser.add_argument("--strict-generation", action="store_true")
    parser.add_argument("--acceptance", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--show-status", action="store_true")
    args = parser.parse_args(argv)

    provider = _provider()
    if args.show_status:
        print(
            json.dumps(
                provider.installation_status(),
                indent=2,
                sort_keys=True,
                default=str,
            )
        )

    if args.acceptance:
        if args.prompt:
            parser.error("--acceptance cannot be combined with --prompt")
        code, _ = asyncio.run(
            run_acceptance(provider, mode=args.mode, as_json=args.json)
        )
        return code

    if args.prompt:
        return asyncio.run(
            run_prompts(
                provider,
                args.prompt,
                mode=args.mode,
                strict_generation=args.strict_generation,
                as_json=args.json,
            )
        )

    return asyncio.run(
        run_interactive(
            provider,
            mode=args.mode,
            strict_generation=args.strict_generation,
            as_json=args.json,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
