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


## Restartable checkpoint — queued validation boundary

Checkpoint date: 2026-09-27

### Repository state

- authoritative main: `d46b2ad3271834449dd69b140dafc5803680a2fa`
- repair branch: `repair/restore-hhs-repo-paths-v1-20260927`
- repair PR: #619
- checkpoint parent head: `b0d06fa7164dbe1f72ebc7359cb279ea3bf48d4c`
- merge target: `main`
- PR mergeable at checkpoint: `null`
- PR mergeable state at checkpoint: `unknown`

### Implemented in this repair branch

1. Consensus Gate package import repair:
   - verification entry points use `python -m hhs_runtime...`;
   - downstream consensus job checks out the repository;
   - full history is available where successor ancestry is validated.
2. Pass 078 immutable-manifest repair:
   - original Pass 078 baseline remains unchanged;
   - `PASS_078_KERNEL_SUCCESSOR_LINEAGE_V1.json` binds only exact validated successors;
   - unlisted drift remains fail-closed.
3. Pre-commit parity:
   - generated hook invokes the acceptance gate through package-module execution.
4. Consensus diagnostics:
   - subprocess return code, stdout, and stderr are preserved in acceptance failures.
5. Regression coverage:
   - repo-path interface;
   - caller imports;
   - Consensus workflow import-root behavior;
   - Pass 078 explicit successor acceptance;
   - pre-commit invocation;
   - subprocess diagnostic preservation.

### Exact validation state

The current repair head has authoritative GitHub Actions queued. Do not repeatedly poll these queued runs.

Queued HHS Consensus Gate run:
- workflow run: `36340165721`
- verify (1): `108678562670`
- verify (2): `108678562642`
- verify (3): `108678562408`

Queued HHS Hash216 Repository Dependency Index run:
- workflow run: `36340165669`
- deep-index job: `108678562059`

No green result is claimed for those queued jobs at this checkpoint.

### Last executed failure frontier

Before the current-head queued run, Consensus advanced beyond:

- the missing `hhs_repo_paths_v1.py` import failure;
- the package import-root defect;
- the obsolete Pass 078 byte-freeze mismatch.

The next observed blocker on the superseded head was:
- `hhs_runtime_certification_v2.py`

The acceptance gate now preserves that subprocess's stdout/stderr so the next executed run will expose the exact inherited defect rather than only the filename.

### Restart rule

On the next prompt:

1. read current main and PR #619;
2. if the queued current-head Consensus run has completed, inspect its final result once;
3. if still queued, do not probe repeatedly — preserve this checkpoint and return control;
4. if red, repair only the newly exposed inherited dependency frontier;
5. if green, reconcile any substantive main drift, require a fresh applicable exact-head validation if needed, then merge #619;
6. only after the Consensus repair is green/merged, bring #618 forward without changing its PR-only Hash216 publication guard;
7. merge #618 only after its Hash216 gate, explicit no-direct-main-push regression, Consensus Gate, and applicable required checks are green;
8. verify main contains no `git push origin HEAD:main` in `.github/workflows/repository-hash216-dependency-index.yml`.

### Post-LiteRT queued architecture tranche

After the LiteRT integration reaches closure, apply the same plug-and-play native integration discipline to:

1. Hugging Face native systems/capabilities;
2. OpenAPI native systems/capabilities.

For each, preserve the same compatibility membrane used for native library/LiteRT work:

- external input/output contract fidelity;
- encoder/decoder ingress-egress stability;
- native internal constructors and execution;
- Lane 5 candidate-only learning/discovery unless separately admitted;
- exact Hash72/Hash216 evidence and dependency binding;
- restartable validation receipts;
- no bypass of canonical VM81 authority.

Do not start those Hugging Face/OpenAPI tranches before LiteRT is complete unless explicitly re-ordered by the user.


## Successor smoke-suite repair — executed failure frontier

The checkpointed PR head `2b9afb742d1707d20d06cea07fe9f7dada373e60` completed HHS Consensus Gate run `36341626895` with a concrete inherited failure in verify job `108682723372`:

```text
ImportError: cannot import name 'HHSSmokeTestSuiteV1' from 'hhs_runtime_smoke_tests_v1'
```

Repository history shows commit `8a2691c535016a23f954f4fa4a24f8fd05f1f16a` intentionally replaced the legacy `HHSSmokeTestSuiteV1` class with the topology-aware `run_smoke_suite()` registry. The certification script remained a stale caller.

Repair-forward action:
- do not restore the removed legacy class;
- update `hhs_runtime_certification_v2.py` to call `run_smoke_suite()`;
- consume the successor report at `summary.all_ok`;
- add regression coverage forbidding reintroduction of `HHSSmokeTestSuiteV1` in the certification caller.

Observed repository state before this repair:
- current main: `7ef287dafae9accda91c540f6f9cb974e05a0f0e`;
- PR #619 head before this commit: `2b9afb742d1707d20d06cea07fe9f7dada373e60`;
- Hash216 dependency index on that head: success, run `36341626871`;
- HHS Consensus Gate on that head: failure, run `36341626895`.

Next action after this commit:
1. inspect the newly triggered current-head Consensus run once when it reaches a terminal state;
2. if red, repair only the newly exposed inherited dependency frontier;
3. if queued, stop rather than repeatedly polling;
4. after Consensus is green, reconcile substantive current-main drift before merge.
