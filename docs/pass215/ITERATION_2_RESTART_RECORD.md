# Pass 215 Iteration 2 Restart Record

## Restart identity

- Pass: 215
- Iteration: 2
- branch: `agent/pass215-transformer-ingestion-benchmark`
- merge target: `main`
- draft PR: `#172`
- inherited base main: `a4b7f6cf4da9111b036b6d4d93ea2d7b50e3eb2a`
- Iteration 1 validated head: `b26780c495288a2dcf4a27c89cf1fbddec0ebc4e`
- Iteration 2 real-model repair head: `a07c958ebf589978a752080f8c317fe9f029894f`
- repository-visible implementation/evidence parent before this restart record: `11b71a63ae44d1e7d955604644f8ecbf27198a88`
- parent tree: `356fda12cb85aec6bdbd3d9e37da39fa649fc27d`
- this restart-record commit becomes the next branch head; resolve it directly from the branch ref rather than relying on chat state.

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

The benchmark profile has not been edited. Pass 215 remains a measurement/execution pass; it cannot promote runtime mutation or canonical mutation authority.

## Files added or modified by Iteration 2

- `contracts/pass215/PASS_215_ITERATION_2_CONTRACT.json`
- `hhs_backend/runtime/hhs_pass215_iteration2_open_transformer_container_v1.py`
- `tools/pass215_iteration2_open_transformer_container.py`
- `tests/test_hhs_pass215_iteration2_open_transformer_container_v1.py`
- `scripts/run_pass215_iteration2_validation.sh`
- `.github/workflows/pass215-iteration2-open-transformer-container.yml`
- `evidence/pass215/PASS_215_ITERATION_2_IMPLEMENTATION_RECORD.json`
- `docs/pass215/ITERATION_2_REAL_OPEN_TRANSFORMER_INCIDENCE.md`
- `docs/pass215/ITERATION_2_RESTART_RECORD.md`

## Implemented capability

- exact Safetensors container inventory;
- exact GGUF v2/v3 inventory;
- contracted classic and K-quant GGUF byte geometry;
- exact tensor storage ranges and hashes;
- float-typed payloads retained only as opaque stored bits;
- whole tensor-storage incidence measurement;
- separate canonical quantized/integer-only incidence measurement;
- exact inherited Pass 212 encode/decode validation for complete hydration windows;
- conservative raw fallback for final incomplete windows;
- Hash216 evidence and Hash72 receipt;
- public CLI generation and independent validation;
- real public GGUF workload in CI.

## Repair-forward record

Initial real-model run:

```text
run: 31200949057
result: failed
```

All cumulative tests and the external model SHA-256 verification had already passed. Failure occurred before container parsing because direct CLI execution did not add the repository root to `sys.path`.

Repair:

```text
commit: a07c958ebf589978a752080f8c317fe9f029894f
```

The CLI now uses the same repository-root bootstrap as the proven Iteration 1 CLI. No benchmark rule, external workload, expected digest, or frozen profile was changed.

## Validated real workload

```text
repo:     ggml-org/tiny-llamas
revision: main
file:     stories15M-q4_0.gguf
SHA-256:  6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04
```

Successful evidence run:

```text
run: 31201031243
result: success
14 cumulative tests passed
external digest verified
public CLI passed
independent evidence validation passed
artifact id: 9002815167
artifact SHA-256: 92e9b495453356b7ed1c033ce2a0a928bf8e9a8a4bf14b0d7829698efbe5875c
```

## Real-model result

```text
GGUF version:                         3
architecture:                     llama
tensors:                              57
file bytes:                   19,077,344
tensor payload bytes:         18,350,208
canonical quantized bytes:     18,335,232
opaque F32 storage bytes:          14,976

whole storage Tier 1 bytes:              0
whole storage Tier 2 bytes:              0
whole storage Tier 3 bytes:     18,350,208
whole storage incidence:               0/1
whole protected bytes:          18,453,888

canonical Tier 1 bytes:                  0
canonical Tier 2 bytes:                  0
canonical Tier 3 bytes:         18,335,232
canonical incidence:                   0/1
canonical protected bytes:      18,438,912
```

Evidence authority:

```text
Hash216
0c18a5055b01bee0401d9ad0b3caba9c5d214d80a6dd809b190e106681b22e70

Hash72
eazJ?HQncuTLTNwn9-UO!PSBI2I)GHgBuN/h75y2Iyi0Nkkd845iC+u/xb?o(CBRQ56DqKLz
```

## Claim state

```text
real_open_transformer_measured: true
canonical_quantized_subset_bit_exact_reproduction: true
full_network_canonical_reproduction: false
canonical_float_interpretation_performed: false
fifty_billion_desktop_feasibility_claimed: false
dense_forward_replaced: false
exact_nonlinear_transformer_operators_implemented: false
arbitrary_compression_claimed: false

benchmark_authority_promoted: true
pass215_authorized: true
pass213_gates_preserved: true
runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false
```

## Interpretation preserved for restart

Iteration 2 establishes a zero-incidence baseline for the raw stored quantized-weight byte stream under the inherited Pass 212 affine/sparse codec. Do not reinterpret this as successful model compression and do not reinterpret it as a general failure of HHS transformer acceleration. It specifically rules out treating ordinary Q4_0/Q8_0 storage bytes as if quantization alone placed them in the affine generator domain.

Subsequent work must attribute structure without modifying the frozen Pass 214 instrument. The next compatible target is exact block-aware quantized ingestion: separate each GGUF block's scale/metadata and packed codes, preserve a reversible mapping to the original bytes, measure repeated generator structure/residual complexity per tensor/layer, and compare it against this raw-byte fallback baseline. Activation/transition/operator-graph measurements remain separate future experiments.

## Validation done / remaining

Done:

- Iteration 1 dependency inheritance;
- Iteration 2 fixture tests;
- Safetensors parser tests;
- GGUF parser tests;
- malformed and unsupported-type negative tests;
- no-float evidence test;
- frozen-profile blob check;
- real external GGUF SHA-256 check;
- real GGUF incidence execution;
- evidence regeneration validation;
- implementation/evidence documentation committed.

Remaining at this checkpoint:

1. Run the dedicated Iteration 2 workflow on the final documentation/restart-record branch head.
2. Confirm exact-head cumulative validation and real-model evidence remain identical.
3. Update draft PR #172 metadata with the final head, run, evidence root, receipt, and zero-incidence interpretation.
4. Keep PR #172 draft for the next Pass 215 iteration unless explicitly instructed to close/merge.

## Next action

Begin Iteration 3 only after the final exact-head Iteration 2 gate is green. Iteration 3 should implement exact reversible quantization-block decomposition and structure attribution against the frozen raw-weight baseline, not alter Pass 214's benchmark profile or claim canonical mutation authority.
