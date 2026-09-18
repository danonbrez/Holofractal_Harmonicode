# Pass 220 I009 — Native causal-LM RAG prompt/response generation

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / NATURAL-LANGUAGE EGRESS ONLY

## Purpose

I009 adds the repository-native causal token-generation path beneath the I008 General Chat / Agentic Application Development / Both mode membrane.

```text
conversation history
+ selected assistant mode
+ cached admitted Pass 219 prompt/response prototype retrieval
→ tokenizer/chat template
→ model.generate(...)
→ verify complete causal input-prefix preservation
→ decode only newly generated token IDs
→ natural-language response
→ exact generation receipt
→ inherited HHS provider receipt/result ingress
```

This is the native assistant equivalent of an ordinary RAG text-generation cycle.

## Runtime

Implementation:

```text
hhs_backend/runtime/hhs_pass220_native_causal_lm_generation_v1.py
```

The service accepts injected tokenizer/model objects or lazily loads an already-local/already-cached Hugging Face-compatible causal model.

```text
HHS_NATIVE_CAUSAL_LM_MODEL=<local path or cached model id>
HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY=1
HHS_NATIVE_CAUSAL_LM_MAX_NEW_TOKENS=256
```

`local_files_only=1` is the default, so a chat request does not silently become a model download. `transformers` is imported only when a configured lazy model is first requested.

## Causal token invariant

For encoded prompt token sequence `I` and generated sequence `G`:

```text
len(G) >= len(I)
G[0:len(I)] == I
response_tokens = G[len(I):]
```

Generation fails closed when the backend does not preserve the complete input prefix. Only `response_tokens` are decoded as assistant output.

## Conversation and RAG context

The generator consumes the normalized conversation history, including the inherited HHS instruction, I008 assistant-mode instruction, optional user custom system instruction, and user/assistant history.

If the tokenizer exposes `apply_chat_template`, it is used with `tokenize=false` and `add_generation_prompt=true`; otherwise a deterministic role-labelled projection is used.

The native provider also reuses the admitted Pass 219 prompt/response prototype selector. Zero-overlap candidates are discarded. Selected prototypes are explicitly rendered as non-authoritative language context.

Prototype metadata remains candidate-only: `truth_promotion=false` and `vm81_commit_invoked=false`. The Pass 219 `hash216_root` field remains its inherited training-lineage field and is not reinterpreted as the separate three-Hash72/216-symbol Pass 220 query ABI.

## No repeated rebuild

The compiled Pass 219 prototype dataset is cached per active Pass 166 model identity:

```text
same active Pass166 model
→ compile once
→ retrieve many times

model identity changes
→ rebuild against the new language-memory identity
```

This prevents rebuilding the same normalized corpus on every chat turn.

## Mode routing

`GENERAL_CHAT`: ordinary prompts use the native causal path when ready and do not require a developer-tool round.

`BOTH`: ordinary conversation uses the same causal path; explicit code/repository/runtime/build/test/deploy intent enters governed tool routing first.

`AGENTIC_APPLICATION_DEVELOPMENT`: the development domain remains primary; I009 does not silently replace it with unrestricted chat behavior.

## Fallback

The causal model is not required for native-provider installation readiness. If it is unconfigured, unavailable, missing optional runtime support, or violates the prefix contract, the provider records that failure and returns to the inherited exact semantic/native language fallback.

A successful causal turn records `generation_path=NATIVE_CAUSAL_LM_RAG`. A fallback turn records `generation_path=EXACT_SEMANTIC_FALLBACK` plus a bounded causal-generation diagnostic.

## Receipt and authority

Successful generation records exact model/prompt/context/token-count/response identities plus `causal_prefix_verified=true` and a Hash72 receipt root.

Authority remains:

```text
natural_language_egress_only = true
canonical_vm81_mutation_authority = false
canonical_hash72_mutation_authority = false
canonical_hash216_mutation_authority = false
```

The ordinary HHS provider proposal/receipt/result-ingress path still wraps the language turn afterward.

## Tests

Dependency-scoped tests verify prefix preservation, suffix-only decoding, exact receipt metadata, fail-closed unconfigured behavior, General Chat causal generation, Both-mode development-tool precedence, and one-time Pass 219 prototype compilation with repeated retrieval.

CI uses injected fake tokenizer/model objects, so validation does not require a large model or a `transformers` installation.

## Deployment boundary

I009 makes the native assistant capable of causal-LM RAG generation. A host reports the causal layer loaded/ready only after a real configured model has actually loaded; the adapter does not infer model readiness from its own presence.