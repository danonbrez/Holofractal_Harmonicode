# Pass 220 I005 restart checkpoint — Hugging Face RAG natural-language assistant

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — CI PENDING**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor I004 checkpoint head: `fe2475c3cc2ca90202c0364549ff23b26452a6ff`
- I005 preimplementation checkpoint: `b0865cffd4933087645c54465c63831030d30ada`
- merge target: `main`
- PR: #491

## Implemented boundary

I005 exposes the language layer as an ordinary Hugging Face-compatible RAG assistant:

```text
user prompt
→ HHS retriever
→ exact query Hash216 + authorized records
→ deterministic whole-record natural-language context
→ tokenizer(..., return_tensors="pt")
→ model.generate(...)
→ tokenizer.decode(...)
→ assistant response
```

The adapter deliberately does not create an alternate prompt-to-Hash216 algorithm.  Hash216 query/record identities are returned by the HHS retrieval authority and validated through the existing Pass 220 Hash216 surface.

## Implemented invariants

- every retrieved Hash216 is validated;
- every retrieved record must explicitly allow assistant context;
- duplicate Hash216 + identical text is reused once;
- duplicate Hash216 + conflicting text fails closed;
- context budgeting includes or omits complete records and never truncates an admitted record mid-payload;
- deterministic context roots provide composition-cache reuse;
- default generation is normal greedy Hugging Face `generate()`;
- ordinary generation kwargs pass through for noncanonical token sampling;
- decoder-only causal generation must preserve the exact input-token prefix;
- only the generated suffix is decoded as the assistant answer;
- response receipts bind prompt, query Hash216, retrieved Hash216 identities, context root, generation inputs, token counts, output hash, and generation kwargs;
- language generation has no VM81/Hash72/Hash216 mutation authority.

## Implemented files

- `hhs_backend/runtime/hhs_pass220_hf_rag_assistant_v1.py`
- `tests/pass220/test_hhs_pass220_hf_rag_assistant_v1.py`
- `docs/pass220/PASS_220_I005_HUGGING_FACE_RAG_NATURAL_LANGUAGE_ASSISTANT.md`
- cumulative workflow updated through I005

## Commit sequence

- preimplementation checkpoint: `b0865cffd4933087645c54465c63831030d30ada`
- RAG assistant runtime: `099c68c73e1600ec70f8476a94db31ce10084ae7`
- RAG assistant tests: `e0269aeec916d3f8c297fc705a0936d2ae82912d`
- formal I005 document: `41cdc5e5b3a567d260f6974b56140cd8a9eb265b`
- cumulative I003-I005 workflow: `476f0df9e772b0066f64c19669b3f548ebd766a4`

## Validation scope

The cumulative workflow now keeps the cold raw x86_64 calibration as the first executable workload, then compiles and executes dependency-scoped I001-I005 tests under `set -o pipefail`.

I005 tests use a fake tokenizer/model pair with the same callable interface as a real Hugging Face causal LM, so CI requires no external model download and no hard `transformers` installation.

Per the repository responsiveness policy, this implementation is checkpointed without blocking on the queued external runner.

## Next action

Inspect the workflow attached to this checkpoint head.  Repair forward only impacted failures.  After green validation, the next cycle can expose this exact I005 service through the production assistant/API control surface and connect a deployment-selected local Hugging Face model plus the existing authorized HHS vector-store retriever.
