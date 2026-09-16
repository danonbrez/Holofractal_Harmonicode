# DigitalOcean Unified Hash72 Ledger Recovery Restart — 2026-09-15/16

## Restart identity

- Base exact main: `09f4366a0dc565a41ca41be4708bd015c5fca0fe`
- Branch: `agent/digitalocean-ledger-recovery-20260915`
- Pull request: `#467` — `Repair production Hash72 ledger recovery and isolate status probe writes`
- Green implementation head: `f84e94e984fad4fe515a13830acdbae14c089a59`
- Pre-merge restart head: `8bec9e57b73849dce82abd5f472b533168d12dd6`
- Merged exact main: `bf0fc25ed06073dcc4ade384ce05b9d7c7826aa6`
- Merge target: `main`
- Failed exact-main production run that triggered this repair: `35038495093`
- Current exact-main production recovery run: `35054474028`

## Frozen production evidence

PR #466 had already merged the mobile-first Runtime OS control surface, real Pass 174 multimodal file ingress/readback, corrected DigitalOcean target, and strict SSH preflight into exact main `09f4366a0dc565a41ca41be4708bd015c5fca0fe`.

Run `35038495093` proved the following production boundaries before failing:

- deployment contract: PASS;
- Runtime OS bundle build and sealing: PASS;
- pinned SSH target configuration: PASS;
- strict SSH host-key and deploy-credential preflight: PASS;
- bundle transfer to production: PASS.

The failure occurred only in `Bootstrap guarded updater and promote exact main`.

The live unified Hash72 ledger failed warm validation at `journal:6930` with:

1. `journal entry_count mismatch`: expected `6930`, actual `6929`;
2. `journal transition payload mismatch`: authoritative entry hash/tip and prior ledger hash remained aligned, while the transition payload carried entry count `6929` instead of `6930`;
3. `journal Hash72 accumulator witness mismatch`.

No logged parent-link, entry-payload, or entry-hash mismatch accompanied this incident. Rollback to predecessor `a8fc0646e21b2a67804468575f364fef1762ec6a` encountered the same persistent runtime ledger and terminated with guarded-update outcome `ROLLBACK_HEALTH_FAILED`.

The production service uses `HHS_RUNTIME_OUTPUT_DIR=/var/lib/hhs/data/runtime`, so the affected state is outside Git checkout rollback and correctly persisted across candidate/predecessor source transitions.

## Root concurrency boundary

The production service uses one Uvicorn worker, but `RuntimeBootstrapGateway` periodically launches `python -m hhs_backend.runtime_status_probe` as a separate process. The child inherits the production runtime environment. Prior to this repair it imported the authoritative application and could reach route surfaces backed by `HHSIOGateway`, whose receipt creation calls unified-ledger `append_payload`.

The unified ledger's existing `_lock_for` authority is a Python `RLock`, which is process-local. Therefore the status-probe child was a concrete second process capable of writing the same append-only journal without sharing the live worker's in-process lock. This repair removes that competing writer while retaining real ledger reads in the probe.

## Changed files

1. `hhs_runtime/hhs_unified_hash72_ledger_recovery_v1.py`
2. `tools/repair_unified_hash72_ledger_transition_metadata.py`
3. `tests/test_hhs_unified_hash72_ledger_recovery_v1.py`
4. `deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py`
5. `hhs_backend/runtime_status_probe.py`
6. `tests/test_hhs_runtime_status_probe_ledger_isolation_v1.py`
7. `tests/test_hhs_digitalocean_ledger_recovery_boundary_v1.py`
8. `.github/workflows/hhs-ledger-latency-repairs.yml`
9. `docs/operations/restart/DIGITALOCEAN_UNIFIED_LEDGER_RECOVERY_RESTART_20260915.md`

## Repair invariants

### Transition-only recovery

`hhs_unified_hash72_ledger_recovery_v1.py` independently proves the authoritative snapshot/journal entry chain before allowing any mutation. Recovery refuses:

- malformed journal JSON;
- snapshot count/tip/ledger-hash corruption;
- journal schema corruption;
- missing journal entry objects;
- parent-link mismatches;
- entry-payload / entry-hash tampering;
- any verifier error outside the explicit transition-metadata allowlist.

The only repairable fields are derived journal metadata:

- `entry_count`;
- `prior_ledger_hash72`;
- `ledger_hash72`;
- `transition_payload`;
- `tip_hash72_kernel_witness`.

Every authoritative journal `entry` object is preserved. Snapshot and journal are backed up first. Journal replacement is atomic. Full-chain verification is mandatory after replacement. A failed post-repair verification restores the original journal. A standalone recovery receipt is written outside the repaired ledger.

### Production recovery boundary

The DigitalOcean normalizer inspects the unified ledger before normal guarded promotion health checks. If the ledger is already valid it performs no ledger mutation.

If and only if the ledger is transition-repairable, production recovery additionally requires the terminal guarded-update receipt to be exactly `ROLLBACK_HEALTH_FAILED`. It then:

1. stops `hhs.service`;
2. verifies no listener remains on port 8080;
3. performs the strict transition-only recovery with backup under `/var/lib/hhs-guarded-update/unified-ledger-recovery`;
4. resets the failed service state;
5. requests `hhs.service` start;
6. leaves service-health acceptance to the inherited guarded installer.

It does not delete the ledger, rebuild arbitrary entries, disable validation, or weaken Hash72 authority.

### Status-probe writer isolation

`hhs_backend.runtime_status_probe` now installs a read-only unified-ledger projection before importing the authoritative visual application. Probe status routes continue to read and fully validate the real production unified ledger, but synthetic probe execution cannot append to it. The main Uvicorn worker retains ordinary canonical append behavior.

## Dependency-scoped validation frozen

Implementation head `f84e94e984fad4fe515a13830acdbae14c089a59`:

- `HHS Ledger Latency Repairs` run `35054349700`: **SUCCESS**.
  - native kernel build/verification: PASS;
  - entrypoint checks: PASS;
  - repaired Python surfaces compile: PASS;
  - dependency-scoped regression tests: PASS;
  - ledger latency benchmark: PASS.
- `DigitalOcean Production Exact Main` PR run `35054349726`: **SUCCESS**.
  - `validate-deployment-contract`: PASS;
  - live deploy correctly skipped for pull-request context.
- PR #467 observed open, non-draft, and mergeable on implementation head before merge.

Merged exact main `bf0fc25ed06073dcc4ade384ce05b9d7c7826aa6`:

- `HHS Ledger Latency Repairs` run `35054474004`: **SUCCESS** on merged main.
- `DigitalOcean Production Exact Main` run `35054474028`:
  - deployment contract: PASS;
  - exact main checkout: PASS;
  - canonical frontend build runtime: PASS;
  - DigitalOcean SSH authority requirement: PASS;
  - Runtime OS bundle build/seal: PASS;
  - pinned SSH target configuration: PASS;
  - strict pinned SSH host/deploy credential preflight: PASS;
  - exact Runtime OS bundle transfer: PASS;
  - `Bootstrap guarded updater and promote exact main`: **IN PROGRESS** at this checkpoint;
  - public HTTPS Runtime OS verification: pending behind guarded promotion.
- DigitalOcean droplet `598826630` (`hhs-production-01`, `165.227.220.193`, `nyc3`) remained `active`; no reboot/shutdown/rebuild was issued.
- Independent HTTPS probes during the owner-held recovery transaction returned no listener. This is not accepted as a terminal deployment result while guarded promotion remains active.

The installer ordering was rechecked on merged main: `normalize_production_checkout` executes before the rollback-boundary `wait_for_production_health` loop. Therefore the transition-only recovery hook is positioned before the 600-second rollback-boundary health wait, and the later portion of the same GitHub step also includes the synchronous candidate updater/promotion.

Unrelated Pass 218/219 workflows are not deployment blockers for this dependency-scoped recovery under repository policy.

## Production mutation state

PR #467 is merged. Production run `35054474028` owns the live guarded deployment transaction. Do not start a competing deployment, reboot the droplet, delete/rebuild the ledger, or push another deployment-triggering commit to `main` while that run owns the transaction.

At this checkpoint the GitHub API does not expose partial text logs for the in-progress deploy job, so there is not yet repository-visible proof that the live transition repair itself completed. Treat the live repair, service recovery, candidate promotion, and public HTTPS result as pending until run `35054474028` reaches a terminal state and its sealed job log can be inspected.

## Exact next action

```text
1. Inspect DigitalOcean Production Exact Main run 35054474028 first; do not launch a competing promotion.
2. If the run succeeds, inspect the sealed deploy job log and require evidence of:
   - HHS_PRODUCTION_UNIFIED_LEDGER_RECOVERY_VERIFIED=1 (or a valid-ledger no-op if another authoritative repair already occurred);
   - recovery backup/receipt path under /var/lib/hhs-guarded-update/unified-ledger-recovery when repair occurred;
   - rollback-boundary health restoration;
   - exact-main promotion of bf0fc25ed06073dcc4ade384ce05b9d7c7826aa6;
   - public HTTPS Runtime OS verification.
3. If the run fails, fetch job 104661694062 logs and repair forward only the newly proven failing boundary. Do not weaken ledger verification.
4. After successful promotion verify public /api/system/status, /api/interface/status, /, /health, and /api/v1/pass174/status.
5. Execute one real multimodal file ingress through /api/v1/pass174/sdlc/run and persisted-vector readback through /api/v1/pass174/hash216/query when an operation key is returned.
6. Verify exact main remains the deployed source authority and record final production receipts.
```

Do not replace this repair with ledger deletion, blind rebuild/compaction, validation suppression, multiple competing writers, SSH trust weakening, or a lightweight semantic-memory substitute for the Pass 174 persistent vector store.
