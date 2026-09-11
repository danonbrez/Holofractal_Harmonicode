# Pass 219 DigitalOcean Runtime OS Permission / Rollback Controller Repair — Restart Checkpoint

Date: 2026-09-10 America/New_York / 2026-09-11 UTC

## Authority and branch state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base `main`: `2def7910b99046821f34e1446bcec33ca4fd4090`
- Base tree: `c26796d17744193a1fb1e3aee13166660a3303a9`
- Repair branch: `agent/pass219-runtime-os-release-permission-rollback-controller-repair-20260910`
- Pull request: `#426`
- Dependency-scoped executable head before this documentation checkpoint: `8f593e5b5028665a02291b8e3d41a9f75201434c`
- Pass202 validation run: `34554768917`
- Runtime OS production-root validation run: `34554768965`

## Production failure being repaired

Exact-main production workflow run `34552690793` targeted `2def7910b99046821f34e1446bcec33ca4fd4090` and passed deployment-contract validation, exact checkout, frontend setup, SSH authority, Runtime OS build/seal, pinned host trust, and bundle transfer. It failed inside guarded promotion after the exact Runtime OS release was activated.

The service failed to read:

`/var/lib/hhs/runtime-os/releases/2def7910b99046821f34e1446bcec33ca4fd4090/index.html`

with `PermissionError: [Errno 13] Permission denied`.

Repository inspection established the release-root defect: `tempfile.mkdtemp()` creates the staging root as mode `0700`; bundle extraction normalized descendant files/directories but never normalized the staging root itself. Atomic `os.replace(stage, release)` therefore preserved an untraversable `0700` exact-SHA release directory for the unprivileged `hhs` service identity.

Rollback exposed a second controller-lifecycle defect. The updater reset `/opt/hhs/app` to the predecessor SHA and then called `sync_installed_assets` from that predecessor checkout before restarting the service. That downgraded the already-validated successor updater/permission tooling during the same recovery transaction, reintroducing the predecessor permission verifier and causing the rollback restart boundary to fail.

## Implemented repair

### Runtime OS release permissions

`deployment/digitalocean/guarded_auto_update/runtime-os-bundle.py`

- Defines `RELEASE_DIR_MODE = 0o755` and `RELEASE_FILE_MODE = 0o644`.
- Normalizes the Runtime OS bundle root and `releases/` parent to `0755`.
- Normalizes the staging/release root itself to `0755`, not only descendants.
- Normalizes all nested directories to `0755` and files to `0644` without changing content bytes.
- Repairs an already-staged release on repeated `stage` before returning it.
- Makes `verify`, `activate`, and rollback `restore` fail closed if release modes do not satisfy the canonical service-readable/traversable boundary.
- Retains symlink rejection and content/digest verification.

### Rollback controller preservation

`deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh`

- `sync_installed_assets` now accepts separate controller and production-service roots.
- During rollback, the previous application checkout and its `hhs.service` definition are restored.
- The already-validated candidate worktree remains the controller source until the transaction exits, so rollback does not downgrade the updater, bundle verifier, drift reconciler, or permission normalizer that are executing the repair.
- If the candidate controller worktree is unavailable, installed controller assets are retained and only the predecessor production service unit is restored.
- Normal successful promotion still synchronizes both controller and production service from the promoted checkout.

### Regression coverage

`tests/test_hhs_runtime_os_release_permission_repair_v1.py`

- stages a real deterministic Runtime OS bundle and proves bundle root/release parent/release root are `0755`;
- proves nested directories are `0755` and files are `0644`;
- deliberately changes a staged exact-SHA release to `0700`, stages it again, and proves the existing release is repaired to `0755`;
- deliberately changes a release to `0700` and proves `verify` rejects it before activation;
- proves rollback controller/source separation remains present in the guarded updater.

### Pass202 successor membrane

`.github/workflows/pass219-cumulative-pass202-membrane-i122.yml`

- historical Pass202 source identities remain unchanged;
- current successor hash pins are updated only for the repaired guarded updater and Runtime OS bundle implementation;
- the new Runtime OS permission regression is included in the dependency-scoped production test set.

`hhs_runtime/hhs_pass219_cumulative_pass_membrane_i122_pass202.py`

- `HISTORICAL_BLOBS` remains unchanged;
- only `CURRENT_SUCCESSOR_BLOBS` is advanced for the repaired updater/bundle files;
- successor hardening now explicitly requires release permission normalization/verification and non-downgraded rollback controller semantics;
- no new canonical mutation, VM81, persistence, Hash72 clock, or C++ authority is granted.

## Commit lineage

- `d063def71de90fbe5772f4097f7411eb216bd8a8` — normalize Runtime OS release root permissions
- `c712202d48ac776e86603b47d7045d68ad19411f` — preserve validated rollback controller across application rollback
- `b3424cf23899539679197ae5065987a94dd10607` — regress Runtime OS permission and rollback controller repair
- `b057b98cebef820a1e2dc204b6b2186a6ee0dbf7` — bind Runtime OS permission repair into Pass202 gate
- `8f593e5b5028665a02291b8e3d41a9f75201434c` — bind release permissions and rollback controller into Pass202 membrane

## Validation completed

### Pass202 cumulative membrane — run `34554768917`

Both `exact` and `synthetic` lanes completed successfully.

Both lanes passed:

- frozen I121 and accepted Pass202 integration lineage;
- frozen historical Pass202 source identities;
- current successor-hardened Pass202 deployment identities;
- approximate-arithmetic and new-authority rejection;
- exact C and C++ ABI compilation/conformance;
- kernel-derived Pass202 membrane preflight;
- expanded production deployment regression;
- frozen Pass203 successor preservation.

The exact lane's expanded production regression reported:

`37 passed in 36.71s`

This includes the new real bundle staging, existing-0700 repair, unreadable-release rejection, and rollback-controller preservation tests.

### Runtime OS production-root — run `34554768965`

Completed successfully, including:

- native runtime authority build;
- TypeScript Runtime OS source/build validation;
- production projection compilation;
- Runtime OS public-root authority enforcement;
- inherited backend route ordering ahead of SPA fallback;
- dependency-scoped production-root regressions;
- Runtime OS production build artifact upload.

### PR-ref deployment workflow

The PR-ref `DigitalOcean Production Exact Main` workflow completed successfully as non-main contract validation. This does not constitute a live production deployment.

## Production host state

The last exact-main production attempt failed after activation and then encountered a rollback restart failure. Therefore the live host must not be assumed healthy from repository CI alone.

The guarded updater timer must remain stopped until the known-good rollback service is explicitly verified healthy.

Previously known-good production boundary before the failed transaction:

- repository SHA: `73652c122ffff6a8b9bde9de00020610964d704c`;
- Runtime OS release: `/var/lib/hhs/runtime-os/releases/73652c122ffff6a8b9bde9de00020610964d704c`;
- service: `hhs.service` on `127.0.0.1:8080` behind nginx;
- public HTTPS: `165.227.220.193`;
- updater timer: intentionally held.

## Required host recovery verification before merge/deploy

Run on `hhs-production-01`:

```bash
set -euo pipefail

systemctl stop hhs-guarded-update.timer || true
systemctl reset-failed hhs.service hhs-guarded-update.service || true

cd /opt/hhs/app
echo "HEAD=$(git rev-parse HEAD)"
echo "CURRENT=$(readlink -f /var/lib/hhs/runtime-os/current || true)"
namei -l /var/lib/hhs/runtime-os/current/index.html || true

systemctl start hhs.service
sleep 3
systemctl is-active hhs.service
curl -fsS http://127.0.0.1:8080/api/system/status | python3 -m json.tool
curl -fsS http://127.0.0.1:8080/api/interface/status | python3 -m json.tool

echo "TIMER=$(systemctl is-active hhs-guarded-update.timer || true)"
```

If service start fails, capture:

```bash
systemctl status hhs.service --no-pager --full
journalctl -u hhs.service -n 120 --no-pager
```

## Remaining closure

1. Verify current `main` is still the PR base or a clean descendant and confirm PR #426 mergeability.
2. Verify the production rollback service is healthy and the updater timer remains inactive.
3. Merge PR #426 with history preserved.
4. Verify the resulting exact `main` SHA.
5. Let the new main-triggered `DigitalOcean Production Exact Main` transaction build a SHA-matched bundle and deploy that exact SHA.
6. Require terminal `PROMOTED` receipt rather than `VALIDATED`, `ROLLED_BACK`, or `ROLLBACK_HEALTH_FAILED`.
7. Verify exact SHA equality across GitHub main, production checkout, updater receipt, and Runtime OS release directory.
8. Verify loopback and public HTTPS system/interface status plus active `hhs.service`, nginx, and updater timer.
9. After the first fully successful external GitHub deployment, remove the temporary deployment private-key copy from the droplet while retaining its authorized public key.

## Restart record

- Base commit: `2def7910b99046821f34e1446bcec33ca4fd4090`
- Branch: `agent/pass219-runtime-os-release-permission-rollback-controller-repair-20260910`
- Merge target: `main`
- PR: `#426`
- Executable validated head: `8f593e5b5028665a02291b8e3d41a9f75201434c`
- Validation: Pass202 exact + synthetic green; exact production regression `37 passed in 36.71s`; Runtime OS production-root green.
- Production blocker: live host recovery/health after the failed rollback must be verified before allowing a new main deployment transaction.
- Next action: verify PR/main lineage and host rollback health; then merge #426 and follow the exact-main deployment through terminal production proof.
