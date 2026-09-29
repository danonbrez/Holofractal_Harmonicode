# Lane 5 Integrated Benchmark Campaign — 2026-09-29 Restart Checkpoint

Status: **RESTARTABLE CHECKPOINT — R3 PREPARED, EXECUTION BLOCKED ONLY BY HASH216 INDEX REFRESH PARSE FAILURE**

## Restart identity

- Authoritative main at checkpoint: `7f34d20819ddbbb8f470f6b87e92621e47b99de4`
- I062 native pytest merge on main: `d6560ba13382282d8cc41fafeece1d862a2b752e`
- Lane 5 native-provider policy merge on main: `7f34d20819ddbbb8f470f6b87e92621e47b99de4`
- Preparation branch: `bench/lane5-integrated-benchmark-20260929-prep-native`
- Preparation branch base: `7f34d20819ddbbb8f470f6b87e92621e47b99de4`
- Final execution branch reserved: `bench/lane5-integrated-benchmark-20260929-r3`
- Merge target: `main`
- Timing authority: observational only.
- Exactness, deterministic replay, authority, and equality gates remain mandatory.

## Current main/index state

The merged provider/I062 tree is authoritative on main, but the repository
hydration projection is stale relative to it.

Current repository hydration receipt:

- receipt schema: `HHS_PASS_219_LANE5_REPOSITORY_HYDRATION_DATABASE_RECEIPT_1_69`
- receipt source commit: `649917c94a54b7d4cf59cace418cc643dd5329a4`
- authoritative main: `7f34d20819ddbbb8f470f6b87e92621e47b99de4`
- repository files: 8,862
- file dependencies: 73,477
- Lane 5 capabilities: 2,074
- constructors: 4,278
- knowledge edges: 13,319
- Hash216 positions: 4,248,936
- journal mode: WAL
- synchronous FULL: true
- restart rehydratable: true
- VM81/Hash72/Hash216/execution authority: false

Because repository-index latency, hydration size, counts, neighbor traversal,
and Hash216 positional lookup are benchmark targets, no R3 measurement may be
accepted until the projection source is refreshed against the provider-merged
main tree.

## Current blocker

The post-provider Hash216 dependency-index refresh has been attempted repeatedly
against main `7f34d20819ddbbb8f470f6b87e92621e47b99de4` and currently fails at
the same attributable frontier.

Latest inspected refresh:

- workflow: `HHS Hash216 Repository Dependency Index`
- run: `36602056930`
- job: `109521633495`
- result: failure
- build cumulative exact ABI: success
- Lane 5 repository hydration knowledge graph 1.69 validation: success
- failing step: `Deep scan repository through Lane 5 and Hash216`

Exact failure:

```text
RuntimeError: structural Python registry scan has parse errors: ['hhs_backend/server.py']
```

Failure path:

```text
build_repository_capability_reverse_discovery(...)
  -> Pass219Lane5RepositoryCapabilityReverseDiscovery.build()
  -> _python_operation_registry()
  -> structural Python registry scan rejects hhs_backend/server.py
```

The deterministic replay, evidence upload, authoritative refresh dispatch, and
projection commit steps are skipped after this failure.

This is the sole current benchmark-launch blocker recorded by this checkpoint.
No repair to `hhs_backend/server.py`, the reverse-discovery scanner, or the
index workflow is included in this checkpoint.

## Prior benchmark attempts

No current performance number is accepted as final campaign evidence.

### Initial run

- run: `36560225418`
- branch: `bench/lane5-integrated-benchmark-20260929`
- result: failure
- failure was the then-missing external FastAPI dependency reached through the
  service-registry import path before the native-provider policy existed.
- no final benchmark metrics were accepted.

### External-FastAPI workaround runs

- run `36562402267`: failure
- run `36562617516` on R2: failure
- dependency-scoped regressions reached green on R2: 30 passed
- the integrated services/index benchmark then failed before timing because
  direct script execution could not import repository-root `hhs_backend`:

```text
ModuleNotFoundError: No module named 'hhs_backend'
```

Those runs predate the final native-provider and I062 integration and are not
authoritative performance evidence.

## Prepared R3 files

The preparation branch is exactly three benchmark files ahead of current main:

1. `.github/workflows/pass219-lane5-integrated-benchmark-20260929.yml`
2. `benchmarks/pass219/pass219_lane5_integrated_services_index_benchmark_20260929.py`
3. `docs/operations/restart/PASS_219_LANE5_INTEGRATED_BENCHMARK_20260929_RESTART.md`

The workflow and harness are prepared but intentionally not executed from this
branch.

## R3 execution contract already prepared

1. Native pytest is the dependency-scoped validation provider.
2. Upstream pytest is not installed.
3. External FastAPI and Starlette are not installed.
4. I062's standard-library provider test runs before using the native provider.
5. Selected I051/I060/Lane5 1.69/Lane5 1.75/service-registry regressions run
   through `hhs_runtime.testing.native_pytest_provider_v1`.
6. Native pytest produces a deterministic 216-character Hash216 receipt stored
   with benchmark evidence.
7. `HHS_LANE5_PROVIDER_CONTEXT=runtime`.
8. All implemented Lane 5 providers must resolve native.
9. Declared incomplete providers remain runtime fail-closed; no implicit
   external fallback is permitted during the benchmark.
10. FastAPI must report native selection.
11. The benchmark harness records the full Lane 5 provider matrix.
12. Existing HNAN, one-million-candidate, Q-info normalization, real-world
    repository/ledger, circular-attractor, Pass214 compound, Pass212 full
    50,388,480-position hydration, and raw5184 audio workloads remain included.

## Environment state

Prepared hosted benchmark target:

- runner: Ubuntu 24.04
- Python: 3.12
- `PYTHONHASHSEED=0`
- `PYTHONDONTWRITEBYTECODE=1`
- `HHS_LANE5_PROVIDER_CONTEXT=runtime`
- cumulative exact ABI built before dependency-scoped tests
- `LD_LIBRARY_PATH` points at repository `hhs_runtime/builds`
- `HHS_DISABLE_C_AUTOBUILD=1` for scoped runtime validation
- Python validation dependencies: NumPy and cryptography only
- upstream pytest: absent
- external FastAPI/Starlette: absent

## Validation completed/frozen

- PR #656 Lane 5 native-provider policy: merged.
- PR #658 Pass 220 I062 native pytest provider: merged.
- I062 is the authoritative installer validation path rather than external
  `python -m pytest`.
- R3 harness/workflow preparation is complete.
- Native-default provider assertions are embedded in the harness.
- Native-pytest receipt assertions are embedded in the campaign seal.
- Exact-work/equality/negative-control gates from the earlier campaign remain
  intact.
- No post-provider R3 benchmark run has been launched.
- No timing result has been promoted from stale-index or pre-provider runs.

## Validation remaining

1. Repair the structural registry parse failure for
   `hhs_backend/server.py` in the Hash216 deep-index path.
2. Rerun only the affected Hash216 repository-index workflow.
3. Require the refreshed repository hydration receipt to bind the then-current
   main/index source rather than `649917c9...`.
4. If main moves because the regenerated projection is committed, use that new
   exact main SHA as the R3 benchmark base.
5. Create `bench/lane5-integrated-benchmark-20260929-r3` from that exact main.
6. Copy the three prepared benchmark files and replace
   `__BENCHMARK_BASE_SHA__` with the exact refreshed main SHA.
7. Commit the workflow last so only the complete R3 state triggers execution.
8. Run and inspect the integrated benchmark.
9. Accept timing only if all exact correctness/replay/authority gates pass.
10. Seal metrics and bottleneck evidence into repository-visible artifacts.

## Exact next action

**Do not launch R3 yet.**

Repair only the Hash216 deep-index structural parser frontier that rejects
`hhs_backend/server.py`. Preserve the merged native-provider and I062
contracts unchanged unless the parser repair exposes a genuine dependency.

Then run the dependency-scoped Hash216 index refresh once. When its receipt is
current, create R3 from that exact main/index root and execute the prepared
benchmark campaign.

## Benchmark result policy

- Timing remains observational.
- Exact work reduction, replay equality, selected-route equality, negative
  controls, provider identity, and authority boundaries are acceptance gates.
- A failed stage invalidates downstream timing for that run.
- Historical timing anchors may be compared only after a new green campaign;
  they are not current reproduced measurements.
- Repair forward only from the first attributable failure.
