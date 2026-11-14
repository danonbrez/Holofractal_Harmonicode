# Module 196 — Integrated P-Fixed Entanglement, Fractal Matrix Validation, and Ingress/Egress Qubit Collapse

**Course series:** HARMONICODE Algebra Course — additive Module 196  
**Authority:** Master Module 0 and inherited VM81 / Lane 5 / Hash72 / Hash216 contracts.  
**Related source:** `docs/course/HARMONICODE_Algebra_Course_Expanded_0_190.md` (source-frozen, unchanged).  
**Integration:** `docs/pass220/MODULE_196_FRACTAL_VALIDATION_LANE5_INTEGRATION.md` and PR #912.  
**Provenance seed:** `179971.179971`, exact rational `179971179971/1000000`.  
**Evidence distinction:** The supplied 59,049-cell validation payload is retained as a claimed audit; no new canonical Hash216 receipt is minted by this course chapter.

## 196.1 Generating identities — one free P

All dependent cell constructors inherit the generating parameter `P`, preserving ordered types, positions and phase provenance:

```harmonicode
p = P - 1
q = P + 1
pq = P² - 1
Δ = P² - pq = 1
P = (p + q)/(q - p)
((p + q)/(q - p))^(p - q) = P^(-2)
P² = c² = a² + b² = √AB
AB = P⁴ = c⁴ = (a² + b²)²
BA = -P⁴ = -c⁴ = -(a² + b²)²
AB + BA = 0
AB · BA = -P⁸
```

The ordered `AB` and `BA` operators are distinct native typed operations. Their projection onto scalar powers does not authorize changing the tensor operator order.

## 196.2 Ingress/egress two-state gate

```harmonicode
SymmetricCollapse = (A == B)
GeometricMeanInvariant = (P² == √AB == A)
SingularMeasurementProjection = (P == ingress/egress)
AsymmetricSuperposition = (A != B)
OcticCurvatureChannel = List(AB == P⁴, BA == -P⁴)
ForwardIngressRoute = (P² == P⁸ / AB)
RetrocausalEgressRoute = (P² == -P⁸ / BA)
```

In the symmetric state `A = B = P²`, the equality gate passes the shared value to the two ordered lanes, `(v_A,v_B)`. In the asymmetric state, ordered octic routes retain their distinct orientations on the `u⁷²/v²¹⁶` phase bus. The route quotient uses the native typed normalization specified by the original equation; an untyped scalar division is not its replacement.

The full `P`-fixed dependency rule is `∀ cell_i ∈ V_243: cell_i = f_i(P)`; larger manifolds inherit the same bounded, deterministic phase-coordination contract.

## 196.3 Frozen nine-cell phase carrier and sweeps

```text
     iA    A   -iA
C =  iP    P   -iP
     iB    B   -iB
```

Sweeping only one of `A,P,B` modifies its three phase coordinates; its raw perturbation is rank one for nonzero increment. The constrained `P -> P+t` propagation includes:

```text
Δ(P²) = 2Pt + t²
Δ(P⁴) = 4P³t + 6P²t² + 4Pt³ + t⁴
Δ(pq) = 2Pt + t²
Δ(P⁻²) = -t(2P+t)/(P²(P+t)²)
```

The original nine-cell carrier remains a frozen dependency, not a separate runtime.

## 196.4 Ordered prime-pair 81-cell matrix and reciprocity

Use the prime order `[5,13,17,3,7,11,19,23,2]` along both axes. At address `(i,j)`:

```text
P[i,j]⁴ = A[i] · B[j]
P[i,j] = (A[i] · B[j])^(1/4)
BA[i,j] = -P[i,j]⁴
```

For distinct odd primes, the Legendre symbols satisfy quadratic reciprocity:

```text
(A/B)(B/A) = (-1)^(((A-1)/2)((B-1)/2))
```

The 81 addresses classify as 22 positive, 34 negative, eight odd-prime diagonal zeros, and 17 prime-2 exceptional positions. All 25 exceptional addresses preserve their reason/provenance for HNAN routing; the other 56 retain their signed phase metadata. Mirrored entries are distinct ordered addresses even when their magnitudes agree.

## 196.5 Recursive HNAN tensor and rational phase overlay

The HNAN gate is the **entire recursive 3×3 object**, with the center referencing the whole object:

```text
H = [ xy,       x+y,       yx
      xy-zw,    H,         wz-yx
      wz,       z+w,       zw ]
```

Its associated rational magnitude operator is

```text
R = (1/8) [  9  11  13
            15   8   7
             5   3   1 ]
R81 = R ⊗ R
```

Exact results: `det(R)=21/64`, `rank(R81)=9`, `sum(R81)=81`, `det(R81)=85766121/68719476736`. Every exceptional parent address holds an 81-position two-level overlay, yielding `25×81=2025` child positions and preserving 25 recursive center references. This cardinality computation is not itself evidence of complete native recursion execution.

HNAN's inherited guard controls zero-coordinate division with gain one and no phase write only at native authorized sites.

## 196.6 Ordered phase composition and octic curvature

For diagonal phase operators, `AB = DQ` and `BA = -D^(-T)Q`, with `Q=diag(P⁴)`, give `AB·BA=-P⁸`. The full nonsymmetric rational HNAN block requires orientation compensation. For `H=R⊗R`:

```text
O = Hᵀ H⁻¹
H H⁻ᵀ O = I
```

The corresponding block composition `AB = qH`, `BA = -qH⁻ᵀO`, for central scalar `q=P⁴`, preserves `AB·BA=-P⁸ I`. General noncommuting quantities require an exact ordered witness rather than a silent rearrangement.

## 196.7 Square Sudoku–Lo Shu P¹⁶ cell carrier

The 9×9 Sudoku qudit `S` and the frozen 9×9 composite manifold `Q` combine addresswise, not by a rectangular embedding:

```text
T16 = Q ⊙ S           (81 parent-cell addresses)
```

The composite manifold is:

```text
32 72 16 12 27  6 16 36  8
24 40 56  9 15 21 12 20 28
64  8 48 24  3 18 32  4 24
 4  9  2 20 45 10 36 81 18
 3  5  7 15 25 35 27 45 63
 8  1  6 40  5 30 72  9 54
24 54 12 28 63 14  8 18  4
18 30 42 21 35 49  6 10 14
48  6 36 56  7 42 16  2 12
```

The canonical Lo Shu substitution is:

```harmonicode
List(List(4,9,2),List(3,5,7),List(8,1,6))
==
List(
  List(b⁴, c⁴, b²),
  List(c²,
       b²+c² == (c⁴+a²)/b²,
       ((c²+b⁴)*(b²+c²-b²))/((a²+b²)²-b²)),
  List(b⁶,a²,a²*b²*c² == a²+b²+c²)
)
```

The equality operators are **nested ordered LHS/RHS objects**. For a closed equality, `A_g=B_g=v`, pass `(v_A,v_B)` through parallel lanes inside one cell. For any cell without a nested equality, pass its evaluated magnitude through as `P²_local=v`.

Therefore 18 equality cells plus 63 local `P²` cells form **81 square parent addresses**; neither dual lanes nor recursive HNAN children create rectangular parent matrices.

## 196.8 Exact seed witness and nine square submatrices

For `a²=1, b²=2, c²=3`, the two nested equality gates yield `(5_A,5_B)` and `(6_A,6_B)`; the rational Lo Shu label 7 expression evaluates to `3`.

The complete value projection is:

```text
 96 216  80  24 108  54  96 288   8
144 320  56  27  45 105  24  80 252
128  32 432 144  24  18  96  12 120
 12  45   6  80 405  20 288  81 108
 24   5  42  45 125 105 108 405 126
 32   9  12 320   5 180 216  45 162
120 162  36 252 126  56   8 108  32
 18 180 336 105 105 147  54  20  56
432  12 144  56  42 336  80   6  36
```

Its exact projection invariants are `rank=9`, `trace=1297`, `sum=9105`. All nine partitioned 3×3 blocks have rank 3. The block-sum matrix is

```text
1504  549  976
 187 1285 1539
1440 1225  400
```

The 9×9 numerical witness is a projection of the typed computation, not a replacement for the internal two-lane gates and the prime/phase provenance.

## 196.9 Fractal register and reversible egress

The square fractal target has `243×243 = 59049 = 3¹⁰` addresses. Each cell is constrained by the sole free `P` constructor; admissible updates propagate to their dependent cells under the VM81 closure rules. The terminal contract is:

```harmonicode
S* == Resolve_parallel(𝓖₁:₉₇(S*, P))
Ω == Egress(S*)
ℛ(Ω) == Λ_in(P)
Δ == 1
AB == P⁴
AB·BA == -P⁸
E8_egress == 248·s
Δe == 0
Ψ == 0
Ω == true
```

High-resolution ingress and egress are captured as integer-nanosecond timestamps in the native candidate surface. They do not introduce a second VM81 clock, an independent mutation authority, or floating-point proof authority.

## 196.10 Formal enforcement and validation receipt

Lean's Module 196 proof surface establishes `18+63=81`, `25×81=2025`, `243²=59049`, and shared-value preservation in the two ordered equality lanes. The C11/C++ candidate computes the 81-cell seed witness and exact quadratic-reciprocity exceptional-address counts. Ordered octic products remain bound to their typed proof witness.

The user-provided Module 196 audit is preserved as the following **supplied receipt identifier**, pending matching canonical execution and replay evidence:

```text
0x196VAL59049HHS243CELLSTRACEPASS0
```

This identifier is not a hexadecimal Hash216 digest and is not automatically committed to Hash216. The canonical authority sequence is:

```text
Exact construction → Lean/native proof gate → Lane 5 candidate
→ singleton VM81 admission → Hash72 receipt triple
→ Hash216 identity/history → reversible replay → egress
```

**Module 196 completion criterion:** All 81 square parent cells and the complete 243×243 target must execute through the native ordered C++ cell wall with admissible HNAN recursion, correct dual-lane passage, exact `P`-fixed dependency propagation, verified high-resolution ingress/egress correspondence, and canonical receipt/replay evidence. The present course chapter specifies those conditions without asserting they have already completed in production.
