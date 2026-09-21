# Pass 220 Production Recovery Before Frontend Integration — Restart

Date: 2026-09-21

## Base

- repository: `danonbrez/Holofractal_Harmonicode`
- base branch: `main`
- base commit: `eccfd7e7922ae68386dd43f8e041b41f6a89d467`
- working branch: `pass220-production-recovery-before-frontend-20260921`
- merge target: `main`

## Why this cycle is required

The backend-first ordering is frozen as:

```text
secure Ubuntu application VM backend
-> exact-main production promotion
-> public /vm-api/ verification
-> only then Runtime OS / FastAPI frontend wiring
```

For current main, `DigitalOcean Production Exact Main` run
`35637112279` failed during the guarded promotion bootstrap. The exact failure
was not SSH, bundle construction, host trust, or transfer. The production
service was inactive and the recovery gate required the terminal receipt to be
exactly `ROLLBACK_HEALTH_FAILED`.

The actual terminal receipt was:

```text
schema=HHS_GUARDED_UPDATE_RECEIPT_V2
phase=validation
outcome=VALIDATED
previous_sha=e9e6fa60752df4ea8d289037330c99a0c92a8e2a
candidate_sha=baaa1799f8772631e1b8904cbc8b0621dd8d5323
runtime_os_bundle_sha=baaa1799f8772631e1b8904cbc8b0621dd8d5323
```

A `VALIDATED` record is written before the live service stop/final
reconciliation/promotion sequence. Therefore a process interruption after
validation can leave the service down without a rollback receipt.

## Repair

Adds one shared verifier:

`deployment/digitalocean/guarded_auto_update/verify-recovery-state.py`

It admits only two recovery classes.

### 1. Existing rollback-health failure

```text
phase=rollback
outcome=ROLLBACK_HEALTH_FAILED
live HEAD == receipt.previous_sha
```

### 2. Proven validated pre-promotion interruption

All of the following are mandatory:

```text
latest.phase=validation
latest.outcome=VALIDATED
latest.candidate_sha == latest.runtime_os_bundle_sha
live HEAD == latest.previous_sha
an earlier PROMOTED receipt exists for latest.previous_sha
that PROMOTED receipt has matching candidate/bundle SHA
repository_root and branch match the live production boundary
port 8080 has no competing listener
```

This deliberately rejects:

- a standalone `VALIDATED` receipt with no prior promoted rollback boundary;
- a live checkout already advanced to the interrupted candidate;
- candidate/bundle identity mismatch;
- receipt branch/repository mismatch;
- malformed or missing 40-character SHAs;
- every other terminal outcome.

## Files changed

- `.github/workflows/digitalocean-production-main.yml`
- `deployment/digitalocean/guarded_auto_update/install.sh`
- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh`
- `deployment/digitalocean/guarded_auto_update/verify-recovery-state.py`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
- this restart record

## Authority preservation

No VM81, Hash72, Hash216, Lane 5, capability-token, operation-registry, or
frontend authority is changed.

The repair changes only production deployment recovery admission. Existing
pinned SSH, fast-forward-only promotion, host-drift preservation, exact bundle
identity, single-listener checks, health checks, rollback, and timer ownership
remain mandatory.

## Validation plan

Dependency-scoped exact-head validation must prove:

1. shell syntax and Python compile;
2. shared recovery verifier positive/negative cases;
3. existing guarded-update and Runtime OS bundle contracts;
4. exact-main workflow order;
5. fail-closed installer recovery;
6. no weakening of fast-forward, drift, bundle, rollback, or health gates.

After merge:

1. verify `DigitalOcean Production Exact Main` promotes the exact merge SHA;
2. verify public Runtime OS HTTPS;
3. verify `Pass 220 Ubuntu Application VM Production` runs instead of skipping;
4. verify public `/vm-api/openapi.json`;
5. verify anonymous protected call returns 401;
6. verify signed short-lived capability status call succeeds;
7. only then create the Pass 220 Runtime OS/frontend adapter cycle.

## Restart rule

If production recovery still rejects, use the verifier's exact failure code and
repair forward. Do not bypass the verifier or manually force the service state.
