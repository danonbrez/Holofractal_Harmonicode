# Pass 219 — Approved External Projector Execution v1

## Purpose

This layer executes explicitly approved, immutable open-source embedding models **outside** the canonical VM81 kernel and emits a sealed `EXTERNAL_EVIDENCE_V1` object that can be supplied to the persistent Pass 219 acquisition job service.

It does not grant model inference canonical authority. Model output remains empirical candidate evidence and must pass the already merged source verification, translation-invariant ingress, I29/equivalent validation, and later canonical admission path before any canonical state transition.

## Production-approved profile

`MULTILINGUAL_MPNET_TEXT_V1`

- provider: Hugging Face;
- model: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`;
- immutable revision: `79f2382ceacceacdf38563d7c5d16b9ff8d725d6`;
- license: Apache-2.0;
- modalities: UTF-8 text-like source payloads only;
- `trust_remote_code = false`;
- safetensors required by the runtime load request;
- candidate-only.

The revision is intentionally immutable rather than `main`. A newer upstream revision is not admitted merely because it exists.

## Cross-modal profile boundary

`MULTILINGUAL_CLIP_IMAGE_TEXT_V1` is registered but **not production approved** in v1.

The multilingual text side is pinned to:

- `sentence-transformers/clip-ViT-B-32-multilingual-v1`;
- revision `58edf8cada9e9f1df0dd8a8bc2ae891e7b1a983c`;
- Apache-2.0.

The corresponding `sentence-transformers/clip-ViT-B-32` image model card does not explicitly declare its own license. v1 therefore refuses to infer a production license from related code/model lineage. Image/text execution stays blocked until an explicitly licensed, compatibility-validated image encoder is admitted.

## Exact source-before-model rule

The projector request carries the exact source bytes and their expected SHA-256. The adapter verifies the source digest before any model call. A mismatch rejects execution.

## Floating-point containment

Embedding inference is necessarily floating-point in this external adapter. Those floats never become canonical arithmetic.

1. Every vector element must be finite.
2. Vector dimensions must agree.
3. Zero-norm vectors are rejected.
4. Cosine similarity must be finite.
5. The empirical cosine is bounded to `[0,1]` for the existing semantic-similarity witness contract.
6. The bounded value is quantized to denominator `1,000,000,000` with round-half-even.
7. The resulting numerator/denominator is serialized as an exact rational witness.
8. Raw vector identity is retained as deterministic little-endian float32 bytes and SHA-256 sealed.

The exact rational is a receipt for the bounded empirical observation. It is not a theorem claiming the underlying floating model is exact.

## Evidence envelope

The adapter emits the object consumed by the existing `EXTERNAL_EVIDENCE_V1` job adapter:

- immutable model repository descriptor;
- pivot text and source/pivot languages;
- source modality;
- base64 canonical execution record;
- base64 vector-identity bytes;
- exact rational similarity;
- semantic labels and translation chain;
- projector profile/version identity;
- `candidate_only = true`.

The canonical execution record includes source identity, model identity, vector hashes, dimension, observed cosine string, bounded decimal, quantization denominator, safetensors requirement, `trust_remote_code=false`, and authority-denial flags.

## Mobile control

The production mobile acquisition panel supports both:

- `SOURCE_ONLY_V1` — acquire and verify immutable source bytes;
- `EXTERNAL_EVIDENCE_V1` — paste or inject evidence emitted by this external projector, then reacquire and independently verify the exact source before candidate admission.

The panel also exposes production-approved versus blocked execution profiles.

## Authority denial

This layer has no authority to:

- mutate VM81;
- mint canonical Hash72;
- mint the canonical 216-symbol Hash216;
- commit canonical learning;
- promote candidate evidence to truth;
- authorize an external action;
- permanently prune a candidate.

## Required validation

The dedicated gate must validate:

- immutable model revision registry;
- source digest verification before inference;
- deterministic evidence serialization;
- exact-rational similarity conversion;
- NaN/Inf rejection;
- wrong-modality rejection;
- blocked cross-modal profile rejection;
- acquisition API profile exposure;
- production mobile TypeScript build.
