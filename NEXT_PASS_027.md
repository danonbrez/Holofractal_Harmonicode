# Next Pass — Pass 027 Recommendation

## Recommended Focus

Adapter closure-harness coverage.

## Objective

Before any plugin candidate receives direct import/execution authority, the system should prove that semantic adapter executions can participate in closure convergence.

## Proposed Work

- Add `hhs_plugin_adapter_closure_harness_v1.py`.
- Run selected semantic adapter executions through the system closure signature path.
- Compare stable adapter closure signatures across repeated cycles.
- Emit `PLUGIN_ADAPTER_CLOSURE_HARNESS_PASS_027.json` and `.md`.
- Add guarded service `plugin_adapter_closure_harness.self_test`.
- Add make target `plugin-adapter-closure-harness`.

## Rule

No direct legacy/plugin execution should be enabled in Pass 027. The correct next milestone is closure proof for adapter execution, not raw module execution.
