# Pass 220 — Mobile Self-Host Runtime + Quick Build — POST checkpoint

Date: 2026-09-17

## Restart identity

- Base exact main: `63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- Branch: `pass220/mobile-selfhost-runtime-quickbuild-v1`
- Current implementation head before this checkpoint: `29b40b307686356f8e41fe8db42ac799e707c41a`
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

Repository comparison at implementation head: 13 commits ahead of the exact base and 0 behind; all changed source is repository-visible and restartable. A local clone/test runner was attempted from the conversation sandbox but outbound DNS to `github.com` is unavailable there, so no local build result is claimed. The branch is ready for dependency-scoped GitHub PR validation, which is authoritative for the actual repository environment.

Required gates before merge:

- TypeScript `typecheck` and Runtime OS build.
- `test:e2e:source`, `test:workspace:source`, frontend telemetry source checks.
- production-root and production-gateway regressions.
- guarded DigitalOcean deployment-contract validation.
- exact route-composition boot through `production_visual_server:app`.

## Integration and deployment next action

Open the branch PR to `main`, repair-forward only failing impacted gates, merge after required checks pass, then verify the exact-main DigitalOcean promotion and production endpoints. Do not treat the interface as deployed until the main deployment workflow records successful promotion of the merged SHA.