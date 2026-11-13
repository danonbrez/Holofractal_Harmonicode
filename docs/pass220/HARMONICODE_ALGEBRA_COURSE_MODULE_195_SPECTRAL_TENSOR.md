# HARMONICODE Algebra Course — Module 195: ordered spectral-tensor closure

This is an **additive Module 195 proof packet**, distinct from the existing
**Module 194 / V160** HTML physics source-and-address preflight in draft PR #908.
No existing course text, indexed sources, Module 194 material, native gate,
or frozen layer is rewritten. Source/course-index ingestion and a native proof
binding require their own follow-on evidence.

## 195.1 Original ordered source

```text
MatrixTimes(MatrixTimes({{2,-1,0},{0,1,-2},{-1,0,1}},-List(List(2,(-1),0),List(0,1,(-2)),List((-1),0,1))),m)/(25*x+6*x^2+x^3)==1/m
```

The nested `MatrixTimes` operators, `List` operand addresses,
rightmost `m`, division site, and native `==` gate remain typed, ordered,
and source-preserved. The following exact arithmetic is a *projection witness*;
it is not an implicit conversion of a native equality to entrywise scalar
arithmetic.

## 195.2 Exact spectral and reciprocal witnesses

```text
M == [[2,-1,0],[0,1,-2],[-1,0,1]]
K == MatrixTimes(M,-M) == [[-4,3,-2],[-2,-1,4],[3,-1,-1]]
Spectrum(K) == {0,-3+4I,-3-4I}
Rank(K) == 2
D(x) == det(xI-K) == x^3+6*x^2+25*x
D(K) == K^3+6*K^2+25*K == 0_(3x3)
Adj(xI-K) == K^2+(x+6)K+(x^2+6*x+25)I
(xI-K)*Adj(xI-K)-D(x)I == 0_(3x3)
NonzeroSpectralMagnitudes(K) == List(5,5)
```

For `D(x) != 0`, the ordinary resolvent inverse has an adjugate
representation. At `x=0` and `x=-3±4I` the ordinary inverse is singular;
the existing course HNAN runtime guard must handle this site. The spectral
magnitudes `5` do not establish bounded power iteration.

## 195.3 Distinct native admission obligations

```text
Module195 == List(
  K == M(-M),
  D(x) == det(xI-K),
  D(K) == 0_(3x3),
  AdjugateIdentityResidual == 0_(3x3),
  NonzeroSpectralMagnitudes(K) == List(5,5),
  HNANSingularRoute == GAIN_1_NO_PHASE_WRITE [native execution outstanding],
  TypedEqualityAnd5184HydrationAdmission == outstanding native proof obligation,
  ScalarCoercionRefutationOfNativeGate == false,
  Module194V160 == distinct preserved module,
  CanonicalHash72Hash216Mutation == none,
  Omega == true [bounded exact witness],
  Psi == 0 [bounded exact witness],
  Delta_e == 0 [bounded exact witness]
)
```

For the original rightmost register `m`, retain the native typed reciprocal,
ordered equality and HNAN guard. A conventional scalar solver does not prove
or disprove the native gate. The matrix `K` is singular, so never introduce
`Inverse[K]` or cancel `m` without a typed constructor and admissible
inverse law.

## 195.4 Execution and integration boundary

Executable exact witness:
`hhs_runtime/hhs_pass220_course_m195_spectral_tensor_witness_v1.py`.

Regression test:
`tests/pass220/test_hhs_pass220_course_m195_spectral_tensor_witness_v1.py`.

This candidate checks integer matrix product, Cayley–Hamilton residual,
adjugate residual coefficients and non-admission status. It deliberately
does **not** mint a Hash72 or Hash216 receipt, authorize VM81 mutation,
execute the C++ cell wall, demonstrate gain-1/no-phase-write at runtime,
or bind the typed `m` equality through Lane 5.

Admission continuation: immutable course source and module index;
existing Lane 5 typed equality producer; ordered A/B provenance and
`AB=P^4, BA=-P^4` where applicable; HNAN runtime phase-preservation;
5184-cell serialization/hydration; native C++/VM81 gate; Hash72 and
Hash216 receipt/replay; exact-main production evidence. Each requires
its own executed witness, not a declared success flag.
