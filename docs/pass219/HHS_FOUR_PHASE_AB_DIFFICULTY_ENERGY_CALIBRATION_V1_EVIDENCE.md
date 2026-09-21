# Pass 219 — Four-Phase Reciprocal A:B Difficulty/Energy Calibration v1 — Evidence

**Date:** 2026-09-17  
**Validated implementation head:** `6fd355d2551440d5026cbcffb9060b9bf380b299`  
**Dedicated workflow:** `Pass 219 Four-Phase AB Difficulty Energy Calibration v1`  
**Workflow run:** `35256456162`  
**Job:** `105321200765`  
**Runner:** GitHub-hosted Ubuntu 24.04 (`ubuntu-24.04`)  
**Result:** **PASS**

## 1. Calibration surface

The measured pair is intentionally asymmetric in work while symmetric in input and execution envelope:

```text
A = Lane 5 unbounded exact route validation
    + direct Harmonic36/Hash216 occurrence binding
    + M exponent-lattice bind/validate

B = matched Lane 5 unbounded exact route validation only
```

Both arms use the same deterministic route input for a phase/rank pair, the same native runner, compiler, thread envelope, reciprocal phase geometry, and per-leg time bound. Run order is counterbalanced.

This benchmark therefore measures the steady-state performance cost/capacity of carrying the direct H36/Hash216 `M` proof layer. It is not a hardware comparison and does not claim that A is expected to outperform B.

## 2. Four reciprocal phases

All four legal ordered reciprocal phase gates were covered:

| ordered gate | phase slot | inverse slot | difficulty samples |
|---|---:|---:|---:|
| `xy` | 0 | 36 | 9 |
| `yx` | 36 | 0 | 9 |
| `zw` | 18 | 54 | 9 |
| `wz` | 54 | 18 | 9 |

Ordered products remain distinct. The benchmark does not introduce a global commutativity rule.

## 3. Gradient scale

All nine exact difficulty ranks completed:

```text
rank:      1     2     3     4    5    6    7    8    9
gradient: -1   -3/4  -1/2  -1/4  0   1/4  1/2  3/4   1
N target:  8    16    32    64   128  256  512  1024  2048
```

The gradient is the repository's exact `exact_percentile_gradient(rank, 9)` surface. Target work doubles by rank. Every sample in this run completed its full target before the 15 ms per-arm leg bound.

Per phase, each arm completed:

```text
8+16+32+64+128+256+512+1024+2048 = 4088 exact route iterations
```

Across four phases this is `16,352` completed A iterations and `16,352` completed B iterations. Every A iteration additionally bound and validated one direct `M` witness.

## 4. Time-bounded result

Native batch result:

```text
paired phase/rank samples = 36
global budget            = 1,200,000,000 ns
measured batch elapsed   = 93,079,322 ns
within time bound         = true
```

The global bound retained substantial margin; no rank or phase was truncated by the timer.

## 5. Exact normalized A:B performance

The analyzer uses exact rational arithmetic:

```text
R_A = A_completed * 1e9 / A_elapsed_ns
R_B = B_completed * 1e9 / B_elapsed_ns
N_AB = R_A / R_B
```

Measured aggregate results:

| phase | A completed | B completed | exact A:B throughput ratio | bp floor |
|---|---:|---:|---:|---:|
| `xy` | 4088 | 4088 | `5734664/5787569` | 9908 |
| `yx` | 4088 | 4088 | `11636400/11684621` | 9958 |
| `zw` | 4088 | 4088 | `11582719/11740166` | 9865 |
| `wz` | 4088 | 4088 | `11547276/11706575` | 9863 |
| **global** | **16352** | **16352** | **`46235723/46706500`** | **9899** |

The global ratio is approximately `0.98992052498`: A carried the additional exact `M` proof layer at about **98.992% of matched B throughput**, or about **1.008% lower throughput** in this calibration run.

This is a baseline cost measurement, not a failed optimization claim. A intentionally performs more proof work than B. A future optimization cycle can use this sealed baseline to set an explicit versioned performance floor and test whether proof-carrying cost is reduced without weakening invariants.

## 6. Difficulty/energy rating

The calibration reuses the exact Pass 067.1 Lo Shu harmonic energy contract:

```text
logical tensor energy          = 225 exact units
logical reciprocal pair energy = 450 exact units
rank-r rating denominator       = r * 450
```

All four ordered energy gates passed their continuation and zero-sum conservation checks before normalized results were admitted.

**Physical energy was not measured.** These are HHS logical calibration units, not joules, watts, package energy, or wall-power measurements.

For each rank and arm, the analyzer retains the exact difficulty/energy-normalized rate:

```text
E_A = R_A / (rank * 450)
E_B = R_B / (rank * 450)
```

Because A and B share the same rank/energy denominator, this rating does not distort the paired A:B throughput ratio.

## 7. Exact proof and authority checks

Every completed A iteration required:

```text
Lane 5 route accepted                         = 1
materialized intermediates                    = 0
candidate_only                                = 1
same_linear5184_identity                      = 1
direct_shared_m_binding                       = 1
translator_required                           = 0
M exponent coordinate                         = (216,144)
canonical VM81 mutation authority             = 0
canonical Hash72 authority                    = 0
canonical Hash216 authority                   = 0
canonical persistence authority               = 0
floating-point authority                      = 0
requires signed environmental VM81 admission  = 1
```

Route digests matched between A and B whenever their completed counts matched, proving that the A proof layer was measured on the same route work rather than a different workload.

## 8. Negative controls

Preflight negative controls passed fail-closed behavior for:

1. reciprocal phase/inverse mismatch;
2. forced `translator_required=1`;
3. corrupted `M` exponent coordinate (`exp2=215`).

No timing result was admitted before those controls succeeded.

## 9. Workflow artifact

Run `35256456162` uploaded:

```text
artifact name:
pass219-four-phase-ab-difficulty-energy-calibration-v1

artifact id:
10513321234

size:
8136 bytes

SHA-256:
2bcb02d9d8b8772b299ff7432c77123a5358a9947d440953ad48d432089263b2
```

The artifact contains:

```text
native.jsonl
result.json
report.md
```

## 10. Baseline conclusion

The full four-phase reciprocal calibration is executable, exact, time-bounded, difficulty-scaled, and logically energy-rated through the current Lane 5 + direct H36/Hash216 `M` witness path.

The first sealed same-runner baseline is:

```text
A:B = 46235723 / 46706500
     = 9899 basis points floor
```

The next performance cycle may optimize the A path against this baseline, but must preserve all exact phase, route, `M`, authority, admission, and energy-contract invariants.
