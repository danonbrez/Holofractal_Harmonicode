# HHS Spatial Environment — LOCKED-Ready Acceptance Report (Self-Play V1)

## Scope

- V1 journey implemented: `launch_gui -> runtime.api.command -> deterministic_receipt_observation`.
- Authority boundary preserved: frontend remains projection/orchestration only; runtime authority remains backend/kernel.

## Prompt Suite + Self-Play Outcomes

- Test: `node tests/self_play_contract.mjs`
- Result: `SELF_PLAY_CONTRACT_PASSED`
- Contract count: `3`
- API coverage count: `3` (`state`, `step`, `commit`)
- Telemetry now records:
  - prompt contract pass/fail + clarity proxy,
  - self-play call latency/error class/retries,
  - capability loop deltas and coverage map.

## Deterministic Validation Gates

- Spatial validation suite (`bash tests/run_all.sh`): **PASS** (browser smoke skipped in container by design).
- Runtime regression (`python hhs_regression_suite_v1.py`): **PASS** (`passed=10`, `failed=0`).
- Runtime smoke (`python hhs_runtime_smoke_tests_v1.py`): **FAIL** (`no_mnt_data_dependency` stale refs).
- Bundle runner (`python hhs_v1_bundle_runner.py`): **FAIL** due to smoke failure + optional DB persistence dependency error.

## Required Bundle Findings

1. **Import/path failures**
   - `database_persistence_check` raises `ModuleNotFoundError: No module named 'fastapi'` via `native_projects/hhs_ide_workspace/hhs_unified_runtime_api_v1.py`.
2. **Any modules that can bypass `drift_gate`**
   - No new bypass path introduced in this patch set.
   - Self-play layer does not touch kernel state transitions directly and only calls existing guarded `runtime.*` routes.
3. **Any receipt/replay mismatch**
   - No mismatch in normal regression replay path.
   - Mismatch reasons (`receipt_hash72 recomputation mismatch`, `parent_receipt_hash72 mismatch`) appear only in intentional tamper-negative regression cases.
4. **Minimal patch set to restore LOCKED status**
   - Remove/repair stale `/mnt/data` reference in `tools/pass148/package_release.py` (smoke gate `no_mnt_data_dependency`).
   - Make `database_persistence_check` dependency-soft when `fastapi` is absent (skip with explicit reason), or ensure `fastapi` is installed in certification runtime.

## Unresolved Gaps

- Bundle certification still not `CERTIFIED_LOCKED` until smoke stale-ref and DB dependency gate are resolved.
