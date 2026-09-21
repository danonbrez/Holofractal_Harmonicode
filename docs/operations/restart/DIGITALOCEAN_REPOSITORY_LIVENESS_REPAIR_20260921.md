# DigitalOcean Repository Liveness Probe Repair — 2026-09-21

## Restart identity

- Repository: danonbrez/Holofractal_Harmonicode
- Base main: 8644084bcc1b02ea31be859befc2efd329bf9046
- Branch: repair/digitalocean-repository-liveness-probe
- Merge target: main
- Predecessor exact-main deployment failure: run 35562801267 / deploy job 106219419609
- Scope: candidate repository-liveness validation only; no VM81, Hash72,
  Hash216, RNA, Lane 5, canonical mutation, persistence, or deployment authority
  is widened.

## Production evidence

The ef11047 exact-main candidate proved that the prior production-composition
repair is active:

- /api/health returned 200;
- /api/interface/status returned 200;
- /api/product/health returned 200;
- /api/v1/pass174/status returned 200;
- Pass174 reached HHS_P174_BOOT_READY;
- ready=true;
- authority_ready=true;
- public_interface=HHS_VISUAL_RUNTIME_OS_WORKSPACE;
- legacy_harmonizer_is_public_root=false;
- public_asset_root matched the exact versioned Runtime OS release.

The next probe, /api/runtime/repository/status, did not complete before the
guarded candidate failed. The route's first request synchronously hydrates the
repository pass catalog by recursively scanning repository files through
_catalog(). That is an IDE/history diagnostic operation, not a bounded
deployment-liveness primitive.

## Repair

1. hhs_backend/api/repository_history_routes.py
   - adds /api/runtime/repository/health;
   - returns constant-time read-only liveness metadata;
   - reports whether the catalog cache is already hydrated without calling
     _catalog();
   - leaves /api/runtime/repository/status and the complete catalog unchanged
     for the IDE/history surface.

2. deployment/digitalocean/guarded_auto_update/validate-candidate.sh
   - replaces the deployment probe of /api/runtime/repository/status with
     /api/runtime/repository/health;
   - requires HHS_REPOSITORY_HISTORY_LIVENESS_V1;
   - requires ok=true and frontend_is_authority=false.

3. tests
   - prove the liveness endpoint does not hydrate _catalog();
   - prove the guarded validator uses repository/health and not repository/status;
   - preserve the full catalog/history tests separately.

4. Pass 202 successor evidence
   - historical validator identity remains frozen at
     82250c50fa9d20a82d0b957d2637398760b1c416;
   - the current supported validator is resealed to
     0e74e2508c00507f7045dc8eecaab8a1a29f80ca;
   - the read-only Pass202 membrane now explicitly requires
     /api/runtime/repository/health.

## Repository-visible commits

- 574d4375c5c0df3c440a6b872bd0552b57a61067 — bounded repository liveness route
- f16974b7b75ad0222deba23a1b1b939a4ac9c131 — no-catalog-hydration regression
- b519d2c9db67bbe5dd4b192a1adeae92de014618 — guarded candidate uses bounded repository liveness
- a189082c304c8f5b530910be7f54d15a7c6c559a — Pass202 workflow successor reseal
- c291bb786e131ef535653f46aa46d42fff0f9a14 — Pass202 Python membrane successor reseal
- d821657b2b0b194516c9c07d56be64b27a432704 — guarded deployment contract binding
- 19e8dc04bb46475c5c0b7e3f026cfcbd12baf209 — production-root candidate-probe regression

## Validation required

On one exact PR head require:

1. Pass 219 Cumulative Pass 202 Membrane I122 exact — SUCCESS;
2. Pass 219 Cumulative Pass 202 Membrane I122 synthetic — SUCCESS;
3. DigitalOcean Production Exact Main PR contract — SUCCESS;
4. Validate HHS Runtime OS Production Root — SUCCESS with artifact upload;
5. Validate Full Application IDE — SUCCESS.

After merge to main require:

1. exact-main candidate validation reaches repository health and all subsequent
   workspace/Pass205 probes;
2. guarded updater emits PROMOTED for the exact merged SHA;
3. hhs.service remains hhs_backend.production_visual_server:app;
4. public HTTPS Runtime OS verification completes successfully.

## Next action

Open the repair PR. Repair forward only failures within this dependency scope.
Do not claim production closure until an exact-main promotion receipt and public
HTTPS verification both succeed.
