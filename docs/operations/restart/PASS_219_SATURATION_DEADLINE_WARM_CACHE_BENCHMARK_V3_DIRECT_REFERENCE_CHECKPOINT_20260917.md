# Pass 219 — Saturation Deadline Warm-Cache Benchmark v3 — Direct-Reference Checkpoint

Date: 2026-09-17

## Repository state

- Base / merge target: `main @ 63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- Branch: `pass219/saturation-deadline-warm-cache-benchmark-v3`
- Current substantive head before this checkpoint: `c50634337b6423f8696a3b60dbb95f02df88fdca`
- Current authoritative workflow run: `35264648574`
- Current job: `105348651977`
- Workflow: `Pass 219 Saturation Deadline Warm Cache Benchmark v3`

## Why the earlier benchmark was not the intended comparison

The v2 full-stack arm timed a cold/recompute path. Per record it executed VM81 import/export, Lane 5 route validation, fresh H36/Hash216 M binding, and M validation. It never entered the inherited H36 stack-selection cache or the H36 branch-reference/memoization hot path. Therefore v2 remains an isolated cold/recompute service-cost baseline only.

A first v3 draft then made a second wiring error: it called both `hhs_exact_pass219_h36_stack_cache_lookup` and `hhs_exact_pass219_h36_branch_ref_resolve` in the timed warm loop. The production 1.17 optimization had explicitly replaced repeated parent stack-cache lookup with the direct immutable branch-reference hot path, so serializing both suppressed the optimization being measured.

Repository-frozen production evidence for 1.17 reports:

- 144-entry direct immutable reference lookup: 63.828x versus parent stack-cache lookup;
- 5,184-entry direct immutable reference lookup: 59.883x;
- 144-entry Fibonacci equivalence discovery: 2.287x;
- 5,184-entry Fibonacci equivalence discovery: 1.977x;
- 144 compatible-composition memo hit: 2.651x;
- all optimized paths passed 5/5 beneficial repetitions, required minimum 4/5.

## Corrected v3 execution contract

### C — plain cold control

- Ubuntu/x86_64 native C/libc only;
- no HHS header, object, symbol, receipt, or feature;
- deterministic 648-byte copy/verify workload;
- all exposed runner CPUs saturated with pinned worker processes;
- C runs first.

### B — immutable runtime ABI control

- compile `hhs_runtime_exact_abi_v1_1_base.inc` directly;
- VM81 frame import/export and exact byte equality only;
- no aggregate ABI object and no Pass 219/Lane5/H36/Hash216 optimization object.

### A-cold — full native recompute diagnostic

Per record:

- aggregate exact ABI VM81 import/export;
- Lane 5 route construction/validation;
- fresh H36 stack selection;
- fresh direct H36/Hash216 M witness bind + validate.

### A-warm — direct-reference optimized native path

Warm state is constructed before the timed interval.

- inherited stack-selection cache is filled from repository-frozen measured H36/Linux evidence;
- a 144-entry H36 branch-reference topology is hydrated: 4 lanes × 36 H36 cells;
- parent stack-cache equality and exact replay are proved in preflight only;
- timed path uses direct immutable `branch_ref_resolve`, not parent `stack_cache_lookup`;
- compatible composition uses the inherited adaptive memoized receipt path after threshold 3172;
- direct H36/Hash216 M witnesses are bound before timing and still validated for every operation;
- VM81 import/export and per-record Lane 5 route validation remain in both A-cold and A-warm;
- direct references, memoized receipts, and M witnesses remain candidate/reference metadata and gain no canonical mutation/Hash72/Hash216/persistence authority.

## Saturation method

- deterministic virtual workset: 65,536 records × 648 bytes = 42,467,328 bytes per worker process;
- no file or allocation proportional to completed operation count;
- capacity windows: 5 s, 20 s, 60 s;
- final 60 s sustained capacity for C, B, and A-warm becomes an exact source workload;
- zero safety headroom;
- reverse cross-feed matrix: every source target is attempted by C, B, and A-warm under the same 60 s deadline;
- a target passes only if every worker finishes its exact partition within its timed window;
- warm construction has an 8 s synchronized pre-start runway and is separately reported; the run is invalid if warm fill leaves less than 1 s margin.

## Implemented files

- `benchmarks/pass219/saturation_deadline_v3/saturation_common_v3.h`
- `benchmarks/pass219/saturation_deadline_v3/plain_x86_saturation_v3.c`
- `benchmarks/pass219/saturation_deadline_v3/base_abi_saturation_v3.c`
- `benchmarks/pass219/saturation_deadline_v3/full_hhs_saturation_v3.c` — retained initial cold/reference implementation
- `benchmarks/pass219/saturation_deadline_v3/full_hhs_saturation_v3_optimized.c` — authoritative direct-reference A binary
- `tools/pass219/run_saturation_deadline_benchmark_v3.py`
- `tools/pass219/run_saturation_deadline_benchmark_v3_long.py`
- `.github/workflows/pass219-saturation-deadline-warm-cache-v3.yml`

## Current validation state

For authoritative run `35264648574`:

- checkout: PASS
- runner identity: PASS
- Python controller compile: PASS
- optimized A compile/link: PASS
- immutable B compile/link: PASS
- plain C compile/link: PASS
- binary/optimization symbol isolation: PASS
- long all-core saturation + reverse cross-feed: running at checkpoint creation
- evidence-contract validation: pending long run
- artifact seal/upload: pending long run

## Additional full-stack distinction discovered

The repository also has a higher service-level content-addressed reuse layer in `hhs_runtime.pass165.ingestion.MultimodalLearningService`. Once a source hash is already represented, `analyze` can return the existing result and commit emits a `P165_CONTENT_ADDRESSED_SOURCE_REUSED` receipt. That service-level warm hydration is distinct from the native H36 direct-reference optimization measured by this v3 run.

Do not merge the two measurements into one number. This v3 run measures the corrected native runtime optimization path. A subsequent service-level saturation surface should measure content-addressed full-service warm hydration using the same C-derived deadline methodology if the requested comparison is intended to encompass the entire Pass 165/214 service layer rather than only native Lane 5/H36/Hash216 runtime execution.

## Next action

1. Inspect run `35264648574` after the long stage completes.
2. Repair forward only concrete failures.
3. Seal exact result/report/artifact metadata in repository evidence.
4. Create final restart checkpoint.
5. Open PR to current `main`, merge when validated/mergeable, verify main.
6. Keep the service-level content-addressed hydration comparison separate unless explicitly integrated as an additional A-service arm.
