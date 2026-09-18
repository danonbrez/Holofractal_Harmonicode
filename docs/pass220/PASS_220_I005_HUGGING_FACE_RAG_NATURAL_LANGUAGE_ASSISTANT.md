# Pass 220 I005 — Hugging Face RAG Natural-Language Assistant

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / NO CANONICAL AUTHORITY WIDENING

## 1. External generation model

From the Hugging Face generation-cycle boundary the language system is intentionally ordinary:

```text
user prompt
→ retrieve
→ augment natural-language context
→ tokenizer(...)
→ model.generate(...)
→ tokenizer.decode(...)
→ assistant response
```

The HARMONICODE/Genesis/Hash72/Hash216/Lane 5 machinery remains underneath the retrieval boundary.  A Hugging Face-compatible causal LM does not need to parse HARMONICODE equations or know the internal 5184/72^72 geometry.

## 2. Retrieval boundary

I005 does not invent a new text-to-Hash216 algorithm.

The HHS retriever owns query construction and returns:

```text
query_hash216
records[]
```

Each retrieved record carries:

```text
record_id
hash216
text
assistant_context_allowed
optional source
```

Every Hash216 is validated through the existing Pass 220 Hash216 split/validation surface before it can enter the RAG context.

Thus the natural-language assistant consumes HHS retrieval identity rather than manufacturing a parallel identity system.

## 3. User-controlled assistant context

Inherited Pass 194 authority requires assistant context to remain user controlled.

I005 therefore fails closed if a retrieved record does not explicitly carry:

```text
assistant_context_allowed = true
```

The adapter does not silently promote private/storage-only material into the model context.

## 4. Lossless reuse rule

The universal compression/reuse rule is applied at the RAG boundary.

For duplicate retrieved Hash216 identities:

```text
same Hash216 + same exact text
→ reuse once

same Hash216 + different exact text
→ reject
```

An exact text SHA-256 is retained for each selected record.

The composed context receives a deterministic `context_root_sha256`.  If the same context root is requested again during the service lifetime, the already-assembled context is reused rather than rebuilt.

This cache is an optimization only and has no canonical mutation authority.

## 5. Context-window budgeting

The Hugging Face-facing context is bounded by an exact character budget.

I005 never destroys part of an admitted retrieved record merely to fit the budget.

Instead:

```text
whole record fits
→ include complete record

whole record does not fit
→ omit complete record and record the omission reason
```

This gives deterministic whole-record RAG assembly without mid-payload truncation.

The source record remains in the HHS store; omission from one bounded generation context is not deletion or lossy compression.

## 6. Hugging Face call shape

The callable service is:

```text
hhs_backend/runtime/hhs_pass220_hf_rag_assistant_v1.py
```

It accepts a tokenizer and model by the standard duck-typed Hugging Face interface.

Generation executes:

```python
encoded = tokenizer(
    rendered_prompt,
    return_tensors="pt",
    truncation=False,
)

generated = model.generate(
    **encoded,
    max_new_tokens=...,
    do_sample=...,
    ...
)

response = tokenizer.decode(
    generated_new_tokens,
    skip_special_tokens=True,
)
```

No hard `transformers` or model-download dependency is required by the runtime module itself.

A real local `AutoTokenizer` / `AutoModelForCausalLM` pair can be supplied directly by deployment code.

## 7. Default generation behavior

I005 defaults to:

```text
max_new_tokens = 256
do_sample = false
```

which is normal deterministic greedy causal generation.

Callers may supply ordinary Hugging Face generation kwargs such as:

```text
top_k
top_p
temperature
eos_token_id
pad_token_id
```

These parameters affect natural-language token selection only.

They do not acquire VM81, Hash72, Hash216, or canonical state authority.

## 8. Causal prefix invariant

The adapter expects ordinary decoder-only causal generation semantics:

```text
generated_sequence =
input_prompt_tokens || newly_generated_tokens
```

The input prefix must be preserved exactly.

Only the new suffix is decoded as the assistant response.

A generation backend that returns a shorter sequence or mutates the input prefix is rejected by this adapter.

## 9. RAG receipt

Every response carries deterministic audit metadata including:

- user prompt SHA-256;
- HHS query Hash216;
- selected retrieved Hash216 identities;
- selected record IDs;
- composed context root;
- context reuse flag;
- context size;
- deduplication/reuse count;
- omitted-record count;
- rendered generation-prompt SHA-256;
- input token count;
- generated token count;
- response SHA-256;
- exact generation kwargs;
- the declared Hugging Face call shape.

The receipt is evidence for replay/debugging of the language boundary.  It is not a new canonical HHS transition.

## 10. Authority separation

The service explicitly reports:

```text
retrieval_authority = HHS_HASH216
generation_authority = HUGGING_FACE_COMPATIBLE_CAUSAL_LM

canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
natural_language_egress_only = true
```

The Hugging Face model therefore remains an ordinary natural-language generator over retrieved context.

## 11. Relation to the 72^72 manifold

The `72^72` Hash72 offset manifold, Genesis normalization, Hash216 context identity, Lane 5 ranking, and vector/hydration machinery determine the HHS retrieval/composition side.

From the Hugging Face model's perspective those internals have already resolved into:

```text
natural-language context
+ ordinary user prompt
```

This is the intended abstraction boundary.

The generator need not expose or materialize `72^72` dense floating-point parameters to participate in the HHS retrieval architecture.

## 12. Implemented validation

The dependency-scoped I005 tests use a fake tokenizer/model pair with the same callable shape as a real Hugging Face causal LM and verify:

1. prompt → retrieval → context → tokenizer → generate → decode;
2. deterministic greedy defaults;
3. ordinary sampling kwargs pass-through;
4. duplicate exact Hash216/text reuse;
5. conflicting duplicate identity rejection;
6. user-controlled context authorization;
7. whole-record context budgeting;
8. invalid Hash216 rejection;
9. causal input-prefix preservation;
10. bool-as-integer configuration rejection;
11. no canonical authority widening.

No network access or model download is required for these tests.
