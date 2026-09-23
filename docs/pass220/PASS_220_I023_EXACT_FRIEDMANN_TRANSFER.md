# Pass 220 I023 — T_COSMO-05 Exact Friedmann Transfer

Date: 2026-09-21

## 1. Scope

I023 advances the HHS cosmological transfer from exact committed cadence receipts
into a deterministic symbolic trajectory for:

- physical egress time;
- total Hubble rate;
- logarithmic scale factor;
- redshift;
- Hubble distance;
- comoving distance;
- transverse comoving distance;
- angular-diameter distance;
- luminosity distance.

The projection remains one-way. It does not grant VM81 mutation authority,
Delta admission authority, Hash72 mint authority, Hash216 persistence authority,
floating-point authority, host-wall-clock authority, or inverse H(z)->state
authority.

## 2. Input boundary

Each transfer receipt carries:

~~~text
transition_index
sigma_n
lambda_n = L(Pi_cosmo(Gamma_n))
theta_n
background_h2_n
source_receipt_sha256
~~~

The exact phase route is inherited from I022:

~~~text
sigma_n = (8,24,40,56,72,16,32,48,64)[n mod 9]
~~~

The background H^2 contribution is not a fitted H(z) function. At this theorem
boundary it is an exact committed input associated with the same transition.
A later density-law closure must prove how baryon/radiation/dark-sector
payload receipts generate this term from measured anchors without free
functions.

## 3. Why the trapezoidal proposal is not canonical

The proposed update

~~~text
a[n+1] = a[n] exp(((H[n] + H[n+1])/2) tau theta[n])
~~~

is not generally exact, and it becomes implicit when H[n+1] depends on
a[n+1] through the Friedmann background terms.

I023 therefore defines a canonical zero-order hold on each committed interval:

~~~text
H(t) = H[n],  t in [t[n], t[n+1])
~~~

This is not a fitted interpolation. It is a fixed transfer convention.

The exact interval integral is then:

~~~text
Delta log(a)[n] = H[n] Delta t[n]
Delta t[n]      = tau theta[n]
~~~

and therefore

~~~text
a[n+1] / a[n] = ExpSym(H[n] tau theta[n])
~~~

where ExpSym remains symbolic and is never evaluated in the canonical runtime.

## 4. Exact Friedmann carrier

The phase sector is:

~~~text
H_P[n] = lambda[n] / (tau theta[n])
~~~

The total exact squared Hubble carrier is:

~~~text
H[n]^2 = background_h2[n] + H_P[n]^2
~~~

The positive expanding branch is represented as an exact symbolic square root:

~~~text
H[n] = SqrtSym(H[n]^2)
~~~

If the rational radicand is a perfect square, the runtime reduces it exactly.
Otherwise it remains a typed symbolic root.

No float, decimal approximation, math.sqrt, or numerical exponential enters
the canonical projection.

## 5. Phase-only tau cancellation extends to the scale trajectory

For background_h2[n] = 0 and lambda[n] > 0:

~~~text
H[n] = lambda[n] / (tau theta[n])
~~~

so:

~~~text
Delta log(a)[n]
= H[n] tau theta[n]
= lambda[n]
~~~

Thus:

~~~text
a[n+1]/a[n] = ExpSym(lambda[n])
~~~

and the phase-only expansion-shape increment is independent of tau.

Tau still changes the physical egress time coordinate:

~~~text
Delta t[n] = tau theta[n]
~~~

but it does not alter the intrinsic phase-only scale trajectory.

## 6. Present normalization and redshift

The runtime first accumulates an exact raw logarithmic scale coordinate:

~~~text
L[0] = 0
L[n+1] = L[n] + H[n] tau theta[n]
~~~

After the finite trajectory is known, the present endpoint is normalized to
a_present = 1:

~~~text
ell[n] = L[n] - L[N]
~~~

Then:

~~~text
1 + z[n] = ExpSym(-ell[n])
~~~

No integer redshift quantization is imposed.

## 7. Exact comoving-distance increment

Under the committed-interval zero-order hold,

~~~text
a(t) = a[n] ExpSym(H[n] (t-t[n]))
~~~

so the interval comoving distance is analytically exact:

~~~text
Delta D_C[n]
=
c0 ExpSym(-ell[n])
(1 - ExpSym(-H[n] Delta t[n])) / H[n]
~~~

For H[n] -> 0 the exact limit is:

~~~text
Delta D_C[n] -> c0 ExpSym(-ell[n]) Delta t[n]
~~~

The Wolfram formalization verifies this limit.

Distances to the present endpoint are accumulated from committed intervals:

~~~text
D_C(z[n]) = Sum[k=n..N-1] Delta D_C[k]
~~~

and:

~~~text
D_H[n] = c0 / H[n]
D_M[n] = S_k(D_C[n])
D_A[n] = D_M[n] / (1+z[n])
D_L[n] = (1+z[n]) D_M[n]
~~~

For flat curvature, S_0 is the identity. Non-flat curvature remains an exact
symbolic S_k carrier pending the curvature-radius specialization.

## 8. Wolfram formalization

Connected Wolfram Language returned:

~~~text
schema = HHS_PASS_220_I023_COSMO_FRIEDMANN_TRANSFER_WOLFRAM_20260921_V1
status = PASS
checks = 9/9
failed = []
phase-only Delta log(a) = lambda
phase-only a ratio = E^lambda
phase-only redshift-log step = -lambda
~~~

It additionally verifies the exact zero-Hubble comoving-distance limit and
retains G72 as:

~~~text
Inactive[Power][2, 1/72]
~~~

Evidence:

~~~text
evidence/pass220/i023_exact_friedmann_transfer_wolfram_20260921_v1.wl
evidence/pass220/i023_exact_friedmann_transfer_wolfram_20260921_v1.output.json
~~~

## 9. Executable implementation

Runtime:

~~~text
hhs_runtime/hhs_pass220_exact_friedmann_transfer_v1.py
~~~

Regression:

~~~text
tests/pass220/test_hhs_pass220_exact_friedmann_transfer_v1.py
~~~

The implementation uses:

- int;
- fractions.Fraction;
- immutable exact symbolic expression nodes;
- exact integer square-root recognition for rational perfect squares;
- deterministic JSON serialization and SHA-256 receipts.

No arbitrary numerical solver is present.

## 10. T_COSMO-05 proof obligations

This cycle closes the exact transfer kernel subject to committed exact
background H^2 inputs.

The acceptance conditions are:

1. tau enters only through egress time and H_P units;
2. Gamma/lambda and theta remain upstream committed values;
3. no host wall-clock input exists;
4. no floating-point arithmetic exists;
5. square roots and exponentials remain symbolic unless exactly reducible;
6. the phase-only scale increment is tau-independent;
7. present redshift normalization is deterministic;
8. comoving distance uses the analytic zero-order-hold interval integral;
9. source transition receipts are SHA-bound;
10. replay yields bit-identical trajectory receipts;
11. H(z) cannot be fed back into canonical state evolution;
12. negative total H^2 fails closed.

## 11. Remaining cosmological closure

I023 does not yet claim empirical agreement with LambdaCDM, DESI, supernova,
or CMB data.

The next boundary must remove the remaining background-input freedom:

~~~text
T_COSMO-06:
measured density anchors
+ VM81/Hash payload laws
+ exact conservation/continuity rules
-> unique background_h2[n]
~~~

Only after that closure can a fully generated H(z) trajectory be compared
against observational datasets without hidden fitted functions.
