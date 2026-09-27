# Pass 220 I047 — Native Library Training Dataset Restart Record

## Repository state

- Base commit: 31d89bfaec1521ae35fc4dc248be4c2dd84a67f4
- Branch: pass220/i047-native-library-training-dataset
- Merge target: main
- Pull request: #599
- Checkpoint head before this restart-record refresh: 37c184f45656ee50a9f2be8a987089bb34e38b89
- Scope: additive Pass 220 I047 dataset preparation only

## Implemented

- exact complete raw-library byte capture and content-addressed materialization;
- architecture, ABI, provenance, byte-region, entrypoint, and ordered relationship metadata;
- exact typed input/output reference vectors whose outputs are observed from the source library;
- stable ingress encoder / egress decoder compatibility membrane;
- Lane 5 handoff requesting algebraic lifting, constructor reuse, latency/phase scheduling, and non-linear reuse while implementing none of those authorities here;
- candidate-only flags blocking VM81 mutation, canonical Hash72/Hash216 commitment, canonical persistence, model-weight mutation, and alternate optimizer/scheduler creation;
- CLI materializer, contract documentation, dependency-scoped tests, and CI workflow.

## Changed files

- hhs_runtime/hhs_pass220_i047_native_library_training_dataset_v1.py
- scripts/pass220_i047_native_library_training_dataset_v1.py
- tests/pass220/test_hhs_pass220_i047_native_library_training_dataset_v1.py
- docs/pass220/PASS_220_I047_NATIVE_LIBRARY_TRAINING_DATASET_V1.md
- .github/workflows/pass220-i047-native-library-training-dataset.yml
- docs/operations/restart/PASS_220_I047_NATIVE_LIBRARY_TRAINING_DATASET_RESTART_20260927.md

## Validation completed

Local dependency-scoped preflight:

    python -m py_compile hhs_runtime/hhs_pass220_i047_native_library_training_dataset_v1.py \
      scripts/pass220_i047_native_library_training_dataset_v1.py \
      tests/pass220/test_hhs_pass220_i047_native_library_training_dataset_v1.py
    PYTHONPATH=. pytest -q tests/pass220/test_hhs_pass220_i047_native_library_training_dataset_v1.py

Result: 7 passed.

The test compiles and invokes a real ELF shared-library fixture. Expected outputs are captured from the source library rather than duplicated arithmetic.

Repository diff verification before PR creation:
- branch was six commits ahead and zero behind main;
- exactly six I047 files were added;
- main remained 31d89bfaec1521ae35fc4dc248be4c2dd84a67f4.

## External validation state

- PR: #599
- I047 exact-head workflow run: 36313696817
- observed state at checkpoint refresh: queued
- repository-wide PR workflows also queued; Guarded Continuous Integration was skipped by its own path/event rules.

Queued external CI is not a blocker for this restartable checkpoint. No already-green unrelated evidence should be reopened.

## Authority state

Dataset output is noncanonical training material. No VM81 mutation, canonical Hash72 minting, canonical Hash216 commit, new Lane 5 compiler/scheduler, or codec-boundary removal is introduced.

## Next action

Inspect I047 workflow run 36313696817. If it fails because of these six files, repair forward only this dependency frontier. When I047 validation closes, merge PR #599 and verify authoritative main contains the integrated commit.

## Blockers

No implementation blocker. External CI was queued at checkpoint refresh.
