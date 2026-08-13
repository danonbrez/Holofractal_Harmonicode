# Pass 218 Full Implementation — Iteration 8 Restart State

## Authority

- Pass: 218 — native corpus / relational curriculum / narrative hydration.
- Iteration: 8 — Runtime-OS and service lifecycle integration.
- Base validated Iteration-7 head: `8b4ef996fe16a5c5506542ad9d3395cdf1854d5b`.
- Branch: `agent/pass218-full-iteration8-runtime-os-lifecycle`.
- Merge target: `main`.
- Main observed at Iteration-8 start: `b0656a92ab29507f81eae760e070f74e49db83f4`.
- Latest implementation/evidence head before this restart record: `b807c0a4d7cd4d50d7e84f917a65a539fc56b90b`.
- Pass 218 remains **IN DEVELOPMENT**; this record freezes Iteration 8 only.

## Implemented surface

Iteration 8 composes the frozen Iteration-6 canonical commit boundary and the validated Iteration-7 durable store into the real Runtime-OS service lifecycle.

Canonical lifecycle:

```text
service object created
        ↓
Pass-218 ingress CLOSED
        ↓
FastAPI inherited lifespan startup
        ↓
I7 manifest/generation restore + receipt/VM81 validation
        ↓
valid empty first boot OR valid restored/recovered canonical target
        ↓
Pass-218 ingress OPEN
        ↓
I5-authorized candidate → I6 atomic canonical commit
        ↓
Pass-218 ingress CLOSED
        ↓
I7 durable checkpoint + manifest publication
        ↓
Pass-218 ingress OPEN
        ↓
service shutdown closes ingress first
        ↓
latest committed target idempotently checkpointed
```

If durable publication fails after a successful I6 atomic mutation, the canonical mutation remains real but ingress stays closed in `CANONICAL_COMMITTED_DURABILITY_BLOCKED`. `retry_pending_durability()` persists that exact already-committed target; it does not request another Iteration-5 authorization or perform another Iteration-6 canonical transition.

Startup with a present but invalid/unrecoverable durable manifest is fail-closed for Pass-218 ingestion (`STARTUP_RECOVERY_BLOCKED`) while the surrounding Runtime-OS can remain available for diagnostics. If the active generation is damaged but the immediately previous manifest-bound generation validates, startup binds only that previous sealed generation and reports `RECOVERED_PREVIOUS_READY`.

## Runtime-OS integration

New lifecycle binding: `hhs_backend/runtime_os_pass218_lifecycle.py`.

It:

- installs one lifecycle object on FastAPI application state;
- wraps the inherited lifespan rather than replacing inherited startup/shutdown semantics;
- restores Pass-218 durable authority before yielding application startup;
- checkpoints on service shutdown;
- exposes diagnostic-only `GET`/`HEAD /api/runtime/pass218/lifecycle/status`;
- does not expose a public canonical mutation route;
- installs before the final Runtime-OS SPA root projection in both Runtime-OS entrypoints.

DigitalOcean systemd configuration now binds the durable root explicitly:

```text
HHS_PASS218_STATE_ROOT=/var/lib/hhs/pass218
```

The existing `/var/lib/hhs` writable systemd state boundary admits this path. The production service remains a single Uvicorn worker, matching the Iteration-8 in-process lifecycle ownership model.

## Changed files

- `hhs_runtime/pass218/lifecycle.py`
- `hhs_runtime/pass218/__init__.py`
- `hhs_backend/runtime_os_pass218_lifecycle.py`
- `hhs_backend/runtime_os_visual_server.py`
- `hhs_backend/runtime_os_application_server.py`
- `deploy/digitalocean/hhs-pass196-integrated-environment.service`
- `tests/pass218/test_pass218_iteration8_runtime_os_lifecycle.py`
- `tools/pass218_iteration8_evidence.py`
- `.github/workflows/pass218-full-iteration8.yml`
- `docs/pass218/PASS_218_ITERATION_8_RESTART.md`

## Validation completed before restart record

Dedicated `Pass 218 Full Iteration 8` run `31658493969` completed successfully on exact implementation/evidence head `b807c0a4d7cd4d50d7e84f917a65a539fc56b90b`.

- cumulative Pass-218 + Runtime-OS compilation: PASS
- no-authoritative-float AST gate: PASS
- Iteration 1: 12 passed
- Iteration 2: 13 passed
- Iteration 3: 12 passed
- Iteration 4: 14 passed
- Iteration 5: 18 passed
- Iteration 6: 19 passed
- Iteration 7: 21 passed
- Iteration 8: 23 passed
- repository-native crawler: 14 passed
- Runtime-OS production-root acceptance: 6 passed
- repository-native Iteration-8 lifecycle evidence: PASS

An earlier evidence run failed only because its crash-restart equality was evaluated after the same lifecycle had intentionally been advanced by the second commit. The evidence was repaired to freeze the restart equality immediately after restart; no runtime implementation semantics changed for that repair.

## Repository-native evidence

Workload: `creative_writing/novels/THE_SMALLEST_PERMISSION.md`.

- source SHA-256: `42caa64e6d75aeeedb256f8e9c72b773ab9e5e230bcbc63e76bdff59fae37c03`
- structural narrative beats: 61
- transaction ID Hash72: `9ckHe3R(Hr<W0gU9MA5jYr/UdZCcHHXjY/LZyksp3D>OICUnbFAU<Q-Tw1r/piFmdaZb5D!+`
- candidate entry ID: `2cb8dffce47850123f6f6878ce8e4c107670e493c4d681963d1fde0051fa2eae`
- VM5184 projection SHA-256: `7496cdb5047f7609397ba06adbc0e9c303efd4d9240f9b6a6198164df70b2baa`
- generation-0 checkpoint SHA-256: `7e530edad49a1e215a987e3eaf2300f6328d6182d4f215f02a0cfbf095233025`
- generation-0 canonical root Hash72: `75/?bFggnzcBCYVLK77uPS2jN*EsJ/eRugVtkKSw-gYMFJB?LvXLpJ4tht42SzJF/<C?HWeS`
- generation-0 manifest sequence: 0
- crash restart: `RESTORED_READY`
- crash-restart root equality: true
- crash-restart VM81 snapshot equality: true
- crash-restart consumed I6 receipt equality: true
- restart new authorization minted: false
- restart new canonical mutation invoked: false
- injected post-I6/pre-manifest failure: `P218_I8_COMMIT_DURABILITY_CHECKPOINT_FAILED`
- blocked-state canonical commit count: 2
- blocked-state ingress closed: true
- blocked-state durability pending: true
- durability retry state: `DURABLE_CHECKPOINT_COMMITTED`
- retry root unchanged: true
- retry consumed receipt unchanged: true
- retry reopens ingress: true
- generation-1 manifest sequence: 1
- generation-1 previous checkpoint SHA-256 equals generation-0 checkpoint: true
- corrupted active generation recovery: `RECOVERED_PREVIOUS_VALID_GENERATION`
- fallback lifecycle state: `RECOVERED_PREVIOUS_READY`
- fallback generation-0 root/snapshot equality: true
- source text in persisted generations: false
- source text in authority records: false
- Pass-165 source-retaining path invoked: false
- canonical learning commit invoked: false
- truth promotion: false
- action authority minted: false
- verbatim source retained: false

## Restart instructions

1. Start from this branch and verify its current head before editing.
2. Do not rewrite or normalize frozen Iteration-6 receipts; Iteration 7 owns their compatibility membrane.
3. Do not bypass `Pass218RuntimeLifecycle` when composing Pass-218 canonical service activity.
4. Preserve the rule that a successful I6 mutation whose I7 checkpoint fails closes ingress until the same committed target becomes durable.
5. Preserve first-boot semantics: absence of a manifest is an empty ready state; presence of invalid authority is not.
6. Preserve source purge and the explicit exclusion of the Pass-165 source-retaining path.
7. Rerun only dependency-scoped gates affected by future changes plus the inherited final integration gate.

## Remaining integration concern

Iteration 8 deliberately binds one durable lifecycle owner to the repository's production single-worker Uvicorn service. Cross-process or horizontally replicated canonical writers would require an explicit process/distributed lease or compare-and-swap authority over manifest generation before multiple workers may write the same Pass-218 durable root. Do not infer multi-writer safety from Iteration 8's in-process `RLock` plus filesystem atomic replacement.

A subsequent iteration may formalize multi-process/distributed canonical ownership, lease expiry/recovery, and split-brain prevention if Pass 218 is intended to admit multiple concurrent service writers.
