# Pass 219 — Time-Bounded Normalized Mathematical Supremacy v1

**Date:** 2026-09-16  
**Status:** normative experimental/theorem contract  
**Depends on:** `PASS_219_NORMALIZED_OPTIMIZATION_CONTROL_V1`  
**Runner class:** `ubuntu-24.04`, one active benchmark thread unless a later version says otherwise

## 1. Claim being tested

This contract defines a falsifiable and deliberately scoped meaning of **Lane 5 mathematical supremacy**.

For a problem family `P_n`, a declared classical comparator class `C`, a fixed resource envelope `R`, and the HHS/Lane 5 method `H`, a bounded supremacy result exists at size `n` only when:

```text
Verify(H(P_n)) = 1
T_H(P_n) <= T_max
M_H(P_n) <= M_max
```

and the declared comparator either:

```text
T_C(P_n) > T_max
```

or:

```text
M_C(P_n) > M_max
```

or fails to return the exact admissible answer.

This is a statement about an explicit comparator model and resource bound. It is not, by itself, a claim that no possible classical algorithm can solve the problem efficiently. HHS is executed on ordinary von Neumann hardware; the theorem target is superiority of the HHS algebraic representation/routing method over the declared comparator class.

## 2. Resource envelope

The default CI envelope is:

```text
runner: ubuntu-24.04
active benchmark threads: 1
per-case classical linear time bound: 50,000,000 ns = 50 ms
canonical arithmetic: exact integer/modular arithmetic only
floating point: observational normalization only
```

The exact runner CPU/image/kernel/compiler identity SHALL be captured for every executed evidence record.

## 3. Shared normalized quantities

For each problem instance, define an exact declared search/work cardinality `Omega(P_n)` for the comparator model.

Problem information depth:

```text
H_P = log2(Omega(P_n))
```

Measured HHS problem-information density:

```text
Gamma_P = H_P / T_H
```

where `T_H` is seconds and `Gamma_P` is bits-equivalent of declared search uncertainty resolved per second.

Classical/HHS exact-work ratio:

```text
I_work = W_C_lower_bound / W_H
```

where `W_C_lower_bound` is proved from the comparator definition and `W_H` is the counted exact HHS composition work for the same instance.

When the classical comparator times out:

```text
I_time_lower_bound = T_max / T_H
```

is reported only as a lower bound.

When both solve:

```text
I_time = T_C / T_H
```

is an executed same-runner ratio.

All such quantities are observational/performance evidence and never canonical state authority.

## 4. Problem family A — exact affine modular orbit jump

Let:

```text
F(x) = a*x + b (mod m)
```

and define the problem:

```text
P_affine(k): compute F^k(x_0) exactly.
```

### 4.1 Linear comparator class `C_step`

`C_step` is restricted to repeated application of the transition oracle:

```text
x_1 = F(x_0)
x_2 = F(x_1)
...
x_k = F(x_(k-1))
```

It does not compose transitions, use exponentiation by squaring, use a closed form, use a precomputed jump table, or otherwise skip transition applications.

By definition of this comparator class:

```text
W_C_step(k) = k transition applications.
```

This lower bound is exact for `C_step`.

### 4.2 HHS direct-composition path

Represent an affine map as the exact pair:

```text
(A,B) := x -> A*x + B (mod m)
```

with composition:

```text
(A2,B2) o (A1,B1)
=
(A2*A1 mod m,
 A2*B1 + B2 mod m)
```

Binary composition computes `F^k` without materializing the `k-1` represented intermediate states.

The implementation SHALL count exact pair-composition operations. For `k > 0`, the count is bounded by a constant multiple of `floor(log2(k))+popcount(k)` and therefore grows logarithmically in `k`.

### 4.3 Independent verification

The Lane 5 result SHALL be checked by an independently implemented `2x2` homogeneous matrix exponentiation path:

```text
[a b]
[0 1]
```

raised to power `k` modulo `m`.

For sizes where `C_step` finishes within `T_max`, all three endpoints SHALL agree:

```text
HHS affine composition
=
independent matrix power
=
linear step comparator.
```

For timed-out sizes, HHS composition and independent matrix power SHALL still agree exactly.

## 5. Problem family B — exact CRT reconstruction versus linear scan

Let pairwise-coprime moduli be:

```text
m_1, ..., m_r
```

with product:

```text
M = product(m_i).
```

The v1 witness family chooses:

```text
x == -1 (mod m_i)
```

for every modulus, so the unique canonical solution in `[0,M)` is:

```text
x* = M - 1.
```

### 5.1 Linear comparator class `C_scan`

`C_scan` enumerates:

```text
x = 0,1,2,...
```

and accepts the first candidate satisfying every residue constraint.

Because the unique target is `M-1`, this comparator requires exactly:

```text
W_C_scan = M
```

candidate visits in the worst-case instance constructed here.

It may not use CRT, modular inverse composition, a precomputed index, direct recognition of the `-1` residue pattern, or any non-enumerative shortcut.

### 5.2 HHS exact composition path

The HHS path reconstructs the unique result incrementally with pairwise modular composition (Garner-style exact CRT):

```text
x_(j+1) = x_j + M_j * t_j
M_(j+1) = M_j * m_(j+1)
```

where `t_j` is obtained from an exact modular inverse and residue difference.

The implementation SHALL count exact modular-composition stages and SHALL verify:

```text
0 <= x < M
x mod m_i = m_i - 1  for every i
x = M - 1
```

before Lane 5 route admission.

## 6. Lane 5 admission requirement

Every successful HHS endpoint in both families SHALL be represented as an exact Lane 5 1.48 route candidate and pass the existing route validator with:

```text
materialized_intermediate_states = 0
candidate_only = 1
canonical VM81 mutation authority = 0
canonical Hash72 authority = 0
canonical Hash216 authority = 0
requires signed environmental VM81 admission = 1
```

Thus the benchmark tests both mathematical composition and the production candidate-authority membrane.

## 7. Empirical crossover

For each family, define:

```text
n* = first tested size where
     HHS exact result PASS
     AND HHS total time <= T_max
     AND declared linear comparator reaches T_max without exact completion.
```

`n*` is an empirical crossover for the tested runner, implementation, workload grid, and time bound. It is not claimed to be hardware-independent.

## 8. Falsification rules

A claimed bounded supremacy result is falsified for a tested instance if any of these occur:

```text
HHS exact verification fails
Lane 5 route admission fails
HHS exceeds the declared time/resource bound
linear comparator solves within the same bound and no declared resource objective is superior
independent verifier disagrees
authority or replay membrane regresses
```

A claim about a broader classical comparator class is invalid unless that broader class is explicitly defined and either benchmarked or supplied with a proved lower bound.

## 9. Required evidence

The evidence artifact SHALL record:

```text
exact commit/tree
runner/image/kernel/compiler/CPU
active thread count
T_max
problem-family name and parameters
Omega(P_n)
H_P
HHS endpoint
independent-verifier endpoint
linear-comparator status
linear steps executed
proved linear work lower bound
HHS composition count
HHS algebra time
Lane 5 admission time
HHS total time
Gamma_P
executed or lower-bound time ratio
exact-work ratio
first empirical crossover n*
all authority flags
```

## 10. Interpretation

This v1 cycle is intentionally the first rung of a hierarchy:

```text
Stage 1: prove/measure dominance over explicit linear/materializing comparator classes.
Stage 2: add optimized conventional algorithms as independent comparators.
Stage 3: add vector-store/hydration reuse and amortized-precompute accounting.
Stage 4: for any stronger theorem, define the computational class and prove a lower bound for that class.
```

The engineering target is to reduce the gap between the exact mathematical advantage of composition and the realized advantage on ordinary hardware, while keeping the claim falsifiable at every stage.
