from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "tools" / "hhs_native_chat_cli.py"

spec = importlib.util.spec_from_file_location("hhs_native_chat_cli_test_module", CLI_PATH)
assert spec is not None and spec.loader is not None
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


class FakeProvider:
    def __init__(self, *, fallback: bool = False, duplicate: bool = False) -> None:
        self.fallback = fallback
        self.duplicate = duplicate
        self.prompts: list[str] = []

    async def chat_completion(self, *, messages, tools):
        assert tools == []
        prompt = str(messages[-1]["content"])
        self.prompts.append(prompt)

        if self.fallback:
            answer = cli.CANNED_GENERAL_CHAT_FALLBACK
            trace = {
                "generation_path": "EXACT_SEMANTIC_FALLBACK",
                "causal_generation_failure": (
                    "NativeCausalLMNotReady: HHS_NATIVE_CAUSAL_LM_MODEL is not configured"
                ),
                "response_block_count": None,
                "assistant_mode": "GENERAL_CHAT",
                "runtime_mutation_admitted": False,
                "trace_root_hash72": "f" * 72,
            }
        else:
            answer = (
                "Generated answer."
                if self.duplicate
                else f"Generated answer for: {prompt}"
            )
            trace = {
                "generation_path": cli.EXPECTED_GENERATION_PATH,
                "causal_generation_failure": None,
                "response_block_count": 1,
                "assistant_mode": "GENERAL_CHAT",
                "runtime_mutation_admitted": False,
                "trace_root_hash72": "g" * 72,
            }

        return {
            "choices": [{
                "message": {"role": "assistant", "content": answer},
                "finish_reason": "stop",
            }],
            "hhs_native_trace": trace,
        }


def test_strict_acceptance_passes_only_real_distinct_serialized_generation():
    provider = FakeProvider()
    code, report = __import__("asyncio").run(
        cli.run_acceptance(
            provider,
            prompts=("Explain ice.", "Compare harmony."),
            as_json=True,
        )
    )

    assert code == 0
    assert report["ok"] is True
    assert report["distinct_response_count"] == 2
    assert provider.prompts == ["Explain ice.", "Compare harmony."]
    assert all(
        turn["generation_path"] == cli.EXPECTED_GENERATION_PATH
        for turn in report["turns"]
    )
    assert all(turn["strict_failures"] == [] for turn in report["turns"])


def test_strict_acceptance_rejects_canned_semantic_fallback():
    provider = FakeProvider(fallback=True)
    code, report = __import__("asyncio").run(
        cli.run_acceptance(
            provider,
            prompts=("Explain ice.",),
            as_json=True,
        )
    )

    assert code == 2
    assert report["ok"] is False
    failures = report["turns"][0]["strict_failures"]
    assert "CANNED_GENERAL_CHAT_FALLBACK" in failures
    assert "NO_SERIALIZED_RESPONSE_BLOCKS" in failures
    assert any(
        item.startswith("GENERATION_PATH=EXACT_SEMANTIC_FALLBACK")
        for item in failures
    )
    assert any(
        item.startswith("CAUSAL_GENERATION_FAILURE=")
        for item in failures
    )


def test_strict_acceptance_rejects_same_answer_for_unrelated_prompts():
    provider = FakeProvider(duplicate=True)
    code, report = __import__("asyncio").run(
        cli.run_acceptance(
            provider,
            prompts=("Explain ice.", "Write a story."),
            as_json=True,
        )
    )

    assert code == 2
    assert report["ok"] is False
    assert report["distinct_response_count"] == 1
    assert {
        failure
        for item in report["failures"]
        for failure in item["failures"]
    } >= {"NON_DISTINCT_PROMPT_RESPONSES"}


def test_default_acceptance_prompts_are_open_ended_and_not_memory_shortcuts():
    assert len(cli.ACCEPTANCE_PROMPTS) >= 4
    lowered = [prompt.casefold() for prompt in cli.ACCEPTANCE_PROMPTS]
    assert all("remember" not in prompt for prompt in lowered)
    assert all("previous message" not in prompt for prompt in lowered)
    assert all(prompt.strip() not in {"hello", "hi", "hey"} for prompt in lowered)
    assert len(set(cli.ACCEPTANCE_PROMPTS)) == len(cli.ACCEPTANCE_PROMPTS)
