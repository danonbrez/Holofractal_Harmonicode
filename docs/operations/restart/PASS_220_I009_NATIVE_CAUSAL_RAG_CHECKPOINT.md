# Pass 220 I009 restart checkpoint — native causal-LM RAG prompt/response generation

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — CI PENDING**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor I008 head: `cb2158d859818711dd245015a856fc5ffc919900`
- I009 preimplementation checkpoint: `3114f820b7d5ae12ba9f84340e8c377cb9f1fca5`
- merge target: `main`
- PR: #491

## Implemented

I009 adds a real optional causal token-generation path to the repository-native assistant.

```text
thread/system/mode/custom instructions
+ cached admitted Pass219 prototype retrieval
→ tokenizer/chat template
→ causal model.generate
→ exact prefix verification
→ decode new token suffix only
→ natural-language response
→ Hash72-witnessed generation receipt
→ inherited HHS provider result ingress
```

The implementation is lazy and local-first. `HHS_NATIVE_CAUSAL_LM_MODEL` may identify a local directory or already-cached Hugging Face-compatible model. `HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY=1` is the default and prevents implicit model downloads.

## Optimization

Pass 219 prompt/response normalization is compiled once per active Pass 166 model identity and reused across queries. A model-identity change invalidates that process cache and rebuilds it once.

## Mode integration

- GENERAL_CHAT: ordinary prompts prefer native causal generation when ready.
- BOTH: ordinary prompts prefer native causal generation; explicit development intent still enters governed tool routing first.
- AGENTIC_APPLICATION_DEVELOPMENT: the selected development domain remains primary.

If the causal model is not ready, the native provider falls back to the inherited exact semantic/native-language response path and records the bounded cause. No readiness is fabricated.

## Authority

```text
natural_language_egress_only = true
canonical_vm81_mutation_authority = false
canonical_hash72_mutation_authority = false
canonical_hash216_mutation_authority = false
```

## Added files

- `hhs_backend/runtime/hhs_pass220_native_causal_lm_generation_v1.py`
- `tests/pass220/test_hhs_pass220_i009_native_causal_rag_generation.py`
- `docs/pass220/PASS_220_I009_NATIVE_CAUSAL_RAG_PROMPT_RESPONSE_GENERATION.md`

## Modified files

- `hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py`
- `.github/workflows/pass220-i003-four-phase-abc-max-hardware.yml`
- `.github/workflows/litert-lm-assistant.yml`

## Implementation commits

- preimplementation checkpoint: `3114f820b7d5ae12ba9f84340e8c377cb9f1fca5`
- causal generation service: `94f2e33960894544e14bbd6bb33bee7c61d65896`
- native provider RAG/generation integration: `9e07e3982c0e821741979cb454f67df33dd9e098`
- dependency-scoped tests: `24544861897eeaa405e1bdb39ec6390cd1b42e7c`
- cumulative Pass 220 validation update: `97d9548e81fb1fc17c5790c896ff0610d5296553`
- LiteRT assistant validation update: `90fb91d3221e63555e413f74477eba25e675fdf6`
- formal I009 document: `89c37966c93e0f2678fd57307e0fad9a07b921b8`

## Validation pending

Impacted workflows now include:

1. Pass 220 I003-I009 cumulative calibration/integration;
2. LiteRT-LM Gemma 4 Assistant backend validation;
3. inherited Runtime OS / PR validation as triggered.

Per repository policy, queued external CI does not block this restartable checkpoint.

## Next action

Inspect the newest I009 workflow runs. Repair forward only dependency-scoped failures. After green I009 validation, update PR #491 toward merge readiness and then validate exact-main deployment with:

1. one General Chat causal turn using a configured local/cached model;
2. one Both-mode ordinary chat turn with zero developer tool calls;
3. one Both-mode explicit development turn that routes governed tools before causal generation;
4. one repeated prompt proving Pass219 prototype compilation is reused rather than rebuilt.