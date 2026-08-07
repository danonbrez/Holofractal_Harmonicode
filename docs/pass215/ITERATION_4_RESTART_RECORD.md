# Pass 215 Iteration 4 — Restart Record

## Restart identity

This file is the final planned Iteration 4 repository source mutation. The registered terminal authority workflow must validate the exact commit containing this record before Iteration 4 is treated as repository-frozen.

```text
repository: danonbrez/Holofractal_Harmonicode
branch: agent/pass215-transformer-ingestion-benchmark
pull request: #172 (draft)
merge target: main
base main inherited by Pass 215 branch:
a4b7f6cf4da9111b036b6d4d93ea2d7b50e3eb2a

parent before restart record:
fdd2258fc103ee09685234b8c9f59c35ff9fd9cf
parent tree:
fbbcffd49651595418752a1b3842c699eb4c0e50
```

## Frozen authority inputs

```text
Pass 214 authority Hash216:
c1d7875acd45f02da75101f5953541b6e1ce8ea3bb2cac39645004ab2509aeb8

Pass 215 benchmark-profile Hash216:
a3079f0f0b94d9fb485970662455482d4dab86e01802ca5bfdef6af3fbb6d85e

Pass 213 gate-preservation Hash216:
214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092

frozen Pass 215 profile Git blob:
b458d674a75a4cfc64a32b9203dd693e3603576e

Iteration 4 primitive-work accounting addendum Git blob:
0a2f1448f565fb3eebfb50845c44404b68e93b8b

Iteration 4 comparison-mapping addendum Git blob:
17fc5927c96f944d89a9e06cc2a684ae47e97c56
```

## Inherited empirical controls

Iteration 2 remains the authenticated raw-storage control:

```text
real evidence root:
0c18a5055b01bee0401d9ad0b3caba9c5d214d80a6dd809b190e106681b22e70
canonical quantized/integer bytes: 18,335,232
Pass 212 admission: 0/1
```

Iteration 3 remains the storage-structure control:

```text
real evidence root:
61e301f728e426b46dbdd7c435c06b7c7f0065b177d62313152494467ed7d021
selected reversible bytes: 11,686,284
selected gain bytes: 6,648,948
actual transformer-layer dictionary gain bytes: 0
```

The embedding/output dictionary gain is not counted as Iteration 4 transformer execution gain.

## Iteration 4 implementation surface

Primary files added or changed by this iteration:

```text
contracts/pass215/PASS_215_ITERATION_4_CONTRACT.json
contracts/pass215/PASS_215_ITERATION_4_EXECUTED_WORK_ACCOUNTING_ADDENDUM.json
contracts/pass215/PASS_215_ITERATION_4_COMPARISON_MAPPING_ADDENDUM.json

hhs_backend/runtime/hhs_pass215_iteration4_exact_linear_execution_v1.py
hhs_backend/runtime/hhs_pass215_iteration4_exact_linear_execution_v2.py
hhs_backend/runtime/hhs_pass215_iteration4_exact_linear_execution_v3.py
hhs_backend/runtime/hhs_pass215_iteration4_exact_linear_execution_v4.py

tools/pass215_iteration4_exact_linear_execution.py
tools/pass215_iteration4_exact_linear_execution_v2.py
tools/pass215_iteration4_exact_linear_execution_v3.py

tests/test_hhs_pass215_iteration4_exact_linear_execution_v1.py
tests/test_hhs_pass215_iteration4_primitive_work_accounting_v2.py
tests/test_hhs_pass215_iteration4_comparison_mapping_v3.py

scripts/run_pass215_iteration4_validation.sh
scripts/run_pass215_iteration4_primitive_work_validation.sh
scripts/run_pass215_iteration4_comparison_authority_validation.sh

.github/workflows/pass215-iteration4-exact-linear-execution.yml
.github/workflows/pass215-iteration4-primitive-work-authority.yml
.github/workflows/pass215-iteration4-comparison-authority.yml

docs/pass215/ITERATION_4_EXACT_LINEAR_EXECUTION.md
evidence/pass215/PASS_215_ITERATION_4_IMPLEMENTATION_RECORD.json
docs/pass215/ITERATION_4_RESTART_RECORD.md
```

The standalone `pass215-iteration4-comparison-authority.yml` source is retained, but GitHub did not register the new feature-branch-only workflow for execution. The already-registered `pass215-iteration4-primitive-work-authority.yml` was therefore repair-forwarded to carry the identical terminal v4 comparison-authority checks. This routing change did not alter the execution contract, candidates, deterministic inputs, accounting addenda, source weights, or required computation root.

## Authenticated real workload

```text
repo: ggml-org/tiny-llamas
revision: main
file: stories15M-q4_0.gguf
SHA-256:
6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04
GGUF version: 3
architecture: llama
file bytes: 19,077,344
container tensors: 57
```

Iteration 4 targets the seven Q4_0 linear tensors of `blk.0` only.

```text
operator count: 7
source tensor bytes: 559,872
Q4_0 blocks: 31,104
logical weights: 995,328
```

## Exact execution result

Terminal computation identity:

```text
suite output Hash216:
14de39b3b326eb64bbac5d8be829c289c4a5e1f39b842bfdba59b46fea2c9acb

terminal evidence Hash216:
0462738157042bbd2903ed666a3e05dbc1e27c8a43ea5d2544de9b0c174f87bf

terminal Hash72 receipt:
2SrZvFdR/*41!b++dH9qxM1IrUZMuwuRZmpNw4yl8>QYI(LA9B65A<auqlwyWoi97onfMeMc
```

Exact primitive work:

```text
dense exact rational:   3,014,112
Q4_0 factored exact:    2,049,888
work avoided:             964,224
exact total-work ratio: 31,397 / 21,353

rational scale multiplications:
  dense:    995,328
  factored:  31,104
  avoided:  964,224
  ratio:       32 / 1

single-coordinate continuation: 11,911
single full recompute:        2,049,888
exact full/continuation: 2,049,888 / 11,911

four-coordinate continuation: 47,644
four-coordinate full:      2,049,888
exact full/continuation: 512,472 / 11,911
```

The 32:1 result is specifically the rational scale-multiplication count induced by the 32-element Q4_0 block. It is not the total primitive-work ratio.

## Cache and recovery result

```text
exact repetition primitive work: 7
interruption recovery primitive work: 14
checkpoint bytes: 136,052
checkpoint SHA-256:
558230ce4651c9dde2a0f1d5c0f67f1bc8f6896a81bed4f793029856eb590628
checkpoint Hash216:
41dba751838bb27503d4579e1c6abae58318fc23b517f4c1cce0e6a1f0be04c8
restored entries: 7
semantic compare governance count: 7
```

## Frozen comparison result

```text
dense_reference
  -> aggregate_execution.dense_reference_work
  -> 3,014,112

exact_integer_reference
  -> aggregate_execution.factored_reference_work
  -> 2,049,888

pass213_compiled_rom_only
  -> warm descriptor benchmark analog
  -> 2,049,888
  -> runtime authority false

compiled_rom_plus_cache_layers
  -> exact repetition
  -> 7
  -> runtime authority false

compiled_rom_plus_continuation_delta
  -> single-region mutation
  -> 11,911
  -> runtime authority false

compiled_rom_plus_multimodal_ml
  -> NOT_APPLICABLE

complete_inherited_hhs_stack
  -> PARTIAL_ITERATION4_SUBSET_ONLY

complete_stack_with_ablations
  -> EXECUTED_ITERATION4_SUBSET_ABLATIONS
```

All eight frozen comparison slots are explicit.

## Frozen optimization / stage dispositions

- 29 frozen optimization classes have explicit dispositions.
- A0 through A9 are all present.
- A0/A1 dense/factored reference paths executed.
- A2 descriptor/cache executed.
- A3 single/multi continuation executed.
- A4 explicitly remains a partial Pass 215 subset.
- A5 ablations executed.
- A6 adverse/no-reuse executed.
- A7 interruption recovery executed.
- A8 internal evidence remains `READY_FOR_REQUIRED_EXTERNAL_CROSS_PROCESS_CI_REPLAY`; the separately retained external CI record proves process A/B replay succeeded.
- A9 accelerator path is not applicable to Iteration 4's CPU reference scope.

## Validation performed

### First green execution — retained historical evidence

```text
run: 31221256596
head: 4cfb8241edd81dd773cb939e1e249d0e4bd8b449
artifact: 9010454608
artifact SHA-256:
62435438054ad16b505a7ed99f58658852737515a3065b6f13c393ed67ff00f9
```

Execution/output correctness passed. The aggregate work formula was later superseded because it included capacity/coverage counters and a duplicate delta attribution alias.

### Primitive-work authority — retained historical evidence

```text
run: 31221568421
head: e2ec4ae66df6f0c28f56df996580e4ee787eedeb
artifact: 9010567877
artifact SHA-256:
3fbc59d6daa3fd38d2a95025438351442332442512128ecf87d4f44323bb50c4
```

Primitive work passed. Its comparison projection was later superseded because `dense_reference` pointed at the cold compiled-descriptor work record instead of the independently executed dense exact reference.

### Terminal comparison authority — completed before closure-record commits

```text
workflow: Pass 215 Iteration 4 Primitive Work Authority
run: 31222181816
job: 93008912750
head: 1bc8b04dd47f702e3bd4b9bc498961dd0b687415
tree: cf87c39a74a1356bade7e745863d994a16047d08
result: success
artifact: 9010778255
artifact SHA-256:
d69d05ab3f385f5f04dfe14dc45a45a718cc2f56356123046ec1291e37c83ddf
```

Cumulative tests:

```text
21 inherited Iterations 1-3
 8 Iteration 4 exact execution
 3 primitive-work accounting
 3 comparison mapping
--
35 passed
```

The terminal run also proved:

- authenticated model digest matched;
- process A evidence validated independently;
- independent process B evidence validated independently;
- complete process A/B evidence objects were identical;
- cross-process validation bound the same evidence root, suite root, and receipt;
- no JSON float numbers were present;
- all frozen comparison slots were present;
- all 29 optimization dispositions were present;
- all A0-A9 stages were present;
- claim and authority boundaries were false where required.

## Environment state

The authoritative hosted validation environment was:

```text
GitHub Actions
Ubuntu 24.04
Python 3.12
PYTHONHASHSEED=0
PYTHONDONTWRITEBYTECODE=1
CPU reference scope
public authenticated GGUF downloaded during the workflow
```

No persistent local model file or runtime mutation state is required to restart this work. The authenticated model is re-downloaded and SHA-256 checked by the workflow.

## Authority state

```text
benchmark_authority_promoted: true
pass215_authorized: true
pass213_gates_preserved: true
runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false
```

Iteration 4 does not perform Pass 213 operational compiled-ROM mutation.

## Explicit non-claims

```text
full_transformer_layer_forward_executed: false
rmsnorm_execution_claimed: false
attention_softmax_execution_claimed: false
silu_execution_claimed: false
canonical_float_interpretation_performed: false
dense_forward_replaced: false
exact_nonlinear_transformer_operators_implemented: false
fifty_billion_desktop_feasibility_claimed: false
arbitrary_compression_claimed: false
```

## Validation remaining after this commit

Exactly one closure condition remains after this restart record is committed:

1. the registered `Pass 215 Iteration 4 Primitive Work Authority` workflow must execute successfully on the exact commit containing this restart record;
2. that exact-head run must reproduce the same suite root, terminal evidence root, receipt, primitive work counts, cross-process replay, frozen comparison bindings, and authority boundaries;
3. no repository source file may change after that successful exact-head run for Iteration 4 closure;
4. PR #172 metadata may then be updated without changing the branch head.

## Next action after exact-head closure

Proceed to Pass 215 Iteration 5 on the same cumulative branch/PR. The next technical boundary is the exact nonlinear/symbolic substrate required to compose the validated linear slices into a real transformer block: RMSNorm square/square-root normalization, RoPE phase rotation, attention scaling plus softmax/exponential normalization, and SiLU/sigmoid. Any approximation must be explicitly contracted and measured; floating-point canonical authority must not be introduced implicitly.
