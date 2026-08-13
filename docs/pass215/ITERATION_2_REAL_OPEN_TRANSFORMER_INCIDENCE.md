# Pass 215 Iteration 2 — Real Open-Transformer Container Incidence

## Purpose

Iteration 2 replaces the Iteration 1 transformer-shaped control with a real public quantized transformer artifact while preserving the frozen Pass 214 benchmark instrument and the Pass 213 mutation-admission boundary.

It answers one narrow empirical question: **do the exact bytes of an existing quantized transformer weight container naturally enter the inherited Pass 212 affine-generator/sparse-exception representation?**

It does not dequantize weights, reinterpret stored IEEE values as canonical floating-point numbers, replace transformer forward execution, or claim 50B desktop feasibility.

## Container ingestion

The Iteration 2 runtime supports:

- GGUF v2/v3 container metadata and tensor inventories;
- Safetensors exact header and tensor-range parsing;
- standard GGUF scalar, classic quantization, and K-quant byte geometries required by the contracted surface;
- exact tensor names, shapes, storage types, block geometry, offsets, lengths, and SHA-256 identities;
- fail-closed rejection of malformed ranges, overlaps, unsupported storage types, and inconsistent block geometry;
- opaque storage of floating tensor and metadata bit patterns without converting them to canonical numerical values.

Two measurement streams are produced from tensor payload bytes in physical container order:

1. **whole tensor storage stream** — all tensor payload bytes, including opaque float storage;
2. **canonical quantized/integer stream** — only quantized and integer tensor payload bytes.

Both are run through the unchanged Iteration 1 incidence layer and inherited Pass 212 encode/decode runtime. Complete 6,298,560-byte hydration windows must reconstruct byte-for-byte. An incomplete final window remains raw fallback and is never zero-padded to inflate admission incidence.

## Real workload

The predeclared external workload is:

```text
repository: ggml-org/tiny-llamas
revision:   main
file:       stories15M-q4_0.gguf
SHA-256:    6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04
```

The hosted workflow downloaded the artifact directly and verified this digest before parsing or measurement.

Observed container identity:

```text
format:             GGUF v3
architecture:       llama
file bytes:         19,077,344
tensor data start:     727,136
tensors:                    57
alignment:                   32
```

Tensor storage composition:

```text
Q4_0 tensors: 43
Q8_0 tensors:  1
F32 tensors:  13

tensor payload bytes:                   18,350,208
canonical quantized/integer bytes:       18,335,232
opaque float storage bytes:                  14,976
container/non-tensor bytes:                 727,136
canonical fraction of tensor bytes:        15916/15929
```

The 13 F32 tensors are hashed and inventoried as opaque stored bits. They are excluded from the canonical quantized stream and are not interpreted numerically.

## Empirical admission result

### Whole tensor-storage stream

```text
source bytes:                  18,350,208
complete hydration windows:             2
tail fallback bytes:            5,753,088
Tier 1 generator bytes:                 0
Tier 2 sparse-exception bytes:          0
Tier 3 raw-fallback bytes:     18,350,208
admitted bytes:                         0
admission incidence:                   0/1
codec payload bytes:           18,350,208
protected storage bytes:       18,453,888
source/protected ratio:             15929/16019
semantic exactness:                 true
```

### Canonical quantized/integer stream

```text
source bytes:                  18,335,232
complete hydration windows:             2
tail fallback bytes:            5,738,112
Tier 1 generator bytes:                 0
Tier 2 sparse-exception bytes:          0
Tier 3 raw-fallback bytes:     18,335,232
admitted bytes:                         0
admission incidence:                   0/1
codec payload bytes:           18,335,232
protected storage bytes:       18,438,912
source/protected ratio:               7958/8003
semantic exactness:                 true
```

The two complete hydration windows in each stream were tested by the inherited exact codec and fell to `RAW_PACKED_FALLBACK`. The remaining tail was conservatively raw by contract.

## Meaning of the result

This is a negative result for a specific hypothesis: **raw stored Q4_0/Q8_0 transformer weight bytes do not naturally look like the Pass 212 affine 9,720-leaf generator domain with sparse XOR exceptions.** Conventional weight quantization reduces precision/storage size, but it does not by itself imply low generator complexity under the HHS affine codec.

That result must not be generalized beyond the measurement performed. Iteration 2 did not test:

- block-aware symbolic decomposition of GGUF quantization records;
- repeated scale/min/codebook structure across quantization blocks;
- transformer operator graphs;
- exact nonlinear operator replacement;
- activation-state incidence;
- KV/cache/state continuation incidence;
- nearest-state delta reuse;
- cross-layer or cross-token reuse;
- compiled-ROM transition complexity;
- ingestion of a full unquantized 50B network.

Those are separate structures and require subsequent Pass 215 measurements under the already frozen comparison/ablation framework.

The zero-incidence result therefore narrows the 50B-on-desktop thesis: any substantial benefit cannot be justified by treating arbitrary raw quantized weight bytes as if they were automatically affine-generator states. It must arise from a more structured exact representation and/or from execution/state reuse, and that contribution must be measured separately.

## Evidence authority

Hosted successful run:

```text
Pass 215 Iteration 2 Open Transformer Container
run: 31201031243
cumulative tests: 14 passed
external SHA-256: verified
real GGUF generation: passed
independent evidence validation: passed
```

Evidence:

```text
Hash216:
0c18a5055b01bee0401d9ad0b3caba9c5d214d80a6dd809b190e106681b22e70

Hash72:
eazJ?HQncuTLTNwn9-UO!PSBI2I)GHgBuN/h75y2Iyi0Nkkd845iC+u/xb?o(CBRQ56DqKLz

artifact id:
9002815167

artifact SHA-256:
92e9b495453356b7ed1c033ce2a0a928bf8e9a8a4bf14b0d7829698efbe5875c
```

The first real-run attempt (`31200949057`) failed before container parsing because the new public CLI omitted the repository-root bootstrap used by Iteration 1. That defect was repaired forward in commit `a07c958ebf589978a752080f8c317fe9f029894f`; the external model, expected digest, benchmark profile, and measurement rules were not changed.

## Authority boundary

Iteration 2 preserves:

```text
benchmark_authority_promoted: true
pass215_authorized: true
pass213_gates_preserved: true

runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false
```

The empirical result can inform later Pass 215 design and Pass 213 admission decisions. It cannot promote itself into runtime mutation authority.

## Next empirical boundary

The next iteration should attribute *why* the raw quantized stream falls to fallback without changing the frozen benchmark instrument. A compatible next layer is quantization-block-aware symbolic ingestion and per-tensor/per-layer incidence attribution: preserve each GGUF quantization block exactly, separate scale/metadata fields from packed quantized codes, measure repeated/block-generator structure and residual cost, and compare that structured representation against the raw-byte baseline established here.
