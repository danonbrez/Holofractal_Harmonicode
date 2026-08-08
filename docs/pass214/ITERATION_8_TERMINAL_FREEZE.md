# Pass 214 Iteration 8 — Terminal Benchmark and Pass 215 Freeze

Iteration 8 is the final Pass 214 implementation layer. Its authority is the frozen repository-wide benchmark/evidence profile consumed by Pass 215. It does not promote canonical runtime mutation authority.

## Contract ordering

Pass 214 executes before the downstream operational Pass 213 runtime gate:

```text
repository census/conformance/reconciliation
→ Pass 214 compound + ablation benchmark
→ Pass 214 eight-root terminal freeze
→ Pass 214 benchmark authority promotion
→ Pass 215 benchmark profile authorization
→ Pass 213 live runtime admission before canonical mutation
```

`pass213_gates_preserved` means no optimized result, cache, worker, model, adapter, or accelerator may acquire canonical mutation authority without the inherited Pass 213 gates. It does **not** make deployment-local RFC 3161 material a prerequisite to measuring and freezing Pass 214.

## Repaired authority layers

Authoritative surfaces are:

- benchmark authority: `hhs_backend/runtime/hhs_pass214_final_compound_benchmark_v2.py`;
- terminal contract authority: `hhs_backend/runtime/hhs_pass214_iteration8_terminal_freeze_v2.py`;
- serialized terminal validation authority: `hhs_backend/runtime/hhs_pass214_iteration8_terminal_freeze_v3.py`;
- terminal CLI: `tools/pass214_iteration8_terminal_freeze.py`.

Historical v1 surfaces are retained. Terminal v1 is superseded because it bound `PASS214_AUTHORITY_ROOT_HASH216` to live Iteration 7 admission, adding a prerequisite absent from the frozen contract. Benchmark v1 remains the measurement source; v2 preserves its measured values, corrects the completed status, and reroots authority metadata.

Terminal v2 binds a deterministic Pass 213 gate-preservation record into the Pass 214 authority root. The record includes:

- Pass 213 authoritative closure `86ec461818682fc87232740758769602e8f9fe05`;
- the complete inherited Pass 213 required-authority set;
- `pass213_gates_preserved=true`;
- `pass214_benchmark_is_canonical_mutation=false`;
- `canonical_mutation_requires_pass213_live_admission=true`;
- `runtime_mutation_authority_promoted=false`;
- `migration_active=false`.

Terminal v3 repairs repository serialization without changing those semantics. V2 correctly minted the eight named roots, but its reload validator treated Python mapping insertion order as an authority invariant. Because repository JSON uses sorted keys, v3 requires the exact eight named roots as a set, canonicalizes them into contract order, and then delegates all cryptographic/root/receipt/gate validation to v2. The sorted-JSON round-trip is regression tested.

## Implemented final stack

Iteration 8 contains repository-visible surfaces for:

- exact-head repository census and callable conformance;
- deterministic authority-conflict reconciliation with symbol-Hash216 namespace preservation, zero automatic merges, and the inherited Pass 213 governed VM81/native-dispatch chain retained as the single mutation authority;
- a frozen 15-family workload corpus with 11 required execution modes per family;
- a frozen A0-A9 benchmark method and 26 mandatory ablation dispositions;
- a repository-native final compound benchmark using inherited Pass 165 multimodal ingestion/replay, Pass 212 full-hydration recovery, Pass 197 checkpoint/resume calibration, and Pass 214 Iterations 5–6 callable/candidate evidence;
- a predeclared immutable Pass 215 comparison profile;
- fail-closed Pass 214 terminal benchmark-authority finalization;
- downstream protected Pass 213 operational admission that cannot erase Pass 214 closure.

## Benchmark boundary

```text
workload families: 15
modes per family: 11
mode executions: 165
A0-A9 stages: 10
mandatory ablations: 26
Pass 197 address comparisons: 1,658,880
Pass 212 full hydration: 50,388,480 bits / 6,298,560 bytes
Pass 212 full-state recoveries: 3
cross-process replays: 15
```

The final benchmark status is:

```text
FINAL_BENCHMARK_COMPLETE_READY_FOR_PASS214_TERMINAL_FREEZE
```

Required semantic gates include multimodal compound/ablation participation, incremental/full equality, recovery/replay equality, cross-process equality, negative controls, complete cost accounting, semantic/observational separation, and honest physical compression accounting.

The arbitrary high-entropy full-hydration control remains raw packed fallback with `strict_compression_claim=false`; affine and sparse results are not converted into a universal compression claim.

## Terminal roots

After complete Pass 214 validation, Iteration 8 mints exactly:

```text
PASS214_REPOSITORY_SCAN_ROOT_HASH216
PASS214_OPTIMIZATION_REGISTRY_ROOT_HASH216
PASS214_COMPATIBILITY_GRAPH_ROOT_HASH216
PASS214_WORKLOAD_CORPUS_ROOT_HASH216
PASS214_BENCHMARK_METHOD_ROOT_HASH216
PASS214_COMPOUND_EVIDENCE_ROOT_HASH216
PASS214_AUTHORITY_ROOT_HASH216
PASS215_BENCHMARK_PROFILE_ROOT_HASH216
```

The named root set is bound into one canonical Hash72 terminal receipt. `PASS214_AUTHORITY_ROOT_HASH216` binds the Pass 213 authoritative closure, Iteration 6 candidate-set root, Pass 213 gate-preservation root, exact source commit/tree, authority-reconciliation root, and the seven non-authority terminal roots.

A valid terminal record requires:

```text
terminal_roots_minted: true
authority_promoted: true
benchmark_authority_promoted: true
pass215_authorized: true
pass213_gates_preserved: true
runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false
pass213_live_admission_required_before_canonical_mutation: true
```

`authority_promoted` is explicitly scoped as `PASS214_BENCHMARK_AUTHORITY_ONLY`.

## Execution and CI

`tools/pass214_final_compound_benchmark.py` executes and validates benchmark v2.

`tools/pass214_iteration8_terminal_freeze.py --mode inspect` reports Pass 214 benchmark-authority blockers. Operational Pass 213 trust material is not a Pass 214 readiness input.

`--mode finalize` requires census/conformance/reconciliation, workload corpus, benchmark method, final benchmark bundle, Pass 215 profile, and exact source commit/tree. It does not require RFC 3161 secrets or deployment-local Pass 213 state.

`--mode validate` validates a serialized terminal record through v3 canonical root-set handling and v2 cryptographic authority validation.

`.github/workflows/pass214-iteration8-terminal-freeze.yml` independently executes benchmark readiness, root minting, serialized validation, and terminal-boundary enforcement.

`.github/workflows/pass214-production-terminal-finalize.yml` closes Pass 214 in a job with no `production` environment. Only after that job succeeds does a dependent `production` job inspect downstream Pass 213 operational readiness. Missing Pass 213 trust inputs are post-closure runtime readiness, not a Pass 214 failure.

## Downstream Pass 213 gate

Iteration 7 remains available through `tools/pass214_iteration7_live_admission.py` for operational Pass 213 cross-authority checking. Successful live admission remains required before canonical mutation or migration. Fixtures, synthetic timestamps, test doubles, and recorded admissions cannot satisfy that operational gate.

```text
Pass 214 benchmark authority: repository-visible and terminally frozen by Pass 214
Pass 213 runtime mutation authority: deployment/runtime authority, never promoted by Pass 214
```

This preserves both contracts without placing the downstream runtime gate in front of Pass 214 benchmark work.
