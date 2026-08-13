# Pass 215 — Iteration 3: Exact Quantization-Block Structure Attribution

## Purpose

Iteration 2 established the required negative baseline: feeding the authentic quantized tensor byte stream directly into the inherited Pass 212 affine/sparse codec admitted zero bytes. Iteration 3 does not change that instrument. It asks a narrower question: does the already-quantized GGUF storage contain exact reusable structure when interpreted according to its native block boundaries rather than as one undifferentiated byte stream?

The answer for the authenticated `stories15M-q4_0.gguf` workload is yes, but the structure is sharply localized.

## Frozen workload and inherited authority

```text
repo:     ggml-org/tiny-llamas
revision: main
file:     stories15M-q4_0.gguf
SHA-256:  6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04
```

Iteration 3 regenerates the Iteration 2 evidence root before measuring block structure. For the real workload it must reproduce:

```text
Iteration 2 Hash216:
0c18a5055b01bee0401d9ad0b3caba9c5d214d80a6dd809b190e106681b22e70

canonical quantized bytes: 18,335,232
Pass 212 admitted bytes:   0
```

The frozen Pass 214 profile is not edited.

## Exact block decomposition

The real workload contains 44 quantized tensors:

- 43 `Q4_0` tensors;
- 1 `Q8_0` tensor.

Iteration 3 contracts their exact stored geometry:

```text
Q4_0: 32 logical elements -> 18 stored bytes
       2 opaque scale bytes + 16 packed-code bytes

Q8_0: 32 logical elements -> 34 stored bytes
       2 opaque scale bytes + 32 signed-code storage bytes
```

The two scale bytes are never interpreted as a floating-point number. They remain exact opaque bits. Every block is split and rejoined byte-for-byte, and every dictionary candidate must decode to the original tensor SHA-256 before its size can be counted.

Total measured block geometry:

```text
quantized tensors:     44
quantization blocks:   762,624
raw quantized bytes:   18,335,232
scale bytes:            1,525,248
code bytes:            16,809,984
unsupported bytes:              0
opaque F32 excluded:       14,976
semantic exactness:          true
```

## Predeclared reversible candidates

Before the real measurement, Iteration 3 fixes three candidate representations:

1. `RAW_BLOCK_STREAM` — unchanged original tensor bytes.
2. `WHOLE_BLOCK_DICTIONARY_V1` — first-occurrence dictionary of complete native quantization blocks plus exact references.
3. `SPLIT_SCALE_CODE_DICTIONARY_V1` — independent first-occurrence dictionaries for exact scale bytes and packed-code blocks.

The dictionary header, reference-width rule, first-occurrence ordering, and raw-wins-ties selection rule are all fixed by the Iteration 3 contract. Losing candidate costs remain in evidence.

## Real result

```text
raw compared bytes:          18,335,232
selected reversible bytes:   11,686,284
exact byte reduction:         6,648,948
selected/raw exact:          324619 / 509312
reduction/raw exact:         184693 / 509312
source/selected exact:       509312 / 324619
```

For readability only, the exact fractions correspond to about a 36.26% byte reduction for this measured quantized-weight subset. This is an exact reversible dictionary representation result, not Pass 212 affine-generator admission and not a claim about arbitrary model weights.

Representation selection across the 44 tensors:

```text
RAW_BLOCK_STREAM:                 42 tensors
WHOLE_BLOCK_DICTIONARY_V1:         2 tensors
SPLIT_SCALE_CODE_DICTIONARY_V1:    0 tensors
```

## Where the gain exists

All measured reduction comes from two large non-transformer-block tensors.

### `token_embd.weight`

```text
storage type: Q4_0
source bytes: 5,184,000
blocks:          288,000
selected: WHOLE_BLOCK_DICTIONARY_V1
selected bytes: 2,895,809
gain bytes:     2,288,191

unique full blocks:              112,877
repeated full-block occurrences: 175,123
unique scale values:               7,936
repeated scale occurrences:      280,064
unique code blocks:               91,676
repeated code occurrences:       196,324
```

### `output.weight`

```text
storage type: Q8_0
source bytes: 9,792,000
blocks:          288,000
selected: WHOLE_BLOCK_DICTIONARY_V1
selected bytes: 5,431,243
gain bytes:     4,360,757

unique full blocks:              134,330
repeated full-block occurrences: 153,670
unique scale values:               4,561
repeated scale occurrences:      283,439
unique code blocks:              131,500
repeated code occurrences:       156,500
```

Whole-block dictionaries beat split dictionaries for both tensors, which means preserving the scale/code pairing contains slightly more reusable exact structure than separately indexing those fields.

## What happens inside the six transformer layers

The model has six `blk.N` transformer layers. Each contains seven measured Q4_0 tensors and exactly 559,872 quantized bytes.

For every transformer layer:

```text
selected representation: raw for all 7 tensors
selected gain:           0 bytes
exact code-block repeats: 0
exact full-block repeats: 0
```

Scale values do repeat substantially inside these tensors, but scale repetition alone is not sufficient to offset dictionary/reference overhead because the corresponding packed code blocks remain distinct. Therefore Iteration 3 does not claim block-level compression for the attention or feed-forward tensors.

This is an important boundary: the positive global result is not evidence that dense transformer layers are already reducible by simple repeated-weight dictionaries. It is evidence that the embedding/output surfaces of this particular model contain substantial exact repeated quantization blocks.

## Pass 212 remains negative on the decomposed streams

Separating the native fields does not create affine/sparse admission:

```text
scale stream bytes:                1,525,248
scale Pass 212 admitted bytes:             0

code stream bytes:                16,809,984
code Pass 212 admitted bytes:              0
```

The scale stream is smaller than one full 6,298,560-byte inherited hydration window and therefore remains conservative raw tail fallback. The code stream contains two complete hydration windows plus a tail; all remain Tier 3 raw fallback.

So two facts coexist without contradiction:

- Pass 212 affine/sparse generator incidence remains zero for the real weight bytes and their separated fields.
- A different, predeclared, exact native-block dictionary representation finds substantial repetition in two large tensors.

## Validation

First full hosted Iteration 3 run:

```text
workflow: Pass 215 Iteration 3 Quantization Block Structure
run:      31204252315
job:      92951335970
result:   success
tests:    21 passed
artifact: 9004066249
artifact SHA-256:
321b3907ccf65a2249dc1c0adbe6397d2c216eda4ffd17be5f970728dd330472
```

Iteration 3 evidence authority:

```text
Hash216:
61e301f728e426b46dbdd7c435c06b7c7f0065b177d62313152494467ed7d021

Hash72:
+XV/)UKf1oM2)Y>uURQQ?KG(KURR<*5vl2zFqc6Gj6)xNFx/yzsyd!R!HIBJ4dVkCMEAYui)
```

## Authority and claim boundary

Iteration 3 preserves:

```text
benchmark_authority_promoted: true
pass215_authorized: true
pass213_gates_preserved: true
runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false
```

It does not claim:

- canonical floating-point interpretation;
- dense forward replacement;
- exact transformer nonlinear operators;
- 50B desktop feasibility;
- arbitrary compression;
- Pass 212 generator admission for the real weights;
- that the dictionary representation is canonical runtime mutation authority.

## Next empirical target

Iteration 4 should move from exact stored-weight repetition to exact operator-aware execution structure. The strongest next comparison is to preserve these Iteration 2 and 3 baselines while building a deterministic integer/symbolic forward slice for one transformer layer: quantized matrix-vector operations, normalization/activation components only where exact semantics can be contracted, compiled-ROM/cache/continuation variants, and direct measurement of transition reuse versus dense integer reference execution.

The two large dictionary-positive tensors should remain separately accounted so their storage reuse cannot be mistaken for transformer-layer execution acceleration.
