# HHS Pass 220 I018 — H36 / HASH72 Unit Bridge v1

## Exact source relation

```text
(e/H36=(mc^2)/u^144)
=(a^2/P^4)*(c^2(a^2+b^2))
=(xy+zw)/(q-p)
```

This surface is composed with the inherited Pass 219 H36 identity, canonical
native universal constraint, and the Pass 220 I017 multidimensional manifold.

## Exact Genesis projection

Using the already-admitted projection

```text
a^2=1
b^2=2
c^2=3
P^4=9
P^2-pq=1
xy=1
zw=1
q-p=2
H36=36
u^144_exponent = 72*(b^2/a^4) = 144
u^144_projection = (b^6*c^4)/(c^2-a^2) = 36
HASH72_projection = b^4*P^4 = 36
(mc^2)_projection = (a^2+b^2)^2*b^4 = 36
```

all four ratios close exactly:

```text
e/H36 = 1
(mc^2)/u^144 = 1
(a^2/P^4)*(c^2(a^2+b^2)) = 1
(xy+zw)/(q-p) = 1
```

The repair-forward bridge now computes the three value paths independently:

```text
u^144: 72*(b^2/a^4)=144, then (b^6*c^4)/(c^2-a^2)=36
HASH72: b^4*P^4=36
mc^2:   (a^2+b^2)^2*b^4=36
```

Only after those independent evaluations does the bridge compare them. The
`mc^2/u^144` ratio therefore no longer reuses one projected value as both
numerator and denominator. Typed `e` is not rebound to any unrelated basis
symbol, and the native `m` appearing elsewhere in the universal constraint is
not solved.

## P^4 boundary

The bridge explicitly preserves

```text
P^4 = 9 != 1
```

while

```text
P^2-pq = 1.
```

The two are not flattened into the same scalar role.

## Universal-constraint dependency

I018 binds to the repository-authoritative
`CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE` and recomputes its SHA-256.
The recomputed digest, the Python canonical digest, and the separately pinned
native UQCEL digest must all equal

```text
7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42
```

in addition to requiring the source fragments `P^2-pq`, `m^2-m`,
`u^72`, `pq+xy`, `AB/P^2`, `Sqrt[AB]`, and `Delta/P`.

## Complete ordered phase

The bridge now calls the inherited I017 ordered-curvature witness and requires

```text
(sx,sz,xy,yx,zw,wz) = (0,0,+1,-1,+1,-1)
```

before evaluating `(xy+zw)/(q-p)`. A scalar-equivalent altered `yx` or
`wz` witness is rejected.

## Reproducible Wolfram audit evidence

The repair-forward exact audit is repository-visible at:

- `evidence/pass220/i018_repair_wolfram_audit_v1.wl`
- `evidence/pass220/i018_repair_wolfram_audit_v1.output.json`
- `evidence/pass220/i018_repair_wolfram_audit_v1.receipt.json`

The exact-head workflow verifies the sealed input/output SHA-256 values and all
15 recorded audit checks before running the Python regressions.

## Authority

The numeric value 36 in this bridge is the exact algebraic HASH72 projection
already established by I017 and the exact H36 value already established by
Pass 219. It is not the canonical 72-character Hash72 digest and grants no
Hash72 mint, Hash216 persistence, or VM81 mutation authority.
