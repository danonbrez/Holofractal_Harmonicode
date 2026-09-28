from __future__ import annotations

import asyncio
import json

import pytest

from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    HHSAssistantService,
    LiteRTLMConfig,
)
from hhs_runtime.hhs_pass220_i049_prompt_response_tensor_v1 import (
    LEXICAL_GEOMETRY,
    PromptResponseTensorAdmissionError,
    admit_prompt_response_tensor,
    require_prompt_response_tensor,
    self_test,
)
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry


def _relation_db():
    return {
        "rapid": WordRelationEntry(word="rapid", synonyms=["fast"]),
        "hot": WordRelationEntry(word="hot", antonyms=["cold"]),
        "animal": WordRelationEntry(word="animal", hyponyms=["dog"]),
        "dog": WordRelationEntry(word="dog", hypernyms=["animal"]),
    }


def test_single_ordered_tensor_admits_with_exact_lineage():
    result = admit_prompt_response_tensor(
        "A rapid hot animal.",
        "A fast cold dog.",
        relation_db=_relation_db(),
        explicit_relations=[
            {
                "relation": "holonym",
                "prompt_token": "car",
                "response_token": "wheel",
                "geometry": LEXICAL_GEOMETRY["holonym"],
            },
            {
                "relation": "meronym",
                "prompt_token": "wheel",
                "response_token": "car",
                "geometry": LEXICAL_GEOMETRY["meronym"],
            },
        ],
    )

    assert result["canonical"] is True
    assert result["status"] == "ADMIT_ONE_CLOSED_TENSOR_STATE"
    assert result["prompt_response_sequential_independence"] is False
    assert result["ordered_tensor"]["authority_surface"] == "A"
    assert result["ordered_tensor"]["response_competing_authority_allowed"] is False
    assert result["ordered_tensor"]["direct_closure"] == "AB=P^4"
    assert result["ordered_tensor"]["mirror_closure"] == "BA=-P^4"
    assert result["ordered_tensor"]["commutation_allowed_without_native_proof"] is False
    assert result["phi8"]["ordered_channels"] == [
        "x", "y", "z", "w", "xy", "yx", "zw", "wz"
    ]
    assert result["phi8"]["verified"] is True
    assert result["invariants"]["delta_e"] == 0
    assert result["invariants"]["psi"] == 0
    assert result["invariants"]["h72"] is True
    assert result["invariants"]["h216"] is True
    assert len(result["lineage"]["transition_word216"]) == 216
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_mutation_authority"] is False
    assert result["canonical_hash216_mutation_authority"] is False
    assert result["persistence_authority"] is False


def test_wordnet_relation_geometry_is_typed_not_similarity_only():
    result = admit_prompt_response_tensor(
        "rapid hot animal dog",
        "fast cold dog animal",
        relation_db=_relation_db(),
    )
    typed = {
        (edge["prompt_token"], edge["response_token"], edge["relation"], edge["geometry"])
        for edge in result["wordnet_geometry"]["edges"]
    }

    assert ("rapid", "fast", "synonym", LEXICAL_GEOMETRY["synonym"]) in typed
    assert ("hot", "cold", "antonym", LEXICAL_GEOMETRY["antonym"]) in typed
    assert ("animal", "dog", "hyponym", LEXICAL_GEOMETRY["hyponym"]) in typed
    assert ("dog", "animal", "hypernym", LEXICAL_GEOMETRY["hypernym"]) in typed
    assert result["wordnet_geometry"]["verified"] is True


def test_wrong_lexical_geometry_collapses_whole_tensor_to_bottom():
    result = admit_prompt_response_tensor(
        "hot",
        "cold",
        relation_db=_relation_db(),
        explicit_relations=[
            {
                "relation": "antonym",
                "prompt_token": "hot",
                "response_token": "cold",
                "geometry": LEXICAL_GEOMETRY["synonym"],
            }
        ],
    )

    assert result["canonical"] is False
    assert result["status"] == "BOTTOM"
    assert result["tensor_state"] == "BOTTOM"
    assert result["humility"]["state"] == "BOTTOM"
    assert result["self_awareness"]["all_verified"] is False
    assert any(
        reason.startswith("LEXICAL_GEOMETRY_MISMATCH")
        for reason in result["failure_reasons"]
    )


def test_missing_reciprocal_response_collapses_whole_tensor():
    result = admit_prompt_response_tensor("authoritative prompt", "", relation_db={})

    assert result["canonical"] is False
    assert result["status"] == "BOTTOM"
    assert "RECIPROCAL_RESPONSE_REQUIRED" in result["failure_reasons"]

    with pytest.raises(PromptResponseTensorAdmissionError):
        require_prompt_response_tensor(
            "authoritative prompt",
            "",
            relation_db={},
        )


def test_module_self_test_closes():
    assert self_test()["ok"] is True


class _TextTransport:
    provider_id = "provider:test.i049"
    requested_operation = "test.i049.chat_completion"

    async def list_models(self):
        return {"object": "list", "data": [{"id": "i049-model"}]}

    async def chat_completion(self, **_kwargs):
        return {
            "id": "chatcmpl-i049-text",
            "model": "i049-model",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Derived reciprocal response."},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 3, "completion_tokens": 3, "total_tokens": 6},
        }


class _ToolTransport(_TextTransport):
    async def chat_completion(self, **_kwargs):
        return {
            "id": "chatcmpl-i049-tool",
            "model": "i049-model",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "id": "call-i049",
                        "type": "function",
                        "function": {
                            "name": "hhs_runtime_state",
                            "arguments": json.dumps({}),
                        },
                    }],
                },
                "finish_reason": "tool_calls",
            }],
            "usage": {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4},
        }


def _service(transport):
    config = LiteRTLMConfig(model_id="i049-model", max_messages_per_thread=8)
    return HHSAssistantService(
        config=config,
        transport=transport,
        provider_id=transport.provider_id,
        requested_operation=transport.requested_operation,
    )


def test_shared_assistant_boundary_binds_text_turn_to_tensor_admission():
    service = _service(_TextTransport())
    thread = service.create_thread(project_id="project:i049")
    turn = asyncio.run(
        service.send_message(thread["thread_id"], content="Authoritative prompt.")
    )

    tensor = turn["prompt_response_tensor_admission"]
    assert turn["ok"] is True
    assert tensor["canonical"] is True
    assert tensor["ordered_tensor"]["authority_surface"] == "A"
    assert turn["assistant_message"]["admission"][
        "prompt_response_tensor_admission_root_hash72"
    ] == tensor["admission_root_hash72"]
    assert turn["assistant_message"]["admission"]["prompt_response_tensor_state"] == (
        "ONE_CLOSED_TENSOR_STATE"
    )


def test_tool_call_is_bound_as_derived_reciprocal_payload():
    service = _service(_ToolTransport())
    thread = service.create_thread(project_id="project:i049-tool")
    turn = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Inspect the runtime.",
            tools=[{
                "type": "function",
                "function": {
                    "name": "hhs_runtime_state",
                    "description": "Inspect runtime",
                    "parameters": {"type": "object", "properties": {}},
                },
            }],
        )
    )

    tensor = turn["prompt_response_tensor_admission"]
    assert turn["ok"] is True
    assert tensor["canonical"] is True
    assert tensor["ordered_tensor"]["derived_phase"]["role"] == "TOOL_CALL"
    assert turn["assistant_message"]["content"] == ""
    assert turn["assistant_message"]["tool_calls"]


def test_bottom_tensor_is_not_persisted_as_independent_assistant_state(monkeypatch):
    import hhs_backend.runtime.hhs_litert_lm_assistant_v1 as assistant

    def reject(*_args, **_kwargs):
        return {
            "canonical": False,
            "status": "BOTTOM",
            "tensor_state": "BOTTOM",
            "failure_reasons": ["INJECTED_RECIPROCAL_CLOSURE_FAILURE"],
            "admission_root_hash72": "x" * 72,
        }

    monkeypatch.setattr(assistant, "admit_prompt_response_tensor", reject)
    service = _service(_TextTransport())
    thread = service.create_thread(project_id="project:i049-bottom")
    turn = asyncio.run(
        service.send_message(thread["thread_id"], content="Authoritative prompt.")
    )

    assert turn["ok"] is False
    assert turn["status"] == "REJECT_PROMPT_RESPONSE_TENSOR_BOTTOM"
    assert turn["assistant_message"] is None
    assert turn["provider_output_retained_as_independent_state"] is False
    assert turn["provider_result_ingress_performed"] is False
    stored = service.threads.get(thread["thread_id"])
    assert [message["role"] for message in stored["messages"]] == ["user"]
