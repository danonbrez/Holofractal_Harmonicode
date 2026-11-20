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

## 195.5 Exact Gaussian singularity selector (adapter-level)

The Module 195 HNAN bridge now exposes
`exact_denominator_gaussian(real, imaginary)`, computing both integer
components of `D(real+imaginary*I)` without float approximation.
`bind_m195_source_derived_singular_route` requires both components to equal
zero before calling the **inherited** Module 9 native C passthrough and its
source-bound dependency-graph binding. It rejects a non-root without invoking
the bypass. This addresses test-supplied hardcoded zero flags **at the Module
195 Python adapter**, not the Lane 5 native producer, which remains open.
The compiled native checker continues to receive its existing zero-divisor
flag through its unchanged wrapper; the adapter does not constitute a new
canonical input or equality operator.

Exact roots tested: `(0,0)`, `(-3,4)`, `(-3,-4)`. Non-root `(1,0)`
gives `D(1)=32` and must not invoke the inherited checker. Typed `m`
equality, A/B phase closure, 5184 hydration, VM81 and canonical receipts
remain outstanding independently.

## 195.6 Frozen source integrity blocker (observed in CI)

The existing course proof dependency-graph binder rejects before native binding:
`SOURCE_BLOB_CHANGED:whitepapers/Harmonicode Algebra - Course`.
At the investigated PR head, the freeze manifest pins Git blob
`2744e9ecf1f260ff9a5a02870320698ee2d7dcaf`, while the actual
repository course blob is
`968735b21bb0fda42f9c944ae6987099e624e7a7`.

The M195 regression deliberately separates two checks:
1. A **raw** inherited C11 passthrough is compiled and executed against
   each exact Gaussian singular-root witness. Byte preservation, gain 1,
   and zero phase write are checked directly; this is **not** a source-bound
   course proof receipt or VM81 admission.
2. The existing frozen-course graph binding must still reject the
   mismatched source. Its result is **not** bypassed or replaced with the
   raw C check.

To enable a fully source-bound M195 witness, recover the authoritative
frozen-course source and reconcile the recorded identity through the
existing authorized source-integrity process. Do not silently repin
the manifest or declare the original typed-equality gate admitted.

## 195.7 Immutable source-lineage recovery without bypass

The source-freeze manifest originally captured `whitepapers/Harmonicode
Algebra - Course` as blob `2744e9ecf1f260ff9a5a02870320698ee2d7dcaf`,
which is recoverable through the Git object store. The current file is blob
`968735b21bb0fda42f9c944ae6987099e624e7a7`, an expanded/different
course. Comparing the source at the earlier #807 freeze and after #888
identifies distinct historical objects; this does **not** authorize treating
them as identical or replacing either course text.

The read-only diagnostic
`hhs_runtime/hhs_pass220_course_m195_source_lineage_diagnostic_v1.py`
reads both exact byte objects, independently computes their Git blob identities
and SHA-256 evidence, and emits
`source_graph_binding_eligible=false` while these identities differ.
It never rewrites the freeze manifest, course, or dependency-graph validator.
Its candidate diagnostic cannot elevate source provenance to native admission.
The original source-bound graph must continue to reject the changed working
course until authorized reconciliation is implemented and independently
validated.

## 195.8 Native C11 exact singularity candidate

Module 195 now has a **bounded candidate ingress adapter** in
`hhs_runtime/c/hhs_pass220_course_m195_gaussian_hnan_ingress_v1.c`.
Its exact Gaussian integer computation evaluates
`D(a+bi)=(a+bi)^3+6(a+bi)^2+25(a+bi)` with signed 64-bit arithmetic
for `|a|,|b| <= 100000`; inputs outside that proof range fail closed.
No float, host inverse, or caller-supplied `divisor_zero` flag decides
the C-side singularity. Only exact zero invokes the inherited
`hhs220_course_passthrough_execute` ABI, which retains its
gain-one/no-phase-write scope.

The adapter is **not** registered as a new VM81 authority, new HNAN
checker, native Lane 5 producer, native course typed-equality constructor,
or a trusted Hash72/Hash216 source. Its C11 test exercises the three
spectral roots, nonroot `D(1)=32`, safe-range boundaries,
out-of-range fail-closed behavior, and untouched output buffers on
nonroot and invalid-input rejection. Exact arithmetic/route evidence
is a scoped candidate only.

The existing frozen-course graph identity mismatch remains a separate
source-bound blocker. The adapter does not waive or amend it.
