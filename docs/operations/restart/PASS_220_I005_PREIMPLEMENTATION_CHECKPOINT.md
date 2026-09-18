# Pass 220 I005 preimplementation checkpoint — Hugging Face RAG natural-language assistant

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor head: `fe2475c3cc2ca90202c0364549ff23b26452a6ff`
- merge target: `main`
- PR: #491
- predecessor cumulative workflow: `35304369241` (queued at checkpoint time)

## Authorized interpretation

From the Hugging Face generation-cycle boundary, the Pass 220 language layer is an ordinary retrieval-augmented natural-language assistant:

```text
user prompt
→ HHS/Hash216 retrieval
→ bounded authorized natural-language context
→ Hugging Face tokenizer
→ model.generate(...)
→ assistant text
```

The Genesis/Hash72/Hash216/Lane 5 machinery remains below the retrieval boundary.  The Hugging Face generator does not need to understand HARMONICODE algebra.

## Required invariants

1. Natural-language prompt ingress remains ordinary text.
2. Retrieval authority remains HHS/Hash216; this adapter shall not invent a parallel Hash216 definition.
3. The retriever returns the exact query Hash216 and exact retrieved record Hash216 identities.
4. Retrieved assistant context must be explicitly authorized for assistant-context use.
5. Duplicate content identities are reused/deduplicated before context assembly.
6. A duplicate Hash216 with conflicting text is rejected fail-closed.
7. Context budgeting never truncates an admitted record mid-payload; whole records are included or omitted.
8. Identical context composition is assembled once and reused by deterministic identity.
9. Hugging Face generation is a natural-language egress layer, not VM81/Hash72/Hash216 mutation authority.
10. Default generation is deterministic greedy `generate()`; caller-supplied normal Hugging Face generation kwargs may alter noncanonical language sampling.
11. The adapter must work with ordinary Hugging Face tokenizer/model interfaces but tests must not require downloading a model or adding a hard `transformers` dependency.
12. Prompt, context, retrieval identities, generation inputs, and output receive deterministic receipt hashes for replay/audit without claiming canonical HHS state mutation.

## Planned files

- `hhs_backend/runtime/hhs_pass220_hf_rag_assistant_v1.py`
- `tests/pass220/test_hhs_pass220_hf_rag_assistant_v1.py`
- `docs/pass220/PASS_220_I005_HUGGING_FACE_RAG_NATURAL_LANGUAGE_ASSISTANT.md`
- cumulative I003-I005 workflow wiring
- postimplementation restart checkpoint

## Acceptance

A fake Hugging Face-compatible tokenizer/model pair will exercise the exact same `tokenizer(...) → model.generate(...) → tokenizer.decode(...)` call shape used by a real local Hugging Face causal LM, while HHS retrieval is represented by a deterministic typed retriever fixture.
