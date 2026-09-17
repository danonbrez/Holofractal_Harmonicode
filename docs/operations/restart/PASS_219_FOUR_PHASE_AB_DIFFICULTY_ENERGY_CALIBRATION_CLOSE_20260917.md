# Pass 219 — Four-Phase A:B Difficulty/Energy Calibration — Close Checkpoint

**Date:** 2026-09-17  
**Base commit:** `e2a3dc3358a1b89683c16cf8e6c0a50b81248602`  
**Branch:** `pass219/four-phase-ab-difficulty-energy-calibration-v1`  
**Merge target:** `main`  
**Measured/validated implementation head:** `6fd355d2551440d5026cbcffb9060b9bf380b299`  
**Evidence commit:** `a0d22285892582683b86bfd1087952ae770ab050`

## Delivered surfaces

- `benchmarks/pass219/hhs_lane5_four_phase_ab_gradient_calibration_v1.c`
- `tools/pass219/hhs_four_phase_ab_calibration_analyze_v1.py`
- `contracts/pass219/PASS_219_FOUR_PHASE_AB_DIFFICULTY_ENERGY_CALIBRATION_V1.md`
- `.github/workflows/pass219-four-phase-ab-difficulty-energy-calibration-v1.yml`
- `docs/pass219/HHS_FOUR_PHASE_AB_DIFFICULTY_ENERGY_CALIBRATION_V1_EVIDENCE.md`
- start and close restart checkpoints.

## Dedicated validation

Successful dedicated workflow:

```text
workflow: Pass 219 Four-Phase AB Difficulty Energy Calibration v1
run:      35256456162
job:      105321200765
head:     6fd355d2551440d5026cbcffb9060b9bf380b299
result:   PASS
```

Validated stages:

1. aggregate exact ABI compile under strict C11 warnings-as-errors;
2. inherited exact ABI link support build;
3. native calibration benchmark compile;
4. analyzer compile;
5. native time-bounded four-phase execution;
6. exact difficulty/energy normalization;
7. calibration artifact upload.

The prior run `35256209410` had already completed the native benchmark successfully and failed only because the path-invoked analyzer could not import the repository package. That tooling defect was repaired by deriving and inserting the repository root in the analyzer. No benchmark/runtime semantics were weakened.

## Measured calibration

```text
phases:                     xy, yx, zw, wz
difficulty ranks:           1..9
gradient:                   -1 .. +1 in exact quarter steps
paired phase/rank samples:  36
iterations per arm/phase:   4088
iterations per arm total:   16352
batch elapsed:              93,079,322 ns
global time bound:          1,200,000,000 ns
```

Exact aggregate A:B results:

```text
xy = 5734664/5787569     (9908 bp floor)
yx = 11636400/11684621  (9958 bp floor)
zw = 11582719/11740166  (9865 bp floor)
wz = 11547276/11706575  (9863 bp floor)

global = 46235723/46706500
       = 9899 bp floor
       ~= 0.98992052498
```

A is the route plus direct H36/Hash216 M witness; B is the same route-only control. The baseline therefore measures about 98.992% of matched B throughput while carrying the additional exact proof layer. It is a calibration baseline, not a claimed speedup.

## Difficulty and energy calibration

- Exact difficulty ranks use `exact_percentile_gradient(rank,9)`.
- Target work doubles from 8 to 2048 iterations per phase/arm across ranks 1..9.
- Logical tensor energy is 225 exact Pass 067.1 units.
- Logical reciprocal-pair energy is 450 units.
- Rank-r difficulty/energy denominator is `r*450`.
- Physical joules/watts were not measured and are not claimed.

## Authority state

Frozen unchanged:

```text
candidate_only                               = 1
canonical VM81 mutation authority            = 0
canonical Hash72 authority                   = 0
canonical Hash216 authority                  = 0
canonical persistence authority              = 0
floating-point authority                     = 0
direct_shared_m_binding                      = 1
translator_required                          = 0
requires signed environmental VM81 admission = 1
```

## Negative controls

Fail-closed controls passed for:

- invalid reciprocal phase/inverse pairing;
- forced translator requirement;
- corrupted M exponent coordinate.

## Artifact receipt

```text
artifact id:   10513321234
artifact name: pass219-four-phase-ab-difficulty-energy-calibration-v1
size:          8136 bytes
SHA-256:       2bcb02d9d8b8772b299ff7432c77123a5358a9947d440953ad48d432089263b2
```

## Remaining closure action

This checkpoint commit intentionally triggers one final exact-head dedicated validation. If that validation remains green and `main` has not drifted incompatibly, open/merge the integration PR and verify the resulting `main` commit. If unrelated repository-wide workflows fail, repair only when they are dependency-relevant to this cycle.

## Next optimization cycle

Use the sealed global and per-phase ratios as the initial performance floor candidate for reducing direct M-proof overhead while preserving every exact route, phase, energy, admission, authority, and no-translator invariant.
