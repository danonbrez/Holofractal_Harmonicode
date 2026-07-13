# Changelog — Pass 026

## Focus

Semantic plugin adapter runtime: move from guarded invocation plans to live guarded adapter execution without importing or executing legacy/plugin module code.

## Added

- `hhs_runtime/hhs_semantic_plugin_adapter_runtime_v1.py`
- `tests/test_hhs_semantic_plugin_adapter_runtime_v1.py`
- `SEMANTIC_PLUGIN_ADAPTER_EXECUTIONS_PASS_026.json`
- `SEMANTIC_PLUGIN_ADAPTER_EXECUTIONS_PASS_026.md`
- guarded service `semantic_plugin_adapter_runtime.self_test`
- make target `semantic-plugin-adapter-runtime`

## Changed

- Default service registry now exposes the semantic plugin adapter runtime as a guarded plugin-adapter service.
- Runtime reachability audit advanced to Pass 026 artifacts.
- `PROJECT_STATE.json` updated to mark Pass 026 as complete and preserve the direct-plugin-execution block.

## Preserved Boundaries

- No legacy/plugin module is directly imported.
- No legacy/plugin function body is executed.
- Live execution is limited to the semantic adapter runtime itself.
- Direct execution remains blocked until dedicated adapter closure-harness coverage and an explicit allowlist exist.
