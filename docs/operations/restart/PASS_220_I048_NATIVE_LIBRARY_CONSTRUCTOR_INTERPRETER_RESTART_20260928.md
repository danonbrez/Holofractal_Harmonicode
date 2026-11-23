# Pass 220 I048 Native Library Constructor/Interpreter Restart

## Repository state

- Base commit: 4a299f3bf5fa92ec2f1d1f738cd76082975cddfe
- Branch: pass220/i048-native-library-constructor-interpreter
- Merge target: main
- Parent implementation: Pass 220 I047 native-library training dataset
- Scope: I047 constructor binding + fail-closed interpreter nucleus

## Implemented

- deterministic constructor bindings derived from validated I047 records;
- exact ABI, ordered input/output type, encoding, symbol, codec, relationship,
  state/effect, and source identity preservation;
- read-only HHS compiler IR projection with execution authorization false;
- exact source-observed reference-vector replay for PURE/READ_ONLY entrypoints;
- unseen-input fail-closed plan requiring a Lane 5 native constructor;
- effectful entrypoint fail-closed plan requiring explicit runtime admission;
- constructor equivalence witness over observed reference vectors without
  overclaiming generalized equivalence;
- deterministic multi-library/entrypoint constructor registry;
- CLI materialization surface;
- real ELF shared-library dependency-scoped tests.

## Changed files

- hhs_runtime/hhs_pass220_i048_native_library_constructor_interpreter_v1.py
- scripts/pass220_i048_native_library_constructor_interpreter_v1.py
- tests/pass220/test_hhs_pass220_i048_native_library_constructor_interpreter_v1.py
- docs/pass220/PASS_220_I048_NATIVE_LIBRARY_CONSTRUCTOR_INTERPRETER_V1.md
- .github/workflows/pass220-i048-native-library-constructor-interpreter.yml
- docs/operations/restart/PASS_220_I048_NATIVE_LIBRARY_CONSTRUCTOR_INTERPRETER_RESTART_20260928.md

## Validation target

    python -m py_compile \
      hhs_runtime/hhs_pass220_i048_native_library_constructor_interpreter_v1.py \
      scripts/pass220_i048_native_library_constructor_interpreter_v1.py \
      tests/pass220/test_hhs_pass220_i048_native_library_constructor_interpreter_v1.py

    pytest -q \
      tests/pass220/test_hhs_pass220_i047_native_library_training_dataset_v1.py \
      tests/pass220/test_hhs_pass220_i048_native_library_constructor_interpreter_v1.py

## Authority

Candidate/read-only only. No VM81 mutation, canonical Hash72 mint, canonical
Hash216 persistence, foreign-bytecode execution, alternate optimizer/scheduler,
or codec-boundary removal.

## Next action

1. inspect exact-head I048 workflow once;
2. repair only attributable failures;
3. after green, bind validated Lane 5 native constructors to a runtime adapter
   for unseen-input execution;
4. keep reference replay and generalized-equivalence claims separate;
5. repair forward mainline merge conflicts only when they actually appear.
