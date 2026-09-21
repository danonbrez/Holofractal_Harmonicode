# Pass 220 Production Runtime Recovery — 2026-09-21

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main: `857f2c1c43fe734560a7ecf8fc615e1d049a530a`
- Branch: `repair/pass220-production-runtime-recovery-20260921`
- Merge target: `main`
- Failed exact-main run: `35630070715`
- Failed deploy job: `106434092151`
- Failure step: `Bootstrap guarded updater and promote exact main`
- Production host: `hhs-production-01` / `165.227.220.193`

## Frozen failure evidence

The exact-main run proved these stages before failure:

- deployment contract: PASS;
- exact source checkout: PASS;
- Runtime OS bundle build/seal: PASS;
- production SSH secret presence: PASS;
- pinned host-key and SSH credential verification: PASS;
- exact Runtime OS bundle transfer: PASS.

The live production service was inactive and no competing listener was reported
on port 8080. Recovery then rejected the host because the terminal guarded
receipt was:

- schema: `HHS_GUARDED_UPDATE_RECEIPT_V2`;
- phase: `validation`;
- outcome: `VALIDATED`;
- candidate: `baaa1799f8772631e1b8904cbc8b0621dd8d5323`;
- previous: `e9e6fa60752df4ea8d289037330c99a0c92a8e2a`.

The inherited recovery gate admitted only terminal
`ROLLBACK_HEALTH_FAILED`, so exact-main stopped before fetching/promoting the
new target.

## Coupled pre-existing production boot defects

PR #530 had already isolated two production defects but remained a stale draft
62 commits behind current main:

1. `hhs_runtime_api_server_v1.py` created
   `demo_reports/runtime_api` relative to the protected source checkout during
   import. Under production `ProtectSystem=full`, user `hhs` cannot create
   that directory, so the backend can crash before binding port 8080.
2. the installed guarded permission normalizer derived its recovery import root
   from `/usr/local/lib/hhs-guarded-update`, resolving to `/usr` instead of
   the validated live repository and causing `ModuleNotFoundError: hhs_runtime`
   during rollback recovery.

Those deltas are ported onto this current-main repair branch rather than
merging the stale PR.

## Repair

### Production runtime artifact state

`hhs_runtime_api_server_v1.py` now selects:

1. `HHS_RUNTIME_API_ARTIFACT_ROOT`, if explicit;
2. `HHS_RUNTIME_OUTPUT_DIR/runtime_api` in production;
3. legacy `demo_reports/runtime_api` only as local fallback.

### Installed rollback import root

`normalize-service-permissions.py` binds recovery imports to the explicit,
already-validated `repo-root` argument rather than to `__file__` parents.

### Bounded interrupted-VALIDATED recovery

The recovery membrane retains the inherited
`ROLLBACK_HEALTH_FAILED` behavior. It additionally admits a terminal
`VALIDATED` receipt only when all of these are true:

- service is inactive;
- port 8080 has no listener;
- receipt schema is exactly `HHS_GUARDED_UPDATE_RECEIPT_V2`;
- receipt branch is `main`;
- receipt repository root resolves to the production checkout;
- receipt phase is `validation`;
- candidate and predecessor are exact 40-hex SHAs;
- current live HEAD equals either the receipt candidate or predecessor.

For `ROLLBACK_HEALTH_FAILED`, the existing predecessor-health restoration path
is unchanged.

For bounded `VALIDATED`, the installer does not pretend the broken predecessor
is healthy. It proceeds directly to the inherited guarded updater, which still:

- fetches and proves expected repository/branch;
- requires a fast-forward descendant;
- validates the isolated exact candidate;
- verifies the exact prebuilt Runtime OS bundle;
- reconciles host drift;
- promotes by `git merge --ff-only`;
- rebuilds native/runtime language assets;
- activates the exact Runtime OS release;
- starts the service;
- requires post-promotion health;
- rolls back on any promotion failure and writes the inherited receipts.

## Pass 202 successor reseal

Historical Pass 202 identities are unchanged.

Current successor identities advance only for:

- `deployment/digitalocean/guarded_auto_update/install.sh`:
  `f964e2daf6fad4dd716fb74613a02ddf2caf2f7c`;
- `deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py`:
  `6934f540060f36ca78b6e4dc2b2461d8327f54b9`.

## Validation surfaces

Added/extended:

- `tests/test_hhs_production_runtime_artifact_root_v1.py`;
- `tests/test_hhs_digitalocean_ledger_recovery_boundary_v1.py`;
- `tests/test_hhs_guarded_auto_update_contract_v1.py`;
- Runtime OS production-root workflow coverage;
- DigitalOcean exact-main path coverage;
- Pass 202 exact/synthetic successor checks.

## Remaining gate

1. Open the repair PR from this exact branch.
2. Require dependency-scoped exact-head CI.
3. Merge only the current-main repair, not stale PR #530.
4. Require exact-main production promotion to emit `PROMOTED`.
5. Require public Runtime OS HTTPS verification.
6. Require the chained Pass 220 Ubuntu Application VM Production workflow:
   Ubuntu GUI components, `hhs-vm` Bash parity, loopback-only port 8720,
   nginx `/vm-api/`, OpenAPI security, unauthenticated 401, signed-capability
   public status.
7. Only after those production receipts are green begin frontend/FastAPI client
   wiring.
