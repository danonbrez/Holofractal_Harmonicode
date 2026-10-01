# Pass 220 external frontend / Pass 219 1.76 reconciliation restart — 2026-10-01

## Restart identity

- Parent checkpoint: `bbb92bd83520310c348375164b3cbe921f720dc1`
- Parent PR: #674 `pass219-lane5-global-capability-visibility-1-76`
- Branch: `pass220-reconcile-588-global-capability-1-77`
- Merge target while stacked: `pass219-lane5-global-capability-visibility-1-76`
- Final merge target after #674 lands: `main`
- Source lineage recovered from stale PR #588: external ingress/egress benchmark and nonblocking host-warming acceptance only.
- Explicitly rejected from #588: Pass219/220-only capability discovery, static narrow tool inventory, and any semantics that remove discovered capabilities from Lane 5 visibility.

## Implemented

1. Production mobile ingress is aligned with the authoritative Pass 165 `MAX_SOURCE_BYTES = 16 MiB` bound instead of permitting 24 MiB and failing later in the pipeline.
2. The real browser/API/native external ingress-egress benchmark is restored.
3. Benchmark host state now targets `HHS_PASS219_LANE5_CAPABILITY_STATE_ROOT`.
4. Benchmark readiness reads `/api/runtime/pass219/lane5/capabilities/status`.
5. Acceptance asserts Pass 220 is host-only and has no Lane 5 selection, runtime-validation, or canonical-mutation authority.
6. Static acceptance now validates the Pass 219 1.76 nonblocking capability lifecycle rather than #588's obsolete global-tool lifecycle.
7. Contract preserves global visibility:
   `DiscoveredCapability AND NOT ExplicitNonExecutableEvidence => VisibleToLane5`.
8. Demo/reference/disabled/needs_adapter/needs_configuration/not_ready remain metadata unless explicit non-executable evidence exists.

## Changed files

- `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
- `hhs_verification/pass220/__init__.py`
- `hhs_verification/pass220/external_frontend_ingress_egress_benchmark_v1.py`
- `tests/pass220/test_hhs_pass220_external_frontend_ingress_egress_v1.py`
- `contracts/pass220/PASS_220_EXTERNAL_FRONTEND_INGRESS_EGRESS_LOSSLESS_NONBLOCKING_V1.md`
- `.github/workflows/pass220-external-frontend-ingress-egress-benchmark.yml`
- this restart record

## Validation state

- Source reconciliation: complete.
- Exact parent: frozen at `bbb92bd83520310c348375164b3cbe921f720dc1`.
- #674 dedicated dependency-scoped workflow: still externally queued at time of branch creation; no green claim is made here.
- This branch's workflow is the dependency-scoped executable validation for the restored browser/API/native benchmark.
- Required checks: Python compile, Pass 219 1.76 visibility tests, Pass 220 host hydration tests, Pass165/Pass174 ingress preservation, native 648-byte/RNA regressions, Runtime OS typecheck/build, Chromium benchmark, concurrency/nonblocking checks, oversize frontend preflight, negative media/API checks, and evidence sealing.

## Remaining closure

1. Consume #674 scoped CI when it completes; repair only attributable failures.
2. Merge #674 and verify `main`.
3. Retarget this branch/PR to `main` without changing the inherited Pass 219 1.76 authority.
4. Run/consume this branch's dependency-scoped benchmark CI.
5. Repair only attributable failures.
6. Merge, verify `main`, and close stale #588 as superseded if no unreconciled useful delta remains.

## Authority boundaries

The browser, FastAPI host, benchmark, vector projection, and Pass 220 lifecycle have no direct Linux/service bypass into canonical HHS state, no Lane 5 selection authority, no runtime-validation authority, and no Hash72/Hash216 mint or canonical mutation authority. Capabilities remain visible to Lane 5 and become executable only through their declared typed contract and the normal C++ RNA/PQC runtime-validation membrane.
