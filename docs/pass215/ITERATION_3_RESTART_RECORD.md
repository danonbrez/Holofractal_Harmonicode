# Pass 215 Iteration 3 Restart Record

## Restart identity

- Pass: 215
- Iteration: 3
- branch: `agent/pass215-transformer-ingestion-benchmark`
- merge target: `main`
- draft PR: `#172`
- inherited base main: `a4b7f6cf4da9111b036b6d4d93ea2d7b50e3eb2a`
- Iteration 2 validated head: `cbb477de7acf7461916f13ca3d670b511cb483c2`
- Iteration 2 validated tree: `4803cd565e1b97990706b183fd18a34fa03a710f`
- Iteration 3 implementation/documentation head before this restart record: `d64c78794ba90edf704d8c95526186bae6706133`
- Iteration 3 implementation/documentation tree: `72e073c85618ff7686ed19c5b78a90ff2df18e0a`
- this restart-record commit becomes the next branch head; resolve it directly from the branch ref.

## Frozen inherited authority

```text
PASS214_AUTHORITY_ROOT_HASH216
c1d7875acd45f02da75101f5953541b6e1ce8ea3bb2cac39645004ab2509aeb8

PASS215_BENCHMARK_PROFILE_ROOT_HASH216
a3079f0f0b94d9fb485970662455482d4dab86e01802ca5bfdef6af3fbb6d85e

PASS213_GATE_PRESERVATION_ROOT_HASH216
214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092

FROZEN_PROFILE_GIT_BLOB_SHA1
b458d674a75a4cfc64a32b9203dd693e3603576e
```

The Pass 214 benchmark profile is byte-frozen. Iteration 3 remains a measurement and representation-attribution layer only. It does not promote runtime mutation or canonical mutation authority.

## Files added by Iteration 3

- `contracts/pass215/PASS_215_ITERATION_3_CONTRACT.json`
- `hhs_backend/runtime/hhs_pass215_iteration3_quant_block_structure_v1.py`
- `tools/pass215_iteration3_quant_block_structure.py`
- `tests/test_hhs_pass215_iteration3_quant_block_structure_v1.py`
- `scripts/run_pass215_iteration3_validation.sh`
- `.github/workflows/pass215-iteration3-quant-block-structure.yml`
- `evidence/pass215/PASS_215_ITERATION_3_IMPLEMENTATION_RECORD.json`
- `docs/pass215/ITERATION_3_QUANT_BLOCK_STRUCTURE.md`
- `docs/pass215/ITERATION_3_RESTART_RECORD.md`

## Implemented capability

- exact Q4_0 and Q8_0 native quantization-block geometry;
- byte-exact split of each block into opaque scale bits and packed code bytes;
- byte-exact block reconstruction;
- deterministic first-occurrence fixed-width dictionaries;
- predeclared candidate set:
  - `RAW_BLOCK_STREAM`;
  - `WHOLE_BLOCK_DICTIONARY_V1`;
  - `SPLIT_SCALE_CODE_DICTIONARY_V1`;
- explicit dictionary header/reference accounting;
- raw-wins-ties selection;
- exact repeat accounting for scales, code blocks, and whole blocks;
- per-tensor, per-layer, per-storage-type, and global structure attribution;
- unsupported quantized-layout raw passthrough with no structure claim;
- opaque float storage exclusion;
- inherited Pass 212 measurement on decomposed scale and code streams;
- deterministic Hash216 evidence and Hash72 receipt;
- public CLI generation and independent evidence validation;
- cumulative Iterations 1–3 hosted gate.

## Real workload

```text
repo:     ggml-org/tiny-llamas
revision: main
file:     stories15M-q4_0.gguf
SHA-256:  6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04
```

Iteration 3 regenerates and verifies the Iteration 2 baseline before its own measurement:

```text
Iteration 2 Hash216:
0c18a5055b01bee0401d9ad0b3caba9c5d214d80a6dd809b190e106681b22e70

Iteration 2 canonical quantized bytes: 18,335,232
Iteration 2 Pass 212 admitted bytes:  0
```

## Exact Iteration 3 result

```text
supported quantized tensors:       44
quantization blocks:          762,624
raw compared bytes:        18,335,232
selected reversible bytes: 11,686,284
exact gain bytes:           6,648,948
scale stream bytes:         1,525,248
code stream bytes:         16,809,984
unsupported passthrough:            0
opaque F32 bytes excluded:      14,976
semantic exactness:                true
```

Exact ratios:

```text
selected/raw:     324619 / 509312
gain/raw:         184693 / 509312
source/selected:  509312 / 324619
```

Representation selections:

```text
RAW_BLOCK_STREAM:                 42 tensors
WHOLE_BLOCK_DICTIONARY_V1:         2 tensors
SPLIT_SCALE_CODE_DICTIONARY_V1:    0 tensors
```

## Positive structure is localized

### token_embd.weight

```text
storage: Q4_0
source bytes: 5,184,000
blocks:          288,000
selected: WHOLE_BLOCK_DICTIONARY_V1
selected bytes: 2,895,809
gain bytes:     2,288,191
unique full blocks:              112,877
repeated full-block occurrences: 175,123
unique scales:                     7,936
repeated scale occurrences:      280,064
unique code blocks:               91,676
repeated code occurrences:       196,324
```

### output.weight

```text
storage: Q8_0
source bytes: 9,792,000
blocks:          288,000
selected: WHOLE_BLOCK_DICTIONARY_V1
selected bytes: 5,431,243
gain bytes:     4,360,757
unique full blocks:              134,330
repeated full-block occurrences: 153,670
unique scales:                     4,561
repeated scale occurrences:      283,439
unique code blocks:              131,500
repeated code occurrences:       156,500
```

## Transformer-layer boundary

The six `blk.N` transformer layers contain 42 Q4_0 tensors total, seven per layer. Every one remains selected as raw storage.

For every transformer layer:

```text
source bytes:                 559,872
selected gain bytes:               0
exact code-block repeats:           0
exact whole-block repeats:          0
```

Scale bits do repeat, but paired packed code blocks remain distinct enough that neither predeclared dictionary candidate beats raw storage. Therefore Iteration 3 does not claim simple dictionary compression of the attention/feed-forward tensor weights.

## Pass 212 decomposition result

```text
scale stream bytes:             1,525,248
scale Pass 212 admitted bytes:          0

code stream bytes:             16,809,984
code Pass 212 admitted bytes:           0
```

Pass 212 affine/sparse generator incidence therefore remains zero for the real weights and their decomposed fields. The positive result is a separate exact native-block dictionary representation measured under the predeclared Iteration 3 candidate set.

## Evidence authority

```text
ITERATION_3_EVIDENCE_ROOT_HASH216
61e301f728e426b46dbdd7c435c06b7c7f0065b177d62313152494467ed7d021

ITERATION_3_RECEIPT_HASH72
+XV/)UKf1oM2)Y>uURQQ?KG(KURR<*5vl2zFqc6Gj6)xNFx/yzsyd!R!HIBJ4dVkCMEAYui)
```

The root and receipt regenerated identically on the initial implementation head and the documentation/evidence head.

## Validation done

Initial implementation gate:

```text
run: 31204252315
job: 92951335970
result: success
21 cumulative tests passed
artifact id: 9004066249
artifact SHA-256: 321b3907ccf65a2249dc1c0adbe6397d2c216eda4ffd17be5f970728dd330472
```

Repository-visible documentation/evidence gate:

```text
head: d64c78794ba90edf704d8c95526186bae6706133
tree: 72e073c85618ff7686ed19c5b78a90ff2df18e0a
run: 31204486428
job: 92952082730
result: success
21 cumulative tests passed
artifact id: 9004156883
artifact SHA-256: 1d95a43cedc2069b6e919a661c306a4156ac3ece714a0b80aa728844dd87c90c
```

The sole pytest warning is the repository-level unknown `asyncio_mode` configuration option and is outside the Iteration 3 surface.

## Authority / claim state

```text
benchmark_authority_promoted: true
pass215_authorized: true
pass213_gates_preserved: true
runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false

block_dictionary_compression_claimed_for_measured_weight_subset: true
pass212_generator_admission_claimed: false
dictionary_representation_is_runtime_authority: false
canonical_float_interpretation_performed: false
dense_forward_replaced: false
exact_nonlinear_transformer_operators_implemented: false
fifty_billion_desktop_feasibility_claimed: false
arbitrary_compression_claimed: false
```

## Remaining at this checkpoint

1. Run the dedicated Iteration 3 gate once on the restart-record branch head.
2. Require the same authenticated workload, 21 cumulative tests, exact 6,648,948-byte gain, Hash216 root, and Hash72 receipt.
3. Update draft PR #172 metadata with the final Iteration 3 head/tree/run/artifact.
4. Keep PR #172 draft and unmerged while Pass 215 continues.

## Next action after closure

Begin Iteration 4 with operator-aware execution structure rather than another storage-only representation. Preserve the Iteration 2 zero-incidence raw baseline and the Iteration 3 localized dictionary baseline while constructing a deterministic integer/symbolic forward slice for one transformer layer. Measure quantized matrix-vector execution, exact contracted normalization/activation components where possible, compiled-ROM/cache/continuation variants, transition reuse, replay equality, and direct work counts against a dense integer reference. Keep embedding/output storage reuse separately accounted so it cannot be mistaken for transformer-layer execution acceleration.
