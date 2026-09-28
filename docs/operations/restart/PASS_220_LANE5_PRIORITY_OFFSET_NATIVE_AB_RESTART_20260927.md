# Pass 220 Native Lane 5 Priority-Offset A/B — Restart Record

**Date:** 2026-09-27  
**Base commit:** `e3431286c4719c130599718c043e2c8d95f3d953`  
**Branch:** `experiment/pass220-lane5-priority-offset-native-ab-20260927`  
**Merge target:** `main`

## Objective

Continue the NumPy/U9 optimization after information-preservation, HNAN and
literal firing-pattern provenance were closed.

Move the selected compact representation into a real exact-C Lane 5 candidate
hydration path and benchmark it against the dense reference on the same runner.

## Inherited, unchanged runtime geometry

```text
sigma_n = 8 + 16 n (mod 72)
8 -> 24 -> 40 -> 56 -> 72 -> 16 -> 32 -> 48 -> 64 -> 8
```

The implementation reuses the existing U9/Pass 219 Lane 5 engine. No metaphor,
replacement schedule, or second phase engine is introduced.

## Added implementation

- `hhs_runtime/include/hhs_pass220_lane5_priority_offset_hydration_1_0.h`
- `hhs_runtime/c/hhs_pass220_lane5_priority_offset_hydration_1_0.inc`
- cumulative exact ABI includes
- native C regression
- native paired A/B benchmark
- dependency-scoped Python regression
- dedicated workflow
- this restart record

## Native state

Each of 81 cells carries:

```text
(counted_value, phase72, rotation4, source_index)
```

Compact U9 motion preserves the entire tagged cell. Inverse replay must recover
the exact source byte-for-byte.

## Lane 5/HNAN path

The native adapter ends at:

```text
hhs_exact_pass219_lane5_mediate_candidate
```

so the existing HNAN global preflight remains mandatory. Candidate mediation
must report zero-sum closure, VM5184 binding and RNA cell-wall binding before
the adapter returns success.

The adapter is candidate-only and has no canonical VM81/Hash72/Hash216
authority.

## A/B benchmark

Dense path:

```text
9x9 one-hot substitution materialization
-> complete tagged state
-> candidate request
-> Lane 5/HNAN mediation
```

Compact path:

```text
scalar symbol + U9 offset permutation
-> complete tagged state
-> candidate request
-> Lane 5/HNAN mediation
```

Both arms must produce identical tagged states and identical mediation inputs
before timing is considered.

The workflow records nine same-runner batches of 64 candidates per channel.
Timing is observational and is not canonical.

## Validation commands

```bash
python -m pytest -q \
  tests/pass220/test_hhs_pass220_lane5_priority_offset_native_ab_v1.py \
  tests/pass220/test_hhs_pass220_priority_offset_information_translation_v1.py

make clean
make c-abi

cc -O3 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Ihhs_runtime/include \
  tests/pass220/test_hhs_pass220_lane5_priority_offset_hydration_1_0.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" \
  -o /tmp/pass220-priority-offset-test

/tmp/pass220-priority-offset-test
```

Then compile/run the paired benchmark in
`benchmarks/pass220/pass220_lane5_priority_offset_native_ab_v1.c`.

## Environment state

GitHub Actions Ubuntu 24.04 is the authoritative dependency-scoped validation
runner for this checkpoint. The connected chat environment has no repository
checkout shell.

## Remaining validation

1. dedicated workflow compile/test;
2. paired native benchmark artifact;
3. inspect exact-head workflow once;
4. if green, freeze measured native result without altering raw evidence;
5. if red, repair only attributable frontier.

## Next action after green

Use the measured result to decide whether compact priority-offset hydration is
promoted for this native Lane 5 boundary. Then reconcile the same representation
with PR #625 I048 constructor/interpreter runtime-adapter work for unseen-input
native library execution.
