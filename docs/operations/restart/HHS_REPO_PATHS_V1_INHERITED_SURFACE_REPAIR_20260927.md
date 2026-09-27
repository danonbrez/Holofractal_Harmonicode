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


## Pass 078 successor-lineage repair

After package-import repair, Consensus Gate advanced to the immutable-manifest gate and rejected two evolved runtime sources:

- `hhs_runtime/HARMONICODE_VM_RUNTIME.c`
- `hhs_runtime/c/hhs_runtime_abi.c`

This is not being repaired by replacing the Pass 078 baseline hashes.

Repository evidence establishes explicit later successors:

### VM81 runtime

- current Git blob: `92afd8d0e26119b6db6420740c05db25a37d389a`
- current SHA-256: `91ec97378f793e1f00d251538c9ed732222edf40896ed4c24c4d0e2733a46e53`
- Pass 220 I028 final PR head: `8a750bb56d14fc9847166736bbbf2ca0660bff7f`
- dedicated exact-head run: `35723417642` — success
- merge PR: #547
- merge commit: `86a66d32ba3c17430887cb4ff9fa0da7dbb4bf6f`
- semantic boundary: legacy opcodes 0..23 preserved; G3 24..34 append-only.

### Runtime ABI implementation

- current Git blob: `6a3ed4a10c5d83fa77bb4d118819fc230d32248a`
- current SHA-256: `58188c6927d03a486d5b4dfb8d5f94356d4de2a01e1c83808d46670984d3be3f`
- already bound by `artifacts/pass206/CORE_SUCCESSOR_REPAIR_LINEAGE.json`
- repair PR: #254
- repair merge: `284bf652d9635cc0c940f79dfe6aff6f8b787c3c`
- validated head: `3235f9066219bf2e665503d9f94aa11701d4c20e`
- semantic boundary: legacy v1 layout preserved; exact v1.1 extension linked additively.

The new `PASS_078_KERNEL_SUCCESSOR_LINEAGE_V1.json` preserves the Pass 078 baseline and allows only exact, explicitly validated successors. The validator requires exact current size/SHA-256/Git blob, ancestral validated and merge commits, and repository-visible evidence files. Unlisted drift remains a `FROZEN_FILE_MISMATCH`.

Consensus checkout now uses full history so ancestry is proved locally rather than assumed.


## Diagnostic-preservation repair

Exact-head Consensus validation advanced past the repository import and Pass 078 successor-lineage blockers, then failed at `hhs_runtime_certification_v2.py`. The acceptance gate's subprocess wrapper discarded stdout/stderr from its raised failure and exposed only the script filename.

Repair: retain subprocess return code/stdout/stderr in the rejection record. Pass/fail semantics remain identical; the change only makes the next inherited blocker reproducible and inspectable.
