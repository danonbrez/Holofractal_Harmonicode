# Pass 215 Iteration 4 — Exact Q4_0 Linear Execution and Transition Complexity

## Status

Iteration 4 has completed its implementation and terminal comparison-authority validation on the authenticated real GGUF workload. It is an execution benchmark layer, not runtime/canonical mutation authority and not a complete transformer-layer forward.

The iteration executes the seven Q4_0 linear weight tensors of `blk.0` through two exact, independently comparable execution paths:

1. `DENSE_EXACT_RATIONAL_REFERENCE_V1`
2. `Q4_0_FACTORED_EXACT_BLOCK_KERNEL_V1`

It then measures immutable block-descriptor reuse, exact input/output cache replay, exact sparse linear continuation, interruption recovery, and independent cross-process replay. Every comparison remains bound to the frozen Pass 215 benchmark profile.

## Frozen inherited authority

- Pass 214 authority root: `c1d7875acd45f02da75101f5953541b6e1ce8ea3bb2cac39645004ab2509aeb8`
- Pass 215 benchmark profile root: `a3079f0f0b94d9fb485970662455482d4dab86e01802ca5bfdef6af3fbb6d85e`
- Pass 213 gate-preservation root: `214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092`
- frozen profile Git blob: `b458d674a75a4cfc64a32b9203dd693e3603576e`
- Iteration 2 evidence root: `0c18a5055b01bee0401d9ad0b3caba9c5d214d80a6dd809b190e106681b22e70`
- Iteration 3 evidence root: `61e301f728e426b46dbdd7c435c06b7c7f0065b177d62313152494467ed7d021`

The Iteration 2 control remains `0/1` Pass 212 admission for the `18,335,232` canonical quantized/integer bytes. The Iteration 3 control remains `0` dictionary-gain bytes for all 42 actual transformer-layer tensors. Iteration 3's embedding/output storage gain is explicitly excluded from Iteration 4 execution gain.

## Authenticated real workload

```text
repository: ggml-org/tiny-llamas
revision:   main
file:       stories15M-q4_0.gguf
GGUF:       version 3
architecture: llama
file bytes: 19,077,344
tensors:    57
SHA-256:    6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04
```

### Target operator suite

The benchmark executes these seven independent linear slices from `blk.0`:

| Tensor | GGML shape `[ne0, ne1]` | Source bytes | Q4 blocks | Logical weights |
|---|---:|---:|---:|---:|
| `blk.0.attn_q.weight` | `[288,288]` | 46,656 | 2,592 | 82,944 |
| `blk.0.attn_k.weight` | `[288,288]` | 46,656 | 2,592 | 82,944 |
| `blk.0.attn_v.weight` | `[288,288]` | 46,656 | 2,592 | 82,944 |
| `blk.0.attn_output.weight` | `[288,288]` | 46,656 | 2,592 | 82,944 |
| `blk.0.ffn_gate.weight` | `[288,768]` | 124,416 | 6,912 | 221,184 |
| `blk.0.ffn_up.weight` | `[288,768]` | 124,416 | 6,912 | 221,184 |
| `blk.0.ffn_down.weight` | `[768,288]` | 124,416 | 6,912 | 221,184 |
| **Total** | — | **559,872** | **31,104** | **995,328** |

These are not composed into a complete transformer layer in Iteration 4. RMSNorm, RoPE/attention composition, softmax, SiLU, residual composition, and final layer semantics remain outside the execution claim.

## Exact Q4_0 semantics

Iteration 4 contracts the native Q4_0 storage geometry directly:

```text
32 logical weights -> 18 bytes
2 bytes: IEEE-754 binary16 scale storage
16 bytes: packed 4-bit codes
```

For packed byte `j`:

- low nibble is logical element `j`, positions `0..15`;
- high nibble is logical element `j+16`, positions `16..31`;
- signed quant integer is `nibble - 8`;
- exact weight is `exact_binary16_scale_rational * quant_integer`.

The binary16 scale is never converted through Python floating point. Sign, exponent, and significand bits are decoded with integer operations into a reduced exact rational. NaN and infinity scale patterns fail closed. Canonical evidence contains no JSON floating-point numbers.

## Exact dense versus block-factored execution

The dense reference conceptually applies the exact rational block scale to every logical weight before accumulation. The factored kernel performs the same 32 integer products and integer additions inside each Q4 block, then applies the exact block scale once to the integer dot product.

All seven real operator outputs match exactly.

### Primitive executed work

The final accounting is bound by:

- work-accounting addendum Git blob: `0a2f1448f565fb3eebfb50845c44404b68e93b8b`
- comparison-mapping addendum Git blob: `17fc5927c96f944d89a9e06cc2a684ae47e97c56`

Primitive execution excludes capacity/population fields and attribution aliases while retaining every raw counter in evidence.

```text
dense exact rational primitive work:  3,014,112
factored exact primitive work:         2,049,888
primitive work avoided:                  964,224
exact dense/factored work ratio:     31,397 / 21,353
```

This is a total primitive-work comparison, not a claim of a 32x total execution acceleration.

### Exact rational scale-multiplication decomposition

```text
dense exact rational scale multiplications: 995,328
factored exact scale multiplications:         31,104
scale multiplications avoided:               964,224
exact ratio:                                    32 / 1
```

The 32:1 ratio is specific to the rational scale-multiplication operation induced by the 32-value Q4_0 block structure.

## Exact continuation / delta execution

The linear continuation candidate is strictly:

```text
child_output = parent_output + W * delta_input
```

It is permitted only from a validated exact parent output and exact source-bound descriptor. Each continuation output is compared against a complete factored recomputation.

### One-coordinate mutation

The deterministic mutation changes one coordinate at `input_width // 3` by `+7`.

```text
continuation primitive work: 11,911
full factored recomputation: 2,049,888
exact full/continuation ratio: 2,049,888 / 11,911
semantic exactness: true
```

### Four-coordinate mutation

The deterministic mutation changes indices `0`, `width//4`, `width//2`, and `width-1` by `+3,-5,+7,-11`.

```text
continuation primitive work: 47,644
full factored recomputation: 2,049,888
exact full/continuation ratio: 512,472 / 11,911
semantic exactness: true
```

The continuation ratios are usage-pattern-specific exact work-count results. They are not generalized model-wide speedup claims.

## Frozen workload-mode results

Primitive work totals retained by mode:

```text
cold:                    2,112,096
warm:                    2,049,888
exact_repetition:                7
shared_structure:        2,049,888
single_region_mutation:     11,911
multi_region_mutation:      47,644
novel_content:           2,049,888
contradictory_content:   2,049,888
no_reuse_control:        2,049,888
interruption_recovery:          14
cross_process_replay:            0  # external validation work is separate governance evidence
```

`exact_repetition = 7` means one exact output-cache hit for each of the seven operators. It does not imply zero governance cost outside the execution primitive axis.

## Interruption recovery

The checkpoint is source-bound and descriptor-bound and carries the validated input/output cache state for all seven operators.

```text
checkpoint bytes: 136,052
checkpoint SHA-256:
558230ce4651c9dde2a0f1d5c0f67f1bc8f6896a81bed4f793029856eb590628
checkpoint Hash216:
41dba751838bb27503d4579e1c6abae58318fc23b517f4c1cce0e6a1f0be04c8
restored entries: 7
primitive recovery work: 14
semantic exactness: true
```

The primitive `14` consists of seven exact output-cache hits plus seven recovery work units. Seven semantic comparisons remain separately reported on the governance axis.

## Frozen Pass 215 comparison bindings

The terminal evidence repairs and locks the comparison projection so the dense reference cannot be confused with the cold compiled-descriptor path.

```text
dense_reference
  source: aggregate_execution.dense_reference_work
  primitive work: 3,014,112

exact_integer_reference
  source: aggregate_execution.factored_reference_work
  primitive work: 2,049,888

pass213_compiled_rom_only
  source: frozen_workload_modes.warm.work
  primitive work: 2,049,888
  runtime authority: false

compiled_rom_plus_cache_layers
  source: frozen_workload_modes.exact_repetition.work
  primitive work: 7
  runtime authority: false

compiled_rom_plus_continuation_delta
  source: frozen_workload_modes.single_region_mutation.work
  primitive work: 11,911
  runtime authority: false

compiled_rom_plus_multimodal_ml
  NOT_APPLICABLE in this single text-transformer linear slice

complete_inherited_hhs_stack
  PARTIAL_ITERATION4_SUBSET_ONLY

complete_stack_with_ablations
  EXECUTED_ITERATION4_SUBSET_ABLATIONS
```

The `compiled_rom` wording above is a benchmark comparison slot inherited from the frozen profile. Iteration 4 uses an immutable descriptor analog only; it does not invoke or promote Pass 213 operational runtime mutation authority.

## Optimization-class and A0-A9 coverage

All 29 frozen optimization classes have an explicit disposition: executed, not applicable, optional/experimental, or deferred. None is silently omitted.

All Pass 214 stages A0-A9 are also explicitly represented:

- A0 dense exact rational reference: executed.
- A1 isolated Q4_0 factored kernel: executed.
- A2 descriptor + exact output cache: executed.
- A3 continuation/delta subsystem: executed.
- A4 complete inherited stack: explicitly partial at Iteration 4.
- A5 descriptor/cache/continuation ablations: executed.
- A6 no-reuse/adverse control: executed.
- A7 interruption recovery: executed.
- A8 internal evidence state: `READY_FOR_REQUIRED_EXTERNAL_CROSS_PROCESS_CI_REPLAY`.
- A8 external retained CI validation: succeeded using two separate process invocations with identical evidence root, suite root, and receipt.
- A9 accelerator/no-accelerator: not applicable to this CPU reference scope.

The A8 internal/external distinction is intentional: the evidence bundle is not mutated after execution merely to label its own external validation complete.

## Terminal computation identity

The same computational suite root survived both repair-forward stages because neither repair changed execution semantics:

```text
suite output root Hash216:
14de39b3b326eb64bbac5d8be829c289c4a5e1f39b842bfdba59b46fea2c9acb
```

Terminal comparison-authority evidence:

```text
evidence root Hash216:
0462738157042bbd2903ed666a3e05dbc1e27c8a43ea5d2544de9b0c174f87bf

Hash72 receipt:
2SrZvFdR/*41!b++dH9qxM1IrUZMuwuRZmpNw4yl8>QYI(LA9B65A<auqlwyWoi97onfMeMc
```

Process A and independent process B regenerated identical complete evidence bundles. The retained cross-process record binds the identical evidence root, suite root, and receipt.

## Validation lineage and repair-forward history

Iteration 4 intentionally retains all three hosted evidence stages rather than hiding superseded accounting/reporting results.

### Stage 1 — first green execution

```text
run: 31221256596
head: 4cfb8241edd81dd773cb939e1e249d0e4bd8b449
artifact: 9010454608
artifact SHA-256:
62435438054ad16b505a7ed99f58658852737515a3065b6f13c393ed67ff00f9
```

Execution and exact outputs were correct, but audit showed the aggregate executed-work total included descriptive capacity/coverage fields and double-counted `delta_weight_products` as an additional multiplication. The evidence is retained but its inclusive aggregate work totals are superseded.

### Stage 2 — primitive-work accounting authority

```text
run: 31221568421
head: e2ec4ae66df6f0c28f56df996580e4ee787eedeb
artifact: 9010567877
artifact SHA-256:
3fbc59d6daa3fd38d2a95025438351442332442512128ecf87d4f44323bb50c4
```

The corrected primitive totals passed and the computational suite root remained unchanged. Artifact audit then found that the frozen `dense_reference` comparison projection was incorrectly pointing at the `cold` compiled-descriptor mode instead of the separately executed dense exact reference.

### Stage 3 — terminal comparison authority

```text
run: 31222181816
job: 93008912750
head: 1bc8b04dd47f702e3bd4b9bc498961dd0b687415
tree: cf87c39a74a1356bade7e745863d994a16047d08
artifact: 9010778255
artifact SHA-256:
d69d05ab3f385f5f04dfe14dc45a45a718cc2f56356123046ec1291e37c83ddf
```

Validation composition:

```text
Iterations 1-3 cumulative tests: 21 passed
Iteration 4 exact execution tests: 8 passed
primitive-work accounting tests: 3 passed
comparison-mapping tests: 3 passed
-------------------------------------------
total: 35 passed
```

The model SHA-256 gate, process A validation, independent process B validation, cross-process replay, terminal comparison mapping, primitive accounting, recovery, controls, A0-A9 dispositions, optimization dispositions, and claim boundaries all passed.

## Authority / claim boundary

Iteration 4 establishes:

- authenticated real open-transformer linear-weight execution measured: **true**;
- seven `blk.0` linear operators executed: **true**;
- dense exact rational reference executed: **true**;
- Q4_0 block-factored exact kernel executed: **true**;
- dense/factored semantic exactness: **true**;
- exact continuation/delta execution: **true**;
- exact output-cache replay: **true**;
- interruption recovery: **true**;
- independent cross-process deterministic replay: **true** externally.

It does **not** establish:

- complete transformer-layer forward execution;
- RMSNorm execution;
- attention softmax execution;
- SiLU execution;
- exact nonlinear transformer operators;
- replacement of the complete dense transformer forward;
- Pass 213 operational compiled-ROM runtime mutation;
- canonical mutation authorization;
- runtime mutation authority promotion;
- migration activation;
- a 50B-model desktop feasibility result;
- arbitrary compression.

Current authority remains:

```text
benchmark_authority_promoted: true
pass215_authorized: true
pass213_gates_preserved: true
runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false
```

## Next iteration boundary

Iteration 5 should attack the nonlinear/exact-symbolic barrier required before these seven exact linear slices can become a complete transformer block. The next contract should freeze exact representations and validation controls for RMSNorm square/square-root normalization, RoPE phase rotation, attention score scaling and softmax/exponential normalization, and SiLU/sigmoid behavior. Approximation policy, if any, must be explicitly contracted against a bit-exact or rigorously bounded reference rather than silently introducing floating-point canonical authority.
