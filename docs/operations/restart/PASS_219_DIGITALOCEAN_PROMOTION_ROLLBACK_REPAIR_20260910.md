# Pass 219 DigitalOcean Promotion/Rollback Repair — Restart Checkpoint

Date: 2026-09-10 America/New_York / 2026-09-11 UTC

## Base authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base `main`: `c7f079ad3c0ed67d39bb0be840d47b8d52b24c05`
- Base tree: `a8caa0300866c1b69b48afc2396f017f85046dc9`
- Branch: `agent/pass219-digitalocean-promotion-rollback-repair-20260910`
- Pull request: `#425`
- Production rollback boundary: `73652c122ffff6a8b9bde9de00020610964d704c`

## Failure evidence

The exact-main DigitalOcean deployment reached candidate validation and promotion for `c7f079ad3c0ed67d39bb0be840d47b8d52b24c05` after the Pass205 host validation completed `12 passed in 33.07s`.

Promotion then failed in the configured post-merge native command because the guarded updater process did not inherit the hosted native-language fallback contract. The native provider defaults to requiring Pass166 Word2Vec unless `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0` is present, while `bin/post_compile` and the production service already define the hosted fallback as Word2Vec-optional.

Rollback restored repository SHA `73652c122ffff6a8b9bde9de00020610964d704c`, then permission normalization failed inside `hhs-guarded-update.service` while `_service_access()` attempted `runuser -u hhs` under the unit's `NoNewPrivileges=true` hardening. The host subsequently verified `/opt`, `/opt/hhs`, `/opt/hhs/app`, and `/opt/hhs/app/hhs_backend` as mode `0755` and directly traversable by `hhs`, proving the reported `/opt` traversal failure was not persistent filesystem mode drift.

The rollback checkout also contained untracked `.hhs/`. Repository inspection proved `tools/install_production_language_assets.py` writes `production_language_assets_status.json` beneath `ROOT/.hhs` by default, so the production post-merge check itself can dirty the live checkout and violate exact-main cleanliness after an otherwise successful promotion.

The first PR #425 cumulative Pass202 run then failed only at `Prove current successor-hardened Pass 202 deployment identities`; both historical Pass202 identity steps passed. The failure was therefore a successor hash-sentinel mismatch caused by the authorized production boundary changes, not frozen Pass202 drift.

## Implemented changes

1. `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.service`
   - adds `Environment=HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0`;
   - adds `Environment=HHS_PRODUCTION_LANGUAGE_STATUS_PATH=/var/lib/hhs/runtime-bootstrap/production_language_assets_status.json`;
   - preserves `NoNewPrivileges=true` and all existing systemd hardening.

2. `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.env.example`
   - records `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0` as the production updater default;
   - records the external production language status path outside `/opt/hhs/app`.

3. `deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py`
   - removes the `runuser` subprocess from access verification;
   - resolves the target service UID, primary GID, and supplementary groups directly;
   - verifies read/traverse authority from canonical Unix DAC mode bits without requiring a privileged identity transition from the hardened updater service;
   - emits `service_access_verification=mode-bits-with-resolved-supplementary-groups` in the permission receipt.

4. `tools/install_production_language_assets.py`
   - adds `HHS_PRODUCTION_LANGUAGE_STATUS_PATH` support;
   - keeps the repository-local `.hhs` path only as the development/default fallback;
   - exposes `status_path` in the installation report;
   - corrects fail-closed diagnostics to include the native HHS provider as a valid assistant authority.

5. `tests/test_hhs_digitalocean_promotion_rollback_repair_v1.py`
   - regression coverage for native-provider environment inheritance;
   - regression coverage for the external production status path;
   - regression guard that permission verification does not spawn `runuser`;
   - executable mode-bit access checks using the current test identity.

6. `.github/workflows/pass219-cumulative-pass202-membrane-i122.yml`
   - preserves all historical Pass202 source identity pins unchanged;
   - updates only current successor deployment identities for the repaired service, environment, permission normalizer, and production language installer;
   - expands path coverage to all affected production-boundary files;
   - expands the inherited Pass202 deployment regression to the five dependency-scoped production tests.

## Commits

- `140bf794f12a699ea520e12bc0fb65fbbe6f73a3` — align guarded updater native language authority
- `57347ecea598fa16e2a54e1fb0fd863efeb67638` — make rollback permission verification NoNewPrivileges-safe
- `e33e3946b5f5254d150d98e19d889649eb1ecf43` — document native language fallback in updater environment
- `30afee3bbba35a302197ccee93b65c45de973dd1` — regress DigitalOcean promotion and rollback boundaries
- `d44026252abfd56dc64aad75ff2507c83bc1fe65` — keep production language status outside checkout
- `cb2d8293f1ec42354e0ea279fe6929603c1ad68d` — document external production language status path
- `a62f1bc1f338ce88a63feed840128c57a73a8eb6` — externalize production language status state
- `b65bbbbb6b8e2f5f89cbbdb3e54e90f596de917a` — cover clean-checkout production status boundary
- `6aa5c24c8d020b1a94b5bb7bc9a6e669c2982703` — expand DigitalOcean repair checkpoint with clean-checkout boundary
- `180fb2fdd1a787fe2d8cf38de9f3f044e6fb5a10` — reconcile Pass202 successor deployment identities

## Validation completed

- Production host Pass205 bounded test set: `12 passed in 33.07s`.
- Production four-file light gate completed successfully on exact `c7f079ad...`.
- Host rollback checkout confirmed at `73652c122ffff6a8b9bde9de00020610964d704c`.
- Host permission normalizer returned `HHS_PRODUCTION_CHECKOUT_PERMISSIONS_VERIFIED=1` with backend/runtime library readable.
- Host permission chain confirmed mode `0755` for `/opt`, `/opt/hhs`, `/opt/hhs/app`, and `/opt/hhs/app/hhs_backend`.
- Known-good `hhs.service` restored and active.
- Loopback `/api/system/status` and `/api/interface/status` returned healthy Runtime OS status.
- Public HTTPS `/api/system/status` and `/api/interface/status` returned the same healthy state.
- Runtime OS asset root is `/var/lib/hhs/runtime-os/releases/73652c122ffff6a8b9bde9de00020610964d704c`.
- `hhs-guarded-update.timer` remains intentionally inactive.
- PR #425 targeted Production Root Browser Acceptance, Production Public API Verification, Guarded Continuous Integration, DigitalOcean contract validation, and Runtime OS smoke were green on the pre-I122-repair head.
- First cumulative Pass202 exact and synthetic jobs passed frozen I121/Pass202 integration and historical Pass202 source identities, then failed only on stale current successor deployment hashes.

## Validation remaining

1. Require the new cumulative Pass202 exact and synthetic jobs triggered by `180fb2fd...` to pass the successor identity step and the five-test deployment regression.
2. Repair-forward only branch-local impacted failures, if any.
3. Merge PR `#425` to `main` when the dependency-scoped gate is green.
4. Verify exact `main` SHA after merge.
5. Preserve then remove only the generated rollback-era `.hhs/` checkout drift before exact-main promotion so `/opt/hhs/app` is clean.
6. Rerun/newly execute `DigitalOcean Production Exact Main` against the merged exact `main` SHA, not the historical c7f run.
7. Require a terminal `PROMOTED` receipt, clean production checkout, SHA-matched Runtime OS release, active `hhs.service`, active updater timer, and loopback/public HTTPS verification.

## Environment state / blockers

- Production is healthy on rollback SHA `73652c122ffff6a8b9bde9de00020610964d704c`.
- Production updater timer intentionally remains stopped.
- Production checkout still has generated untracked `.hhs/` diagnostic state unless separately archived/removed after this checkpoint.
- The failed c7f deployment established `VALIDATED` but not `PROMOTED`.
- PR `#425` is the repair vehicle; cumulative Pass202 successor validation is the current repository gate.

## Next action

Wait only on the already-triggered cumulative Pass202 successor gate for `180fb2fd...`; repair-forward any branch-local failure, merge PR #425 when green, verify the new exact main SHA, clean/preserve the rollback-era `.hhs/` host drift, and deploy the new exact main with the timer held until promotion succeeds.
