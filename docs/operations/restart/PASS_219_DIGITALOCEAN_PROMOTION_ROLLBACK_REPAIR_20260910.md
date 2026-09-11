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

## Commits

- `140bf794f12a699ea520e12bc0fb65fbbe6f73a3` — align guarded updater native language authority
- `57347ecea598fa16e2a54e1fb0fd863efeb67638` — make rollback permission verification NoNewPrivileges-safe
- `e33e3946b5f5254d150d98e19d889649eb1ecf43` — document native language fallback in updater environment
- `30afee3bbba35a302197ccee93b65c45de973dd1` — regress DigitalOcean promotion and rollback boundaries
- `d44026252abfd56dc64aad75ff2507c83bc1fe65` — keep production language status outside checkout
- `cb2d8293f1ec42354e0ea279fe6929603c1ad68d` — document external production language status path
- `a62f1bc1f338ce88a63feed840128c57a73a8eb6` — externalize production language status state
- `b65bbbbb6b8e2f5f89cbbdb3e54e90f596de917a` — cover clean-checkout production status boundary

## Validation completed before this checkpoint

- Production host Pass205 bounded test set: `12 passed in 33.07s`.
- Host rollback checkout confirmed at `73652c122ffff6a8b9bde9de00020610964d704c`.
- Host permission chain confirmed mode `0755` for `/opt`, `/opt/hhs`, `/opt/hhs/app`, and `/opt/hhs/app/hhs_backend`.
- Direct `runuser -u hhs -- test -x` checks succeeded for `/opt`, `/opt/hhs`, and `/opt/hhs/app` outside the hardened updater service.
- Repository source inspection confirmed `bin/post_compile` already defines `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0`, while the guarded updater's configured direct post-merge command bypasses that export.
- Repository source inspection identified `ROOT/.hhs/production_language_assets_status.json` as the source of the live checkout's untracked `.hhs/` state.
- PR `#425` opened from the repair branch to `main`; branch CI was queued after PR creation.

## Validation remaining

1. Run dependency-scoped tests on this branch, at minimum:
   - `tests/test_hhs_digitalocean_promotion_rollback_repair_v1.py`
   - `tests/test_hhs_guarded_auto_update_contract_v1.py`
   - `tests/test_hhs_production_service_permissions_v2.py`
   - `tests/test_hhs_production_checkout_readability_repair_v1.py`
   - `tests/test_hhs_production_public_app_v1.py`
2. Validate shell/Python parsing for guarded updater assets.
3. Repair-forward branch-local CI failures only; do not rerun unrelated frozen evidence.
4. Merge PR `#425` to `main` when the dependency-scoped gate is green.
5. Verify exact `main` SHA after merge.
6. Restore the known-good production service at `73652c12...` if still stopped, without re-enabling the updater timer until the repair is merged.
7. Reconcile/remove only the generated `.hhs/production_language_assets_status.json` host drift after preserving its diagnostic content; exact-main deployment requires a clean checkout.
8. Rerun `DigitalOcean Production Exact Main` against the new exact `main` SHA.
9. Require a terminal `PROMOTED` receipt, clean production checkout, SHA-matched Runtime OS release, active `hhs.service`, active updater timer, and loopback/public HTTPS verification.

## Environment state / blockers

- Production updater timer intentionally remains stopped after the failed promotion.
- Production checkout is rolled back but contains generated untracked `.hhs/` diagnostic state from the pre-repair production language installer.
- The failed deployment did not establish a `PROMOTED` receipt for `c7f079ad...`.
- PR `#425` is the current repair vehicle; its CI must validate the new head before merge.

## Next action

Keep the updater timer stopped. Restore/verify the known-good `hhs.service` on `73652c12...`, preserve then remove the generated `.hhs/` checkout drift, validate PR `#425`, merge when green, verify exact `main`, then rerun exact-main production deployment.
