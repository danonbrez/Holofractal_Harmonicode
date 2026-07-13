# Changelog — Pass 027

## Summary

Pass 027 adds the first controlled live plugin execution layer.

## Added

- `hhs_runtime/hhs_controlled_live_plugin_executor_v1.py`
- `tests/test_hhs_controlled_live_plugin_executor_v1.py`
- `CONTROLLED_LIVE_PLUGIN_EXECUTIONS_PASS_027.json`
- `CONTROLLED_LIVE_PLUGIN_EXECUTIONS_PASS_027.md`
- service registry entry: `controlled_live_plugin_executor.self_test`
- Make target: `controlled-live-plugin-executor`

## Policy

Controlled live execution is restricted to explicit allow-listed `*_self_test` functions. Raw direct plugin execution remains blocked.
