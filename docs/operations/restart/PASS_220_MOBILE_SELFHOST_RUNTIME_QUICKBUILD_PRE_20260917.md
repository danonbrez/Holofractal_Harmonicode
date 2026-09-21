# Pass 220 — Mobile Self-Host Runtime + Quick Build — PRE checkpoint

Date: 2026-09-17

## Restart identity

- Base exact main: `63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- Branch: `pass220/mobile-selfhost-runtime-quickbuild-v1`
- Merge target: `main`
- Production droplet: `hhs-production-01` (`598826630`)
- Public IPv4: `165.227.220.193`

## User-visible failure reproduced from production capture

The public Runtime OS loads the React shell, but the default mobile Control surface reports repeated `signal is aborted without reason` failures, runtime/vector status remains unresolved, and the useful source → compile → emulator workflow is buried behind the Workspace surface instead of being the primary mobile application-development path.

## Source-level diagnosis frozen before implementation

1. The production service launches `hhs_backend.production_visual_server:app`.
2. `production_visual_server.py` currently wraps `hhs_backend.runtime_os_visual_server:app`.
3. `runtime_os_visual_server.py` inherits `hhs_backend.visual_server:app`.
4. The production-only workspace/product routes consumed by the React product shell (`/api/runtime/workspace/session` and `/api/product/health`) are defined by `hhs_backend.production_server`, and are inherited by the full application path through `production_ide_server` → `pass174_server` → `application_ide_server` → `runtime_os_application_server`.
5. Therefore the DigitalOcean production gateway is projecting the Runtime OS over the older visual composition rather than the full self-host application composition already used by the canonical runtime-os application entrypoint.
6. `ProductionMobileControlCenter.requestJson` lets browser AbortError text leak directly to the UI, and its health refresh couples `/health` and `/api/v1/pass174/status` with `Promise.all`, so one slow peer makes the whole control surface appear failed.
7. The existing `HHSWorkspaceShell` already implements project creation, source registration, compilation, emulator creation, and bounded run, but that workflow is too deep for the requested phone-first click-through/copy-paste experience.

## Implementation plan

- Preserve the Pass 209 status-cache gateway but point its downstream authority at `runtime_os_application_server:app` so production inherits the complete workspace/product/Pass174 application surface.
- Add a phone-first Quick Build panel to Control: paste or load source, choose filename/target, and run one click-through Project → Witness → Compile → Emulator → Run sequence through `WorkspaceCommandClient` without granting frontend runtime authority.
- Make timeout/errors endpoint-aware and human-readable.
- Decouple baseline liveness from Pass174 vector-store readiness so one slow status route cannot blank the entire control surface.
- Keep advanced acquisition, multimodal/vector ingress, full Workspace, Visual Program, Authority, receipts, and canonical authority boundaries intact.
- Add source/static acceptance checks for the production composition and mobile Quick Build flow.

## Validation remaining

- TypeScript typecheck/build.
- Runtime OS source verification.
- Production-root and production-gateway dependency-scoped tests.
- Exact route-composition smoke checks for `/health`, `/api/product/health`, `/api/runtime/workspace/session`, `/api/runtime/workspace/command`, `/api/v1/pass174/status`.
- PR CI, merge to main, exact-main DigitalOcean deployment, and live mobile verification.

## Next action

Implement the production composition correction first, then the mobile Quick Build and transport UX repairs. Commit each restartable stage before integration.