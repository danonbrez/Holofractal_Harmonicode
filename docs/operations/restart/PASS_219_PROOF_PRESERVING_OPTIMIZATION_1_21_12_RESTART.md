# Pass 219 I121.12 — proof-preserving optimization activation restart

## Authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Canonical authoritative base: `main @ f5d8fdc014d888f93c0d85d40d2a2c0c198eefdf`
- Active delivery branch: `agent/pass219-orthogonal-glyph-parallel-membrane-1-21`
- Existing PR: `#315`, draft, unmerged
- I121.11 terminal evidence seal / I121.12 parent: `9e17ff8e2fde1e3c50cb17b3cd5cac5b61a131a7`
- User authorization: safe optimization changes are authorized only where they reflect facts already undeniably proved and remain aligned with authoritative `main`.
- No canonical-main merge is authorized by this tranche.

## Proven facts this tranche may use

I121.8–I121.11 already established all of the following without modifying authoritative `main`:

1. the complete combined Harmonicode source is exactly 632 UTF-8 bytes with SHA-256 `3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53`;
2. the exact 139-byte `NcalcMatrixPower(...)` denominator occurs twice byte-identically in that source;
3. the two denominator occurrences are separate source/provenance witnesses even when one memoized value node is used for read-only optimization work;
4. denominator CSE must not reduce execution-receipt provenance;
5. the denominator projection has 9 cells and can be validated as 3 general representatives plus 6 exact phase-witness checks while still verifying all 9 cells;
6. ordered `xy/yx` and `zw/wz` identities remain distinct in native HHS even where a bounded complex projection maps them into `I^4/I^2` classes;
7. the complete combined equation remains distinct from the numerator through every frozen Pass159 stage: source, tokens, CST, AST, types, constraint graph, HIR, and VMIR;
8. I121.9 propagates only when every source-bound Boolean witness is true in one shared revalidated environment;
9. I121.10 provides whole-expression provenance but no Boolean gate truth;
10. I121.11 binder behavior is validated but real Pass169 runtime authority remains absent, so production remains `UNRESOLVED`.

## Authorized optimization boundary

I121.12 SHALL activate only proof-preserving optimizations inside read-only validation/optimization work:

```text
exact 632-byte combined source
        ↓
I121.8 structural proof
        ↓
proof-preserving optimization schedule
        ├─ denominator value work: 2 identical source occurrences → 1 memoized value node
        │  while retaining 2 independent occurrence witnesses
        └─ projection validation work: 9 general checks → 3 general representatives + 6 exact phase witnesses
           while retaining 9 verified final cells
```

This is an optimization of redundant read-only work, not a new algebraic authority.

## Explicit prohibitions

I121.12 MUST NOT:

- cancel the repeated denominator;
- rewrite the full relation as ordinary scalar `N=D^2`;
- reimplement or substitute `NcalcMatrixPower`;
- use the denominator magnitude projection as canonical evaluation;
- collapse `xy` with `yx` or `zw` with `wz` in native state;
- scalarize primitive `x,y,z,w`, VM81, Hash72, Hash216, or the 5,184 hydration surface;
- manufacture Pass169 gate truth;
- claim canonical monolithic proof;
- mutate VM81;
- mint Hash72 or Hash216 receipts;
- persist canonical state;
- modify frozen Pass159, Pass169, I121.8, I121.9, I121.10, or I121.11 semantic files;
- modify root `Makefile` or cumulative exact ABI merely to make the optimization pass.

## Planned additive implementation

- `HHS_PASS_219_APPEND_ONLY_PROOF_PRESERVING_OPTIMIZATION_AMENDMENT_1_21_12.md`
- `hhs_runtime/core_sandbox/hhs_pass219_proof_preserving_optimizer_1_21_12.py`
- `tests/pass219/test_pass219_proof_preserving_optimizer_1_21_12.py`
- `.github/workflows/pass219-proof-preserving-optimizer-1-21-12.yml`
- this restart record

The new optimizer will consume the already-validated I121.8 verifier rather than duplicating equation parsing or evaluation.

## Required optimization semantics

### Denominator CSE

Authorized only when all of these remain true:

```text
combined_source_sha256 = 3315641c...
denominator_sha256 = 5c4080c9...
denominator_occurrences = 2
source_occurrence_witnesses = 2
memoized_value_nodes = 1
receipt_count_reduction_authorized = false
algebraic_cancellation_authorized = false
```

### Projection validation fast path

Authorized only as read-only validation:

```text
baseline_general_checks = 9
optimized_general_checks = 3
optimized_exact_phase_witness_checks = 6
final_verified_cells = 9
projection_substitution_authorized = false
projection_derivation_authority = false
```

### Whole-expression binding

The optimizer must remain bound to the complete source identity and must expose that Pass159 whole-expression distinction through VMIR has been externally validated. It may not infer or synthesize Pass169 truth from that fact.

## Validation gates

1. `main @ f5d8fdc...` and I121.11 seal are ancestors;
2. frozen I121.8–I121.11 semantic files remain unchanged;
3. frozen Pass159 and Pass169 remain unchanged;
4. exact combined source identity and exact denominator identity remain unchanged;
5. inherited Pass043 preflight remains green through I121.8;
6. additive optimizer returns one denominator memoized value node with two occurrence witnesses;
7. additive optimizer returns 3 general + 6 exact phase checks and 9 final verified cells;
8. optimizer reports no receipt-count reduction, no cancellation, no projection substitution, no canonical proof, no VM81/Hash72/persistence authority;
9. tampered combined source is rejected through inherited I121.8;
10. tampered projection is rejected through inherited I121.8;
11. deterministic replay of the optimization schedule is byte-for-byte stable;
12. I121.8 tests remain green;
13. I121.9 membrane test remains green;
14. I121.10 whole-expression identity census remains preserved where dependency-scoped compilation is available;
15. I121.11 production no-provider state remains fail-closed;
16. exact and synthetic lanes must reach terminal state.

## Completion classification

A green I121.12 may be classified as:

`PASS_219_I121_12_PROOF_PRESERVING_OPTIMIZATION_ACTIVATED`

with the mandatory authority qualifier:

`READ_ONLY_OPTIMIZATION_ONLY / PASS169_RUNTIME_AUTHORITY_STILL_REQUIRED`

## Next action

Implement the additive optimizer, tests, amendment, and exact/synthetic workflow. Repair only I121.12-local defects. Preserve the I121.11 blocker: no real non-test Pass169 runtime provider currently exists in this repository.
