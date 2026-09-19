# Pass 220 I009 preimplementation checkpoint — native causal-LM RAG prompt/response generation

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor I008 head: `cb2158d859818711dd245015a856fc5ffc919900`
- merge target: `main`
- PR: #491

## Objective

Close the remaining gap between "general-chat mode exists" and "the repository-native assistant can perform a normal causal-language-model prompt/response token-generation cycle."

I009 SHALL add an optional, lazy, repository-native Hugging-Face-compatible causal-LM generation service beneath the existing native provider.

The generation path is:

```text
conversation history
+ selected assistant mode
+ cached Pass 219 admitted prompt/response prototype retrieval
→ tokenizer/chat template
→ causal model.generate(...)
→ decode only newly generated tokens
→ natural-language assistant response
→ exact noncanonical generation receipt
→ existing HHS provider receipt/result ingress
```

## Constraints

- no model download is silently required;
- local model loading is opt-in/configured and lazy;
- CI MUST work with injected fake tokenizer/model objects and no transformers installation;
- the text generator has zero VM81/Hash72/Hash216 mutation authority;
- retrieved Pass 219 prototypes are candidate context only;
- prototype compilation MUST be process-cached so the same normalized corpus is not rebuilt every turn;
- ordinary General Chat and ordinary Both-mode prompts may use this path;
- Agentic Application Development retains governed tool routing;
- when no native causal model is configured/ready, the inherited exact semantic fallback remains available;
- user custom system instructions, mode selection, conversational history, Copy/Paste, and vector-ingress boundaries remain intact.

## Configuration target

```text
HHS_NATIVE_CAUSAL_LM_MODEL
HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY=1
HHS_NATIVE_CAUSAL_LM_MAX_NEW_TOKENS=256
```

The model identifier may be a local directory or an already-cached Hugging Face model identifier. Network acquisition is not implicit in the native assistant runtime.

## Acceptance

1. injected fake tokenizer/model completes a causal generation roundtrip;
2. input-prefix preservation is verified before decoding new tokens;
3. the native provider prefers the causal generation path for ordinary General Chat when ready;
4. Both mode also uses causal generation for ordinary conversation but still routes explicit development intent to governed tools;
5. Pass 219 prototype compilation is cached and retrieval is exact/candidate-only;
6. no causal-language output gains canonical state authority;
7. missing/unconfigured causal model falls back without fabricating readiness;
8. restartable checkpoint is committed before waiting for external CI.
