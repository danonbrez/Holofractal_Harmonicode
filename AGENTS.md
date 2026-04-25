# AGENTS.md — HHS Codex Navigation Contract

This repository hosts the Holofractal Harmonicode (HHS) general programming environment.

## Current Layout

The runtime files are currently committed at the repository root.

Primary files include:

- `hhs_general_runtime_layer_v1.py`
- `hhs_state_layer_v1.py`
- `hhs_physics_model_v1.py`
- `hhs_physics_evolution_v1.py`
- `terminal_hhsprog_v5_macro_algebra.py`
- `hhs_receipt_replay_verifier_v1.py`
- `hhs_runtime_smoke_tests_v1.py`
- `hhs_regression_suite_v1.py`
- `hhs_v1_bundle_runner.py`
- `HARMONICODE_KERNEL_*.py`

If the project is later reorganized under `hhs_runtime/`, update this file and test commands in the same commit.

## Ground Rules

- All computation must pass kernel invariants:
  - Δe = 0
  - Ψ = 0
  - Θ15 = true
  - Ω = true
- No float arithmetic inside the kernel; use rational representations.
- All state transitions must be audited and receipt-committed.
- New layers must remain thin adapters over existing kernel/runtime modules.

## Prohibited Changes

Do not:

- redefine Hash72
- bypass `Manifold9` or `drift_gate`
- create alternate integrity or truth paths
- replace rational arithmetic with floats
- silently collapse ordered products such as `xy` and `yx`
- mutate state without a state patch and receipt

## Execution Pattern

Every operation must follow:

```text
Input → Symbolic/Macro Expansion → State Patch → Kernel Audit → Receipt Commit
```

## Test Commands

Run these from the repository root:

```bash
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
```

If a test fails because of path assumptions, patch the path adapter rather than weakening the invariant checks.

## Codex Guidance

- Prefer modifying existing modules over creating new abstractions.
- Preserve the kernel as the only authority.
- Preserve replayability for every new transition.
- Add tests before expanding a new layer.
- Treat failures as quarantine signals unless proven to be path/setup issues.

## First Codex Task

Run:

```bash
python hhs_v1_bundle_runner.py
```

Then produce a short report identifying:

1. any import/path failures,
2. any modules that can bypass `drift_gate`,
3. any receipt/replay mismatch,
4. the minimal patch set needed to restore LOCKED status.
