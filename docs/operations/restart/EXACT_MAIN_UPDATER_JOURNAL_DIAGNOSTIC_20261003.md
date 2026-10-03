# Exact-Main updater-journal diagnostic restart — 2026-10-03

## Authority

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base/current main: `9749e3a09046b1f95e809152bb80cc5a9ef65211`
- branch: `repair/exact-main-updater-journal-diagnostics-20261003`
- merge target: `main`
- preceding repair PR: `#696`
- PR #696 merge: `39390872f82ee39ddb1b6954845b576f4f1f7838`
- Hash216 generated main: `9749e3a09046b1f95e809152bb80cc5a9ef65211`

## Verified preceding closure

PR #696 repaired candidate filesystem-ledger isolation. Its exact-head required gates were green before merge.

Merge-triggered Hash216 run `37129179148`:
- generated repository projection: PASS;
- commit to main: PASS;
- explicit Exact-Main dispatch for generated current main: PASS.

The resulting authoritative main is `9749e3a09046b1f95e809152bb80cc5a9ef65211`.

## New production failure boundary

Authoritative Exact-Main workflow-dispatch run:
- run: `37129375877`
- deploy job: `111221286629`

The deployment contract passed. SSH authority, Runtime OS bundle build/transfer, checkout permission normalization, unified Hash72 ledger permissions/recovery, host-drift cleanliness, and pre-promotion service health all passed.

The outer Exact-Main wrapper then failed because synchronous:

`systemctl start hhs-guarded-update.service`

returned failure from `install.sh`. The wrapper reported exit `24`.

The existing Exact-Main failure diagnostics printed `hhs.service` state but did not print the failing `hhs-guarded-update.service` journal or guarded-update receipts, so the exact updater invariant is not yet evidenced.

The diagnostic output does show `hhs.service` active and Runtime OS readiness complete on release/main identity `9749e3a09046b1f95e809152bb80cc5a9ef65211`. This is not accepted as deployment closure because the guarded updater did not return success and public HTTPS verification was skipped.

No `production checkout is dirty after promotion` failure was emitted in this run. The filesystem-ledger repair is therefore not reclassified as failed from the available evidence.

## Diagnostic-only repair

`.github/workflows/digitalocean-production-main.yml` now emits on `install.sh` failure:

- production checkout HEAD and short status;
- full `hhs-guarded-update.service` status;
- updater `ActiveState`, `SubState`, `Result`, `ExecMainCode`, and `ExecMainStatus`;
- last 800 updater journal lines;
- last 30 guarded-update receipts when present;
- `last-success.json` when present;
- the pre-existing `hhs.service` diagnostics.

No deployment, rollback, validation, membrane, listener, nginx, ledger, or runtime behavior is changed.

`tests/test_hhs_guarded_auto_update_contract_v1.py` requires these fail-only diagnostic tokens.

## Commits

- `de81e90085a5efed3610268678d638d59441bd09` — expose guarded updater failure evidence.
- `31dfdc71f2f23168433fdddc9b0b8b7c153ea009` — require updater failure receipts in deployment contract regression.

## Next transition

1. open PR from this branch;
2. require exact-head deployment/Pass 202/source/runtime gates green;
3. expected-head merge;
4. follow Hash216 generated-main projection and explicit Exact-Main redispatch;
5. inspect the guarded updater journal/receipt if promotion still fails;
6. repair only the evidenced updater invariant;
7. require PROMOTED receipt, clean checkout, Lane 5/nginx zero-bypass, and public HTTPS closure.
