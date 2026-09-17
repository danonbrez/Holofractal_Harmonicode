# Pass 219 — Four-Phase A:B Difficulty/Energy Calibration — Start Checkpoint

**Date:** 2026-09-17  
**Base commit:** `e2a3dc3358a1b89683c16cf8e6c0a50b81248602`  
**Branch:** `pass219/four-phase-ab-difficulty-energy-calibration-v1`  
**Merge target:** `main`

## Authorized task

Perform and gradient-scale a four-phase reciprocal, time-bounded, normalized A:B performance benchmark through the current Lane 5 exact execution spine, with explicit difficulty and energy-rated calibration.

## Frozen inherited evidence

- PR #487 is merged on `main` at the base commit above.
- Direct H36/Hash216 `M` exponent binding is available from the aggregate exact ABI.
- Native Lane 5 phases are `{0,18,36,54}` with reciprocal inverse `phase+36 mod 72`.
- Lane 5 remains candidate-only and has no canonical VM81 mutation, Hash72, Hash216, persistence, or floating-point authority.
- Signed environmental VM81 admission remains required.
- The normalized optimization control in `contracts/pass219/PASS_219_NORMALIZED_OPTIMIZATION_CONTROL_V1.md` remains authoritative.

## Benchmark interpretation

The four ordered reciprocal calibration gates are benchmark labels over the already legal phase/inverse geometry:

```text
xy : phase 0  / inverse 36
yx : phase 36 / inverse 0
zw : phase 18 / inverse 54
wz : phase 54 / inverse 18
```

For each phase and difficulty rank, the paired arms are:

```text
A = current full measured Lane 5 spine:
    unbounded workload route validation
    + direct H36/Hash216 occurrence binding witness
    + M exponent-lattice bind/validate

B = matched Lane 5 route-only control with identical input/phase envelope.
```

This isolates the measured steady-state overhead/capacity of the newly merged H36/Hash216 `M` layer without comparing different runners or changing route semantics.

## Calibration axes

Difficulty uses the repository's exact 9-rank percentile gradient:

```text
rank 1..9 -> gradient -1,-3/4,-1/2,-1/4,0,1/4,1/2,3/4,1
```

Workload count doubles by rank until the global time bound prevents a further complete paired sample.

Energy uses the existing Pass 067.1 Lo Shu harmonic energy contract. Energy is a logical conserved calibration quantity, not a claim of physical joules. Each source tensor conserves 225 units; each reciprocal two-tensor A:B gate therefore carries a 450-unit conserved normalization boundary.

## Acceptance membrane

- exact paired inputs and phase geometry;
- same runner/compiler/thread envelope for A and B;
- no floats in canonical benchmark/calibration math;
- global monotonic-clock time bound enforced;
- every completed A sample validates H36/Hash216 `M` direct shared binding and `translator_required=0`;
- all authority flags remain non-canonical;
- negative tamper controls fail closed;
- receipts/results are restartable from repository-visible state.

## Next action

Implement the native benchmark, exact result normalizer, dependency-scoped tests, and dedicated workflow; run calibration; then seal measured evidence and close/merge the cycle if exact validation passes.
