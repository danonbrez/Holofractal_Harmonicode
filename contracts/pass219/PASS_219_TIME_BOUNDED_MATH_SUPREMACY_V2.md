# Pass 219 — Time-Bounded Mathematical Supremacy v2

**Date:** 2026-09-16  
**Status:** normative experimental/theorem contract  
**Depends on:** `PASS_219_TIME_BOUNDED_MATH_SUPREMACY_V1`, Lane 5 1.48  
**Runner class:** `ubuntu-24.04`, one active benchmark thread

## 1. The theorem target

The v2 target is an existential bounded-computation claim.

For an exact mathematical problem family `P_n`, HHS method `H`, declared legacy comparator class `L`, fixed runner `R`, and common deadline `T_max`, a bounded supremacy witness exists at `n` iff:

```text
Verify(H(P_n)) = 1
T_H(P_n) <= T_max
M_H(P_n) <= M_max
```

and:

```text
L(P_n) does not return the exact completed state by T_max
```

while any smaller calibration cases on which both methods finish must satisfy exact endpoint equality.

The empirical witness is therefore:

```text
same problem
same exact target state
same runner
same active thread count
same deadline
HHS = complete + independently verified + Lane5 admitted
legacy comparator = incomplete at deadline
```

This is falsifiable: if the declared legacy comparator completes the same problem within the deadline, or HHS fails exact verification/admission/deadline, that witness fails.

## 2. Scope of "legacy architecture"

v2 does not use the phrase `all classical computing`.

The declared legacy class is a **state-materializing transition architecture**:

```text
L_step:
  state_(i+1) = F(state_i)
  for i = 0 .. k-1
```

It must explicitly execute each dependent transition and may not replace the chain with composition/exponentiation, a closed form, jump table, vector-cache witness, or precomputed route.

This models the linear/materializing execution pattern whose lower bound is part of the problem definition.

Because HHS itself runs on von Neumann hardware, the theorem is about algorithmic representation and execution method, not about different processor physics.

## 3. Problem family — exact modular affine orbit

Let:

```text
F(x) = a*x + b (mod m)
```

with fixed exact integers `a,b,m,x0` and problem:

```text
P_k: compute F^k(x0) exactly.
```

### 3.1 Legacy lower bound

For `L_step`, by construction:

```text
W_L(k) = k dependent transition applications.
```

This is an exact work lower bound for the declared class because state `i+1` is not available until transition `i` is executed.

### 3.2 HHS composition bound

Represent an affine map as:

```text
(A,B) := x -> A*x + B (mod m)
```

with exact composition:

```text
(A2,B2) o (A1,B1)
=
(A2*A1 mod m,
 A2*B1 + B2 mod m)
```

Binary composition computes `F^k` with counted exact compositions growing logarithmically in `k` and with no requirement to materialize the `k-1` represented intermediate states.

Every HHS endpoint SHALL also pass:

```text
independent exact 2x2 homogeneous matrix-power verification
production Lane 5 1.48 route admission
materialized_intermediate_states = 0
candidate_only = 1
canonical VM81/Hash72/Hash216 authority = 0
signed environmental VM81 admission required before canonical commit
```

## 4. Common deadline

The default v2 deadline is:

```text
T_max = 120,000,000 ns = 120 ms
```

Both architectures receive the same `T_max` independently and execute sequentially on the same runner with one active benchmark thread.

The deadline is a resource limit for each architecture, not a claim that two sequential measurements consume only 120 ms of wall-clock CI time.

## 5. Adaptive scaling gradient

The runner begins at a small deterministic `k_0` and scales:

```text
k_(n+1) = 10 * k_n
```

while:

```text
HHS remains exact and below T_max
```

For each `k_n`:

1. execute HHS exact composition;
2. independently verify with exact matrix exponentiation;
3. pass the endpoint through Lane 5 admission;
4. execute `L_step` until it either completes `k_n` transitions or reaches `T_max`;
5. if both complete, require identical endpoints;
6. if HHS completes and `L_step` does not, freeze the first crossover witness and stop increasing `k`.

Thus the runner converts successful lower-gradient completion into greater mathematical difficulty rather than increasing the deadline.

## 6. Reasonable-completion calibration

The first one or more small `k` values act as runner calibration. At least one calibration point where both architectures finish and agree exactly is required before a supremacy witness is accepted.

This prevents a broken or unreasonably short deadline from being interpreted as architecture superiority.

The evidence SHALL record:

```text
largest both-complete calibration k
first HHS-complete / legacy-incomplete k*
legacy steps actually executed before deadline
legacy completion fraction
HHS composition count
HHS algorithm time
independent verifier time
Lane 5 admission time
HHS total time
```

## 7. Information/work normalization

For each instance:

```text
Omega(k) = k
H_P(k) = log2(k)
```

for the declared linear transition uncertainty/work depth.

Exact-work ratio:

```text
I_work = k / W_H(k)
```

where `W_H(k)` is the counted exact affine-composition count.

When the legacy route is incomplete at the common deadline:

```text
I_time_lower_bound = T_max / T_H
completion_fraction_L = executed_steps / k
unresolved_fraction_L = 1 - completion_fraction_L
```

These are observational evidence and carry no canonical state authority.

## 8. Bounded supremacy witness

The v2 run may emit:

```text
BOUNDED_SUPREMACY_WITNESS
```

only when all conditions hold:

```text
at least one smaller k calibrated with exact HHS == legacy endpoint
HHS exact endpoint at k* verified independently
HHS total time <= T_max
Lane 5 admission PASS
HHS materialized intermediates = 0
legacy L_step did not complete k* by T_max
legacy executed at least one transition
same runner / one active thread / same arithmetic parameters
```

The witness SHALL identify `k*` and the declared comparator class in the artifact.

## 9. Falsification

The witness is falsified if:

```text
HHS and independent verifier disagree
Lane 5 rejects the HHS route
HHS exceeds T_max
legacy L_step completes k* within T_max
calibration endpoints disagree
legacy and HHS are not given identical P_k
runner/thread/deadline equality is violated
```

## 10. Interpretation

A passing v2 witness proves an existence statement of the form:

```text
There exists a tested exact mathematical operation P_k and a fixed reasonable
runner/deadline envelope for which the HHS algebraic composition method returns
the exact verified result while the declared linear state-materializing legacy
execution class cannot complete the same operation inside the deadline.
```

That is a precise theorem/engineering target. It is stronger than a throughput metaphor and narrower than a universal claim about every possible classical algorithm.
