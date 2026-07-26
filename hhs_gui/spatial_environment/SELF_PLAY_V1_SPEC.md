# HHS Spatial Environment — Agentic Self-Play V1 Spec

## Narrow V1 Scope

- **Journey:** launch GUI → issue guarded runtime command through existing API route → observe deterministic runtime status/receipt signal.
- **Boundary:** frontend remains `PROJECTION_AND_ORCHESTRATION_ONLY`; VM81 backend remains authoritative.
- **Success criteria:**
  - all prompt contracts complete (`completionRate = 1.0`) in healthy backend conditions,
  - each contract observes required runtime signals,
  - retries stay within `maxPromptRetriesPerContract = 1`.

## Prompt Contracts

1. `prompt.runtime.state.observe`
   - developer prompt: get current runtime state with deterministic witness.
   - expected calls: `runtime.state`
   - expected signals: `step`, `state`
2. `prompt.runtime.step.then.observe`
   - developer prompt: step once then observe state.
   - expected calls: `runtime.step`, `runtime.state`
   - expected signals: `step`, `state`
3. `prompt.runtime.receipt.check`
   - developer prompt: commit then check continuity witness.
   - expected calls: `runtime.commit`, `runtime.state`
   - expected signals: `state`

## Agentic Roles

- **Developer agent:** supplies fixed prompt contracts and assesses usability outputs.
- **Runtime agent:** executes only through existing `runtime.*` command routes.
- **Harness outputs:** latency, retries, error class, completion, prompt-clarity proxy, and API command coverage.

## Capability-Maximization Loop

1. Run baseline suite.
2. Rank friction by failures, retries, latency, and prompt-clarity penalty.
3. Apply smallest prompt-contract improvement (de-ambiguation only).
4. Replay suite and compare completion/latency/error/clarity deltas.

## Deterministic Gates

- `python hhs_v1_bundle_runner.py`
- `python hhs_runtime_smoke_tests_v1.py`
- `python hhs_regression_suite_v1.py`
- spatial environment contracts in `hhs_gui/spatial_environment/tests/`, including `self_play_contract.mjs`.
