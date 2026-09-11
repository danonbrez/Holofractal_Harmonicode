# Pass 219 SPI Scalar Projection Proof Layer v2

Status: `IMPLEMENTED SEED REGISTRY / EXACT PROJECTION AUTHORITY ONLY / NATIVE AUTHORITY UNCHANGED`

Audited base: `main @ 2def7910b99046821f34e1446bcec33ca4fd4090`

Implementation:

- `hhs_spi_scalar_projection_registry_v1.py`
- `hhs_spi_scalar_projection_registry_tests_v1.py`

## 1. Authority boundary

The scalar calculus is downstream of the native HARMONICODE constraint graph.

A native HARMONICODE state is typed:

```text
S in L_H
```

Registered scalar projections have the form:

```text
pi_i : E_i(L_H) -> Q
```

`Q` is an exact projection codomain, never the native carrier. Projection equality is not native identity. A scalar proof MUST NOT:

- rewrite or replace native source;
- commute ordered products;
- identify `xy` with `yx`, `AB` with `BA`, or `A/B` with `B/A`;
- identify `O` with `Pi`;
- admit VM81 state;
- mint canonical Hash72/Hash216 lineage;
- establish a second transition authority.

The existing native bilateral fixed-point authority remains `A=P=B` in `hhs_self_solving_constraint_modules_v1.py`.

## 2. Scalar proof object

Every scalar proof is a typed record:

```text
Pi_E = (
  source_expression,
  profile,
  premises,
  domain,
  derivation,
  result,
  modulus,
  residual,
  lost_information,
  reverse_lift_status,
  proof_status,
  implementation_status,
  receipt_status,
  coverage_state
)
```

Mandatory distinctions:

```text
mathematically proved != implemented != canonically admitted
```

`lost_information` is mandatory. A projection with no declared information loss is rejected as unaudited rather than presumed lossless.

Coverage states are exactly:

```text
PROVEN
SYMBOLIC
UNSUPPORTED_DOMAIN
MISSING_PROJECTION
```

Scalar proof receipts are deterministic SHA-256 commitments over the exact proof record and are tagged `SCALAR_PROOF_ONLY`. They are not canonical Hash72/Hash216 mutation receipts.

## 3. Foundational projection rules

### D1 — Native carrier

Native symbols do not live in `Q`. Statements such as

```text
pi(t^3-t)=1
pi(m^2-m)=1
```

may be registered without solving `t` or `m` as rational, real, or complex scalars.

### D2 — Equality edges

Each native equality edge may carry zero or more scalar proofs. Scalar correspondence never grants a substitution license back into the native graph.

### D3 — Symmetric-pair orientation

For offset `d`, the ordered pair is

```text
(p,q)=(P-d,P+d)
```

`d=+1` and `d=-1` are distinct ordered lattice states even though they project to the same unordered scalar shell.

### D4 — Self-cancelling phase carriers

`O` and `Pi` are distinct symbols. Authorized scalar projections may cancel each against itself:

```text
pi(O-O)=0
pi(Pi-Pi)=0
```

Cross-cancellation or identification is forbidden.

### D5 — Lane orientation

Native `A/B`, `B/A`, `xy`, `yx`, `AB`, and `BA` retain source order. Reciprocal cancellation is only a registered commutative scalar projection.

## 4. Closed theorem surfaces

### T1 — SPI-Q-v1

For `P in Q`, `P != 0`, `p=P-1`, `q=P+1`:

```text
P^2 = pq + 2P/(p+q)
```

because `p+q=2P`, the correction is exactly `1`, and `pq=P^2-1`.

### T2 — Unit shell and shell tower

```text
delta_SPI(d)=P^2-[(P-d)(P+d)+1]=d^2-1=(d-1)(d+1)
```

Unit closure occurs exactly at `d=+/-1`: one unordered unit shell, two ordered orientations. The exact tower is

```text
P^2=(P-d)(P+d)+d^2.
```

### T3 — Cubic and modular surfaces

Polynomial factorization:

```text
t^3-t=t(t-1)(t+1)
m^2-m=m(m-1)
```

For integral projections, `6 | t^3-t` and `2 | m^2-m`.

For integer `P>1` under SPI:

```text
P^3-P == 0 mod pq
P^2 == 1 mod pq
pq=P^2-1
```

These are separate scalar modular receipts. The source edge `P^2(MOD)(pq)` remains a separately typed native edge and is not replaced by either receipt.

### T4 — Scalar reciprocal units

Inside the registered commutative nonzero scalar projection:

```text
pi(A/B)*pi(B/A)=1
pi(x/y)*pi(y/x)=1
```

No native commutation follows.

### T5 — Equality discrepancy

For nonzero scalar lanes:

```text
F(A,B)=AB-(A-AB/BA)(B-BA/AB)=A+B-1.
```

Three surfaces remain distinct:

```text
SPI-DYADIC-Q-v1:       A=B=P^2/2 over Q
SPI-GENERATOR-MOD-v1: A=B=P^2 with residual P^2 == 0 mod P^2
native authority:      A=P=B
```

The native fixed point is independently implemented; it is not derived by scalarizing `P^2=A+B`.

### T6 — Pythagorean and u^72 closure

Canonical source:

```text
b²=(c²-a²)²/(2u⁷²)=(Pi-b²+b⁴-Pi)/(c²-b²)==c²-a²
```

Let

```text
alpha=pi(a²)
beta=pi(b²)
gamma=pi(c²)
```

under `beta!=0`, `gamma-beta!=0`, and projected `u^72!=0`.

Exact derivation:

```text
gamma=2beta-1
alpha=beta-1
alpha+beta=gamma
pi(u^72)=beta/2
```

With primitive `beta=2`:

```text
a² -> 1
b² -> 2
c² -> 3
u^72 -> 1
```

The primitive triple is therefore reconstructed by the chain rather than used as a native rewrite.

### Squared-coordinate surd profile

For `alpha=beta-1>0`:

```text
N=gamma²-beta*gamma-beta²+beta=alpha²
D=gamma-beta=alpha
N/D=alpha
```

which proves the registered squared-coordinate projection of

```text
[sqrt(c⁴-b²c²-b⁴+b²)/sqrt(c²-b²)]² -> a².
```

The real-root domain is explicit; no scalar sign choice for `a` or `b` is introduced.

## 5. RealSurd-QROOT-v1

Registered exact root projection:

```text
source_type: SYMBOLIC_REAL_SURD
target_type: EXACT_ALGEBRAIC_PROJECTION
radicand: positive exact rational
index: positive integer
outer power: nonnegative integer
```

For the first implementation, rational collapse is admitted only when the root index divides the outer exponent:

```text
RealSurd(r,n)^k -> r^(k/n), n | k.
```

Other cases return `UNSUPPORTED_DOMAIN`; they are never approximated by float.

This proves the inherited exact precedent

```text
RealSurd(72,72)^144 = 72^2
```

and the u^0 projection below.

## 6. O4 — u^0 exact closure

Source:

```text
u⁰=(Power(RealSurd(b²,b⁴c²),a²))^(b⁶c⁴)/(b⁶)²
```

Under `a²->1`, `b²->2`, `c²->3`:

```text
b⁴c²=12
b⁶c⁴=72
RealSurd(2,12)^72=2^6=64
(b⁶)²=64
u⁰ -> 64/64 = 1
```

Residual is exactly zero.

## 7. Seed scalar registry

The first implemented registry contains exact proof ancestry for:

```text
a² -> 1
b² -> 2
c² -> 3
b⁴ -> 4
c⁴ -> 9
b⁶ -> 8
b²c² -> 6
b²c²-a² -> 5
b⁴+c² -> 7
b⁶c⁴ -> 72
(b^(2c²)c^(b⁴))² -> 5184
```

plus T1-T6, RealSurd-QROOT-v1, u^0, the exact boundary literal `179971.179971`, and explicitly open records for unresolved surfaces.

Each occurrence keeps its own proof identity even when two expressions project to the same numeral.

## 8. AST coverage membrane

The registry binds preserved source to the existing non-executing HARMONICODE parser. The parser's node ID, node root Hash72, source span, kind, and ordered-symbol-preservation flag are retained as source identity only.

Exact source matches receive their registered proof IDs. An unmatched AST node is classified:

```text
MISSING_PROJECTION
```

No heuristic scalarization is allowed.

This is the first coverage membrane for later repository-wide corpus enumeration.

## 9. Open obligations

### O2 — Matrix witness

Still open. Required exact witness:

```text
W_matrix=(x,y,z,w,ordered_matrix,exact_inverse_or_lift,fourth_power,root_witness,residual=0)
```

Source preservation is not sufficient.

### O3 — residual provenance

The boundary literal

```text
179971.179971 = 179971179971/1000000
```

is verified exactly. Its claimed provenance specifically from the `f==t/m` state change remains open and must not be inferred from repeated literal use.

## 10. Required negative behavior

The implementation MUST fail closed for:

- float or boolean inputs at exact rational boundaries;
- empty `lost_information`;
- scalar proofs claiming canonical VM81 admission;
- zero divisors for T1/T4/T5/T6;
- invalid RealSurd radicand/index/exponent domain;
- non-divisible RealSurd rational collapse;
- cross-identification of `O` and `Pi`;
- substitution of T3b receipts for the T3c native MOD edge;
- unknown source AST nodes, which remain `MISSING_PROJECTION`.

## 11. Acceptance rule

A scalar proof may be marked `CLOSED/IMPLEMENTED/VERIFIED/PROVEN` only when its exact evaluator and focused regression receipt pass. This status does not authorize native mutation.

VM81 remains the canonical transition/admission authority.
