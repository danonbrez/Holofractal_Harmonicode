# Pass 219 Lane 5 1.50 — Rational P-Manifold and Ordered-Phase Gate

**Status:** EXECUTED_EXACT_CANDIDATE_SWEEP  
**Semantics:** exact scalar projection + independent ordered-phase witness  
**Parent lane:** Pass 219 Lane 5 1.49  
**Canonical mutation authority:** unchanged

## 1. Source-preservation rule

The complete HARMONICODE source remains an indivisible typed constraint surface. This contract does not grant a scalar proof permission to rewrite native source, commute ordered products, or substitute equal projected values back into the native graph.

The present theorem decomposes only named proof obligations. The decomposition is proof instrumentation, not a replacement for the governing source.

## 2. Inherited exact premises

The repository already proves the nonzero rational unit-residue branch:

```text
Delta = t^3-t = m^2-m = xy = P^2-pq = q-P = P-p
Delta != 0
Delta^2 = Delta
=> Delta = 1
```

Therefore:

```text
p = P-1
q = P+1
p+q = 2P
q-p = 2
pq = P^2-1
```

The current user-supplied bridge

```text
P^2 = pq + ((q-p)P/(p+q))
```

then closes on this inherited branch because:

```text
((q-p)P)/(p+q)
= (2P)/(2P)
= 1
```

for `P != 0`. Hence:

```text
P^2 = pq + 1.
```

This is the exact bridge used by the 1.50 proof.

## 3. Lemma set

### L1 — Unit-residue symmetric pair

On the inherited rational residue gate:

```text
Delta=1
=> (p,q)=(P-1,P+1).
```

### L2 — Macro single-parameter projection

On L1:

```text
p=P-1
q=P+1
p+q=2P
q-p=2
pq=P^2-1.
```

Thus `p` and `q` are exact functions of `P` on this admitted projection.

### L3 — Rationality equivalence on the gate

If `P in Q`, then `p=P-1` and `q=P+1` are rational.

Conversely, on the same gate:

```text
P=(p+q)/2,
```

so rational `p,q` imply rational `P`.

This is the proved rationality gate. It is scoped to the inherited symmetric-pair projection.

### L4 — Independent ordered-phase gate

The inherited Lane 5 exact witness is:

```text
x = {{0,1},{1,0}}
y = {{0,-1},{1,0}}
z = x
w = y

x^2 = +I
y^2 = -I
xy = -yx
xy+yx = 0
zw = xy
wz = yx
```

This is an exact noncommutative `q=-1` ordered-phase witness. It is not derived from rationality alone.

The operation64 support is exactly:

```text
{4,5,6,7,16,17,18,19,44,45,46,47,56,57,58,59}
```

giving:

```text
16 phase-bearing positions per VM81 cell
48 non-phase positions per VM81 cell
1296 phase-bearing positions across 81 cells
3888 non-phase positions across 81 cells.
```

### L5 — Coupled compatibility

For the 72 exact nonzero integer values:

```text
P in {-36,...,-1,1,...,36}
```

the audit evaluates every one of the 5,184 Lane 5 state positions.

Total exact candidate checks:

```text
72 * 5184 = 373248.
```

Result:

```text
373248 / 373248 PASS
phase-bearing checks = 93312
non-phase checks     = 279936.
```

Therefore the exact rational P-manifold projection and the independent ordered-phase gate are compatible over the executed candidate sweep.

### L6 — Bridge-alone non-authority guard

Let:

```text
s=p+q
d=q-p.
```

Ordinary exact projection of the isolated bridge gives:

```text
d^2 + 4P^2 = 4dP/s + s^2

d = (2P +/- sqrt(s^4 - 4P^2(s^2-1)))/s.
```

The bridge therefore does not, by itself, determine a unique `(p,q)` pair from `P`.

The Wolfram guard sweeps 5,184 exact rational `(P,s)` grid cells and finds 752 verified bridge states; every one of the 72 tested `P` values has multiple `(p,q)` solutions on the bridge-only projection.

The single-parameter result depends on the inherited unit-residue/symmetric-pair gate, not on the bridge in isolation.

### L7 — Rationality does not cause the phase gate

A visible-subconstraint counterexample is sealed in the audit:

```text
P=1/2
p=-1/2
q=3/2
u^72=1
Delta=1/4
x=1
y=-1.
```

It satisfies the isolated bridge, the displayed `Delta/P` gate, and `xy=-1`, while `x^2=+1`.

Therefore those rationality subconstraints alone do not force an imaginary/quaternionic/fermionic phase representation. The ordered-phase witness remains an independent exact HHS gate.

This negative guard does not claim that the counterexample is a full HHS-admitted state.

### L8 — Full-manifold obligation

The executed result proves:

```text
macro P-manifold projection
+
independent ordered-phase gate
+
373248 exact compatibility checks.
```

It does not yet prove that every symbol in the full governing source — including `t,m,u,Delta,A,B,At,Bt,f,s` and every nested cell — is uniquely determined by `P`.

That stronger statement remains:

```text
OPEN_FULL_MANIFOLD_OBLIGATION.
```

It may be promoted only after the complete typed source evaluator proves unique closure without whole-subtree substitutions.

## 4. Metric anchors

The repository projection used by this theorem remains:

```text
a^2=1
b^2=2
c^2=3.
```

No `c^2=1` branch is introduced by this contract.

## 5. Wolfram evidence

```text
evidence/pass219/hhs_rational_p_manifold_lane5_v1.wl
evidence/pass219/hhs_rational_p_manifold_lane5_v1.output.json
evidence/pass219/hhs_rational_p_manifold_lane5_v1.receipt.json
```

Sealed execution:

```text
macro P values                       = 72
combined Lane 5 state-slot checks   = 373248
combined passes                     = 373248
bridge-only rational grid cells     = 5184
bridge-only verified states         = 752
```

The receipt cryptographically binds the exact Wolfram source and output bytes.

## 6. Native hydration-cycle evidence

The native gate:

```text
tests/pass219/test_pass219_rational_p_manifold_lane5_1_50.c
```

repeats the 72 P-state macro proof while calling the inherited exact 1.49 classifier for all 5,184 positions per state. It asserts exact phase code, sign, representative, support ordinal, address identity, candidate-only status, and full-state-identity requirement.

The C gate therefore executes the same 373,248 state-slot compatibility cycle against the runtime ABI rather than only reproducing the Wolfram mathematics.

## 7. Classical quadratic-reciprocity comparison boundary

The chalkboard theorem supplied with this pass is the classical odd-prime law:

```text
(p/q)(q/p) = (-1)^(((p-1)/2)((q-1)/2)).
```

Its lattice proof counts integer points on opposite sides of `qx=py` and converts the count to a parity sign.

That theorem is useful as a reference for discrete parity geometry. It is not used as an authority substitution for the HHS theorem above. The 1.50 result is a different proof object: an exact internal projection theorem plus an ordered noncommutative phase witness and an executable VM81 compatibility sweep.

## 8. Authority boundary

This pass does not create:

```text
canonical VM81 mutation authority
canonical Hash72 mint authority
canonical Hash216 persistence authority
floating-point canonical authority
scalar-to-native substitution authority.
```

The Lane 5 result remains candidate-only and requires exact CPU/VM81 replay.
