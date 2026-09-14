# Pass 219 DigitalOcean Promotion/Rollback Repair — Restart Checkpoint

Date: 2026-09-10 America/New_York / 2026-09-11 UTC

## Base and delivery authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Original base `main`: `c7f079ad3c0ed67d39bb0be840d47b8d52b24c05`
- Original base tree: `a8caa0300866c1b69b48afc2396f017f85046dc9`
- Branch: `agent/pass219-digitalocean-promotion-rollback-repair-20260910`
- Pull request: `#425`
- Production rollback boundary: `73652c122ffff6a8b9bde9de00020610964d704c`
- Dependency-scoped green head before this checkpoint update: `7f96cda2ef3b49c9f595abe2c7659a0d04b25b16`
- Green cumulative gate: workflow `Pass 219 Cumulative Pass 202 Membrane I122`, run `34552456487`

## Failure evidence

The DigitalOcean exact-main deployment of `c7f079ad3c0ed67d39bb0be840d47b8d52b24c05` passed SSH authority, pinned host trust, Runtime OS build/seal, transfer, isolated candidate validation, native compilation, the production integration gate, and Pass205 (`12 passed in 33.07s`). It then failed after promotion began because the guarded updater's direct post-merge command did not inherit the hosted native-language fallback contract.

Rollback restored `73652c122ffff6a8b9bde9de00020610964d704c`. The rollback permission verifier then attempted `runuser -u hhs` inside `hhs-guarded-update.service`, whose `NoNewPrivileges=true` hardening made the verifier report a false traversal failure even though the host later proved `/opt`, `/opt/hhs`, `/opt/hhs/app`, and `/opt/hhs/app/hhs_backend` were mode `0755` and directly traversable by `hhs`.

The old production language installer also wrote `.hhs/production_language_assets_status.json` beneath the live repository checkout, creating host-local dirtiness that would violate exact-main cleanliness after otherwise valid promotion.

## Implemented repair

1. `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.service`
   - exports `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0`;
   - exports `HHS_PRODUCTION_LANGUAGE_STATUS_PATH=/var/lib/hhs/runtime-bootstrap/production_language_assets_status.json`;
   - retains `NoNewPrivileges=true` and existing hardening.

2. `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.env.example`
   - records the same production native-provider and external-status defaults.

3. `deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py`
   - removes privileged `runuser` access probes;
   - resolves UID, primary GID, and supplementary groups directly;
   - evaluates Unix DAC read/traverse mode bits deterministically;
   - emits `service_access_verification=mode-bits-with-resolved-supplementary-groups`.

4. `tools/install_production_language_assets.py`
   - supports `HHS_PRODUCTION_LANGUAGE_STATUS_PATH`;
   - keeps repository-local `.hhs` only as a development/default fallback;
   - reports the effective status path;
   - identifies the native HHS provider as a valid assistant authority.

5. `tests/test_hhs_digitalocean_promotion_rollback_repair_v1.py`
   - covers updater native-provider inheritance, external production status state, NoNewPrivileges-safe permission verification, and target-identity DAC checks;
   - fixes the permission fixture so the payload read boundary is tested before parent traversal is removed.

6. `tests/test_hhs_production_public_app_v1.py`
   - updates the stale Procfile assertion to the current canonical `hhs_backend.runtime_os_application_server:app` dispatcher;
   - verifies that dispatcher retains the inherited `application_ide_server` composition rather than treating the retired direct entrypoint as current authority.

7. `.github/workflows/pass219-cumulative-pass202-membrane-i122.yml`
   - preserves frozen historical Pass202 identity pins unchanged;
   - updates only the current successor deployment hashes;
   - expands dependency-scoped production regression coverage.

8. `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i122_pass202.py`
   - preserves `HISTORICAL_BLOBS` unchanged;
   - updates only `CURRENT_SUCCESSOR_BLOBS` and current successor contract tokens for the repaired deployment boundary.

## Commit lineage

- `140bf794f12a699ea520e12bc0fb65fbbe6f73a3` — align guarded updater native language authority
- `57347ecea598fa16e2a54e1fb0fd863efeb67638` — make rollback permission verification NoNewPrivileges-safe
- `e33e3946b5f5254d150d98e19d889649eb1ecf43` — document native language fallback
- `30afee3bbba35a302197ccee93b65c45de973dd1` — add DigitalOcean promotion/rollback regressions
- `d44026252abfd56dc64aad75ff2507c83bc1fe65` — keep production language status outside checkout
- `cb2d8293f1ec42354e0ea279fe6929603c1ad68d` — document external production status path
- `a62f1bc1f338ce88a63feed840128c57a73a8eb6` — externalize production language status state
- `b65bbbbb6b8e2f5f89cbbdb3e54e90f596de917a` — cover clean-checkout status boundary
- `6aa5c24c8d020b1a94b5bb7bc9a6e669c2982703` — restart checkpoint
- `180fb2fdd1a787fe2d8cf38de9f3f044e6fb5a10` — reconcile Pass202 successor deployment identities
- `d861fe7a4c59fd03dedead5effc2534799b5f77c` — checkpoint Pass202 successor repair
- `6a0b9830d2d8e479a2f8dd6b354d588ba8020969` — reconcile Python Pass202 successor membrane
- `96e05507d4e5254d661b99ed9b1c718b87921a45` — repair permission verifier regression fixture
- `7f96cda2ef3b49c9f595abe2c7659a0d04b25b16` — align production entrypoint regression with Runtime OS authority

## Validation completed

### Production host

- Pass205 bounded validation: `12 passed in 33.07s`.
- Four-file light production gate: success on exact `c7f079ad...`.
- Permission normalizer: `HHS_PRODUCTION_CHECKOUT_PERMISSIONS_VERIFIED=1`.
- Known-good rollback checkout: `73652c122ffff6a8b9bde9de00020610964d704c`.
- `hhs.service`: active.
- Loopback `/api/system/status`: HARMONICODE online.
- Loopback `/api/interface/status`: `HHS_RUNTIME_OS_PUBLIC_ROOT`, `HHS_VISUAL_RUNTIME_OS_WORKSPACE`.
- Public HTTPS system/interface status: healthy and matches loopback.
- Runtime OS asset root: `/var/lib/hhs/runtime-os/releases/73652c122ffff6a8b9bde9de00020610964d704c`.
- `hhs-guarded-update.timer`: intentionally inactive.

### Repository / PR #425

Cumulative Pass202 run `34552456487` completed successfully in both `exact` and `synthetic` lanes. Both lanes passed:

- frozen I121 and accepted Pass202 integration;
- historical Pass202 source identities;
- current successor-hardened deployment identities;
- approximate-arithmetic/new-authority rejection;
- exact C and C++ ABI compilation/conformance;
- kernel-derived Pass202 Python membrane preflight;
- the expanded five-file production regression (`33` tests in the prior failing run; all repaired tests green in the closing run);
- frozen Pass203 successor preservation.

The historical Pass202 identities were never modified. Only current successor deployment evidence was repaired.

## Remaining delivery steps

1. Re-read current `main` and PR #425 head/mergeability.
2. If current-main ancestry remains merge-clean, merge PR #425 with history preserved.
3. Verify the resulting exact `main` SHA.
4. On production, preserve and remove only the rollback-era generated `.hhs/` diagnostic drift so `/opt/hhs/app` is clean; keep the updater timer held.
5. Run the new `DigitalOcean Production Exact Main` workflow for the merged exact-main SHA; do not reuse the historical c7f run.
6. Require terminal `PROMOTED`, exact SHA equality, clean checkout, SHA-matched Runtime OS release, active `hhs.service`, active updater timer, and loopback/public HTTPS verification.
7. After the first fully successful external GitHub deployment, remove the temporary deployment private-key copy from the droplet while retaining its authorized public key.

## Restart state

- Base commit: `c7f079ad3c0ed67d39bb0be840d47b8d52b24c05`.
- Merge target: `main`.
- Repair branch: `agent/pass219-digitalocean-promotion-rollback-repair-20260910`.
- PR: `#425`.
- Production live rollback SHA: `73652c122ffff6a8b9bde9de00020610964d704c`.
- Production service health: verified healthy.
- Production updater timer: intentionally inactive.
- Repository dependency-scoped gate: green at `7f96cda2ef3b49c9f595abe2c7659a0d04b25b16` / run `34552456487`.
- Next action: verify current-main/PR lineage, merge #425, verify new exact main, clean preserved host drift, then execute exact-main production promotion.
