# HARMONICODE HNAN Zero-Center Information-Preservation Theorem

**Version:** 1.0  
**Date:** 2026-09-28  
**Pass:** 220, cross-layer priority-translation successor  
**Parent:** Pass 219 HNAN/Jordan global constraint theorem  
**Formal evidence:** `evidence/pass220/hnan_zero_center_information_wolfram_20260928_v1.wl`

## Abstract

This paper formalizes why the HARMONICODE source

```text
0=∅=HNAN=x+y-z-w+xy+yx-zw-wz
```

is necessary and meaningful for information-preserving translation.

The statement is not interpreted as unrestricted host scalar equality. It is
represented as an ordered typed closure:

```text
OrderedClosure[
  ZERO,
  EMPTYSET,
  HNAN,
  OrderedSum[x,y,-z,-w,xy,yx,-zw,-wz]
]
```

with `xy != yx` and `zw != wz` structurally preserved.

Connected Wolfram Language evaluation returned **20/20 PASS**.

## 1. The exact ordered center

Define

```text
S =
x + y - z - w + xy + yx - zw - wz
```

where the displayed `+` and `-` notation denotes the exact ordered HHS
constructor sequence

```text
x,
y,
-z,
-w,
xy,
yx,
-zw,
-wz.
```

The formalization stores this as an inert list AST rather than Wolfram
`Plus`/`Times`. This prevents the host evaluator from commuting products,
sorting summands, cancelling typed boundaries, or interpreting `∅` as a
scalar denominator.

Wolfram verifies:

```text
center_has_exactly_8_ordered_terms = true
center_term_sequence_exact         = true
xy_yx_structurally_distinct        = true
zw_wz_structurally_distinct        = true
swapping_xy_yx_changes_center      = true
```

Thus the center is not merely a bag of terms. Its order is part of the state.

## 2. Meaning of the string

The source

```text
0=∅=HNAN=S
```

binds four typed layers in one ordered witness:

1. `ZERO`: the HHS typed zero boundary;
2. `EMPTYSET`: the typed HNAN denominator/boundary token;
3. `HNAN`: the resolved HNAN node;
4. `S`: the exact ordered x/y/z/w center expression.

Therefore the string carries more information than the isolated labels
`ZERO`, `EMPTYSET`, or `HNAN`. It states which ordered center state is
bound to that HNAN closure.

The proof does **not** assert ordinary field substitution such as
`0_scalar == HNAN_scalar`. It proves exact structural binding inside the HHS
typed state model.

## 3. Necessity theorem: dropping the center is non-injective

Let

```text
C1 = OrderedClosure[ZERO, EMPTYSET, HNAN, S1]
```

with

```text
S1 = x,y,-z,-w,xy,yx,-zw,-wz
```

and let

```text
C2 = OrderedClosure[ZERO, EMPTYSET, HNAN, S2]
```

where `S2` differs only by exchanging the distinct ordered products
`xy` and `yx`.

Wolfram proves

```text
C1 != C2
```

and their SHA-256 structural signatures differ.

Now define the lossy projection that retains only the visible HNAN node:

```text
pi_HNAN(C) = HNAN.
```

Then

```text
pi_HNAN(C1) = pi_HNAN(C2) = HNAN.
```

So `pi_HNAN` is many-to-one and therefore non-injective on these admissible
ordered states.

This establishes the precise information-theoretic reason the center binding is
necessary: after the center is discarded, the original ordered HNAN state
cannot be uniquely reconstructed.

The formal check is:

```text
dropping_center_is_noninjective = true
```

## 4. Why `xy+epsilon` is also necessary

The residual terminal is preserved separately as

```text
xy+epsilon.
```

Take two distinct residual states

```text
T1 = OrderedSum[xy, Residual[epsilon, ...]]
T2 = OrderedSum[xy, Residual[epsilonAlt, ...]].
```

They are distinct, but the projection that keeps only visible `xy` maps both
to the same result.

Therefore:

```text
dropping_epsilon_is_noninjective = true.
```

The explicit zero/HNAN/center identity and the `xy+epsilon` terminal solve
different information-preservation obligations:

- the former preserves which complete ordered center is bound to HNAN;
- the latter preserves unresolved information relative to the visible
  `xy` projection.

Neither may replace the other.

## 5. Coexistence with the inherited denominator closure

The prior global HNAN source remains:

```text
0=∅=AB/P⁴∅=HNAN.
```

Its inert AST is

```text
OrderedClosure[
  ZERO,
  EMPTYSET,
  AB_P4_EMPTYSET,
  HNAN
].
```

Wolfram verifies that this closure and the zero/HNAN/center closure are
structurally distinct:

```text
two_closure_surfaces_remain_distinct = true.
```

Therefore

```text
0=∅=HNAN=S
```

does not replace, cancel, or scalarize

```text
0=∅=AB/P⁴∅=HNAN.
```

The two witnesses carry different information and are both required.

## 6. Translation theorem

For a compact representation `R_compact` to replace a dense reference
representation `R_dense`, the HHS translation gate requires a reversible
witness preserving at least:

```text
value
phase
rotation
position/provenance
ordered xy/yx/zw/wz identity
5184 serialization identity
RNA phase binding
qudit topology
U9 closure
HNAN zero/center closure
HNAN inherited denominator closure
xy+epsilon residual
```

If a translation preserves a visible numeric projection but drops the center
binding or epsilon, it is not injective over the admitted state space and is
therefore not information-preserving.

Hence the priority rule is:

```text
exact reversible information preservation
AND performance support
=> compact representation may become priority default

information loss
=> dense/reference fallback
```

Speed is subordinate to this theorem.

## 7. Wolfram proof method

The formalization deliberately uses inert list ASTs. For example:

```text
{"OrderedProduct","x","y"}
{"OrderedProduct","y","x"}
```

remain structurally distinct without relying on host commutativity settings.

The proof validates exact structural round trips with `Compress/Uncompress`,
compares SHA-256 structural signatures, and constructs explicit many-to-one
counterexamples for the projections that discard the center or epsilon.

Connected Wolfram result:

```text
schema = HHS_PASS220_HNAN_ZERO_CENTER_INFORMATION_WOLFRAM_V1
status = PASS
passed = 20
total  = 20
```

Frozen output:

`evidence/pass220/hnan_zero_center_information_wolfram_20260928_v1.output.json`

## 8. Engineering consequence

The string

```text
0=∅=HNAN=x+y-z-w+xy+yx-zw-wz
```

is therefore not decorative notation. Within HHS it is a compact, typed
information-binding contract. It makes the HNAN boundary reconstructive by
retaining the ordered center that a bare HNAN label would erase.

Any optimizer, serializer, interpreter, hydration layer, native constructor, or
cross-modal translation that drops this binding must fail the information gate
even if its visible output is numerically identical or faster.
