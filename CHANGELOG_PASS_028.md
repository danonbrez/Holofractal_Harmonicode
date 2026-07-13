# CHANGELOG — Pass 028

## Focus

Controlled read-only live plugin adapter execution.

## Added

- `hhs_runtime/hhs_readonly_live_plugin_adapter_v1.py`
- `tests/test_hhs_readonly_live_plugin_adapter_v1.py`
- guarded service `readonly_live_plugin_adapter.self_test`
- make target `readonly-live-plugin-adapter`
- `READONLY_LIVE_PLUGIN_ADAPTERS_PASS_028.json`
- `READONLY_LIVE_PLUGIN_ADAPTERS_PASS_028.md`

## Changed

- Extended the plugin integration pipeline beyond self-test-only execution into allow-listed module import/introspection.
- Preserved the no-bypass authority chain:
  - canonical execution request
  - canonical runtime packet
  - HHS-M001..M007 foundational audits
  - authorized runtime tick
  - C `u^72` Hash72 Digital DNA witness
  - unified ledger append

## Boundaries Preserved

- No arbitrary legacy/plugin function body execution.
- No mutation.
- No write/network/process surfaces.
- Read-only live import/introspection only for explicit allow-listed modules.
