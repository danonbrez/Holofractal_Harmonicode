# Pass 220 I011 — Möbius quarter-phase / harmonic closure

Status: **IMPLEMENTED — PROJECTION/WITNESS ONLY; CI VALIDATION PENDING**

Schema: `HHS_PASS_220_MOBIUS_QUARTER_PHASE_HARMONIC_V1`  
Lemma: `HHS-L146-013`

Implementation:

- `hhs_runtime/hhs_pass220_mobius_quarter_phase_v1.py`
- `tests/pass220/test_hhs_pass220_mobius_quarter_phase_v1.py`

This iteration is additive to the existing Pass 220 Lo Shu normalization and VM81 work. It does not widen canonical VM81, Hash72, Hash216, persistence, receipt, or mutation authority.

## 1. Exact Möbius drift channel

Define the exact rational projective map

```text
C(m) := (m - 1) / (m + 1)
```

on the finite nonsingular branch. Its inverse is

```text
C^-1(rho) := (1 + rho) / (1 - rho)
```

and therefore no floating approximation is required to move between the unbounded `m` coordinate and bounded reciprocal `rho` coordinate.

The exact iterates are

```text
C^0(m) = m
C^1(m) = rho
C^2(m) = -1/m
C^3(m) = -1/rho
C^4(m) = m
```

where the finite chart excludes branches that cross a projective pole.

Hence

```text
C^2: reciprocal phase inversion
C^4: projective closure
```

## 2. Quarter-phase lift into Z_72

The order-four orbit is indexed by the existing Hash72 quarter-phase positions:

```text
0   -> m
18  -> rho
36  -> -1/m
54  -> -1/rho
72  -> m
```

with

```text
18 = 72/4
36 = 2*18
54 = 3*18
72 = 4*18 == 0 mod 72
```

This is a typed correspondence between the exact projective C4 orbit and the existing quarter-phase address cycle. It does not flatten the phase carrier `u^k` into an ordinary rational number.

The projective matrix representative is

```text
M = [[1,-1],
     [1, 1]]
```

and exact integer multiplication gives

```text
M^2 = [[0,-2],
       [2, 0]]

M^4 = -4 I
```

so `M^4 ~ I` projectively.

## 3. Harmonic phase involution

The separate phase-channel self-normalization map is

```text
T(r) := r/(r-1)
```

with

```text
T(T(r)) = r.
```

For a channel pair `r=xy`, `s=zw`, the admissible harmonic closure is represented equivalently by

```text
(rs)/(r+s) = 1
rs = r+s
1/r + 1/s = 1
(r-1)(s-1) = 1
s = r/(r-1)
```

on the nonzero nonsingular branch.

Every finite translated reciprocal branch can therefore be parameterized by one exact rational `lambda != 0`:

```text
xy = 1 + lambda
zw = 1 + lambda^-1
```

The symmetric fixed point is

```text
lambda = 1
xy = zw = 2.
```

The generic witness

```text
lambda = 2
xy = 3
zw = 3/2
```

also closes exactly.

## 4. VM81 local-to-global coherence fold

VM81 contains nine 3x3 nuclei. I011 requires each nucleus to prove local harmonic closure before the existing global coherence idea can admit the projection:

```text
G_i := harmonic_closed(xy_i, zw_i)

G_VM81 := AND_{i=0..8} G_i
```

The executable witness returns

```text
ADMIT_LOCAL_HARMONIC_AND_FOLD
```

only when all nine local predicates close. One incoherent nucleus returns

```text
REJECT_HARMONIC_INCOHERENCE
```

without manufacturing a replacement channel value.

This is projection/witness infrastructure; it does not itself commit VM81 state.

## 5. Golden-unit exact extension

I011 carries the Genesis golden construction in the exact quadratic extension `Q(sqrt(5))`:

```text
phi = (1 + sqrt(5))/2
phi^2 = phi + 1
```

represented as exact Fraction pairs `a + b sqrt(5)`.

No float is instantiated.

## 6. Norm-polynomial covariance

The prior golden-phase scalar projection yields the rational norm polynomial

```text
F(m) = m^4 - 3m^3 - m - 1.
```

In the reciprocal coordinate,

```text
G(rho) = rho^4 + 3rho^3 + rho - 1.
```

I011 verifies exactly that

```text
(1-rho)^4 F((1+rho)/(1-rho)) = 4 G(rho).
```

Thus the `m` and `rho` norm surfaces are one algebraic state in two projective coordinates.

## 7. Terminal typing remains strict

The following objects remain distinct:

```text
E^(I Pi)
E^(-Pi)
u^72
```

I011 does not flatten them.

Where the licensed Euler projection is used elsewhere, `E^(I Pi) -> -1` is a typed projection. The v1-style phase anchor `u^72 = -E^(-Pi)` remains a separate symbolic relation. This iteration introduces no numeric manufacture of `E^(-Pi)` or of a symbolic modular pole.

## 8. Exactness and fail-closed rules

The implementation enforces:

- no float inputs;
- exact `Fraction` arithmetic;
- exact `Q(sqrt(5))` pair arithmetic;
- `m=-1` rejected at the Möbius pole;
- finite four-cycle branches that cross projective poles rejected;
- harmonic zero/singular branches rejected;
- VM81 fold requires exactly nine nucleus pairs;
- all receipts carry `floating_point_authority: false`;
- all composed witnesses remain `projection_only`;
- `canonical_admission_authority: false`.

## 9. Dependency-scoped validation

CI command:

```text
PYTHONPATH=. pytest -q tests/pass220/test_hhs_pass220_mobius_quarter_phase_v1.py
```

The test module covers:

1. exact Möbius inverse;
2. half-cycle `-1/m` inversion;
3. projective matrix order four;
4. explicit `0/18/36/54/72` phase indexing;
5. harmonic involution;
6. symmetric and generic harmonic closure;
7. translated reciprocal parameterization;
8. exact golden identity;
9. norm-polynomial covariance;
10. nine-nucleus VM81 harmonic AND-fold;
11. one-nucleus incoherence rejection;
12. singular/float fail-closed paths and composed receipt typing.

External CI status is intentionally not claimed until the workflow reports it.
