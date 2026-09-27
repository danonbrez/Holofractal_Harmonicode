from __future__ import annotations

import asyncio
import json

from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
    DEFAULT_HHS_ASSISTANT_TOOLS,
)
from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
    HHSNativeLiteRTLMTransport,
)
from hhs_backend.runtime.hhs_native_response_block_stream_v1 import (
    NativeResponseBlockStream,
    RECORD_SEPARATOR,
    UNIT_SEPARATOR,
    verify_stream,
)


class ScriptedGenerationService:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []
        self.index = 0
        self.max_new_tokens = 256

    def status(self):
        return {
            "configured": True,
            "loaded": True,
            "ready": True,
            "model_id": "scripted-native",
            "max_new_tokens": self.max_new_tokens,
        }

    def generate(self, messages, *, retrieval_context=None, max_new_tokens=None):
        self.calls.append({
            "messages": [dict(item) for item in messages],
            "retrieval_context": retrieval_context,
            "max_new_tokens": max_new_tokens,
        })
        if self.index >= len(self.outputs):
            response, token_count = self.outputs[-1]
        else:
            response, token_count = self.outputs[self.index]
        self.index += 1
        return {
            "response": response,
            "receipt": {
                "generated_token_count": token_count,
                "response_sha256": "witnessed-by-stream",
                "receipt_root_hash72": "r" * 72,
                "canonical_vm81_mutation_authority": False,
            },
            "status": self.status(),
        }


class FakeWord2Vec:
    def status(self):
        return {
            "offline_ready": True,
            "active_model_id": "fake-word2vec",
            "installed_models": 1,
        }

    def nearest(self, token, top_k=4):
        return {
            "model_id": "fake-word2vec",
            "approximate": False,
            "results": [],
        }


def test_short_semantic_answer_is_extended_by_native_generation_until_ratio_closes():
    short = "Short answer. "
    extension = (
        "The continuation expands the same answer with useful explanatory detail, "
        "downstream consequences, examples, and ethical-invariant context. "
    ) * 30
    generator = ScriptedGenerationService([
        (short, 40),
        (extension, 120),
    ])
    stream = NativeResponseBlockStream(
        generator,
        buffer_max_new_tokens=256,
        max_blocks=4,
        max_fill_attempts=4,
    )

    result = stream.generate([{"role": "user", "content": "Explain the system."}])

    assert result["response"] == short + extension
    assert result["finish_reason"] == "stop"
    assert len(result["blocks"]) == 1
    block = result["blocks"][0]
    assert block["generation_calls"] == 2
    assert block["ratio_satisfied"] is True
    assert block["payload_bytes"] >= 8 * block["delimiter_bytes"]
    assert result["manifest"]["generated_payload_rewritten"] is False
    assert verify_stream(result) is True

    continuation_messages = generator.calls[1]["messages"]
    assert continuation_messages[-2]["role"] == "assistant"
    assert continuation_messages[-2]["content"] == short
    assert "HHS_INTERNAL_SOPHEON_SIMSANE_CONTINUATION" in continuation_messages[-1]["content"]


def test_generation_buffer_boundary_creates_chained_blocks_without_ending_answer():
    first = "A" * 3200
    second = "B" * 3200
    generator = ScriptedGenerationService([
        (first, 256),
        (second, 80),
    ])
    stream = NativeResponseBlockStream(
        generator,
        buffer_max_new_tokens=256,
        max_blocks=4,
    )

    result = stream.generate([{"role": "user", "content": "Produce a long response."}])

    assert result["response"] == first + second
    assert result["finish_reason"] == "stop"
    assert len(result["blocks"]) == 2
    assert result["blocks"][0]["terminal"] is False
    assert result["blocks"][1]["terminal"] is True
    assert result["blocks"][1]["prior_hash72"] == result["blocks"][0]["block_hash72"]
    assert result["manifest"]["terminal_block_hash72"] == result["blocks"][1]["block_hash72"]
    assert RECORD_SEPARATOR in result["serialized_response"]
    assert UNIT_SEPARATOR in result["serialized_response"]
    assert verify_stream(result) is True


def test_stream_verification_rejects_payload_or_order_tamper():
    generator = ScriptedGenerationService([("C" * 3200, 40)])
    stream = NativeResponseBlockStream(generator, buffer_max_new_tokens=256)
    result = stream.generate([{"role": "user", "content": "answer"}])
    assert verify_stream(result) is True

    tampered = dict(result)
    tampered["blocks"] = [dict(item) for item in result["blocks"]]
    tampered["blocks"][0]["payload"] = "X" + tampered["blocks"][0]["payload"][1:]
    assert verify_stream(tampered) is False


def test_tool_receipt_is_synthesized_into_plain_english_generation_context():
    answer = (
        "The repository evidence shows that the generated text is available and should "
        "be returned to the user as the conversational answer rather than replaced by "
        "receipt metadata. "
    ) * 24
    generator = ScriptedGenerationService([(answer, 200)])
    provider = HHSNativeLiteRTLMTransport(
        word2vec_service=FakeWord2Vec(),
        require_word2vec=False,
        generation_service=generator,
    )

    tool_receipt = {
        "ok": True,
        "tool_name": "hhs_repository_search",
        "response": {
            "result": {
                "content": "ACTUAL_NESTED_GENERATED_TEXT",
                "receipt": {"hash72": "r" * 72},
            }
        },
    }
    response = asyncio.run(
        provider.chat_completion(
            messages=[
                {"role": "system", "content": "HHS_ASSISTANT_MODE=BOTH."},
                {"role": "user", "content": "Inspect the repository and explain the result."},
                {"role": "tool", "content": json.dumps(tool_receipt)},
            ],
            tools=DEFAULT_HHS_ASSISTANT_TOOLS,
        )
    )

    assert response["choices"][0]["message"]["content"] == answer
    assert "ACTUAL_NESTED_GENERATED_TEXT" in generator.calls[0]["retrieval_context"]
    trace = response["hhs_native_trace"]
    assert trace["tool_evidence_synthesized_into_plain_english"] is True
    assert trace["generation_path"] == "NATIVE_CAUSAL_LM_SERIALIZED_BLOCK_STREAM"
    assert trace["serialized_response"] != answer
    assert trace["response_stream_manifest"]["response_sha256"]
    assert trace["response_stream_manifest"]["serialized_response_sha256"]


def test_exact_fallback_extracts_nested_text_instead_of_field_count_only():
    provider = HHSNativeLiteRTLMTransport(
        word2vec_service=FakeWord2Vec(),
        require_word2vec=False,
        generation_service=ScriptedGenerationService([("D" * 3200, 20)]),
    )
    sections = provider._tool_evidence_lines([
        {
            "ok": True,
            "tool_name": "test_tool",
            "response": {
                "outer": {
                    "response": "This is the actual nested response text."
                }
            },
        }
    ])

    assert sections == [
        "test_tool:\nThis is the actual nested response text."
    ]
