# Pass 219B I8 — Sparse Dirty Projection Optimization Restart Record

## Status

`IMPLEMENTED_AND_VALIDATED — CHECKPOINT_SEAL_REVALIDATION_REQUIRED — NOT MERGED`

## Repository

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative main observed before this task: `3c926453d65b71a6d1789e06b748544f5f2bd228`
- Inherited runtime parent / Pass 219B I6 merge: `ff66e376a44c8b928a9a42c2e6d8aa1846785fc2`
- Validated Pass 219B I7 parent: `6df75bc39fd7c58108b8cf7aee3758341fe345a5`
- I8 implementation head validated before evidence seal: `a82993c9df7d59c141eb0078fb34230a1e0c485e`
- Working branch: `agent/pass219b-i8-sparse-dirty-projection-optimization`
- Review PR: `#323`
- Review base: `agent/pass219b-i7-exact-selective-projection-optimization`

## Purpose

Continue the selective-projection optimization without promoting device-specific FPS or density constants. I8 implements and tests the general repository principle:

```text
SPARSE AUTHORITATIVE CHANGE
=> SPARSE DERIVED / PROJECTION WORK
```

using I7's exact precomputed selected-identity cell ranges.

The implemented lowering is:

```text
full exact authoritative state remains active
        +
complete inherited I7 selected_count
        +
precomputed exact selected-ID cell ranges
        +
sorted unique complete dirty source-cell witness
        -> exact coalesced selected-index spans
        -> update only those derived/projection spans
```

If dirty-set completeness is not proven, the optimization is not admitted and the declared fallback is:

`FULL_DERIVED_PROJECTION_PATH`

## Binding inherited boundaries

- Singleton VM81/kernel authority remains unchanged.
- Hash72 and Hash216 semantics remain unchanged.
- I7 selected identities and cell ranges remain inherited rather than redefined.
- GPU/graphics work remains projection-only/candidate-only.
- No I8 function mutates or persists canonical state or commits Hash72.
- No float/double arithmetic exists in the exact I8 planner.
- No division/modulo operator exists in the exact sparse span planner.
- Timing/FPS/device observations remain benchmark witnesses only and are not canonical constants.

## Changed files

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

## Implemented exact rules

```text
complete range coverage through inherited selected_count
AND sorted unique dirty cells
AND dirty-set completeness proof
AND minimal coalesced nonempty selected spans
AND sparse/full derived equivalence
AND zero canonical authority
```

Exact count laws:

```text
update_selected_count
= sum(end_selected-first_selected for dirty cells)

avoided_selected_count
= selected_count-update_selected_count

span_count <= dirty_cell_count
```

Separated dirty spans cannot bridge clean selected data. Touching dirty selected regions are coalesced.

## Executed validation

Dedicated workflow:

- run: `32681087219`
- exact job: `97297809412` — `SUCCESS`
- synthetic job: `97297809630` — `SUCCESS`
- validated implementation head: `a82993c9df7d59c141eb0078fb34230a1e0c485e`

Both lanes passed:

1. exact I7 ancestry;
2. float/double rejection in the exact sparse module;
3. division/modulo rejection in the sparse span planner;
4. canonical-authority export rejection;
5. cumulative exact ABI compilation under C11 warnings-as-errors;
6. I8 exhaustive C conformance;
7. I8 C++ conformance;
8. inherited I7 C/C++ conformance;
9. inherited Pass 219B phase-hydration C/C++ conformance;
10. graphics capability syntax and completeness fallback;
11. evidence JSON and non-device admission policy.

The exhaustive C model covered cell counts 1 through 8, five variable-length range layouts including zero-length cells, and every dirty subset: `2,550` exact dirty-subset cases.

Negative cases passed for:

- incomplete dirty-set witness;
- sparse/full inequality;
- canonical authority request;
- insufficient span capacity;
- unsorted dirty cells;
- duplicate dirty cells;
- truncated selected-count coverage;
- noncontiguous range metadata.

## External benchmark witness

The optimization was motivated by the user-supplied rerun receipt:

`64b4963017da2cf22d3ca912702ace07e6f9f9f30321e7dbcf85041619477827`

which reported one exact state digest across mirrored projection runs:

`69c042f32e861d61816067d2268a76a3eb1bcc52ef369421693f6964b1b9c8df`

and a small dirty-cell set per tick. Device FPS and projection-density boundaries are deliberately not promoted into I8 semantics.

## Environment

The ChatGPT execution container could not resolve `github.com`; no local clone/test state is authoritative. Repository writes and executable validation were performed through the connected GitHub repository and GitHub Actions.

## Remaining validation

The evidence and restart seal commits occur after the validated implementation head, so one final exact/synthetic dedicated workflow run on the sealed branch head is required before marking I8 ready for review.

No unchanged full-history rerun is required beyond the workflows automatically triggered by the aggregate ABI files unless a new failure appears.

## Next action

Wait only for the dedicated I8 exact/synthetic seal run, repair forward if it fails, then record the exact final head and leave PR #323 ready for review.

## Merge status

PR #323 remains stacked on I7. No merge is authorized or performed.
