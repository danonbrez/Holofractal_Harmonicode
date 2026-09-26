# Pass 219 — Polarity s Half-Turn 1.65

Status: **NORMATIVE / ORDERED / TYPED / SOURCE-PRESERVING / LANE-5 PREFLIGHT / SIGNED-VM81 PREFLIGHT**

## 1. Polarity definitions

The native ordered polarity surface is:

```text
xy=s/zw
yx=-s/zw
zw=s/xy
wz=-s/xy
```

These are four typed ordered relations. They do not grant reciprocal cancellation or commutation.

For `s=+1`, the ordered sign vector is:

```text
(xy,yx,zw,wz)=(+,-,+,-)
```

For `s=-1`:

```text
(xy,yx,zw,wz)=(-,+,-,+)
```

Thus each chiral pair remains opposed while the global polarity orientation flips.

## 2. Existing phase operator

The inherited RML5 chiral-pair operator is:

```text
u^36
phase modulus = 72
phase steps = 36
self inverse = true
```

The 1.65 contract identifies `s=-1` with this existing typed half-turn.

No new phase operator is introduced.

## 3. p-q:q-p phase rotation

On the inherited scalar unit shell:

```text
p=P-1
q=P+1
p-q=-2
q-p=+2
```

The ordered pair is:

```text
(p-q):(q-p)=(-2):(+2)
```

At `s=-1`, the half-turn rotates it to:

```text
(+2):(-2)
```

Applying the same `u^36` half-turn again restores:

```text
(-2):(+2).
```

This is a typed phase rotation of the ordered pair, not an equality asserting `p-q=q-p`.

## 4. Reciprocal correction parent

The 1.65 layer requires the 1.64 ordered correction:

```text
((p/q)*(q/p))/(P²-pq)=((q-p)*P)/(p+q)
```

and preserves the raw user source independently.

The existing scalar projection proves both correction sides equal `1` on the nonzero unit-residue branch, but that proof does not authorize native cancellation.

## 5. Negative-s surface

The exact supplied surface is preserved as:

```text
-s=x²(((p÷q)−(q÷p))+((q÷p)−(p÷q))×(q−p)−(p−q))
```

Under the separately registered commutative scalar projection:

```text
p=P-1
q=P+1
```

the inner polarity factor projects exactly to:

```text
2 + 4P/(P²-1)
```

equivalently:

```text
(-2+2P(2+P))/(-1+P²).
```

For `s=-1`, the scalar witness therefore gives:

```text
x²=(P²-1)/(2(P²+2P-1))
```

on the corresponding nonzero denominator domain.

This is scalar-proof evidence only. It does not replace the native source manifold.

## 6. Inherited inner manifold

The supplied `x²*y==...==1/x` nested manifold is inherited from the frozen 1.64 source identity.

The 1.65 verifier SHALL first require the full 1.64 verifier to pass before applying polarity semantics.

## 7. Runtime rule

The exact C surface:

```text
hhs_exact_pass219_polarity_s_verify(s, receipt)
```

admits only:

```text
s=+1
s=-1
```

For `s=-1`, the receipt SHALL prove:

```text
phase_steps=36
xy_sign=-1
yx_sign=+1
zw_sign=-1
wz_sign=+1
p_minus_q_orientation=+1
q_minus_p_orientation=-1
half_turn_self_inverse=true
```

## 8. Authority boundary

The 1.65 layer grants no:

```text
commutation authority
reciprocal cancellation authority
equality reversal authority
floating-point canonical authority
VM81 canonical mutation authority
Hash72 authority
Hash216 authority
```

The signed environmental VM81 path remains the only canonical mutation seam.


## 9. Successor conservation layer

Pass 219 Lane 5 successor 1.66 composes this polarity half-turn with the Pell negative-defect witness, the positive unit shell, the 72-phase seed, and the master conservation conditional.

Normative successor:

```text
contracts/pass219/PASS_219_GLOBAL_CONSERVATION_POLARITY_1_66.md
```

The successor explicitly forbids cross-gate substitution and keeps ordinary quotient, quadratic-reciprocity symbol, and polarity `s` as distinct typed operators unless a specific gate binds them.
