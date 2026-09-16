# Pass 219 — 120 ms Reciprocal x,y,z,w Wave-Normalization Benchmark v3

**Date:** 2026-09-16  
**Status:** normative benchmark contract  
**Depends on:** `PASS_219_120S_RECIPROCAL_XYZW_V2`, Lane 5 1.48, normalized optimization control v1

## 1. Objective

Measure HHS/Lane 5 and an optimized exact conventional architecture in a reciprocal four-pass design where **all four measurements have the identical wall-clock bound**:

```text
Delta_t = 120,000,000 ns = 120 ms

A / x = HHS maximum exact capacity on stream X during Delta_t
B / y = optimized conventional maximum exact capacity on stream Y during Delta_t
C / z = optimized conventional progress on frozen Dataset X during Delta_t
D / w = HHS progress on frozen Dataset Y during Delta_t
```

The equal `Delta_t` makes `x,y,z,w` directly comparable rate/amplitude channels. No leg receives an unbounded completion interval.

## 2. Two datasets, two observations each

Use two deterministic domain-separated lazy streams:

```text
X_i = Query(seed_X, i)
Y_i = Query(seed_Y, i)
seed_X != seed_Y
```

A alone selects Dataset X by processing the longest complete prefix it can finish inside its 120 ms producer window.

B alone selects Dataset Y by processing the longest complete prefix it can finish inside its 120 ms producer window.

The frozen dataset identities are:

```text
Dataset X = (seed_X, A.query_count, A transition sum, A descriptor bits, A descriptor digest, A endpoint digest)
Dataset Y = (seed_Y, B.query_count, B transition sum, B descriptor bits, B descriptor digest, B endpoint digest)
```

C may process only Dataset X, in original order, for 120 ms.
D may process only Dataset Y, in original order, for 120 ms.

Thus each dataset appears in exactly two passes:

```text
X: A -> C
Y: B -> D
```

Neither reciprocal pass may choose a new dataset, alter a seed, reorder queries, or process beyond the frozen producer prefix.

## 3. Architectures

### HHS architecture: A and D

Each completed query requires:

```text
exact affine composition
+ independent exact 2x2 matrix-power verification
+ endpoint equality
+ production Lane 5 1.48 admission
```

with:

```text
materialized_intermediate_states = 0
candidate_only = 1
canonical VM81 mutation authority = 0
canonical Hash72 authority = 0
canonical Hash216 authority = 0
signed environmental VM81 admission required
```

### Optimized conventional architecture: B and C

Each completed query uses exact 2x2 homogeneous matrix exponentiation by squaring over the same modular integer arithmetic. It has no Lane 5 admission step.

This is the optimized skip-ahead comparator. The v1 literal-step comparator remains separate evidence.

## 4. Equal-time timing rule

Every pass receives exactly the same nominal bound:

```text
Delta_t = 120 ms
```

Producer passes A/B stop starting new queries once the clock reaches `Delta_t`.

Reciprocal passes C/D stop when either:

```text
(a) the full frozen dataset is complete, or
(b) Delta_t is reached.
```

If the reciprocal architecture completes the frozen dataset early, it records `dataset_complete=true` and the exact `completion_elapsed_ns`, but its normalized measurement interval remains `Delta_t`. The unused interval is not reused for a different dataset.

The analyzer permits only bounded current-query overrun and rejects any pass outside the declared timing tolerance.

## 5. Reciprocal prefix identity

When C or D does not finish its frozen dataset inside 120 ms, it must still prove that its completed prefix is exactly the producer's corresponding prefix.

For every reciprocal pass report:

```text
completed prefix query count
completed prefix represented-transition sum
completed prefix descriptor bits
ordered descriptor digest
ordered endpoint digest
```

The producer prefix of the same length is independently replayed and MUST match all five fields.

If the reciprocal pass completes the full dataset, these fields MUST equal the full producer dataset identity.

## 6. Raw x,y,z,w measurement channels

For one common `Delta_t`, define raw completed represented work:

```text
x = A.represented_transitions_completed
    [HHS on X during Delta_t]

y = B.represented_transitions_completed
    [conventional on Y during Delta_t]

z = C.represented_transitions_completed
    [conventional on frozen X during Delta_t]

w = D.represented_transitions_completed
    [HHS on frozen Y during Delta_t]
```

Because all four use the same time interval, their rates are simply:

```text
R_x = x / Delta_t
R_y = y / Delta_t
R_z = z / Delta_t
R_w = w / Delta_t
```

The benchmark SHALL also report query counts, descriptor bits, endpoint state-space bits-equivalent, exact control-operation counts, dataset completion fractions, and early-completion timestamps.

## 7. Dimensionless normalized amplitudes

To insert measured values into an algebraic `x,y,z,w` tensor without mixing physical units, first normalize the four same-unit rates against one fixed positive reference `Gamma_0`:

```text
x_hat = R_x / Gamma_0
y_hat = R_y / Gamma_0
z_hat = R_z / Gamma_0
w_hat = R_w / Gamma_0
```

`Gamma_0` SHALL be recorded explicitly. v3 uses a fixed unit reference of one represented transition per second for the primary transition-rate tensor, so the numerical amplitudes equal the measured rates while remaining dimensionless by definition of the normalization unit.

A second endpoint-information tensor may use one endpoint bit-equivalent per second as its reference.

## 8. HHS reciprocal measurement tensor

The measured dimensionless channels may be projected into the existing ordered relational surface:

```text
T(x_hat,y_hat,z_hat,w_hat) =

List(
  List((x_hat*y_hat), x_hat+y_hat, (y_hat*x_hat)),
  List(
    (x_hat*y_hat)-(z_hat*w_hat),
    x_hat+y_hat-z_hat-w_hat
      +(x_hat*y_hat)+(y_hat*x_hat)
      -(z_hat*w_hat)-(w_hat*z_hat),
    (w_hat*z_hat)-(y_hat*x_hat)
  ),
  List((w_hat*z_hat), z_hat+w_hat, (z_hat*w_hat))
)
```

The scalar numeric projection is commutative, so numerically `x_hat*y_hat == y_hat*x_hat` and `z_hat*w_hat == w_hat*z_hat`. The ordered labels remain preserved in evidence because HHS operator direction is a typed semantic channel even when this scalar benchmark projection has equal product magnitudes.

The central reciprocal imbalance observable is:

```text
Delta_xyzw = x_hat*y_hat - z_hat*w_hat
```

and the paired same-dataset capacity ratios are:

```text
rho_X = x / z     if z > 0
rho_Y = w / y     if y > 0
```

`rho_X` asks how much producer-X represented work HHS resolves in the common window relative to conventional progress on the same frozen X.

`rho_Y` asks how much HHS progresses on conventional-produced Y relative to the conventional capacity that created Y.

## 9. Discrete-time wave series

One four-pass execution produces one reciprocal state vector:

```text
Psi_n = (x_hat_n, y_hat_n, z_hat_n, w_hat_n)
```

Repeated executions with the same benchmark definition and common `Delta_t` form a discrete series. Only with at least three successive normalized observations may a second-time difference be reported:

```text
D2_t Psi_n = (Psi_(n+1) - 2*Psi_n + Psi_(n-1)) / Delta_t^2
```

This is the precise discrete wave/curvature comparison observable for benchmark evolution over time. A single four-pass run defines `Psi_n` and `T(Psi_n)`; it does not by itself establish a physical wave equation.

## 10. Acceptance

The v3 cycle passes only if:

```text
A/B/C/D all use the same Delta_t = 120 ms
all four execute sequentially on one runner with one active benchmark thread
A and D use the identical HHS architecture
B and C use the identical optimized conventional architecture
X is selected only by A and consumed only by C
Y is selected only by B and consumed only by D
C's completed prefix exactly matches A's prefix of equal length
D's completed prefix exactly matches B's prefix of equal length
no reciprocal pass processes beyond its frozen dataset
all HHS endpoints pass independent verification and Lane 5 admission
HHS materialized_intermediate_states remains zero
raw integer evidence is preserved before normalized/tensor calculations
```

## 11. Claim scope

This benchmark creates a falsifiable equal-time reciprocal architecture comparison on two exact deterministic datasets. It defines a mathematically uniform `x,y,z,w` measurement surface and discrete-time normalization suitable for HHS relational analysis.

It does not claim that the scalar benchmark tensor is a physical quantum wavefunction, nor does it by itself establish universal classical-computing supremacy.