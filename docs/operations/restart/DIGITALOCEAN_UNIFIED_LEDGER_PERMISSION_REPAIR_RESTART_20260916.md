# DigitalOcean Unified Ledger Permission Repair Restart — 2026-09-16

## Restart identity

- Base exact main: `bf0fc25ed06073dcc4ade384ce05b9d7c7826aa6`
- Branch: `agent/digitalocean-ledger-permission-repair-20260916`
- Pull request: `#468` — `Repair production unified ledger service permissions`
- Green implementation head before this restart record: `6c762af661b64b37ab1c212b69553ea230e0c834`
- Merge target: `main`
- Triggering failed exact-main production run: `35054474028`
- Triggering deploy job: `104661694062`

## Frozen production evidence

Run `35054474028` proved the previously merged transition-only Hash72 recovery worked. It produced:

- `HHS_PRODUCTION_UNIFIED_LEDGER_RECOVERY_VERIFIED=1`;
- recovery backup directory `/var/lib/hhs-guarded-update/unified-ledger-recovery/20260916T041252.617912Z-95031c17ac99ad23`;
- recovery receipt `/var/lib/hhs-guarded-update/unified-ledger-recovery/20260916T041252.617912Z-95031c17ac99ad23/recovery-receipt.json`;
- repaired entry count `6943`;
- repaired `ledger_hash72` `Otq/ghDdPGHbLroXIQJX61Qa`;
- repaired `tip_hash72` `5Lg?R!els9C1)W14xo>wlPHI`;
- terminal prior guarded-update outcome `ROLLBACK_HEALTH_FAILED`.

The next failure was not ledger-content validation. The restarted `hhs` service repeatedly raised:

`PermissionError: [Errno 13] Permission denied: '/var/lib/hhs/data/runtime/hhs_unified_hash72_ledger.json.journal.jsonl'`

The root cause is the recovery helper's root-run atomic replacement: a new temporary journal was created and swapped into place without preserving the original journal UID/GID/mode. The production checkout normalizer did not cover the persistent runtime-ledger permission surface.

SSH host-key verification, deploy credential authentication, bundle build/seal, and transfer remained green. Do not rotate SSH trust for this incident.

## Changed files

1. `hhs_runtime/hhs_unified_hash72_ledger_recovery_v1.py`
2. `deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py`
3. `tests/test_hhs_unified_hash72_ledger_recovery_v1.py`
4. `tests/test_hhs_digitalocean_ledger_recovery_boundary_v1.py`
5. `docs/operations/restart/DIGITALOCEAN_UNIFIED_LEDGER_PERMISSION_REPAIR_RESTART_20260916.md`

## Repair contract

### Atomic recovery authority preservation

The transition-only recovery now captures the existing journal UID, GID, and mode, applies them to the fsynced temporary replacement before `os.replace`, and verifies the authority metadata remains identical after replacement. Restore follows the same rule. Recovery fails closed if ownership cannot be preserved.

### Existing live-state permission repair

Because production already contains a content-valid but root-owned journal from the prior successful repair, the DigitalOcean normalizer now has a narrow runtime-state permission boundary covering only:

- the configured runtime output directory;
- `hhs_unified_hash72_ledger.json`, when present;
- `hhs_unified_hash72_ledger.json.journal.jsonl`, when present.

It grants the configured service group only the read/write/traverse bits required for canonical ledger reads and appends. It does not recurse through `/var/lib/hhs` or mutate unrelated runtime files.

This permission normalization runs both before and after transition recovery. Therefore the already-repaired live ledger can return `LEDGER_VALID` without rewriting content while its service access is restored.

### Fail-closed path authority

Runtime output, snapshot, and journal symlinks are rejected before any permission mutation. The negative test verifies symlink refusal leaves both the runtime directory and target metadata/content unchanged.

## Dependency-scoped validation

Implementation head `6c762af661b64b37ab1c212b69553ea230e0c834`:

- PR #468 observed open, non-draft, and mergeable against exact base `bf0fc25ed06073dcc4ade384ce05b9d7c7826aa6`.
- `DigitalOcean Production Exact Main` PR run `35057607544`:
  - deployment contract: **PASS**;
  - live deployment: correctly **SKIPPED** in pull-request context.
- `HHS Ledger Latency Repairs` run `35057607521`:
  - dependency installation: PASS;
  - native kernel build/verification: PASS;
  - one-command entrypoints: PASS;
  - repaired Python surfaces compile: PASS;
  - dependency-scoped regression tests, including permission preservation and zero-write symlink refusal: **PASS**;
  - ledger latency benchmark: still running when this restart record was sealed.
- The immediately preceding implementation head `cbdfc1ddf75c6bf304c4d773b24257138010b976` completed the same ledger/native gate including its benchmark successfully. The only later code delta is zero-write symlink preflight ordering plus its negative test.

Under the repository responsiveness policy, do not delay the restartable checkpoint or merge solely for the remaining external benchmark timing when the affected regressions are already green.

## Production mutation state

No manual `chmod`, `chown`, ledger rewrite, SSH change, droplet reboot, or direct production filesystem mutation was performed from this branch. Production remains recoverable only through the guarded exact-main workflow.

## Exact next action

```text
1. Merge PR #468 with an exact expected-head guard after confirming main has not moved unexpectedly.
2. Verify the resulting exact main SHA.
3. Inspect the new DigitalOcean Production Exact Main run.
4. Require production evidence for:
   - HHS_PRODUCTION_UNIFIED_LEDGER_PERMISSIONS_VERIFIED=1;
   - LEDGER_VALID or a narrowly justified transition-only repair;
   - HHS_PRODUCTION_UNIFIED_LEDGER_SERVICE_RW_VERIFIED=1;
   - restored rollback/pre-promotion service health;
   - exact-main candidate promotion;
   - public HTTPS Runtime OS verification.
5. Verify public `/api/system/status`, `/api/interface/status`, `/`, `/health`, and `/api/v1/pass174/status`.
6. Execute one harmless real file ingress through `/api/v1/pass174/sdlc/run` and persisted Hash216-vector readback through `/api/v1/pass174/hash216/query` when an operation key is returned.
7. Record the final deployment/ingress receipts and verify exact main remains production source authority.
```

Do not replace this repair with recursive permission widening, ledger deletion/rebuild, validation suppression, SSH trust weakening, or manual production mutation that bypasses the guarded workflow.
