# HHS Pass 220 I020 — RNA operation64 / C4 / G41 Radical Proof v1

## Scope

I020 proves the three constructive correspondences left explicit after I019:

1. the ordered three-symbol Digital-DNA/RNA word over `{x,y,z,w}` is exactly a 64-state carrier and is bijective with the inherited `operation64 = 8*left_basis8 + right_basis8` address;
2. the I011 quarter-phase carrier proves `x_D^3=y_D` on the typed dyadic C4 projection;
3. the exact Genesis radical differential carries the prime factor `41`, and the 41 canonical I014 reciprocal classes map constructively and bijectively to `Z_41`.

No new VM81, Hash72, Hash216, persistence, receipt, or floating-point authority is introduced.

## 1. 4^3 RNA triplets and the inherited 8^2 operation64

Assign the ordered phase symbols the exact base-4 codes

```text
x -> 0
y -> 1
z -> 2
w -> 3
```

For an ordered RNA/Digital-DNA triplet `(d0,d1,d2)`, define

```text
n = 16*d0 + 4*d1 + d2
```

so `0 <= n < 64`.

Three base-4 symbols are exactly six bits. Split those six bits as `3|3`:

```text
left_basis8  = floor(n/8)
right_basis8 = n mod 8
operation64  = 8*left_basis8 + right_basis8 = n
```

The inverse is

```text
d0 = floor(n/16)
d1 = floor((n mod 16)/4)
d2 = n mod 4
```

and therefore every one of the `4^3=64` ordered triplets maps to exactly one
of the `8^2=64` inherited operation slots and round-trips exactly.

This is an ordered identity/address theorem. It does not assert global
commutativity or replace the inherited eight-basis phase algebra.

## 2. Dyadic C4 cubic conjugate identity

I011 already fixes

```text
phase modulus = 72
quarter phase = 18
phase positions = 0,18,36,54,72
```

I020 defines the typed dyadic projection

```text
x_D := u^18
y_D := x_D^-1 := u^54
1_D := u^72 == u^0
```

Then exact phase-index arithmetic gives

```text
x_D^3 = (u^18)^3 = u^54 = y_D
x_D^4 = (u^18)^4 = u^72 = 1_D
x_D*y_D = u^(18+54) = u^72 = 1_D
```

This proof uses the C4 projection law. It does not rewrite or replace the
separate I015 braid surface.

## 3. Exact Genesis radical

Under the canonical Genesis projection

```text
a^2=1
b^2=2
c^2=3
P^2=3
P^4=9
q-p=2
```

the parametric macro term is

```text
(b^4)^(P^4/c^2) * (a^2+b^2)^(b^2(q-p))
= 4^3 * 3^4
= 5184.
```

The reciprocal term is

```text
(c^2+a^2)^(c^4/P^2) / (a^2+b^2)^(b^2+c^2-a^2)
= 4^3 / 3^4
= 64/81.
```

Hence

```text
5184 - 64/81 = 419840/81
```

and the exact normalized radical is

```text
sqrt(419840/81) = 32*sqrt(410)/9.
```

The equality is checked without an irrational floating approximation by
squaring the normalized radical:

```text
(32^2 * 410)/(9^2) = 419840/81.
```

The square-free radicand factors as

```text
410 = 2 * 5 * 41 = 10 * 41.
```

## 4. Constructive G41 quotient bridge

I014 already enumerates exactly 41 canonical reciprocal fingerprint classes,
with class identifiers `1..41`.

I020 supplies the explicit finite-coordinate map

```text
g(class_id) = class_id mod 41
```

so

```text
classes 1..40 -> residues 1..40
class 41      -> residue 0
```

and the inverse is

```text
residue 0 -> class 41
residue r -> class r, 1<=r<=40.
```

The executable proof verifies all 41 class keys are distinct and that the
resulting residues exhaust `Z_41` exactly once.

Thus the radical's prime-41 coordinate is now linked constructively to the I014
41-class quotient cardinality rather than only numerically observed.

## 5. Independent exact audit

Before repository implementation, Wolfram verified:

```text
64 ordered RNA triplets
codes exactly 0..63
all 64 8x8 basis pairs reached
all 64 triplets round-trip
operation64 = 8*left + right for all 64

x_D = 18
y_D = 54
3*x_D mod 72 = 54
4*x_D mod 72 = 0
x_D+y_D mod 72 = 0

macro = 5184
micro = 64/81
differential = 419840/81
sqrt(differential) = 32 sqrt(410)/9
410 = 2*5*41
41 class residues bijectively cover 0..40
10*41 = 410
```

The independent audit is now sealed in-repository:

- `evidence/pass220/i020_wolfram_audit_v1.wl`
- `evidence/pass220/i020_wolfram_audit_v1.output.json`
- `evidence/pass220/i020_wolfram_audit_v1.receipt.json`

The I020 exact-head workflow verifies both evidence SHA-256 values and all
18 audit checks before running the executable proof regressions.

## 6. Authority

I020 is a read-only proof layer:

```text
canonical VM81 mutation authority = false
canonical Hash72 authority = false
canonical Hash216 authority = false
canonical persistence authority = false
floating-point authority = false
```
