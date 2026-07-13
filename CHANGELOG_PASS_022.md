# CHANGELOG — Pass 022

## Priority

Runtime reachability reduction and explicit integration decisions.

## Added

- `hhs_runtime/hhs_runtime_integration_decisions_v1.py`
- `RUNTIME_INTEGRATION_DECISIONS.json`
- `RUNTIME_INTEGRATION_DECISIONS_PASS_022.md`
- `tests/test_hhs_runtime_integration_decisions_v1.py`
- Guarded service: `runtime_integration.decisions_self_test`
- Make target: `runtime-integration-decisions`

## Changed

- Upgraded reachability audit version from `PASS_021` to `PASS_022`.
- Reachability audit now applies explicit integration decisions after canonical boot/service/API/GUI classification.
- Former silent orphan candidates are converted to one of:
  - `PLUGIN_READY`
  - `DOCUMENTED_ONLY`
  - `DEPRECATED`
  - `WIRED`
- `PROJECT_STATE.json` now records Pass 022 runtime reachability policy.

## Result

- Orphan candidates reduced from **291** to **0** without deletion or semantic substitution.
- High-value legacy/runtime/AI/database/front-end candidates are retained as `PLUGIN_READY` for guarded adapter integration.
- Reports/config/generated state/test artifacts are classified as `DOCUMENTED_ONLY` where appropriate.

## Verification

- `make verify-c`
- `make runtime-integration-decisions`
- `make runtime-reachability`
- `make service-registry`
- targeted pytest set including new Pass 022 tests
