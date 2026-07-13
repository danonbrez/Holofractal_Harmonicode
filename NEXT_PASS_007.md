# NEXT PASS 007 — GUI Command Surface Binding

## Recommended Objective
Bind the GUI command palette/runtime shell to backend service discovery and guarded dispatch.

## Priority Tasks

1. Add TypeScript service-client functions for:
   - `GET /api/runtime/services`
   - `GET /api/runtime/services/status`
   - `POST /api/runtime/services/dispatch`
2. Add command palette entries from discovered service specs.
3. Surface authority/ledger status in runtime topbar or console.
4. Preserve GUI as projection/control surface only; no GUI-side authority bypass.
5. Add lightweight static checks where possible without requiring bundled `node_modules`.

## Acceptance Criteria

- GUI has a clear API client path for service discovery and guarded dispatch.
- Runtime command palette can represent guarded services.
- No frontend path invents execution semantics or bypasses backend authority.
- Existing Python/C tests continue to pass.
