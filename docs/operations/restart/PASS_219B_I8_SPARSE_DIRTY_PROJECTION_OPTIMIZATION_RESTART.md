# Pass 219B I8 — Sparse Dirty Projection Optimization Restart Record

## Status

`IMPLEMENTATION_IN_PROGRESS — STACKED ON VALIDATED I7 — NOT MERGED`

## Repository

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative main observed before this task: `3c926453d65b71a6d1789e06b748544f5f2bd228`
- Inherited runtime parent / Pass 219B I6 merge: `ff66e376a44c8b928a9a42c2e6d8aa1846785fc2`
- Validated Pass 219B I7 parent: `6df75bc39fd7c58108b8cf7aee3758341fe345a5`
- Working branch: `agent/pass219b-i8-sparse-dirty-projection-optimization`
- Intended review base: `agent/pass219b-i7-exact-selective-projection-optimization`

## Purpose

Continue the selective-projection optimization without promoting device-specific FPS or density constants. I8 tests and implements the general repository principle:

```text
SPARSE AUTHORITATIVE CHANGE
=> SPARSE DERIVED / PROJECTION WORK
```

using I7's exact precomputed selected-identity cell ranges.

The intended lowering is:

```text
full exact authoritative state remains active
        +
precomputed selected-ID ranges remain exact
        +
sorted dirty source-cell identities
        -> exact coalesced selected-index spans
        -> update only those derived/projection spans
```

## Binding inherited boundaries

- Singleton VM81/kernel authority remains unchanged.
- Hash72 and Hash216 semantics remain unchanged.
- I7 selected identities and cell ranges remain inherited rather than redefined.
- GPU/graphics work remains projection-only/candidate-only.
- No I8 function may mutate or persist canonical state or commit Hash72.
- No float/double arithmetic may enter the exact I8 planner.
- Timing/FPS/device observations are benchmark witnesses only and shall not become canonical constants.

## Planned changed files

Expected additive/updated surfaces:

- `hhs_runtime/include/hhs_pass219b_sparse_dirty_projection_1_0.h`
- `hhs_runtime/include/hhs_pass219b_sparse_dirty_projection_1_0.hpp`
- `hhs_runtime/c/hhs_pass219b_sparse_dirty_projection_1_0.inc`
- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `hhs_backend/api/runtime_graphics_routes.py`
- `tests/pass219/test_pass219b_sparse_dirty_projection_1_0.c`
- `tests/pass219/test_pass219b_sparse_dirty_projection_1_0.cpp`
- `docs/pass219/PASS_219B_I8_SPARSE_DIRTY_PROJECTION_OPTIMIZATION.md`
- `docs/pass219/PASS_219B_I8_SPARSE_DIRTY_PROJECTION_EVIDENCE.json`
- `.github/workflows/pass219b-i8-sparse-dirty-projection.yml`
- this restart record

## Validation plan

1. prove exact I7 ancestry;
2. compile cumulative exact ABI under C11 warnings-as-errors;
3. run I8 C conformance including exhaustive small-model dirty-set equivalence;
4. run I8 C++ conformance;
5. rerun I7 C/C++ conformance;
6. rerun inherited Pass 219B phase-hydration C/C++ conformance;
7. reject float/double and division/modulo in the exact sparse planner;
8. reject mutation/persistence/Hash72 authority exports;
9. validate graphics capability declaration;
10. parse machine-readable evidence;
11. validate exact head and synthetic merge through CI.

## Current execution state

Completed:

- reconciled current main and PR #319;
- confirmed PR #319 remains open, mergeable, unmerged, validated at `6df75bc39fd7c58108b8cf7aee3758341fe345a5`;
- identified I7 precomputed equal-cell ranges as the reusable prerequisite;
- created this I8 branch from exact validated I7.

Remaining:

- implement sparse dirty-span planner and wrappers;
- add exact conformance and evidence;
- wire aggregate ABI and graphics capabilities;
- run exact/synthetic CI;
- open review PR if green.

## Environment

The ChatGPT execution container could not resolve `github.com`, so no local clone/test state is authoritative. Repository writes and executable validation are being kept GitHub-resident through the connected repository and GitHub Actions.

## Next action

Implement `HHS_PASS219B_SPARSE_DIRTY_PROJECTION_1_0` as an additive projection-only exact ABI surface, then validate dependency-scoped exact/synthetic CI.

## Merge status

No merge is authorized or performed by this checkpoint.
