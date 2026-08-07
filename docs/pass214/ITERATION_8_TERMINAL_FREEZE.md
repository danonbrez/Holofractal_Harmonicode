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

This ordering preserves the frozen Pass 214 contract. `pass213_gates_preserved` means no optimized result, cache, worker, model, adapter, or accelerator may acquire canonical mutation authority without the inherited Pass 213 gates. It does **not** make deployment-local RFC 3161 material a prerequisite to measuring and freezing Pass 214.

## Repaired terminal authority

The authoritative implementation is:

- `hhs_backend/runtime/hhs_pass214_iteration8_terminal_freeze_v2.py`
- `tools/pass214_iteration8_terminal_freeze.py`

The earlier v1 runtime is retained as pre-merge history but is superseded for terminal authority because it bound `PASS214_AUTHORITY_ROOT_HASH216` to a live Iteration 7 admission root. That added a prerequisite absent from the frozen Pass 214 contract.

V2 instead binds a deterministic Pass 213 gate-preservation record into the Pass 214 authority root. The preservation record includes:

- Pass 213 authoritative closure `86ec461818682fc87232740758769602e8f9fe05`;
- the complete inherited Pass 213 required-authority set;
- `pass213_gates_preserved=true`;
- `pass214_benchmark_is_canonical_mutation=false`;
- `canonical_mutation_requires_pass213_live_admission=true`;
- `runtime_mutation_authority_promoted=false`;
- `migration_active=false`.

## Implemented final stack

Iteration 8 contains repository-visible surfaces for:

- exact-head repository census and callable conformance;
- deterministic authority-conflict reconciliation with symbol-Hash216 namespace preservation, zero automatic merges, and the inherited Pass 213 governed VM81/native-dispatch chain retained as the single mutation authority;
- a frozen 15-family workload corpus with 11 required execution modes per family;
- a frozen A0-A9 benchmark method and 26 mandatory ablation dispositions;
- a repository-native final compound benchmark executor using inherited Pass 165 multimodal ingestion/replay, Pass 212 full-hydration physical recovery, Pass 197 checkpoint/resume calibration, and Pass 214 Iterations 5-6 callable/candidate evidence;
- a predeclared immutable Pass 215 comparison profile;
- v2 fail-closed terminal benchmark-authority finalization;
- a downstream protected Pass 213 operational-admission check that cannot erase Pass 214 closure.

## Benchmark boundary

The frozen final benchmark covers:

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

Required semantic gates include multimodal compound/ablation participation, incremental/full equality, recovery/replay equality, cross-process equality, negative controls, complete cost accounting, semantic/observational separation, and honest physical compression accounting.

The arbitrary high-entropy full-hydration control remains a raw packed fallback with `strict_compression_claim=false`; affine and sparse results are not converted into a universal compression claim.

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

The ordered root set is bound into one canonical Hash72 terminal receipt. `PASS214_AUTHORITY_ROOT_HASH216` binds the Pass 213 authoritative closure, Iteration 6 candidate-set root, Pass 213 gate-preservation root, exact source commit/tree, authority-reconciliation root, and the seven non-authority terminal roots.

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

Here `authority_promoted` is explicitly scoped as `PASS214_BENCHMARK_AUTHORITY_ONLY`.

## Execution modes

`tools/pass214_final_compound_benchmark.py` executes and validates the frozen final benchmark bundle.

`tools/pass214_iteration8_terminal_freeze.py --mode inspect` reports Pass 214 benchmark-authority blockers. Operational Pass 213 trust material is not a Pass 214 readiness input.

`--mode finalize` requires census/conformance/reconciliation, workload corpus, benchmark method, final benchmark bundle, Pass 215 profile, and exact source commit/tree. It does not require RFC 3161 secrets or deployment-local Pass 213 state.

`--mode validate` validates the completed terminal record, eight roots, Hash72 receipt, Pass 213 gate-preservation binding, benchmark-authority scope, and the prohibition on runtime mutation promotion.

`.github/workflows/pass214-production-terminal-finalize.yml` executes Pass 214 closure in a job that has no `production` environment. Only after that job succeeds does a dependent `production` job inspect the downstream Pass 213 operational state. Missing Pass 213 trust inputs are recorded as post-closure runtime readiness, not as a Pass 214 failure.

## Downstream Pass 213 gate

Iteration 7 remains available through `tools/pass214_iteration7_live_admission.py` for the operational Pass 213 cross-authority check. A successful live admission is still required before canonical mutation or migration. Fixtures, synthetic timestamps, test doubles, or recorded admissions cannot satisfy that operational gate.

The distinction is:

```text
Pass 214 benchmark authority: repository-visible, terminally frozen by Pass 214
Pass 213 runtime mutation authority: deployment/runtime authority, never promoted by Pass 214
```

This keeps both contracts intact without placing a later runtime gate in front of the Pass 214 work it is supposed to govern after optimization.
