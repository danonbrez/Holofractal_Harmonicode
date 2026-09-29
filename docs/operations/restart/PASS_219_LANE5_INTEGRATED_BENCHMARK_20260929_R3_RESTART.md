# Pass 219 Lane 5 Integrated Benchmark R3 — Restart

Status: **R3 INDEX FRONTIER REPAIRED — REVALIDATION PENDING**

## Identity

- Base/main at branch creation: `7f34d20819ddbbb8f470f6b87e92621e47b99de4`
- Branch: `bench/lane5-integrated-benchmark-20260929-r3`
- Merge target: `main`
- Provider policy prerequisite: PR #656 merged
- I062 native pytest prerequisite: PR #658 merged
- Harness commit: `1abd32cc3816c85ad5b72b8795d3c9abfb67bdb3`
- Workflow commit: `ce8c0f4ad595894a86fe4c8d4dbe2fe4cbfe0e3c`

## Why R3

R2 was blocked by an external FastAPI import in the service-registry path.
That is now replaced by the merged Lane 5 native-provider policy.

I062 is also merged, so R3 removes both the temporary external FastAPI
workaround and upstream pytest from the benchmark validation path.

The inherited main repository-index receipt was stale at branch creation:
receipt source `649917c94a54b7d4cf59cace418cc643dd5329a4` versus main
`7f34d20819ddbbb8f470f6b87e92621e47b99de4`.

R3 regenerates the repository dependency graph, Lane 5 hydration knowledge
graph and database receipt from the exact benchmark HEAD before measuring
indexes and asserts generated `source_commit == HEAD`.

## Changed files

- `benchmarks/pass219/pass219_lane5_integrated_services_index_benchmark_20260929.py`
- `.github/workflows/pass219-lane5-integrated-benchmark-20260929.yml`
- this restart record

## Added measurements

- Lane 5 provider registry/status
- runtime native selections and unavailable-native set
- PR fallback capability set and warning receipts
- I062 native pytest cold execution
- I062 execution median/p95
- I062 collect-only median/p95
- deterministic config/collection/result Hash72
- deterministic 216-character I062 receipt
- proof external pytest execution authority is false

## Hosted campaign

The workflow:

1. verifies the exact main lineage;
2. installs bounded dependencies but not upstream pytest or FastAPI;
3. builds the cumulative exact ABI;
4. regenerates and verifies the exact benchmark-head repository index;
5. runs scoped regressions through I062 native pytest;
6. benchmarks integrated services/indexes;
7. runs HNAN;
8. runs the 1M-candidate native scaling workload;
9. normalizes information throughput;
10. runs real-world repository/ledger workloads;
11. runs circular-attractor exact reduction;
12. runs Pass 214 15-family x 11-mode compound validation;
13. checks full 50,388,480-position Pass 212 hydration;
14. runs raw5184 audio;
15. seals and uploads campaign evidence.

Timing remains observational only. Exact parity/replay and negative controls
remain mandatory.

## Hosted run evidence and repair-forward

- Run `36608109734` failed before benchmark timing.
- Run `36608301338`, job `109542917674`, reproduced the same first frontier.
- Build and harness compilation passed.
- Exact-head repository-index regeneration failed inside Lane 5 reverse discovery because `hhs_backend/server.py` was not parseable.
- Root cause: the merged provider boundary contained the literal characters `\\n` between two `os.environ.setdefault(...)` calls instead of a source newline.
- Repair commit: `a2dfabc8550b1ca5bfcd0243b9d73249840c1f48`.
- The repair changes only that tokenization defect; provider selection semantics are unchanged.
- No timing result from the failed runs is accepted because the campaign never passed index regeneration.

## Next action

Use the newest `Pass 219 Lane 5 Integrated Benchmark 2026-09-29 R3` run
triggered from a checkpoint containing `a2dfabc8550b1ca5bfcd0243b9d73249840c1f48`.

If failed, repair only the first attributable R3 frontier. Do not restore
upstream pytest or the temporary FastAPI install as a bypass.

If green, freeze the artifact, extract current metrics, compare observational
timing against historical anchors, commit benchmark evidence, and close the
benchmark delivery path.
