# Pass 214 Final Iteration Restart Record

## Branch and authority

- Branch: `agent/pass214-operating-compression-gradient`
- Merge target: `main`
- Draft PR: `#170`
- Pass 213 authoritative closure: `86ec461818682fc87232740758769602e8f9fe05`
- Iteration 6 candidate-set root: `f11bdbb9940e90500692cd0a0c505727ad94cafc0ea4fca85b134253f72cab9f`
- Benchmark authority: `hhs_backend/runtime/hhs_pass214_final_compound_benchmark_v2.py`
- Terminal contract authority: `hhs_backend/runtime/hhs_pass214_iteration8_terminal_freeze_v2.py`
- Serialized terminal validation authority: `hhs_backend/runtime/hhs_pass214_iteration8_terminal_freeze_v3.py`
- Pass 214 contract rule: Pass 213 gates are preserved; they do not precede or suppress Pass 214 benchmark execution.
- Canonical runtime mutation remains downstream behind Pass 213 live admission.

## Contract-ordering repair

The pre-merge Iteration 8 v1 terminal layer incorrectly added operational Pass 213 live admission as a prerequisite to Pass 214 terminal benchmark authority. The v1 final benchmark also labeled fully measured evidence as `FINAL_BENCHMARK_COMPLETE_AWAITING_LIVE_ADMISSION`. Neither condition belongs in the frozen Pass 214 benchmark contract.

The repaired ordering is:

```text
Pass 214 cumulative validation
→ repository census/conformance/reconciliation
→ final compound + ablation benchmark
→ eight-root Pass 214 terminal freeze
→ Pass 214 benchmark-authority promotion
→ Pass 215 benchmark-profile authorization
→ downstream Pass 213 live admission before any canonical mutation
```

Benchmark v2 preserves every v1 measurement, changes only authority/ordering metadata, and recomputes its Hash216/Hash72 identities under:

```text
FINAL_BENCHMARK_COMPLETE_READY_FOR_PASS214_TERMINAL_FREEZE
```

Terminal v2 binds the Pass 213 authoritative closure and complete required gate set into `PASS214_AUTHORITY_ROOT_HASH216`. It requires:

```text
pass213_gates_preserved: true
runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false
pass213_live_admission_required_before_canonical_mutation: true
```

## Serialization repair

Exact-head diagnostic run `31193486383` on commit `0c80feec6d72356808353b55cac233361f03d8af` proved that benchmark v2 and terminal v2 executed through root minting:

- cumulative Pass 214 validation: success;
- census/conformance/reconciliation: success;
- final benchmark v2: success;
- eight terminal roots generated: yes;
- terminal Hash72 receipt generated: yes;
- subsequent reload validation: failed with `PASS214_I8_TERMINAL_ROOT_SET_OR_ORDER_INVALID`.

The failure was caused by JSON serialization using `sort_keys=True`: v2 incorrectly treated Python mapping insertion order as an authority invariant after reload. V3 now requires the exact eight named roots as a set, canonicalizes them into contract order, and then delegates all cryptographic/root/receipt/gate validation to v2. A sorted-JSON round-trip regression is included.

Diagnostic v2 receipt from that superseded source head:

```text
8NM)B1QxahUUav4J/WZLt3wWk*g*ffcv?EpSKPSg)bUoi7(k12BfOwGa<aIGuFXZjf5uDZ(8
```

It is diagnostic only because the v3 repair changes the final source tree.

## Authoritative repaired surfaces

- `hhs_backend/runtime/hhs_pass214_final_compound_benchmark_v2.py`
- `hhs_backend/runtime/hhs_pass214_iteration8_terminal_freeze_v2.py`
- `hhs_backend/runtime/hhs_pass214_iteration8_terminal_freeze_v3.py`
- `tools/pass214_final_compound_benchmark.py`
- `tools/pass214_iteration8_terminal_freeze.py`
- `hhs_backend/runtime/hhs_pass214_authority_conflict_reconciliation_v1.py`
- `tests/test_hhs_pass214_iteration8_terminal_freeze_v1.py`
- `tests/test_pass214_terminal_workflow_ordering.py`
- `scripts/run_pass214_contract_validation.sh`
- `.github/workflows/pass214-iteration8-terminal-freeze.yml`
- `.github/workflows/pass214-production-terminal-finalize.yml`
- `evidence/pass214/PASS_214_ITERATION_8_IMPLEMENTATION_RECORD.json`
- `evidence/pass214/PASS_214_PRODUCTION_FINALIZE_TRIGGER.json`

Historical v1 and v2 layers are retained. Iteration 7 remains the downstream operational Pass 213 live-admission mechanism; it does not determine whether Pass 214 benchmark authority exists.

## Benchmark boundary

```text
workload families: 15
modes per family: 11
mode executions: 165
A0-A9 stages: 10
mandatory ablations: 26
Pass 197 address comparisons: 1,658,880
Pass 212 full hydration bits: 50,388,480
Pass 212 full hydration bytes: 6,298,560
Pass 212 full-state recoveries: 3
Pass 165 replay families: 15
cross-process replays: 15
Iteration 5 consecutive exact runs: 3
Iteration 6 candidate bindings: 5
```

The high-entropy control remains raw fallback and does not acquire a false universal compression claim.

## Required final state

```text
terminal_roots_minted: true
benchmark_authority_promoted: true
pass215_authorized: true
pass213_gates_preserved: true
runtime_mutation_authority_promoted: false
canonical_mutation_authorized: false
migration_active: false
```

The downstream Pass 213 operational gate may report not-ready when deployment-local RFC 3161/verifier/trust state is absent. That cannot erase or redefine completed Pass 214 benchmark authority; it only blocks canonical runtime mutation.

## Next exact action

1. Freeze one final source trigger after v3 evidence/documentation is complete.
2. Require exact-head success from cumulative Pass 214, standalone Iteration 8 terminal freeze, and production terminal finalizer.
3. Require standalone and production terminal jobs to emit the same deterministic eight terminal roots and Hash72 receipt for one commit/tree.
4. Treat downstream Pass 213 admission as post-closure runtime readiness only.
5. Update PR #170 metadata without changing the source head, merge that exact validated head to `main`, and verify the resulting main tree.
6. Begin Pass 215 from the frozen Pass 214 benchmark profile; canonical Pass 215 mutation remains subject to inherited Pass 213 gates.
