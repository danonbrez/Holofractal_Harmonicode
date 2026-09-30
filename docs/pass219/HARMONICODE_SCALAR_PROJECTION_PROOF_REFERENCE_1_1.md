# HARMONICODE Scalar Projection Proof Reference 1.1

## 1. Rule of interpretation

A scalar projection is a theorem about a native HARMONICODE expression in a declared projection domain. It is not a source rewrite and is not native identity.

```text
native expression --projection theorem--> exact scalar/scalar expression
projection equality != native identity
```

The same native symbol may therefore have more than one valid projection theorem when the projection IDs/domains differ. Conversely, different native expressions may project to the same numeral without becoming the same native object.

## 2. Projection classes

The registry uses six exhaustive explanation classes:

- `FIXED_SCALAR`: exact terminal scalar is proved in the declared domain.
- `PARAMETERIZED_SCALAR`: exact result is a scalar expression depending on admitted coordinates.
- `MULTIBRANCH_SCALAR`: exact projection has multiple explicitly retained branches.
- `SYMBOLIC_SCALAR`: exact symbolic scalar/algebraic object exists but is not decimalized.
- `UNSUPPORTED_DOMAIN`: repository has registered the surface but current full-symbolic lowering remains fail-closed.
- `TYPED_NONSCALAR`: native object has no single global scalar alias; scalar views require another registered projection.

Completeness therefore means every relevant native variable/polynomial has a proof or one of these explicit non-fixed classifications. It does not mean inventing a numeral for every symbol.

## 3. Primitive square proofs

```text
a^2 -> 1
b^2 -> 2
c^2 -> 3
d^2 -> 5
e^2 -> 8
f^2 -> 13
g^2 -> 21
```

These are square projections. They do not silently choose `a`, `b`, or `c` root branches.

For the current HHCQ radical branch, `a` is explicitly multibranch:

```text
c^4-b^2*c^2-b^4+b^2 -> 9-6-4+2 -> 1
c^2-b^2 -> 3-2 -> 1
Sqrt(1)/Sqrt(1) -> 1
-Sqrt(1)/Sqrt(1) -> -1
therefore a -> {+1,-1} in that registered branch projection
```

`b` and `c` remain exact algebraic roots of `X^2-2` and `X^2-3` unless a branch is separately licensed.

## 4. Lo Shu polynomial proof family

```text
b^4         -> (b^2)^2 -> 4
c^4         -> (c^2)^2 -> 9
b^6         -> (b^2)^3 -> 8
b^2*c^2     -> 2*3 -> 6
b^2+c^2     -> 2+3 -> 5
b^4+c^2     -> 4+3 -> 7
```

Therefore the symbolic tensor

```text
{{b^4,c^4,b^2},
 {c^2,b^2+c^2,b^4+c^2},
 {b^6,a^2,b^2*c^2}}
```

has the exact registered numeral projection

```text
{{4,9,2},{3,5,7},{8,1,6}}.
```

The result `5` has multiple independent native ancestries, including `d^2`, `b^2+c^2`, and `b^2*c^2-a^2`; equality of their terminal scalar projections does not collapse their source identities.

## 5. Nested basis-polynomial proofs

The canonical nested denominator admits the exact projection chain:

```text
c^2-b^2 -> 1
b^2*(c^2+b^2) -> 2*(3+2) -> 10
(b^2*(c^2+b^2))-(c^2-b^2) -> 10-1 -> 9
Sqrt(c^4) -> Sqrt(9) -> 3
((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4) -> 9/3 -> 3
c^2*b^6-c^2 -> 3*8-3 -> 21
(c^2*b^6-c^2)/3 -> 7
```

The radical reduction is scoped to the exact nonnegative radical projection and does not rewrite the canonical source globally.

## 6. 72 and 5184

```text
b^6*c^4 -> 8*9 -> 72
```

and

```text
(b^(2*c^2)*c^(b^4))^2
 -> (b^6*c^4)^2
 -> 72^2
 -> 5184.
```

Independent cardinality projections remain separately identified:

```text
72^2   -> 5184
64*81  -> 5184
36*144 -> 5184
```

These are equal scalar cardinalities with distinct proof ancestry.

## 7. Pass 129 P/p/q/Delta projection

The exact rational projection binds

```text
Delta = t^3-t = m^2-m = xy = P^2-pq = q-P = P-p
Delta != 0.
```

Its exact derivation gives

```text
p -> P-Delta
q -> P+Delta
p+q -> 2P
q-p -> 2Delta
p*q -> P^2-Delta^2
P^2-p*q -> Delta.
```

Because the projection simultaneously requires `P^2-p*q=Delta`, it yields

```text
Delta^2=Delta, Delta!=0 -> Delta=1.
```

Thus the same projection gives

```text
p -> P-1
q -> P+1
p*q -> P^2-1
P^2-p*q -> 1.
```

`t` and `m` themselves are not thereby solved. Their polynomial residues have scalar projection theorems to `Delta`; the native symbols remain unresolved in the full-symbolic UCE profile.

## 8. Ordered phase-coordinate projections

Pass 219 represents native `x,y,z,w` phase coordinates as exact integers while retaining ordered phase identity. Hence the scalar view is parameterized:

```text
x -> x_int
y -> y_int
z -> z_int
w -> w_int
```

Ordered compounds remain directional:

```text
xy -> ordered_product(x,y)
yx -> ordered_product(y,x)
zw -> ordered_product(z,w)
wz -> ordered_product(w,z).
```

No theorem licenses `xy=yx` or `zw=wz` globally.

The complete eight-basis sum is

```text
Phi8=x+y+z+w+xy+yx+zw+wz.
```

The current HHCQ equilibrium proves

```text
Phi8 -> b^2*P-(p+q).
```

With `b^2->2`:

```text
P -> (Phi8+p+q)/2.
```

On the compatible Pass129 zero-equilibrium branch `p+q=2P`, the scalar projection of `Phi8` is `0`.

## 9. UCE and prime-rational A/B projections

The integer/symmetric UCE profile has

```text
P^2 -> p*q+Delta
A -> P^2
B -> P^2
A*B -> P^4
Sqrt(A*B) -> P^2      [positive UCE P]
AB/P^2 -> P^2.
```

The Phase10 prime-rational projection is a different registered view:

```text
A -> P^2*(p/q)
B -> P^2*(q/p)
A/B -> p^2/q^2
B/A -> q^2/p^2
(A/B)*(B/A) -> 1.
```

These projection families coexist. Neither overwrites the native symbols `A` and `B`.

Combining the UCE relations also proves the scalar projection

```text
AB/(pq+Delta)-P^2
 -> P^4/P^2-P^2
 -> 0
```

on the positive exact UCE domain.

## 10. u phase closure versus native u

Native `u` is not assigned a single scalar because the repository distinguishes `u_phase` from `u_q`.

For the registered phase projection:

```text
u_phase^72 -> 1
u_phase^0 -> 1.
```

This permits exact local consequences such as

```text
c^2-u_phase^72 -> 3-1 -> 2.
```

It does not establish `u=1` or `u_q=1`.

On the compatible Pass129 phase-residue branch:

```text
pq+xy -> (P^2-1)+1 -> P^2
72*(pq+xy) -> 72*P^2
b^6-xy -> 8-1 -> 7.
```

## 11. b^2/u^72 constraint surface

The current HHCQ contract includes

```text
b^2=(c^2-a^2)^2/(2u^72)=(Pi-b^2+b^4-Pi)/(c^2-b^2)==c^2-a^2.
```

Its compatible scalar projections are:

```text
c^2-a^2 -> 3-1 -> 2
(c^2-a^2)^2 -> 4
(c^2-a^2)^2/(2*u_phase^72) -> 4/(2*1) -> 2
Pi-b^2+b^4-Pi -> Pi-2+4-Pi -> 2
(corresponding numerator)/(c^2-b^2) -> 2/1 -> 2.
```

The repeated `Pi` cancellation occurs inside the declared exact symbolic scalar projection; it does not identify `Pi` with a decimal literal and does not rewrite the native source.

## 12. u^0 / RealSurd proof

The current HHCQ contract also contains

```text
u^0=(Power(RealSurd(b^2,b^4c^2),a^2))^(b^6c^4)/(b^6)^2.
```

The exact projection chain is:

```text
b^4*c^2 -> 4*3 -> 12
RealSurd(b^2,b^4*c^2) -> RealSurd(2,12)
a^2 -> 1
b^6*c^4 -> 72
(RealSurd(2,12))^72 -> (2^(1/12))^72 -> 2^6 -> 64
(b^6)^2 -> 8^2 -> 64
64/64 -> 1
u_phase^0 -> 1.
```

The algebraic root remains exact; no IEEE approximation is required.

This also exposes why scalar-projection proofs must be attached to each expression separately. A chain may contain expressions with different scalar magnitudes under different typed projections; the native equality/constraint edge cannot be replaced by an assumption that all visually connected syntax is one ordinary scalar identity.

## 13. Exact symbolic constants

`Pi`, `O`, and `E` remain exact source symbols. Their registered projection records preserve them symbolically:

```text
Pi -> Pi
O  -> O
E  -> E
```

The source-identity constraints `O!=Pi` and `E!=2.71828182846_SOURCE_IDENTITY` remain intact.

`I` is a typed phase/complex basis object; the registered quartic projection proves `I^4->1` without converting `I` into an ordinary real scalar.

## 14. Explicit unresolved surfaces

Completeness also requires recording what is not yet scalar-evaluated. The current UCE full-symbolic profile leaves these families fail-closed:

```text
t / m native solutions
nested s tensor
f / At / Bt correspondence chain
Mod(f/u,72*(pq+xy))
Delta/P=Sqrt(pq+u^72)^x^2.
```

They are assigned `UNSUPPORTED_DOMAIN`, not guessed numerical values.

The ordered `NcalcMatrixPower(...,4)` surface is `SYMBOLIC_SCALAR`/ordered symbolic matrix output until a separately authorized exact matrix evaluator proves a scalar projection.

## 15. Machine-readable theorem object

Every theorem record carries:

```text
theorem_id
claim_type=PROJECTION_THEOREM
native_expression
projection_class
projection_id
domain
result_expression
premises[]
derivation[]
fixed_proof_id | null
source_needles[]
source_scope
reverse_lift_rule
lost_information[]
theorem_sha256
theorem_receipt_hash72
```

and mandatory authority flags:

```text
projection_equality_implies_native_identity=false
source_rewrite_authorized=false
canonical_vm81_mutation_authority=false
canonical_hash72_mint_authority=false
canonical_hash216_persistence_authority=false
floating_point_canonical_authority=false.
```

This makes the explanatory mathematics mechanically inspectable while retaining the HARMONICODE constructor as the higher authority.

## 16. Current coverage

Version 1.0 supplies 35 fixed proof nodes. Version 1.1 adds 87 theorem/classification records spanning fixed, parameterized, multibranch, symbolic, unsupported, and typed-nonscalar surfaces.

The next expansion boundary is mechanical source/AST coverage: every scalar-capable node emitted by the authoritative Pass159/Pass169 frontend should carry one theorem reference or explicit non-fixed classification. That annotation must consume the existing frontend artifact; it must not become a competing parser or transition authority.
