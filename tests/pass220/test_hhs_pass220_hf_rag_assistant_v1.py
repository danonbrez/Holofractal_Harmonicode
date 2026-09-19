import pytest

from hhs_backend.runtime.hhs_pass220_hf_rag_assistant_v1 import (
    Pass220HFRAGError,
    Pass220HuggingFaceRAGAssistant,
    normalize_retrieval,
)
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    HASH72_ALPHABET,
    compose_hash216,
)


def _word(symbol_index: int) -> str:
    return HASH72_ALPHABET[symbol_index] * 72


def _hash216(seed: int) -> str:
    return compose_hash216(_word(seed % 72), _word((seed + 1) % 72), _word((seed + 2) % 72))


class FakeRetriever:
    def __init__(self, records):
        self.records = list(records)
        self.calls = []

    def retrieve(self, *, prompt, top_k):
        self.calls.append({"prompt": prompt, "top_k": top_k})
        return {
            "schema": "TEST_RETRIEVER_V1",
            "query_hash216": _hash216(0),
            "records": self.records,
        }


class FakeTokenizer:
    def __init__(self):
        self.calls = []
        self.decode_calls = []

    def __call__(self, text, *, return_tensors, truncation):
        self.calls.append(
            {
                "text": text,
                "return_tensors": return_tensors,
                "truncation": truncation,
            }
        )
        return {"input_ids": [[ord(ch) for ch in text]]}

    def decode(self, token_ids, *, skip_special_tokens):
        self.decode_calls.append(
            {
                "token_ids": list(token_ids),
                "skip_special_tokens": skip_special_tokens,
            }
        )
        return "".join(chr(value) for value in token_ids)


class FakeModel:
    def __init__(self, response="retrieved answer"):
        self.response = response
        self.calls = []

    def generate(self, *, input_ids, **kwargs):
        self.calls.append({"input_ids": input_ids, "kwargs": dict(kwargs)})
        return [list(input_ids[0]) + [ord(ch) for ch in self.response]]


def _record(index: int, text: str, **overrides):
    result = {
        "record_id": f"record-{index}",
        "hash216": _hash216(index + 3),
        "text": text,
        "source": f"source-{index}",
        "assistant_context_allowed": True,
    }
    result.update(overrides)
    return result


def test_normal_hugging_face_rag_generation_call_shape():
    retriever = FakeRetriever(
        [
            _record(0, "The first retrieved fact."),
            _record(1, "The second retrieved fact."),
        ]
    )
    tokenizer = FakeTokenizer()
    model = FakeModel("final answer")
    assistant = Pass220HuggingFaceRAGAssistant(
        tokenizer=tokenizer,
        model=model,
        retriever=retriever,
        top_k=2,
        max_context_characters=4096,
    )

    result = assistant.generate("What was retrieved?")

    assert result["response"] == "final answer"
    assert retriever.calls == [{"prompt": "What was retrieved?", "top_k": 2}]
    assert len(tokenizer.calls) == 1
    rendered = tokenizer.calls[0]["text"]
    assert "The first retrieved fact." in rendered
    assert "The second retrieved fact." in rendered
    assert "User:\nWhat was retrieved?" in rendered
    assert tokenizer.calls[0]["return_tensors"] == "pt"
    assert tokenizer.calls[0]["truncation"] is False
    assert model.calls[0]["kwargs"]["max_new_tokens"] == 256
    assert model.calls[0]["kwargs"]["do_sample"] is False
    assert tokenizer.decode_calls[0]["skip_special_tokens"] is True
    assert result["receipt"]["hf_call_shape"] == (
        "tokenizer(...) -> model.generate(...) -> tokenizer.decode(...)"
    )
    assert result["receipt"]["retrieval_authority"] == "HHS_HASH216"
    assert result["receipt"]["canonical_vm81_mutation_authority"] is False
    assert result["receipt"]["canonical_hash72_authority"] is False
    assert result["receipt"]["canonical_hash216_authority"] is False


def test_duplicate_hash216_same_payload_is_reused_not_rebuilt():
    shared = _hash216(20)
    records = [
        _record(0, "shared exact context", hash216=shared),
        _record(1, "shared exact context", hash216=shared),
    ]
    retriever = FakeRetriever(records)
    assistant = Pass220HuggingFaceRAGAssistant(
        tokenizer=FakeTokenizer(),
        model=FakeModel(),
        retriever=retriever,
        top_k=8,
        max_context_characters=4096,
    )

    first = assistant.generate("same prompt")
    second = assistant.generate("same prompt")

    assert first["retrieval"]["duplicate_reuse_count"] == 1
    assert len(first["retrieval"]["selected_records"]) == 1
    assert first["receipt"]["context_reused"] is False
    assert second["receipt"]["context_reused"] is True
    assert first["receipt"]["context_root_sha256"] == second["receipt"]["context_root_sha256"]


def test_duplicate_hash216_conflicting_text_fails_closed():
    shared = _hash216(25)
    retriever = FakeRetriever(
        [
            _record(0, "payload A", hash216=shared),
            _record(1, "payload B", hash216=shared),
        ]
    )
    assistant = Pass220HuggingFaceRAGAssistant(
        tokenizer=FakeTokenizer(),
        model=FakeModel(),
        retriever=retriever,
    )
    with pytest.raises(Pass220HFRAGError, match="conflicting"):
        assistant.generate("prompt")


def test_unauthorized_assistant_context_fails_closed():
    retriever = FakeRetriever(
        [_record(0, "private context", assistant_context_allowed=False)]
    )
    assistant = Pass220HuggingFaceRAGAssistant(
        tokenizer=FakeTokenizer(),
        model=FakeModel(),
        retriever=retriever,
    )
    with pytest.raises(Pass220HFRAGError, match="not authorized"):
        assistant.generate("prompt")


def test_context_budget_uses_whole_records_without_mid_payload_truncation():
    long_record = _record(0, "X" * 500)
    short_record = _record(1, "short")
    payload = {
        "query_hash216": _hash216(0),
        "records": [long_record, short_record],
    }
    normalized = normalize_retrieval(
        payload,
        top_k=8,
        max_context_characters=180,
    )

    assert [r["record_id"] for r in normalized["selected_records"]] == ["record-1"]
    assert [r["record_id"] for r in normalized["omitted_records"]] == ["record-0"]
    assert "short" in normalized["context"]
    assert "X" * 50 not in normalized["context"]
    assert normalized["whole_record_budgeting"] is True


def test_normal_generation_kwargs_pass_through_to_model_generate():
    retriever = FakeRetriever([_record(0, "context")])
    model = FakeModel("sample")
    assistant = Pass220HuggingFaceRAGAssistant(
        tokenizer=FakeTokenizer(),
        model=model,
        retriever=retriever,
    )

    result = assistant.generate(
        "prompt",
        generation_kwargs={
            "max_new_tokens": 12,
            "do_sample": True,
            "top_k": 5,
            "top_p": 0.9,
            "temperature": 0.7,
        },
    )

    kwargs = model.calls[0]["kwargs"]
    assert kwargs["max_new_tokens"] == 12
    assert kwargs["do_sample"] is True
    assert kwargs["top_k"] == 5
    assert kwargs["top_p"] == 0.9
    assert kwargs["temperature"] == 0.7
    assert result["receipt"]["natural_language_egress_only"] is True
    assert result["receipt"]["probability_may_select_natural_language_tokens_only"] is True


def test_invalid_retrieval_hash216_is_rejected():
    payload = {
        "query_hash216": "not-hash216",
        "records": [],
    }
    with pytest.raises(Pass220HFRAGError):
        normalize_retrieval(payload, top_k=8, max_context_characters=1024)


def test_causal_generate_must_preserve_input_prefix():
    class BadModel:
        def generate(self, *, input_ids, **_kwargs):
            return [[1, 2, 3]]

    assistant = Pass220HuggingFaceRAGAssistant(
        tokenizer=FakeTokenizer(),
        model=BadModel(),
        retriever=FakeRetriever([_record(0, "context")]),
    )
    with pytest.raises(Pass220HFRAGError, match="include the input prefix|preserve the input token prefix"):
        assistant.generate("longer prompt")


def test_configuration_rejects_bool_as_integer():
    with pytest.raises(Pass220HFRAGError):
        Pass220HuggingFaceRAGAssistant(
            tokenizer=FakeTokenizer(),
            model=FakeModel(),
            retriever=FakeRetriever([]),
            top_k=True,
        )
