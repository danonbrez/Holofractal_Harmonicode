# Changelog — Pass 024

## Priority

Plugin capability metadata and safe invocation planning for the next high-value `PLUGIN_READY` frontier.

## Added

- `hhs_runtime/hhs_plugin_capability_planner_v1.py`
- `tests/test_hhs_plugin_capability_planner_v1.py`
- `PLUGIN_CAPABILITY_PLANS_PASS_024.json`
- `PLUGIN_CAPABILITY_PLANS_PASS_024.md`
- `make plugin-capability-planner`
- guarded service: `plugin_capability_planner.self_test`

## Changed

- `hhs_service_registry_v1.py` now exposes the capability planner through the guarded service registry.
- `hhs_runtime_integration_decisions_v1.py` upgraded to Pass 024 and treats the capability planner artifacts as documented repository-state artifacts.
- `PROJECT_STATE.json` now records the plugin capability planner as an active release-integration surface.

## Safety Boundary

Pass 024 does **not** import or execute plugin-ready modules. It uses static AST inspection to generate capability metadata, risk flags, function-level invocation plans, runtime packets, C `u^72` Hash72 kernel witnesses, and foundational audits.
