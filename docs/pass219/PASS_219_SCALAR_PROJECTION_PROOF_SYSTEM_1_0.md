# Pass 219 — HARMONICODE Scalar Projection Proof System 1.0

## Purpose

Every scalar-visible result used to explain HARMONICODE must be an explicit source-bound projection proof or an explicit non-fixed classification. A projected scalar never replaces the native expression that produced it.

```text
native expression E --registered projection + proof witness--> scalar v
projection equality != native identity
```

This layer is additive over the byte-preserved Pass 169 corpus and does not rewrite, simplify, commute, reassociate, or independently solve the canonical manifold.

## Canonical source lock

```text
HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode
632 bytes
SHA-256 3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53
```

A source mismatch fails closed.

## Proof object

Each fixed proof records its native expression, projection/domain, exact rational result, dependency proof IDs, ordered derivation, information lost by projection, reverse-lift rule, deterministic SHA-256 identity, and canonical Hash72 proof receipt. Every proof explicitly records that projection equality does not imply native identity and that it has no VM81 mutation, Hash72 mint, or Hash216 persistence authority.

## Coverage states

Every variable or compound surface is assigned one of five states:

- `PROVEN`: a fixed exact scalar projection has a proof node.
- `PARAMETERIZED`: exact evaluation requires legal input values/witnesses.
- `SYMBOLIC`: the expression is exact but no fixed scalar is asserted.
- `UNSUPPORTED_DOMAIN`: the active full-symbolic UCE profile still leaves the clause unresolved.
- `TYPED_NONSCALAR`: the native value is phase/tensor/ordered data and has no global fixed scalar projection.

The system therefore explains every variable without fabricating scalar values for `P,p,q,A,B,x,y,z,w,u,...`.

## Primitive proof nucleus

```text
a^2 -> 1
b^2 -> 2
c^2 -> 3
d^2 -> 5
e^2 -> 8
f^2 -> 13
g^2 -> 21
```

The unsquared symbols `a,b,c` remain typed native symbols; the square projections do not authorize choosing scalar square-root branches.

## Lo Shu polynomial proof DAG

From the primitive proofs:

```text
b^4             -> (b^2)^2 -> 2^2 -> 4
c^4             -> (c^2)^2 -> 3^2 -> 9
b^6             -> (b^2)^3 -> 2^3 -> 8
b^2*c^2         -> 2*3 -> 6
b^2+c^2         -> 2+3 -> 5
b^4+c^2         -> 4+3 -> 7
b^2*c^2-a^2     -> 6-1 -> 5
```

Thus:

```text
{{b^4,c^4,b^2},
 {c^2,b^2+c^2,b^4+c^2},
 {b^6,a^2,b^2*c^2}}
 ->
{{4,9,2},{3,5,7},{8,1,6}}
```

`d^2`, `b^2+c^2`, and `b^2*c^2-a^2` all project to `5`, but they remain three distinct native proof nodes.

## Nested canonical basis chain

The registry also proves:

```text
c^2-b^2                                              -> 1
b^2*(c^2+b^2)                                       -> 10
(b^2*(c^2+b^2))-(c^2-b^2)                          -> 9
Sqrt(c^4)                                           -> 3
((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)              -> 3
c^2*b^6-c^2                                         -> 21
(c^2*b^6-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)) -> 7
```

The radical proof is scoped to the registered nonnegative exact-radical projection and does not rewrite `Sqrt(c^4)` globally.

## 72 and 5184

```text
b^6*c^4 -> 8*9 -> 72
```

and:

```text
(b^(2*c^2)*c^(b^4))^2
 -> (b^6*c^4)^2
 -> 72^2
 -> 5184
```

Independent cardinality proofs retain distinct ancestry:

```text
72^2   -> 5184
64*81  -> 5184
36*144 -> 5184
```

Same numeral, different proof identity.

## Scoped phase and number-theory proofs

The registry includes:

```text
u_phase^72       -> 1   under PI-U-PHASE-v1
I^4              -> 1   under registered phase projection
Delta            -> 1   under Pass129 nonzero exact-rational projection
P^2-p*q          -> 1   under the same Pass129 projection
(A/B)*(B/A)      -> 1   for exact nonzero A,B
0^4              -> 0   under ordinary exact-integer projection
```

These are projection theorems, not globally licensed source substitutions.

## Non-fixed source surfaces

`P,p,q,A,B,Delta` remain parameterized without a compatible witness. `x,y,z,w,xy,yx,zw,wz,u,I` remain typed native values. The full-symbolic residuals involving `t,m,s,f,At,Bt` remain fail-closed where the repository currently marks them unsupported. Compound clauses such as `t^3-t`, `m^2-m`, `Mod(f/u,72*(pq+xy))`, and `Delta/P=Sqrt(pq+u^72)^x^2` are classified rather than approximated.

## Callable API

```text
verify_canonical_source(source)
extract_source_symbols(source)
validate_dependency_graph()
build_scalar_projection_coverage(source)
prove(native_expression)
```

`prove()` returns only registered fixed projection proofs. A request for an unresolved expression fails with `NO_FIXED_SCALAR_PROOF`.

## Falsification conditions

The layer fails if the canonical source identity changes, a source variable lacks classification, a proof dependency is absent, a fixed proof uses floating point, same-valued proofs collapse native identity, unresolved surfaces acquire invented scalars, receipts become nondeterministic, or the layer claims canonical mutation/mint/persistence authority.

## Version 1.0 result

The initial implementation contains 35 deterministic fixed proofs plus complete variable-token classification for the canonical 632-byte Pass 169 corpus. The next expansion is exhaustive source-to-AST scalar-capability coverage: every scalar-capable AST node must point to a proof ID or to an explicit non-fixed classification while retaining the original AST as authority.
