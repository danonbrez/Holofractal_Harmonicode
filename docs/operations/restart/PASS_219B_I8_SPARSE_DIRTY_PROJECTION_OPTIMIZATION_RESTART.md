# Pass 219B I8 — Sparse Dirty Projection Optimization Restart Record

## Status

`IMPLEMENTED_AND_VALIDATED — READY_FOR_REVIEW — NOT MERGED`

## Repository

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative main observed before this task: `3c926453d65b71a6d1789e06b748544f5f2bd228`
- Inherited runtime parent / Pass 219B I6 merge: `ff66e376a44c8b928a9a42c2e6d8aa1846785fc2`
- Validated Pass 219B I7 parent: `6df75bc39fd7c58108b8cf7aee3758341fe345a5`
- I8 implementation/evidence-seal head before compatibility repair: `a30cf59984576e330d088618f68341f4c6985e37`
- Validated compatibility-repair head: `a824988a618d10e573241a89f5915a838d5285d2`
- Working branch: `agent/pass219b-i8-sparse-dirty-projection-optimization`
- Review PR: `#323`
- Review base: `agent/pass219b-i7-exact-selective-projection-optimization`

The exact final review head is recorded in the terminal PR checkpoint comment after the documentation-seal commit and its final CI run. This avoids claiming a commit's own hash inside content that necessarily precedes creation of that commit.

## Purpose

Continue selective-projection optimization without promoting device-specific FPS or density constants. I8 implements and tests the general repository principle:

```text
SPARSE AUTHORITATIVE CHANGE
=> SPARSE DERIVED / PROJECTION WORK
```

using I7's exact precomputed selected-identity cell ranges.

Implemented lowering:

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

If dirty-set completeness is not proven, sparse execution is not admitted and the declared fallback is:

`FULL_DERIVED_PROJECTION_PATH`

## Binding inherited boundaries

- Singleton VM81/kernel authority remains unchanged.
- Hash72 and Hash216 semantics remain unchanged.
- I7 selected identities and cell ranges remain inherited rather than redefined.
- GPU/graphics remains projection-only/candidate-only.
- No I8 function mutates or persists canonical state or commits Hash72.
- No float/double arithmetic exists in the exact I8 planner.
- No division/modulo operator exists in the exact sparse span planner.
- Timing/FPS/device observations remain calibration witnesses only and are not canonical constants.

## Changed files

New I8 surfaces:

- `hhs_runtime/include/hhs_pass219b_sparse_dirty_projection_1_0.h`
- `hhs_runtime/include/hhs_pass219b_sparse_dirty_projection_1_0.hpp`
- `hhs_runtime/c/hhs_pass219b_sparse_dirty_projection_1_0.inc`
- `tests/pass219/test_pass219b_sparse_dirty_projection_1_0.c`
- `tests/pass219/test_pass219b_sparse_dirty_projection_1_0.cpp`
- `docs/pass219/PASS_219B_I8_SPARSE_DIRTY_PROJECTION_OPTIMIZATION.md`
- `docs/pass219/PASS_219B_I8_SPARSE_DIRTY_PROJECTION_EVIDENCE.json`
- `.github/workflows/pass219b-i8-sparse-dirty-projection.yml`
- this restart record

Updated integration surfaces:

- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `hhs_backend/api/runtime_graphics_routes.py`
- `hhs_runtime/c/hhs_pass219b_selective_projection_1_0.inc` only for historical standalone include-path compatibility; I7 selector semantics are unchanged.

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

## General conformance

The exhaustive C model covers:

- cell counts 1 through 8;
- five variable-length contiguous range layouts;
- zero-length cell ranges;
- every dirty-cell subset for every model;
- `2,550` exact dirty-subset cases total.

Each case compares direct dirty selected membership with I8's emitted spans. The I7 integration case reconstructs the current derived projection from a previous projection by copying only emitted sparse spans and requires byte-for-byte equality with the full derived result.

Negative cases cover:

- incomplete dirty-set witness;
- sparse/full inequality;
- canonical authority request;
- insufficient span capacity;
- unsorted dirty cells;
- duplicate dirty cells;
- truncated selected-count coverage;
- noncontiguous range metadata.

## Executed validation

### Initial implementation gate

- run `32681087219`
- exact job `97297809412` — `SUCCESS`
- synthetic job `97297809630` — `SUCCESS`

### First sealed gate

- run `32681178420`
- exact job `97298046745` — `SUCCESS`
- synthetic job `97298046640` — `SUCCESS`

### Repair-forward final implementation gate

- validated repair head: `a824988a618d10e573241a89f5915a838d5285d2`
- run `32681343205`
- exact job `97298466166` — `SUCCESS`
- synthetic job `97298466077` — `SUCCESS`

Both final dedicated lanes passed:

1. exact I7 ancestry;
2. float/double rejection in exact sparse surfaces;
3. division/modulo rejection in sparse span planner;
4. canonical-authority export rejection;
5. cumulative exact ABI compilation under C11 warnings-as-errors;
6. exhaustive I8 C conformance;
7. I8 C++ conformance;
8. inherited I7 C/C++ conformance;
9. inherited Pass 219B phase-hydration C/C++ conformance;
10. graphics capability syntax, complete-surface binding, dirty-set completeness fallback;
11. evidence JSON and non-device admission policy.

### Broad Pass 219 quantization / ABI audit

An earlier sealed head exposed one compatibility defect after all quantization/UQCEL tests had passed: the historical standalone public C ABI smoke compiled `hhs_runtime/c/hhs_runtime_abi.c` with only the historical `hhs_runtime/c` include directory, while I7's aggregate `.inc` used a bare include name for a public header in `hhs_runtime/include`.

Failure classification:

`INCLUDE_PATH_COMPATIBILITY_DEFECT_NOT_SEMANTIC_REGRESSION`

Repair-forward action:

```text
hhs_pass219b_selective_projection_1_0.inc
hhs_pass219b_sparse_dirty_projection_1_0.inc
```

now resolve their public headers with source-relative `../include/...` paths. The historical test flags and standalone ABI contract were preserved rather than weakened.

Post-repair audit:

- run `32681343152`
- job `97298465879` — `SUCCESS`

That audit passed:

- strict additive exact-ABI compile;
- integrated shared ABI build;
- UQCEL/Fibonacci/composed symbol exports;
- Pass 192 oracle;
- UQCEL correspondence/enforcement/inherited/monolithic/Fibonacci tests;
- historical standalone public C ABI link smoke;
- standalone VM81 exactness.

Inherited Pass 219 RNA transcription, grammar, admission, retrieval, and execution-composer workflows on the repair head were also observed green.

## External benchmark witness

The optimization was motivated by the user-supplied rerun receipt:

`64b4963017da2cf22d3ca912702ace07e6f9f9f30321e7dbcf85041619477827`

which reported one exact state digest across mirrored projection runs:

`69c042f32e861d61816067d2268a76a3eb1bcc52ef369421693f6964b1b9c8df`

and a small dirty-cell set per tick. Device FPS and projection-density boundaries are deliberately not promoted into I8 semantics.

## Environment

The ChatGPT execution container could not resolve `github.com`; no local clone/test state is authoritative. Repository writes and executable validation were performed through the connected GitHub repository and GitHub Actions.

## Repository-wide candidate principles produced by I8

These are reusable principles, not automatic authorization to alter unrelated subsystems:

1. hoist invariant exact work out of repeated hot paths;
2. reuse validated exact metadata through direct lookup;
3. bind optimization metadata to the complete inherited state surface;
4. use sparse derived work only when the sparse change witness is complete;
5. coalesce only semantically contiguous affected regions;
6. optimize active work/proof surface rather than deleting invariants;
7. fall back to the complete path whenever sparse preconditions are unproven;
8. require exact full-result equivalence before promotion;
9. preserve inherited build/ABI entry paths when extending aggregate runtimes;
10. treat device-specific timings and limits as calibration witnesses, not semantic laws.

Each application to cache, vector indexing, hydration, serialization, replication, or another subsystem still requires its own dependency-scoped proof.

## Next action

After the terminal documentation-seal exact/synthetic run is green, leave PR #323 ready for review. The next optimization iteration should select another subsystem-specific application of the same principles and prove equivalence independently rather than encoding the browser's device-specific numeric boundary.

## Merge status

PR #323 remains stacked on I7. No merge is authorized or performed.
