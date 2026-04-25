# AGENTS.md — HHS Codex Navigation Contract

This repository hosts the Holofractal Harmonicode (HHS) general programming environment.

## Ground Rules

- All computation must pass kernel invariants:
  - Δe = 0
  - Ψ = 0
  - Θ15 = true
  - Ω = true
- No float arithmetic inside the kernel; use rational representations.
- All state transitions must be audited and receipt-committed.

## Primary Entry Points

- `hhs_runtime/hhs_general_runtime_layer_v1.py`
- `hhs_runtime/hhs_state_layer_v1.py`
- `hhs_runtime/hhs_hash_commitment_layer.py`
- `hhs_runtime/HARMONICODE_KERNEL_*.py`

## Test Commands

```bash
python hhs_runtime/hhs_runtime_smoke_tests_v1.py
python hhs_runtime/hhs_regression_suite_v1.py
```

## Execution Pattern

Every operation must follow:

Input → Symbolic/Macro Expansion → State Patch → Kernel Audit → Receipt Commit

## Codex Guidance

- Prefer modifying existing modules over creating new abstractions.
- Do not bypass the kernel or drift_gate.
- All new features must produce replayable receipts.

## First Task Suggestion

Hydrate the repository from the bundled archive and verify:

```bash
python hhs_runtime/hhs_v1_bundle_runner.py
```

Then implement incremental improvements without breaking invariant checks.
