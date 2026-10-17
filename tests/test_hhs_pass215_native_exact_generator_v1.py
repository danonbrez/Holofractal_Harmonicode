"""Native Pass 215 exact executor service/ABI integration regressions.

Pure routing controls do not replace the real pinned-model replay.
The live GGUF check remains a separately required admission gate.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_pass215_native_exact_generator_v1 import (
    NativePass215CertifiedGenerator,
    NativePass215ProfileError,
    CONTRACTED_PROMPT,
    MODEL_SHA256,
    EXPECTED_TOKEN_IDS,
    EXPECTED_TOKENS,
)
from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
    HHSNativeLiteRTLMTransport,
)


def _messages(prompt=CONTRACTED_PROMPT):
    return [
        {"role": "system", "content": "HHS_ASSISTANT_MODE=GENERAL_CHAT."},
        {"role": "user", "content": prompt},
    ]


def test_exact_engine_denies_other_prompts_without_loading_model(monkeypatch):
    model = NativePass215CertifiedGenerator("/missing/certified.gguf")
    with pytest.raises(NativePass215ProfileError, match="OUTSIDE_CERTIFIED_PROFILE"):
        model.generate(_messages("Generate an arbitrary poem."))
    with pytest.raises(NativePass215ProfileError, match="OUTSIDE_CERTIFIED_PROFILE"):
        model.generate(_messages() + [{"role": "assistant", "content": "prior"}])
    with pytest.raises(NativePass215ProfileError, match="OUTSIDE_CERTIFIED_PROFILE"):
        model.generate(_messages(), retrieval_context="unlicensed context")
    with pytest.raises(NativePass215ProfileError, match="BOUND_OUTSIDE"):
        model.generate(_messages(), max_new_tokens=8)


def test_exact_engine_requires_existing_model_file():
    model = NativePass215CertifiedGenerator("/missing/certified.gguf")
    status = model.status()
    assert status["configured"] is True
    assert status["ready"] is False
    assert status["arbitrary_prompt_generation_supported"] is False
    assert status["pass213_rom_compilation_claimed"] is False
    with pytest.raises(NativePass215ProfileError, match="MODEL_FILE_NOT_FOUND"):
        model.generate(_messages())


def _evidence():
    # A purpose-built interface fixture. Real exactness is proved only by the
    # inherited validator over a source-model execution, not this fixture.
    return {
        "bounded_generation_control": {
            "selected_token_ids": list(EXPECTED_TOKEN_IDS),
            "selected_tokens": list(EXPECTED_TOKENS),
            "termination_reason": "MAX_NEW_TOKENS",
            "generation_control_root_hash216": "d" * 64,
            "per_token_proof_receipt_chain_terminal_hash72": "e" * 72,
        },
        "claims": {
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
        },
        "evidence_root_hash216": "f" * 64,
        "bounded_generation_control_suite_root_hash216": "a" * 64,
        "receipt_hash72": "b" * 72,
        "resume_checkpoint": {"checkpoint_root_hash216": "c" * 64},
    }


class FakeExactExecutor:
    def __init__(self, evidence):
        self.calls = []
        self.evidence = evidence
        self.validations = 0

    def execute_bounded_generation_with_resume_from_path(self, path, **kwargs):
        self.calls.append((path, kwargs))
        return self.evidence, {"checkpoint": "interface fixture"}

    def validate_bounded_generation_control_evidence(self, evidence):
        assert evidence is self.evidence
        self.validations += 1


def test_exact_generator_calls_real_entrypoint_and_validator_boundary(
    monkeypatch, tmp_path
):
    from hhs_backend.runtime import hhs_pass215_native_exact_generator_v1 as adapter

    container = tmp_path / "stories15M-q4_0.gguf"
    container.write_bytes(b"test-only-non-model")
    executor = FakeExactExecutor(_evidence())
    monkeypatch.setattr(adapter, "_exact_engine", lambda: executor)
    result = NativePass215CertifiedGenerator(container).generate(_messages())
    assert executor.validations == 1
    assert len(executor.calls) == 1
    source_path, args = executor.calls[0]
    assert source_path == str(container)
    assert args["expected_sha256"] == MODEL_SHA256
    assert args["prompt"] == CONTRACTED_PROMPT
    assert args["source"]["kind"] == "public_open_transformer"
    assert args["certification_bits"] == 256
    assert args["resume_after_steps"] == 4
    assert result["receipt"]["selected_token_ids"] == list(EXPECTED_TOKEN_IDS)
    assert result["receipt"]["generated_token_count"] == 7
    assert result["receipt"]["canonical_vm81_mutation_authority"] is False
    assert result["response"] == " The sun was shining and the"


def test_exact_generator_rejects_wrong_certified_output(monkeypatch, tmp_path):
    from hhs_backend.runtime import hhs_pass215_native_exact_generator_v1 as adapter

    container = tmp_path / "stories15M-q4_0.gguf"
    container.write_bytes(b"test-only-non-model")
    evidence = _evidence()
    evidence["bounded_generation_control"]["selected_token_ids"][0] = 1234
    executor = FakeExactExecutor(evidence)
    monkeypatch.setattr(adapter, "_exact_engine", lambda: executor)
    with pytest.raises(NativePass215ProfileError, match="CERTIFIED_CHAIN_MISMATCH"):
        NativePass215CertifiedGenerator(container).generate(_messages())


def test_explicit_native_service_routes_to_certified_executor(monkeypatch):
    monkeypatch.setenv("HHS_NATIVE_GENERATION_ENGINE", "PASS215_EXACT_CERTIFIED")
    monkeypatch.setenv("HHS_PASS215_EXACT_MODEL_PATH", "/pinned/native.gguf")
    monkeypatch.delenv("HHS_NATIVE_CAUSAL_LM_REQUIRED", raising=False)

    provider = HHSNativeLiteRTLMTransport(require_word2vec=False)
    # Scoped interface test: production readiness is not disabled. The live
    # test must execute the full semantic membrane and actual GGUF kernel.
    monkeypatch.setattr(provider, "_require_ready", lambda: {"ready": True})
    calls = []

    def witnessed_generate(messages, *, retrieval_context=None, max_new_tokens=None):
        calls.append(messages)
        return {
            "response": " The sun was shining and the",
            "receipt": {
                "generated_token_count": 7,
                "model_sha256": MODEL_SHA256,
                "receipt_hash72": "r" * 72,
                "selected_token_ids": list(EXPECTED_TOKEN_IDS),
            },
            "finish_reason": "length",
        }

    exact = provider._causal_generation()
    assert isinstance(exact, NativePass215CertifiedGenerator)
    assert provider.installation_status()["pass215_exact_bounded_profile_only"] is True
    monkeypatch.setattr(exact, "generate", witnessed_generate)
    result = asyncio.run(provider.chat_completion(messages=_messages(), tools=[]))
    trace = result["hhs_native_trace"]
    assert len(calls) == 1
    assert trace["generation_path"] == "PASS215_EXACT_CERTIFIED_BOUNDED_GENERATION"
    assert trace["pass215_certified_egress"]["receipt_hash72"] == "r" * 72
    assert trace["arbitrary_prompt_generation_claimed"] is False
    assert trace["pass213_rom_compilation_claimed"] is False
    assert trace["runtime_mutation_admitted"] is False
    assert result["usage"]["completion_tokens"] == 7
    assert result["choices"][0]["message"]["content"].startswith(" The sun")


def test_explicit_native_engine_does_not_silently_fallback(monkeypatch):
    monkeypatch.setenv("HHS_NATIVE_GENERATION_ENGINE", "PASS215_EXACT_CERTIFIED")
    provider = HHSNativeLiteRTLMTransport(require_word2vec=False)
    monkeypatch.setattr(provider, "_require_ready", lambda: {"ready": True})
    with pytest.raises(NativePass215ProfileError, match="OUTSIDE_CERTIFIED_PROFILE"):
        asyncio.run(provider.chat_completion(
            messages=_messages("This prompt is not certified"), tools=[]
        ))


def test_unified_fabric_declares_pass215_bounded_capability_not_general_generation():
    from hhs_backend.runtime.hhs_unified_language_model_fabric_v1 import (
        build_unified_language_model_fabric,
    )

    causal_status = NativePass215CertifiedGenerator("/missing/certified.gguf").status()
    fabric = build_unified_language_model_fabric(
        configured_model_id="",
        registered_model_ids=[],
        native_installation={"causal_lm": causal_status},
        native_health={"ok": True, "online": True},
    )
    members = [
        m for m in fabric["members"]
        if m.get("role") == "PASS215_EXACT_CERTIFIED_BOUNDED_GENERATOR"
    ]
    assert len(members) == 1
    assert members[0]["frozen_exact_profile_only"] is True
    assert members[0]["arbitrary_prompt_generation_supported"] is False
    assert members[0]["capabilities"] == ["CERTIFIED_BOUNDED_TEXT_GENERATION"]
