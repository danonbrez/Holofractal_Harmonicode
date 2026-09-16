# Pass 219 — Translation-Invariant Multimodal Open-Source Ingress v1

## 1. Purpose

This contract defines a bounded ingress layer for revision-pinned open-source
Hugging Face and GitHub repositories. The layer hydrates repository artifacts
through the inherited Pass 165 multimodal analyzer and allows external
multilingual or multimodal models to contribute candidate semantic projections.

The target property is **translation-invariant semantic correspondence without
source-identity collapse**.

Two source objects may therefore remain bytewise and cryptographically distinct
while being grouped into the same candidate semantic family when independently
revision-pinned projection evidence maps them to the same normalized meaning.

```text
raw source identity A != raw source identity B

while

semantic_family(A) == semantic_family(B)
```

The semantic-family equality is candidate retrieval/hydration evidence. It is
not a truth proof and does not overwrite either source.

## 2. Inherited authority

This layer inherits and does not replace:

- Pass 165 source-byte preservation, modality detection, deterministic token and
  chunk analysis, projection receipts, and VM81-governed learning boundary;
- Pass 166 exact semantic-vector evidence semantics;
- Pass 174/194 vector-store and hydration authority;
- Pass 219 Lane 5 candidate-search authority;
- the strict distinction between candidate metadata and canonical VM81 / Hash72
  / canonical 216-symbol Hash216 mutation.

The v1 implementation uses `MultimodalLearningService.analyze()` only. It does
not call Pass 165 learning commit.

## 3. External repository boundary

Network retrieval is not part of the canonical kernel.

A remote fetcher SHALL resolve every admitted artifact to:

```text
(provider, repository_id, immutable_revision, path, bytes, license_id)
```

where `immutable_revision` is a 40-character Git object / Hub commit identity.
Mutable references such as `main`, `master`, `latest`, branch names, tags that
can move, or unversioned URLs do not satisfy the v1 admission contract.

Supported providers are:

```text
HUGGING_FACE
GITHUB
```

The kernel receives bytes and locked provenance. It does not trust a URL as the
identity of the bytes.

## 4. Open-source license admission

Public download availability is not sufficient for production admission.

The v1 allowlist is deliberately narrow:

```text
apache-2.0
mit
bsd-2-clause
bsd-3-clause
cc-by-4.0
```

A repository or model whose declared license is not in the allowlist is rejected
before semantic hydration. This includes non-commercial licenses in the v1
production path.

The registry therefore records `facebook/nllb-200-distilled-600M` as an excluded
example because its Hub card declares `cc-by-nc-4.0`; it may be studied under its
license but is not silently treated as production-open-source input by this
contract.

## 5. Initial open-source reference set

The discovery registry binds the first reference surface to:

### Hugging Face

1. `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
   - Apache-2.0;
   - multilingual sentence/paragraph semantic alignment;
   - 50-language class reference.

2. `sentence-transformers/clip-ViT-B-32-multilingual-v1`
   - Apache-2.0;
   - multilingual text aligned to CLIP image space;
   - text/image correspondence reference.

Hub model entries are discovery references only until a fetcher supplies an
immutable Hub revision for the concrete hydration event.

### GitHub

1. `huggingface/sentence-transformers`
   - Apache-2.0;
   - discovery revision at contract creation:
     `2236e4f6ec18191ef73b91dbd17f60fbbfd97bc6`.

2. `huggingface/transformers`
   - Apache-2.0;
   - discovery revision at contract creation:
     `af980eefb90517d6ae767fba968ad7d33df2b4b7`.

The discovery SHAs do not authorize future moving-head ingestion. Every actual
artifact continues to carry the revision used for its bytes.

## 6. Projection contract

An external semantic projector may use an approved revision-pinned model to
produce a candidate projection. The kernel requires:

```text
model_repository
pivot_text
source_language
pivot_language
source_modality
model_output_sha256
vector_identity_sha256
exact similarity numerator / denominator
semantic labels
translation chain
candidate_only = true
```

The exact similarity field is represented as a rational number. Floating-point
model calculations, if used externally, are compatibility computation only; the
admitted witness must serialize its resulting evidence identity and bounded
exact ratio before entering this layer.

A model output cannot set `candidate_only = false` or otherwise self-grant
canonical authority.

## 7. Translation-invariant semantic family

The implementation normalizes pivot text using Unicode NFKC/casefold semantics,
then expands recognized terms through the inherited WordNet relation database.
The candidate family is Hash72-sealed over:

```text
pivot language
normalized semantic terms
semantic labels
```

Source bytes, source repository, source language, source modality, projection
model, and provenance remain outside the semantic-family identity and are kept
in their own receipts.

Therefore two translations can converge to the same semantic-family receipt
without making their source hashes equal.

## 8. Multimodal normalization

Pass 165 remains responsible for source modality detection and raw observation
projection across:

```text
TEXT / MARKDOWN / SOURCE_CODE / JSON / JSONL / CSV / HTML / XML
PDF
IMAGE
AUDIO
VIDEO
BINARY_OBJECT
```

An approved external model may project any supported modality into a pivot
semantic representation. The semantic family may then contain members from
multiple modalities.

Example:

```text
English text: "A cat sits on a mat"
Spanish text: "Un gato se sienta en una estera"
image: cat-on-mat.png

raw SHA256 identities: all distinct
candidate semantic family: shared
```

This is a retrieval/hydration equivalence candidate, not a claim that every
information-bearing detail in each source is interchangeable.

## 9. Batch hydration

A batch groups records by their candidate semantic-family Hash72 receipt and
records:

- member count;
- source languages;
- modalities;
- source providers;
- all distinct raw SHA256 source identities;
- whether cross-language correspondence was observed;
- whether cross-modal correspondence was observed.

The batch also receives a Hash72 receipt and noncanonical SHA256 candidate index.

The SHA256 candidate index is not canonical 216-symbol Hash216.

## 10. Authority boundary

Every v1 output must preserve:

```text
candidate_only = true
truth_promotion = false
action_authority_minted = false
canonical_learning_commit_invoked = false
vm81_commit_invoked = false
canonical_hash72_minted = false
canonical_hash216_minted = false
```

A projected record must pass I29 or an equivalent validated semantic-state
boundary before it can become a Lane 5 canonical-Hash216 search candidate.

No translation model, embedding model, repository popularity metric, cosine
score, cross-modal similarity, or semantic-family match can bypass that rule.

## 11. Failure policy

Fail closed on:

- mutable repository revisions;
- unapproved licenses;
- unsupported providers or repository kinds;
- empty or oversized artifacts;
- invalid paths;
- missing pivot text/language;
- malformed model-output/vector identities;
- similarity outside `[0,1]`;
- semantic projection authority drift;
- Pass 165 source-hash divergence;
- projection count above the bounded maximum.

Missing projection evidence is `HOLD`, not rejection of the preserved source.
Low semantic similarity is also `HOLD`, not irreversible cancellation.

## 12. Validation target

The v1 dependency-scoped gate proves:

1. mutable refs are rejected;
2. non-commercial license examples are excluded from production admission;
3. translated text can share a semantic family without raw-source collapse;
4. text and image can share a candidate family;
5. low similarity produces HOLD;
6. absent semantic projection produces HOLD while retaining Pass 165 evidence;
7. external projectors cannot self-grant authority;
8. repository and model receipts remain revision-pinned; and
9. the discovery registry contains only allowlisted production references.

The next cycle after this gate is green is a real-source calibration workload:
fetch a bounded immutable corpus from the approved Hugging Face and GitHub
references, execute multilingual/cross-modal projectors, measure family closure
and false correspondence rates, then connect validated candidates to the merged
non-agentic warm-hydration / Lane 5 pathway.
