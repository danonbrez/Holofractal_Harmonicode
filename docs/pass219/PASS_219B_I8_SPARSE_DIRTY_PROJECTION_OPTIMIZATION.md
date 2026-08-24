# Pass 219B I8 — Sparse Dirty Projection Optimization

## Status

`IMPLEMENTED_ON_REVIEW_BRANCH — VALIDATION PENDING`

Pass 219B I8 is an additive optimization continuation stacked on the exact validated I7 head:

`6df75bc39fd7c58108b8cf7aee3758341fe345a5`

I8 does not replace I7, alter the inherited VM81/kernel authority path, modify Hash72/Hash216 semantics, or promote any device-specific benchmark number into a system constant.

## Purpose

The latest browser witness again preserved one exact authoritative digest while showing that presentation cost rises as more already-authoritative entities are projected. The important repository-level observation is not a particular FPS boundary. It is that the workload reports only a small set of source cells changing per tick while I7 already provides exact selected-index ranges for every source cell.

I8 therefore tests and implements the general rule:

```text
SPARSE AUTHORITATIVE CHANGE
=> SPARSE DERIVED / PROJECTION WORK
```

without changing authoritative state evolution.

## Inherited authority boundary

The cumulative authority ordering remains:

```text
pre-pass state validity
    -> singleton VM81/kernel admission and commit authority
    -> Hash72 admitted receipt/state lineage
    -> numbered pass functionality
    -> Hash216/archive/cache/GPU/projection optimization
```

For I8 specifically:

- the full authoritative state remains active;
- I7 remains the exact selected-identity and cell-range source;
- dirty-cell identities are an input witness, not authority created by I8;
- I8 emits selected-index spans only;
- no I8 function may mutate canonical state;
- no I8 function may persist canonical state;
- no I8 function may commit Hash72;
- no GPU or projection lane receives canonical authority;
- exact I8 planning contains no floating-point arithmetic;
- exact I8 span planning contains no rational division or modulo.

## Exact sparse-span model

Let I7 expose a complete selected projection of size `S` partitioned into ordered cell ranges:

```text
R_c = [a_c, b_c)
```

for source cells `c = 0..C-1`, such that:

```text
a_0 = 0
b_c = a_(c+1)
b_(C-1) = S
```

Let `D` be the sorted unique set of source cells whose projected values changed for the current transition.

I8 computes:

```text
U = union(R_c for c in D)
```

and emits the minimal ordered list of selected-index spans produced by coalescing touching nonempty dirty ranges.

The exact counts are:

```text
update_selected_count
= sum(b_c - a_c for c in D)

avoided_selected_count
= S - update_selected_count

span_count <= |D|
```

No ratio arithmetic is required in this per-transition planner because I7 already resolved the exact rational mapping during setup.

## Complete-surface binding

The planner does not infer `S` from whatever range array it is given.

The caller must supply the inherited I7 `selected_count`, and the range table must prove complete coverage through that exact count.

Therefore truncated metadata cannot silently redefine a smaller projection surface:

```text
last_range.end_selected != inherited_selected_count
=> INVARIANT_FAILURE
```

This is a general optimization law:

```text
OPTIMIZATION METADATA MUST BE BOUND TO THE COMPLETE INHERITED SURFACE
```

not merely internally self-consistent.

## Dirty-set completeness is mandatory

A sorted dirty set can still be incomplete.

Sparse execution is correct only if the upstream transition machinery can prove that every changed projected source partition appears in `D`.

I8 therefore marks:

```text
dirty_set_completeness_required = 1
```

and verification fails if completeness is not proven.

The required fallback is:

```text
DIRTY SET COMPLETENESS NOT PROVEN
=> DO NOT TRUST PARTIAL SPANS
=> USE FULL DERIVED / PROJECTION PATH
```

This fallback affects derived/projection work only. It does not roll back or reinterpret an already-valid canonical state.

## Coalescing law

Touching dirty selected ranges may be coalesced because the resulting byte/index interval contains only dirty selected entries.

Separated ranges may not be bridged across a clean selected interval merely to reduce call count.

After coalescing, emitted spans must be:

- nonempty;
- ordered;
- disjoint;
- non-touching;
- bounded by `S`;
- exactly equal in total selected count to the sum of the dirty cell ranges.

This prevents an optimization from expanding its work surface across clean data while still allowing contiguous dirty regions to become one upload/copy operation.

## Exact equivalence gate

I8 conformance constructs a previous derived projection and a current full derived projection, modifies only the declared dirty source ranges, then reconstructs the current projection by applying only the sparse spans to the previous projection.

The sparse result must be byte-identical to the full result.

Therefore:

```text
SPARSE RESULT == FULL DERIVED RESULT
```

is a correctness requirement, not a performance heuristic.

The I8 verification surface additionally requires:

```text
realized update count == planned update count
AND dirty set complete
AND exact projection equal
AND canonical authority requested == 0
```

## Exhaustive small-model validation

The C conformance test does not depend on one device, one frame rate, or one projection ratio.

It enumerates:

- cell counts from 1 through 8;
- multiple variable-length contiguous range layouts, including zero-length cells;
- every possible dirty-cell subset for those cell counts.

For every case it compares the exact union implied by dirty source cells against the emitted sparse spans and requires identical selected membership.

This converts the optimization claim from a device benchmark observation into an implementation property.

## General repository optimization principles

I8 promotes the following principles for consideration across the repository. Applying them to another subsystem still requires subsystem-specific proof and must not be assumed automatically.

### 1. Hoist invariant work out of hot paths

If an identity mapping, partition, index, route, or algebraic relationship is invariant across many transitions, compute and validate it once, then reuse the exact result.

```text
REPEATED EXACT RECOMPUTATION
-> PRECOMPUTED EXACT METADATA
-> DIRECT HOT-PATH LOOKUP
```

This is the same principle I7 applied to rational selected identities.

### 2. Sparse change should produce sparse derived work

When a complete exact change witness identifies a strict subset of an already-valid state as changed, downstream non-authoritative materialization should touch only the affected derived regions.

Candidate applications include:

- graphics projection updates;
- cache refresh;
- vector-index maintenance;
- hydration projection materialization;
- derived serialization;
- replication/delta preparation;
- non-authoritative analytics.

Each application requires its own exact equivalence and authority-boundary tests.

### 3. Optimize the active proof/work surface, not the invariants

```text
DO NOT REMOVE INVARIANTS TO GET SPEED
REDUCE THE ACTIVE WORK REQUIRED TO PRESERVE THE SAME RESULT
```

I8 removes neither authoritative entities nor exact selected identities. It reduces the amount of derived work required when only part of that already-established state changed.

### 4. Preserve original identity

A compact span is an addressing optimization over the inherited selected sequence. It does not mint a new identity space.

The authoritative/original identity remains the I7-selected original source identity.

### 5. Fail closed to the complete path

An optimization is optional; correctness is not.

If preconditions are unavailable, malformed, incomplete, or inconsistent, the safe response is the inherited complete path rather than a guessed sparse path.

### 6. Performance numbers are witnesses, not laws

Device FPS, thermal state, browser scheduling, GPU presentation cadence, and background-process load are calibration observations.

They may select local defaults but must not define canonical HHS semantics.

Repository-wide promotion should be based on:

- exact equivalence;
- reduced operation/data surface;
- preserved authority boundaries;
- reproducible implementation properties;
- bounded environment-specific calibration only where necessary.

### 7. Benchmark order must expose environment drift

Mirrored ordering, repeated sentinels, cold/warm classification, and exact output equality should remain part of performance studies so environmental drift is not mistaken for a semantic or algorithmic limit.

## External benchmark witness that motivated I8

A user-supplied rerun on 2026-08-24 reported:

- full authoritative state retained for all runs;
- one final exact digest across all projection densities and mirrored directions;
- I7-style static original-ID mapping with no division/modulo in the measured projection path;
- a small dirty-cell count per tick;
- presentation degradation above a local projection-density region.

Receipt identity supplied with that benchmark:

`64b4963017da2cf22d3ca912702ace07e6f9f9f30321e7dbcf85041619477827`

Exact final state digest supplied by all runs:

`69c042f32e861d61816067d2268a76a3eb1bcc52ef369421693f6964b1b9c8df`

Those timing/density values are deliberately not an I8 admission constant. The repository-level consequence is only the optimization hypothesis tested above.

## Implementation surfaces

I8 adds:

- `hhs_runtime/include/hhs_pass219b_sparse_dirty_projection_1_0.h`
- `hhs_runtime/include/hhs_pass219b_sparse_dirty_projection_1_0.hpp`
- `hhs_runtime/c/hhs_pass219b_sparse_dirty_projection_1_0.inc`
- cumulative exact ABI aggregation;
- C exhaustive/reference conformance;
- C++ wrapper conformance;
- graphics capability declaration;
- machine-readable principle/evidence record;
- restart record;
- exact/synthetic CI workflow.

## Non-goals

I8 does not:

- establish a universal projection-density ceiling;
- encode a device FPS threshold;
- change canonical state density;
- make projected samples authoritative;
- move VM81 mutation to GPU/graphics;
- invent dirty-cell identities;
- accept an incomplete dirty set;
- infer a smaller selected surface from truncated metadata;
- weaken I7 identity validation;
- change Hash72 or Hash216;
- generalize sparse mutation into canonical authority.

## Completion gate

I8 is eligible to freeze only after:

1. exact I7 ancestry is proven;
2. cumulative exact ABI compiles under warnings-as-errors;
3. I8 C exhaustive/reference conformance passes;
4. I8 C++ conformance passes;
5. I7 C/C++ conformance remains green;
6. inherited Pass 219B phase-hydration C/C++ conformance remains green;
7. exact I8 planner contains no float/double or division/modulo arithmetic;
8. no new mutation/persistence/Hash72 authority export is present;
9. graphics capability declaration remains projection-only and requires dirty-set completeness;
10. machine-readable evidence parses;
11. exact-head and synthetic-merge CI are green;
12. restart record is bound to the validated head and evidence.
