# Pass 219B canonical scaling composition benchmark — restart record

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `main @ 634db40aaf57ec087b7353d6d9205d896622adb4`
- branch: `agent/pass219b-canonical-scaling-composition-benchmark`
- intended target: `main`
- merge authorization: NOT GRANTED
- classification: BENCHMARK / NON-PROMOTIONAL / NO CANONICAL AUTHORITY CHANGE

## Objective

Measure and compare compatible deterministic scaling compositions across the already-implemented Pass 207, Pass 208, and Pass 219B locality/selective-projection/sparse-dirty modules. Preserve exact semantic equality, original identity, singleton VM81 authority, Hash72/Hash216 authority boundaries, and fail-closed fallbacks.

The benchmark must distinguish deterministic work/capacity reduction from environment-specific wall timing. It must not select a device-specific canonical constant.

## Planned changed files

- `benchmarks/pass219b/pass219b_canonical_scaling_composition_benchmark.cpp`
- `benchmarks/pass219b/analyze_pass219b_canonical_scaling_composition.py`
- `.github/workflows/pass219b-canonical-scaling-composition.yml`
- this restart record
- generated benchmark evidence only if validation is terminal green and a later explicit evidence-seal step is authorized

## Required compositions

1. dense reference
2. phase-local candidate expansion only
3. exact selective projection only
4. exact selective projection + sparse dirty update
5. phase locality + selective projection
6. phase locality + selective projection + sparse dirty update
7. same full stack with actual Pass 208 CPU_REFERENCE candidate expansion and inherited Pass 207 deterministic runtime/cache path
8. recursive phase-locality planner depth sweep through the currently implemented maximum depth

## Required workloads

- exact projection ratios: 1/3, 7/20, 5/14, 4/11, 3/8, 2/5, 5/12
- dirty source-cell counts: 1, 3, 7, 27, 81
- phase-locality depths: 1 through the implemented maximum
- exact-selector available and unavailable/fallback cases
- dirty-set complete and incomplete/fallback cases
- cold/reference and cache/reuse observations where the inherited module exposes them

## Validation gates

- cumulative exact ABI compiles with warnings as errors
- existing Pass 219B I1/I5/I7/I8 conformance remains green
- existing Pass 207 and Pass 208 tests remain green
- new benchmark proves exact selected/projection equality for every admitted composition
- original identities remain preserved
- no float/double in exact planner/decision code
- no canonical mutation/persistence/Hash72 authority added
- incomplete selector/dirty witnesses fail closed to complete path
- wall timings reported as observational only
- deterministic work, bytes, dispatch counts, and potential/materialized phase volumes reported separately

## Environment

Primary validation: GitHub-hosted Ubuntu 24.04 CPU runner. Physical GPU speedup is not claimed by this branch. Existing Fold7 WebGPU evidence remains a hardware witness only.

## Completed

- base resolved to current canonical main `634db40aaf57ec087b7353d6d9205d896622adb4`
- benchmark branch created
- existing Pass 219B I2/I4/I5/I7/I8 evidence and Pass 207/208 interfaces inspected
- benchmark design fixed to ablation/Pareto comparison rather than an arbitrary weighted score

## Remaining

1. implement C++ exact composition benchmark
2. implement deterministic analyzer
3. add dependency-scoped CI
4. run exact branch validation
5. classify result as PASS / NO_SINGLE_WINNER / BLOCKED
6. do not merge without explicit authorization

## Blockers

None at checkpoint creation.
