# HHS Time-Bounded Mathematical Supremacy v1 — Executed Evidence

**Date:** 2026-09-16  
**Status:** EXECUTED / EXACT / RUNNER-NORMALIZED / STAGE-1 BOUNDED CLAIM  
**Contract:** `contracts/pass219/PASS_219_TIME_BOUNDED_MATH_SUPREMACY_V1.md`  
**Validated implementation head:** `afa7f4aac56cbaaeadd845cf56a3e482ab7199d6`

## 1. Claim scope

This evidence establishes a bounded Stage-1 result over the exact comparator classes declared by the contract:

```text
C_step: sequential application of the affine transition oracle, one represented step at a time
C_scan: sequential CRT candidate enumeration from 0 through the unique target M-1
```

It does **not** claim that no optimized conventional algorithm can solve these mathematical families efficiently. HHS itself is running on ordinary x86-64 hardware. The demonstrated claim is that exact algebraic composition plus the Lane 5 candidate membrane dominates the specified linear/materializing execution classes inside the fixed resource envelope.

Stage 2 is explicitly reserved for optimized conventional comparator algorithms.

## 2. Workflow identity

```text
workflow: Pass 219 Time-Bounded Math Supremacy v1
run: 35090442347
job: validate-time-bounded-math-supremacy
job id: 104775224088
result: success
artifact: hhs-time-bounded-math-supremacy-v1
artifact id: 10444171639
artifact ZIP SHA-256:
89cb85f2d42689caeff28f8246f193ddc55149b7c7600041697f557455aa59ca
```

## 3. Runner normalization

```text
runner label: ubuntu-24.04
runner image: 20260907.300.1
OS: Ubuntu 24.04.5 LTS
CPU: AMD EPYC 7763 64-Core Processor
logical CPUs exposed: 4
active benchmark threads: 1
observed memory: 16,373,452 KiB
kernel: 6.17.0-1022-azure
compiler: GCC 13.3.0
per-case linear-comparator time bound: 50,000,000 ns
```

Same-runner Lane 5 normalization control:

```text
candidate routes: 1,000,000
elapsed_ns: 3,787,173,884
candidate-rate floor: 264,049/s
stream state: 568 bytes
materialized intermediate states: 0
basis information rate:
117,299,701.92282056187216167727510868819029891377329803814064846870576483221692565 bits-equivalent/s
```

## 4. Affine modular orbit family

Problem:

```text
F(x) = a*x + b (mod m)
compute F^k(x0)
```

HHS path composes affine maps by exponentiation and independently verifies the endpoint with 2x2 homogeneous matrix exponentiation. Every endpoint is then admitted through the production Lane 5 1.48 route validator with zero represented intermediate states.

| k | HHS compositions | HHS total | Linear result | Linear elapsed/steps | Exact-work ratio `k/compositions` | Time ratio |
|---:|---:|---:|---|---:|---:|---:|
| 1,000 | 15 | 6,713 ns | solved exactly | 11,832 ns / 1,000 | 66.6667x | 1.76255x executed |
| 100,000 | 22 | 3,758 ns | solved exactly | 1,195,122 ns / 100,000 | 4,545.4545x | 318.02076x executed |
| 10,000,000 | 31 | 3,817 ns | timeout | 50,009,375 ns / 4,214,784 | 322,580.6452x | >=13,099.2926x |
| 1,000,000,000 | 42 | 5,531 ns | timeout | 50,005,227 ns / 4,206,592 | 23,809,523.8095x | >=9,039.9566x |
| 1,000,000,000,000 | 52 | 7,805 ns | timeout | 50,042,076 ns / 4,227,072 | 19,230,769,230.7692x | >=6,406.1499x |

### Affine empirical crossover

```text
n* = k = 10,000,000
Omega = 10,000,000
H_P = log2(Omega) = 23.253496664211536 bits-equivalent
HHS total = 3,817 ns
HHS exact affine compositions = 31
linear C_step required work = 10,000,000 sequential transition applications
linear work completed before timeout = 4,214,784
linear time bound = 50,000,000 ns
problem-information density = 6,092,087.153317143 bits-equivalent/s
exact-work ratio = 322,580.6451612903x
bounded time ratio >= 13,099.2926381975x
```

The endpoint agreed exactly between HHS affine composition and independent matrix exponentiation. For smaller cases where `C_step` completed, all three paths agreed exactly.

## 5. CRT reconstruction family

Constructed exact family:

```text
x == -1 (mod m_i)
M = product(m_i)
unique canonical solution in [0,M): x = M - 1
```

The HHS path performs incremental exact CRT composition. `C_scan` enumerates candidates from zero and therefore requires exactly `M` visits for the constructed target.

| Moduli count | M / Omega | HHS compositions | HHS total | Linear result | Linear elapsed/steps | Exact-work ratio `M/compositions` | Time ratio |
|---:|---:|---:|---:|---|---:|---:|---:|
| 2 | 10,403 | 1 | 4,929 ns | solved exactly | 7,444 ns / 10,403 | 10,403x | 1.51025x executed |
| 3 | 1,113,121 | 2 | 3,376 ns | solved exactly | 789,201 ns / 1,113,121 | 556,560.5x | 233.76807x executed |
| 4 | 121,330,189 | 3 | 3,206 ns | timeout | 50,000,879 ns / 61,210,624 | 40,443,396.3333x | >=15,595.75795x |
| 5 | 13,710,311,357 | 4 | 4,729 ns | timeout | 50,002,202 ns / 69,300,224 | 3,427,577,839.25x | >=10,573.05984x |
| 6 | 1,741,209,542,339 | 5 | 4,118 ns | timeout | 50,002,773 ns / 70,549,504 | 348,241,908,467.8x | >=12,141.81642x |

### CRT empirical crossover

```text
n* = 4 moduli
Omega = M = 121,330,189
H_P = log2(Omega) = 26.854363321113087 bits-equivalent
HHS total = 3,206 ns
HHS exact CRT compositions = 3
linear C_scan required work = 121,330,189 candidate visits
linear work completed before timeout = 61,210,624
linear time bound = 50,000,000 ns
problem-information density = 8,376,283.007209322 bits-equivalent/s
exact-work ratio = 40,443,396.33333333x
bounded time ratio >= 15,595.7579538366x
```

At six moduli, the exact composition still completed in 4,118 ns with five composition stages while the declared linear scan has a proved `1,741,209,542,339`-visit requirement for the constructed target.

## 6. Lane 5 authority membrane

Every HHS benchmark endpoint passed the existing production 1.48 route validator with:

```text
materialized_intermediate_states = 0
candidate_only = 1
canonical VM81 mutation authority = 0
canonical Hash72 authority = 0
canonical Hash216 authority = 0
signed environmental VM81 admission required = 1
```

The initial implementation attempt correctly failed this membrane because the benchmark accidentally placed its mathematical composition count in the ABI's `integer_route_cost` field and used an invalid binary/nested-zero tuple. The repair preserved the validator unchanged:

```text
Lane 5 receipt cost = evidence_count + contradiction_check_count + 1 = 7
mathematical composition count = separate benchmark evidence bound into the route witness
collapse tuple = trinary 0 / binary 0 / nested-zero 1
```

The repaired run passed without weakening canonical admission.

## 7. Stage-1 theorem statement supported by this run

For the tested affine family and declared comparator `C_step`, on this runner and 50 ms bound:

```text
for tested k >= 10^7:
HHS exact composition + independent verification + Lane 5 admission completes inside T_max,
while C_step does not complete inside T_max.
```

For the tested CRT family and declared comparator `C_scan`:

```text
for tested modulus counts >= 4:
HHS exact CRT composition + verification + Lane 5 admission completes inside T_max,
while C_scan does not complete inside T_max.
```

The mathematical work separations arise from the declared comparator definitions:

```text
Affine C_step: W_C(k) = k
HHS affine composition: logarithmic number of exact map compositions in k

CRT C_scan: W_C = M for target M-1
HHS CRT composition: r-1 exact modular composition stages for r moduli
```

The engineering measurements show that the implemented HHS paths retain those mathematical advantages after independent verification and production Lane 5 admission overhead on the tested runner.

## 8. Falsifiability and next target

This result is falsifiable under the contract. It would fail if exact endpoints disagreed, Lane 5 admission failed, HHS exceeded the resource bound, or the declared comparator completed inside the bound with no declared HHS resource advantage.

It does not yet establish a lower bound over all conventional algorithms. The required next cycle is Stage 2:

```text
add optimized conventional affine exponentiation and optimized CRT as separate comparators;
separate common mathematical algorithmic advantage from HHS-specific routing/admission advantage;
then add harder number-theory/search families where the strongest known comparator classes remain superlinear/exponential or materialization-bound under an explicitly stated model.
```

That is the path from a proved linear-comparator separation toward progressively stronger computational-class claims without changing the evidence standard.
