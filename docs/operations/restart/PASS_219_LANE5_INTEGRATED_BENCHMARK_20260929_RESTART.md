# Lane 5 Integrated Benchmark Campaign — 2026-09-29 R3 Prep

Status: **PREPARED — WAITING ONLY FOR POST-PROVIDER HASH216 INDEX REFRESH**

## Restart identity

- Preparation base: `7f34d20819ddbbb8f470f6b87e92621e47b99de4`
- I062 merge on main: `d6560ba13382282d8cc41fafeece1d862a2b752e`
- Lane 5 provider merge on main: `7f34d20819ddbbb8f470f6b87e92621e47b99de4`
- Preparation branch: `bench/lane5-integrated-benchmark-20260929-prep-native`
- Final execution branch: `bench/lane5-integrated-benchmark-20260929-r3`
- Final base placeholder: `__BENCHMARK_BASE_SHA__`
- Merge target: `main`
- Timing authority: observational only.
- Exactness/replay/authority gates remain mandatory.

## Why execution is not launched from this prep branch

The repository hydration receipt on provider-merged main still names source commit
`649917c94a54b7d4cf59cace418cc643dd5329a4`. The Hash216 repository-index
refresh for `7f34d20819ddbbb8f470f6b87e92621e47b99de4` is queued. Repository-index
latency, hydration size, counts, neighbor traversal, and Hash216 positional
lookup are benchmark targets, so measurements against the stale projection
would not be authoritative for the merged provider/I062 tree.

When the refresh lands, create r3 from that exact refreshed main and copy these
three prepared files while replacing `__BENCHMARK_BASE_SHA__` with the
refreshed main SHA.

## R3 changes

1. Native pytest is the dependency-scoped validation provider.
2. The workflow creates a clean venv and does not install upstream pytest,
   FastAPI, or Starlette.
3. I062's standard-library provider test is executed before using the provider.
4. Selected I051/I060/Lane5 1.69/Lane5 1.75/service-registry regressions run via
   `hhs_runtime.testing.native_pytest_provider_v1`.
5. The native pytest Hash216 receipt is persisted into the benchmark artifact
   and integrated campaign summary.
6. Provider context is fixed to `runtime`.
7. The benchmark harness records the complete Lane 5 provider matrix.
8. Every implemented provider must resolve native. Declared but incomplete
   providers are recorded as runtime fail-closed states; no implicit external
   fallback is permitted in this runtime benchmark.
9. FastAPI status must report native selection with no external provider selected.
10. Existing HNAN, 1M candidate, Q-info, real-world, circular-attractor,
    Pass214, Pass212 full hydration, and raw5184 workloads remain unchanged.

## Correctness before timing

No performance number is accepted unless:

- native pytest dependency regression exits 0 and produces a 216-character receipt;
- external pytest execution is false;
- all implemented Lane 5 capabilities resolve native;
- no implicit external fallback is used;
- repository index parity/restart checks pass;
- all existing exact equality, deterministic replay, negative-control, and
  authority checks pass.

## Finalization sequence

1. wait for the post-`7f34d208` Hash216 index refresh to update main;
2. verify receipt `source_commit` matches the refreshed projection source;
3. create final r3 branch from that main SHA;
4. copy prepared harness/workflow/restart files and bind exact ancestry SHA;
5. commit workflow last to trigger the integrated run;
6. inspect failures before accepting timing;
7. seal green metrics and optimize only demonstrated bottlenecks.
