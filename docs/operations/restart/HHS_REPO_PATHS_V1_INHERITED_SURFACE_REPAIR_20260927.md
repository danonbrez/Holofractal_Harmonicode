# HHS Repo Paths v1 Inherited Surface Repair — Restart Checkpoint

Date: 2026-09-27

## Base

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main SHA: `ba331f994a29f96ea1881bbfef798c29feb1e75a`
- Branch: `repair/restore-hhs-repo-paths-v1-20260927`
- Merge target: `main`
- Historical source commit: `924f4e4b40500cf2dbccc2e95f7355d22f94ad8d`
- Historical blob SHA: `4cd632a13bc61ec6a2c8e3c814a257b8349732aa`

## Scope

Repair an inherited repository regression where `hhs_runtime/hhs_repo_paths_v1.py` was removed while multiple current-main runtime modules still import it.

This repair restores the last located canonical implementation byte-for-byte. It does not redesign path semantics, rename the interface, or modify surviving callers.

## Restored interface

- `repo_root`
- `data_dir`
- `runtime_output_dir`
- `kernel_dir`
- `runtime_artifact_path`
- `resolve_repo_path`
- `first_existing`

The restored implementation retains its Hash72 filesystem-ledger binding through `hhs_runtime.hhs_filesystem_hash72_ledger_v1`.

## Changed files

- `hhs_runtime/hhs_repo_paths_v1.py` — exact restoration from historical source.
- `tests/test_hhs_repo_paths_v1_regression.py` — regression for established interface, environment overrides, path creation/resolution, first-existing lookup, and representative surviving caller imports.
- this restart record.

## Acceptance

The repair is complete only when the PR's HHS Consensus Gate executes past the prior `ModuleNotFoundError` and applicable checks are green.

## Next action

After this repair merges to main, bring PR #618 forward to the repaired main without altering its PR-only Hash216 publication logic. Re-run its Hash216 dependency-index gate, no-direct-main-push regression, Consensus Gate, and applicable required checks before merging #618.


## Current-main reconciliation

During PR validation, authoritative main was re-read and already contained `hhs_runtime/hhs_repo_paths_v1.py` with the exact historical blob SHA `4cd632a13bc61ec6a2c8e3c814a257b8349732aa`. Therefore the module itself is no longer a diff in this PR.

The remaining HHS Consensus Gate failure was traced to workflow import wiring:

```text
python hhs_runtime/hhs_commit_acceptance_gate_v1.py
→ sys.path[0] = .../hhs_runtime
→ absolute import hhs_runtime.hhs_repo_paths_v1 cannot resolve
```

Repair-forward changes:

- run the two verification entry points as package modules with `python -m ...`, preserving the repository root on the import path;
- add `actions/checkout@v4` to the downstream `consensus` job, which imports repository Python modules but previously had no repository checkout;
- extend the regression to lock both behaviors.

This changes gate invocation only; it does not alter runtime/path semantics or weaken Consensus Gate checks.
