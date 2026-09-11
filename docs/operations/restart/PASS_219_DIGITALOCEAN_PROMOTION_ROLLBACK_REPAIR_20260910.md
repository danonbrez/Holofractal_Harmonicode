# Pass 219 DigitalOcean Promotion/Rollback Repair — Restart Checkpoint

Date: 2026-09-10 America/New_York / 2026-09-11 UTC

## Base authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base `main`: `c7f079ad3c0ed67d39bb0be840d47b8d52b24c05`
- Base tree: `a8caa0300866c1b69b48afc2396f017f85046dc9`
- Branch: `agent/pass219-digitalocean-promotion-rollback-repair-20260910`
- Production rollback boundary: `73652c122ffff6a8b9bde9de00020610964d704c`

## Failure evidence

The exact-main DigitalOcean deployment reached candidate validation and promotion for `c7f079ad3c0ed67d39bb0be840d47b8d52b24c05` after the Pass205 host validation completed `12 passed in 33.07s`.

Promotion then failed in the configured post-merge native command because the guarded updater process did not inherit the hosted native-language fallback contract. The native provider defaults to requiring Pass166 Word2Vec unless `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0` is present, while `bin/post_compile` and the production service already define the hosted fallback as Word2Vec-optional.

Rollback restored repository SHA `73652c122ffff6a8b9bde9de00020610964d704c`, then permission normalization failed inside `hhs-guarded-update.service` while `_service_access()` attempted `runuser -u hhs` under the unit's `NoNewPrivileges=true` hardening. The host subsequently verified `/opt`, `/opt/hhs`, `/opt/hhs/app`, and `/opt/hhs/app/hhs_backend` as mode `0755` and directly traversable by `hhs`, proving the reported `/opt` traversal failure was not persistent filesystem mode drift.

## Implemented changes

1. `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.service`
   - adds `Environment=HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0`;
   - preserves `NoNewPrivileges=true` and all existing systemd hardening.

2. `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.env.example`
   - records `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0` as the production updater default.

3. `deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py`
   - removes the `runuser` subprocess from access verification;
   - resolves the target service UID, primary GID, and supplementary groups directly;
   - verifies read/traverse authority from canonical Unix DAC mode bits without requiring a privileged identity transition from the hardened updater service;
   - emits `service_access_verification=mode-bits-with-resolved-supplementary-groups` in the permission receipt.

4. `tests/test_hhs_digitalocean_promotion_rollback_repair_v1.py`
   - regression coverage for native-provider environment inheritance;
   - regression guard that permission verification does not spawn `runuser`;
   - executable mode-bit access checks using the current test identity.

## Commits

- `140bf794f12a699ea520e12bc0fb65fbbe6f73a3` — align guarded updater native language authority
- `57347ecea598fa16e2a54e1fb0fd863efeb67638` — make rollback permission verification NoNewPrivileges-safe
- `e33e3946b5f5254d150d98e19d889649eb1ecf43` — document native language fallback in updater environment
- `30afee3bbba35a302197ccee93b65c45de973dd1` — regress DigitalOcean promotion and rollback boundaries

## Validation completed before this checkpoint

- Production host Pass205 bounded test set: `12 passed in 33.07s`.
- Host rollback checkout confirmed at `73652c122ffff6a8b9bde9de00020610964d704c`.
- Host permission chain confirmed mode `0755` for `/opt`, `/opt/hhs`, `/opt/hhs/app`, and `/opt/hhs/app/hhs_backend`.
- Direct `runuser -u hhs -- test -x` checks succeeded for `/opt`, `/opt/hhs`, and `/opt/hhs/app` outside the hardened updater service.
- Repository source inspection confirmed `bin/post_compile` already defines `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0`, while the guarded updater's configured direct post-merge command bypasses that export.

## Validation remaining

1. Run dependency-scoped tests on this branch, at minimum:
   - `tests/test_hhs_digitalocean_promotion_rollback_repair_v1.py`
   - `tests/test_hhs_guarded_auto_update_contract_v1.py`
   - `tests/test_hhs_production_service_permissions_v2.py`
   - `tests/test_hhs_production_checkout_readability_repair_v1.py`
   - `tests/test_hhs_production_public_app_v1.py`
2. Validate shell/Python parsing for guarded updater assets.
3. Merge through a green PR to `main`.
4. Verify `main` SHA after merge.
5. Restore the known-good production service at `73652c12...` if still stopped, without re-enabling the updater timer until the repair is merged.
6. Rerun `DigitalOcean Production Exact Main` against the new exact `main` SHA.
7. Require a terminal `PROMOTED` receipt, clean production checkout, SHA-matched Runtime OS release, active `hhs.service`, active updater timer, and loopback/public HTTPS verification.

## Environment state / blockers

- Production updater timer intentionally remains stopped after the failed promotion.
- Production checkout contains untracked `.hhs/`; preserve/inspect it before cleanup because exact-main deployment requires a clean checkout and the guarded drift reconciler owns host-drift migration.
- The failed deployment did not establish a `PROMOTED` receipt for `c7f079ad...`.

## Next action

Open a PR from `agent/pass219-digitalocean-promotion-rollback-repair-20260910` to `main`, run dependency-scoped CI, repair-forward any branch-local failures, merge when green, verify exact `main`, then rerun exact-main production deployment.
