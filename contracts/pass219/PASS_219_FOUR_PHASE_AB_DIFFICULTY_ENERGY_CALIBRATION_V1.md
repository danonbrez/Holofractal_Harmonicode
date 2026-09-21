# Pass 219 — Four-Phase Reciprocal A:B Difficulty/Energy Calibration v1

**Date:** 2026-09-17  
**Status:** normative benchmark/calibration contract  
**Parent optimization control:** `contracts/pass219/PASS_219_NORMALIZED_OPTIMIZATION_CONTROL_V1.md`

## 1. Purpose

Measure the steady-state cost/capacity of carrying the direct Harmonic36/Hash216 `M` exponent-lattice witness through the current Lane 5 exact route under a matched, same-runner A:B control.

The benchmark is performance evidence only. It confers no canonical state, Hash72, Hash216, persistence, clock, PQC-key, or semantic authority.

## 2. Four ordered reciprocal phases

The benchmark covers all legal quarter-cycle slots with the exact reciprocal half-turn:

```text
xy :  0 -> 36
yx : 36 ->  0
zw : 18 -> 54
wz : 54 -> 18
```

The names are ordered benchmark labels for the repository's existing reciprocal phase geometry. They do not collapse ordered products into commutative products.

## 3. Paired A:B arms

For the same generated route input, phase, difficulty rank, compiler, runner, thread count, and leg budget:

```text
A = hhs_exact_pass219_lane5_unbounded_workload_route_validate
    + hhs_exact_pass219_h36_hash216_m_exponent_bind
    + hhs_exact_pass219_h36_hash216_m_exponent_validate

B = hhs_exact_pass219_lane5_unbounded_workload_route_validate
```

A therefore measures the route plus the newly merged direct `M`-binding witness. B is the matched route-only control.

The H36/Hash216 transition binding used by A is initialized before timed legs. Timed A iterations bind and validate one exact occurrence witness per accepted route. This is a steady-state benchmark; setup time is not mixed into per-iteration throughput.

## 4. Difficulty gradient

Difficulty ranks are exactly `1..9`. The signed calibration gradient is inherited verbatim from the Pass 067.1 exact percentile function:

```text
g(rank) = 2 * (rank-1)/(9-1) - 1

rank 1..9:
-1, -3/4, -1/2, -1/4, 0, 1/4, 1/2, 3/4, 1
```

Target iteration count doubles by rank:

```text
N_rank = N_base * 2^(rank-1)
```

The rank and gradient are calibration metadata. The benchmark does not reinterpret the signed gradient as probability, authority, or physical energy.

## 5. Time bound

Default execution controls:

```text
global budget = 1,200,000,000 ns
per-arm leg budget = 15,000,000 ns
base iterations = 8
```

Both are environment-overridable for controlled experiments. Each arm stops at its leg budget or at target completion. A new phase pair is not started when two additional leg budgets cannot fit inside the remaining global budget. Final elapsed time must remain within the global budget plus the explicit timer tolerance.

## 6. A:B normalization

For each paired phase/rank sample:

```text
R_A = A_completed * 1e9 / A_elapsed_ns
R_B = B_completed * 1e9 / B_elapsed_ns

N_AB = R_A / R_B
     = (A_completed * B_elapsed_ns)
       / (B_completed * A_elapsed_ns)
```

`N_AB` is represented as an exact rational. Basis points are reported only as an integer floor for compact inspection.

Aggregate phase and global ratios use the same exact count/time formula over accumulated paired observations.

## 7. Difficulty/energy-rated calibration

Energy is inherited from `PASS_067_1_LO_SHU_HARMONIC_PHASE_ENERGY_V1`:

```text
logical tensor energy = 225 exact units
reciprocal two-tensor boundary = 450 exact units
```

This is a conserved logical HHS calibration quantity, **not physical joules**. The benchmark SHALL emit `physical_energy_measured=false` unless a future version adds an actual hardware energy instrument.

For rank `r`, the calibration rating denominator is:

```text
C_r = r * 450
```

and each arm may report an exact difficulty/energy-normalized rate:

```text
E_A = R_A / C_r
E_B = R_B / C_r
```

Because paired A and B share the same `C_r`, the normalized A:B ratio remains `N_AB`; the extra rate exposes performance per declared calibration-rating unit without changing the paired comparison.

## 8. Exact A-arm membrane

Every completed A iteration must prove:

```text
route accepted = 1
materialized intermediates = 0
candidate_only = 1
canonical mutation authority = 0
canonical Hash72 authority = 0
canonical Hash216 authority = 0
canonical persistence authority = 0
signed environmental VM81 admission required = 1

same_linear5184_identity = 1
direct_shared_m_binding = 1
translator_required = 0
M exponent coordinate = (216,144)
floating-point authority = 0
```

## 9. Negative controls

Before timing, the executable SHALL fail closed for at least:

1. reciprocal phase/inverse mismatch;
2. forced `translator_required=1` on an `M` witness;
3. corrupted `M` exponent coordinate.

Timing results are invalid if any negative control does not fail closed.

## 10. Acceptance

A calibration run passes only when:

- all four ordered reciprocal phases have paired A:B samples;
- native exact/authority checks pass;
- Pass 067.1 energy conservation validates all four ordered gates;
- exact difficulty gradients match ranks;
- the time bound is respected;
- negative controls fail closed;
- no canonical authority is introduced;
- results and generated report are retained as workflow artifacts or repository evidence.

No minimum A:B speed ratio is imposed by this contract because A intentionally performs an additional exact proof layer. The result measures its cost/capacity; a later optimization cycle may establish a versioned performance floor from this calibration baseline.
