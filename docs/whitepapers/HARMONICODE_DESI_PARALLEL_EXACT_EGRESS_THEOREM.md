# HARMONICODE DESI Parallel Exact-Egress Theorem

## 1. Observation source

Let a published DESI numeral be a finite decimal string d.

I038 interprets d exactly as a rational:

~~~text
R(d) in Q.
~~~

The source string and exact rational remain retained.

## 2. Exact IEEE projection

Define:

~~~text
I64(d)
~~~

as the nearest-even IEEE binary64 storage state obtained from R(d) using integer arithmetic only.

The raw 64-bit storage state is then interpreted by the inherited exact IEEE carrier as a dyadic rational:

~~~text
D(I64(d)).
~~~

No host floating-point operation is required for either construction.

## 3. Residue conservation

Define the exact transport residue:

~~~text
epsilon_IEEE(d) = R(d) - D(I64(d)).
~~~

The system stores all three objects:

~~~text
R(d)
I64(d)
epsilon_IEEE(d)
~~~

simultaneously.

Therefore the IEEE transport path cannot silently erase decimal-to-binary representation drift.

## 4. Palindromic phase transport

The raw IEEE state enters the existing G3 reciprocal carrier.

The scalar storage bits remain invariant while the internal ordered phase geometry follows its reciprocal path.

The same operation recovers the original raw storage state.

Hence the IEEE lane is a reversible transport/calculator projection rather than the observational source of truth.

## 5. BigInt geometry

The same observation carrier is associated with the inherited fixed-width 81-cell state:

~~~text
81 * 64 = 5184 characters.
~~~

The 5,184-character serialization remains a distinct co-resident geometry/address view.

## 6. 24D constraint bundle

Each observation binds the root of the I037 mandatory equation/proof constructor bundle.

Thus numerical egress does not discard the native equation geometry.

## 7. Lane 5 composition

The combined object is:

~~~text
(
 exact observational rational,
 exact IEEE bit state,
 exact IEEE dyadic,
 exact IEEE residue,
 palindromic symbolic phase state,
 fixed 5184-character BigInt state,
 I037 24D equation/proof root,
 source provenance
)
~~~

and enters Lane 5 only as a validated constructor input.

## 8. Probability boundary

Measurement uncertainty metadata can be retained exactly without being used as a probability engine.

I038 therefore has:

~~~text
probability_used_in_equation_solve = false
likelihood_used_in_equation_solve  = false
mcmc_used_in_equation_solve        = false
parameter_refit_performed          = false
~~~

This does not assert that observational uncertainty does not exist. It states that uncertainty is not used as the arithmetic solver for the HHS equations.

## 9. Explicit observation map

A DESI observable may constrain an HHS variable only through an explicitly declared later map.

No implicit mapping is permitted at this boundary.
