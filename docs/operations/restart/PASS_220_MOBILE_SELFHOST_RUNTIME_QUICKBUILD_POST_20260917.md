# Pass 220 — Mobile Self-Host Runtime + Quick Build — POST checkpoint

Date: 2026-09-17

## Restart identity

- Base exact main: `63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- Branch: `pass220/mobile-selfhost-runtime-quickbuild-v1`
- Current repair head before this checkpoint update: `f9f2677b91752d96e0a69210df0eb3ddd6b37a0c`
- Merge target: `main`
- Production droplet: `hhs-production-01` (`598826630`)
- Public IPv4: `165.227.220.193`

## Root cause closed in source

The production systemd service starts `hhs_backend.production_visual_server:app`, but that gateway had been wrapping the reduced `runtime_os_visual_server` composition while the React production product requires routes supplied by the full `runtime_os_application_server` inheritance chain. This allowed the SPA to load while `/api/product/health`, workspace, and Pass 174 application surfaces were absent or failed behind the deployed gateway. Browser `AbortController` errors then leaked as the user-visible `signal is aborted without reason` message, and coupled health requests made one slow service appear to take down the whole control surface.

## Implemented closure

1. `production_visual_server.py` now preserves the Pass 209 status-cache membrane while projecting `runtime_os_application_server:app`, matching the complete self-host application authority expected by the frontend.
2. The default phone surface now starts with `MobileQuickBuildPanel`: paste/load source → select target → **Build & Run** through `/api/v1/pass174/sdlc/run` → inspect pipeline receipts/Hash216 → continue in the full workspace. HTML receives an optional sandboxed local preview with no canonical mutation authority.
3. `ProductionMobileControlCenter` decouples `/health` from Pass 174/vector readiness with `Promise.allSettled`; vector warming no longer blanks runtime/build controls.
4. Raw browser abort text is replaced by endpoint-specific bounded timeout messages in product health, control, Quick Build, and acquisition surfaces.
5. Open-source acquisition/replay remains available but is progressively disclosed under an Advanced section rather than dominating the default phone workflow.
6. Runtime OS source-verification scripts now require the Quick Build workflow, warming-safe UX, and full application production bridge.
7. Production-root tests and Runtime OS CI now require the full workspace/product/Pass174 route set ahead of the SPA fallback.
8. The guarded DigitalOcean candidate validator now boots the same `hhs_backend.production_visual_server:app` entrypoint as systemd, while retaining the nested `hhs_backend.runtime_os_application_server:app` authority identity, and actively checks `/health`, `/api/product/health`, `/api/v1/pass174/status`, workspace, Runtime OS, repository, and Pass 205 routes.
9. Pass 219's inherited Pass 209 membrane was repair-forwarded to recognize the full Runtime OS application projection without changing frozen historical Pass 209 source identities.

## Changed files

- `.github/workflows/hhs-runtime-os-deploy.yml`
- `deployment/digitalocean/guarded_auto_update/validate-candidate.sh`
- `hhs_backend/production_visual_server.py`
- `hhs_gui/runtime_os/workspace/HHSProductWorkspace.tsx`
- `hhs_gui/runtime_os/workspace/MobileQuickBuildPanel.tsx`
- `hhs_gui/runtime_os/workspace/OpenSourceAcquisitionPanel.tsx`
- `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
- `hhs_gui/scripts/live-gui-e2e-source-verify.mjs`
- `hhs_gui/scripts/workspace-source-verify.mjs`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i116_pass209.py`
- `tests/test_runtime_os_production_root.py`
- PRE/POST restart records.

## Validation state

PR #493 is open and mergeable.

Validated successfully at head `f22d379d5778af77b3caba6a1309bb0cba19582e` before the browser-acceptance repair:
- DigitalOcean Mobile Control and Vector Ingress: PASS, including integrated source contracts, TypeScript typecheck, production Runtime OS build, and bundle contract.
- DigitalOcean Production Exact Main deployment-contract job: PASS. The deploy job is correctly skipped on pull requests.
- Pass 196 Integrated Environment: PASS.
- Validate HHS Runtime OS Production Root: PASS, including native build, TypeScript build, production projection compilation, full route ordering ahead of the SPA fallback, and dependency-scoped production-root regressions.

One impacted gate failed: **Validate Full Application IDE**. The server, route, and asset probes all returned HTTP 200. Its Playwright step timed out waiting for `[data-testid="registry-visual-programmer"]` because the new required phone-first **Build** surface is now the default and the Visual Program component is intentionally mounted only after the user selects that tab. This was acceptance-test drift, not a production route failure.

Repair-forward commit `f9f2677b91752d96e0a69210df0eb3ddd6b37a0c` updates the browser acceptance path to:
1. verify the canonical Runtime OS and product workspace;
2. verify the default `mobile-quick-build-panel`;
3. click the real **Visual Program** navigation control;
4. then require `registry-visual-programmer`.

That commit triggered the dependency-scoped PR workflows again. No queued external CI is required to keep this task restartable.

## Integration and deployment next action

Wait only for the impacted PR rerun needed for merge acceptance. If it fails, repair-forward that concrete failure. If it passes and required checks permit merge, merge PR #493, verify main contains the merged head, then verify the exact-main DigitalOcean promotion and live production endpoints. Do not treat the interface as deployed until the main deployment workflow records successful promotion of the merged SHA.