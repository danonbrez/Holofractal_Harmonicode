# Release Pass 002 Changelog

## Scope

Pass 002 continues v1 release integration from the Pass 001 clean baseline. The focus is the GUI/runtime boundary and durable repository state so the project remains self-describing across context resets.

## Changes

- Added `PROJECT_STATE.json` as machine-readable release state.
- Added release-pass documentation artifacts:
  - `CHANGELOG_PASS_002.md`
  - `DEVELOPMENT_OUTLINE.md`
  - `SCHEMA_REQUIREMENTS.md`
  - `INTEGRATION_REPORT_PASS_002.md`
  - `TEST_REPORT_PASS_002.md`
  - `KNOWN_ISSUES_PASS_002.md`
  - `NEXT_PASS.md`
- Extended `RuntimeOSConfig` with optional GUI projection flags:
  - `diagnosticsEnabled`
  - `mobileMode`
- Added `RuntimeOS.shutdown()` compatibility alias for the canonical shell lifecycle.
- Flattened `RuntimeOS.getMetrics()` to expose the values already consumed by GUI surfaces:
  - `connected`
  - `replayReady`
  - `graphReady`
  - `transportReady`
  - `totalEvents`
  - `workspaceWindows`
  - `applicationsMounted`
  - `uptimeMs`
- Replaced stale `hhs_gui/src/components/RuntimeShell.tsx` implementation with a compatibility re-export to canonical `runtime_os/core/RuntimeShell`.
- Replaced stale GUI references to removed `runtimeOS.workspace` / `runtimeOS.state` projections with current `windowManager` and `getMetrics()` access.

## Verification

- `python -m pytest -q` → 30 passed.
- `make verify-c` → completed and exported ABI symbols.
- `python -m hhs_python.runtime.hhs_ctypes_bridge` → HHS ABI VALIDATED.
- Backend orchestrator import verified.

## Non-goals

- No new feature invention.
- No changes to HHS kernel semantics.
- No changes to C runtime semantics.
- No package-lock generation because GUI dependencies were not installed in this local environment.
