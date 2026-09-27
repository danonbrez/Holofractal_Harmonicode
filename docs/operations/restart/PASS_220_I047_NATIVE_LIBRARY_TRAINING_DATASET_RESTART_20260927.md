# Pass 220 I047 — Native Library Training Dataset Restart Record

## Repository state

- Base commit: 31d89bfaec1521ae35fc4dc248be4c2dd84a67f4
- Branch: pass220/i047-native-library-training-dataset
- Merge target: main
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

## Validation completed before repository write

    python -m py_compile hhs_runtime/hhs_pass220_i047_native_library_training_dataset_v1.py \
      scripts/pass220_i047_native_library_training_dataset_v1.py \
      tests/pass220/test_hhs_pass220_i047_native_library_training_dataset_v1.py
    PYTHONPATH=. pytest -q tests/pass220/test_hhs_pass220_i047_native_library_training_dataset_v1.py

Result: 7 passed.

The test compiles and invokes a real ELF shared-library fixture. Expected outputs are captured from the source library rather than duplicated arithmetic.

## Validation remaining

- exact-head GitHub Actions execution of the I047 workflow;
- repair forward only the I047 dependency frontier if required;
- merge when dependency-scoped validation closes;
- verify authoritative main contains the I047 integration.

## Authority state

Dataset output is noncanonical training material. No VM81 mutation, canonical Hash72 minting, canonical Hash216 commit, new Lane 5 compiler/scheduler, or codec-boundary removal is introduced.

## Next action

Open the I047 PR, inspect exact-head CI, repair forward if needed, then merge and verify main.

## Blockers

None known at checkpoint creation.
