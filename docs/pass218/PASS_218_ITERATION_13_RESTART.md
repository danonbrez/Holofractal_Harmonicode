# Pass 218 Iteration 13 Restart Record

## Identity

- Pass: 218
- Iteration: 13
- Scope: production authority observability and bounded operator orchestration
- Branch: `agent/pass218-full-iteration13-authority-observability-orchestration`
- Parent / frozen I12 head: `168b41b6db3b25f802c996bf0d61304e3ba8494b`
- Merge target: `main`
- Pass 218 status: **IN DEVELOPMENT**

## Preserved authority hierarchy

```text
I9   local process fence
        +
I10  distributed lease/CAS global fence
        +
I11  verified multi-member mTLS quorum
        ↓
     canonical writer
        +
I12  production maintenance / rotation membrane
        ↓
I13  observability + bounded operator orchestration
```

I13 is downstream and observational. It does not acquire/release ownership, advance an I10 fence, alter I11 quorum semantics, execute I12 maintenance, or mutate the canonical target.

## I13 invariants

1. I9-I12 authority and maintenance implementations remain unchanged.
2. Authority status is derived from the existing lifecycle status record rather than reimplemented.
3. Operator-visible status and actions are Hash72-sealed.
4. Quorum loss is projected as a CRITICAL fail-closed alert.
5. Certificate expiry, snapshot age and rehearsal age use explicit integer policy thresholds.
6. Missing evidence is reported as missing; it is never fabricated as healthy.
7. Operator actions are preparatory receipts only.
8. Credential rotation, member replacement and snapshot rehearsal preparation require an external executor.
9. Maintenance preparation requires I11 quorum.
10. Member-replacement preparation additionally requires the full expected cluster, not merely majority reachability.
11. Operator requests and maintenance-run receipts persist in an append-only JSONL diagnostic journal.
12. A run receipt cannot claim canonical target mutation or authority minting.
13. Automated/operator orchestration has no direct path to the I10 acquire/release or canonical commit surface.
14. RuntimeOS exposes an Authority view for health, fences, quorum, alerts and preparatory operator requests.
15. The browser cannot execute canonical ownership or canonical mutation through I13.
16. No source retention, Pass-165 path, learning commit, truth promotion, action authority or authoritative float is admitted.

## Files introduced or modified

- `hhs_runtime/pass218/observability_i13.py`
- `hhs_backend/runtime_os_pass218_authority_i13.py`
- `hhs_backend/runtime_os_application_server.py`
- `hhs_gui/runtime_os/workspace/AuthorityOperationsPanel.tsx`
- `hhs_gui/runtime_os/workspace/HHSProductWorkspace.tsx`
- `scripts/pass218_iteration13_observability_validation.py`
- `tests/pass218/test_pass218_iteration13_authority_observability_orchestration.py`
- `tests/pass218/test_pass218_iteration13_runtime_os_control_plane.py`
- `.github/workflows/pass218-full-iteration13.yml`
- `docs/pass218/PASS_218_ITERATION_13_RESTART.md`

## Validation design

The I13 workflow must validate the synthetic merge candidate and perform:

- cumulative Pass 218 compile;
- no-authoritative-float enforcement on I13 Python authority/control surfaces;
- I1-I13 dependency-scoped tests;
- RuntimeOS production-root regression;
- strict TypeScript typecheck and Vite build;
- source-visible Authority UI verification;
- a complete real I12 three-member mTLS etcd rotation/replacement/quorum-loss/recovery/snapshot sequence;
- independent I12 snapshot digest re-check;
- I13 authority status built from the resulting real I12 evidence;
- bounded member-replacement preflight receipt over that real recovered state;
- ABORTED preflight run receipt proving that operator orchestration records work without executing or minting canonical authority;
- combined I12/I13 evidence artifact upload.

## Current checkpoint

Initial I13 implementation commits include:

- `31a3a75e975adb1de37911b91e18c81af3c13668` — authority observability/orchestration core
- `1a1ee94531a49222df1880bf980dc56cd5fcf7b1` — I13 core invariant tests
- `025cf92169939272a89c04de69bf06d8c7a6b606` — RuntimeOS/API authority control plane
- `afb1dd2463b045b817dc84aa563fd2df543bea2e` — production application installation
- `b7235cb8e87c2d57bd048ed1b88e82409d5baa4f` — RuntimeOS control-plane tests
- `3fb492990f265a33c6a74ab71401a6053f082a2e` — Authority UI
- `4f4fc8bd5998ad2912cf9260893ed45d7b39608e` — RuntimeOS Authority navigation
- `d56dd1ac9c83066851332aec6ff0ac075dedbb0d` — real-evidence I13 validator
- `95e23f63cf8949274bfec91bb39cbe95b979d9fd` — I13 merge-candidate workflow

Exact-head validation is still required after this restart record. Do not call I13 validated or frozen until the final branch head and synthetic merge candidate pass the dedicated and inherited workflows.

## Next action

1. Open a draft PR against unchanged `main`.
2. Execute the I13 workflow against the synthetic merge candidate.
3. Inspect failures and repair only the affected surface.
4. Re-run impacted validation.
5. Confirm inherited Pass 217 / RuntimeOS / IDE / Pass196 / DigitalOcean workflows on the exact final head.
6. Freeze the validated head and write the terminal PR checkpoint without mutating it.
