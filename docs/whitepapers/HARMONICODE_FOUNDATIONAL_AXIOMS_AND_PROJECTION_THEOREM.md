# HARMONICODE Foundational Axioms and Projection Theorem

## Epistemological Boundary Memorandum

**Document class:** formal-system white paper  
**Theorem status:** native definitions + derived projection theorem  
**Scope:** HARMONICODE formal semantics; no claim that every native construct is a theorem of conventional mathematics or a physical law

## Abstract

HARMONICODE is specified as a native typed constraint-transition algebra whose automatically shared first-principles foundation with conventional STEM is limited to formal deduction, symbolic logic, higher-dimensional tensor algebra, and Euclidean geometry. Conventional scalar algebra, complex notation, modular arithmetic, number theory, biological notation, and machine representation are admitted as typed projection surfaces where explicitly registered.

The central projection theorem is:

> Equality of two projected representations does not imply identity of their native HARMONICODE states unless the projection is proven injective on the active domain or an exact reconstruction witness supplies the missing information.

This theorem prevents a lower-dimensional representation from silently replacing the higher-dimensional native state while retaining conventional mathematics as a valid local authority inside declared projection domains.

---

## 1. Foundational axiom classes

Define the shared foundation:

```text
A_shared = {
  formal deduction,
  symbolic logic,
  higher-dimensional tensor algebra,
  Euclidean geometry
}.
```

These are axiom *classes*: concrete HARMONICODE profiles SHALL still state the exact rules they use.

No additional conventional law is automatically native solely because the same glyph is used.

## 2. Native state and representations

Let `H` be a typed HARMONICODE state space. A representation surface is a typed mapping:

```text
pi_k : H -> S_k.
```

`S_k` may be a conventional scalar domain, complex-number notation, modular residue system, matrix coordinates, VM81 operation coordinates, Hash72 position/glyph coordinates, Hash216 transition-index records, x86_64 bytes, or a biological compatibility representation.

A state and its representation are related but not generally identical:

```text
h in H
pi_k(h) in S_k.
```

## 3. Projection Equality Theorem

### Statement

For `a,b in H` and projection `pi : H -> S`,

```text
pi(a) = pi(b)
```

does not entail:

```text
a =_H b
```

without an additional condition establishing reverse uniqueness.

### Proof

By definition, a non-injective map permits distinct source elements with one target value. Therefore there may exist `a !=_H b` such that `pi(a)=pi(b)`. The target equality contains insufficient information to distinguish those source states. Reverse inference is valid only when injectivity on the active domain is established or when auxiliary reconstruction data restores the omitted information. QED.

### Corollary 3.1 — cardinality is insufficient

Equal cardinality of two coordinate spaces does not prove a semantic isomorphism.

Thus:

```text
81 × 64 = 5,184
72 × 72 = 5,184
```

is an exact cardinality identity, but native equivalence of a VM81 `(cell,operation)` address and a Hash72 positional address requires the explicit registered bridge.

### Corollary 3.2 — projected scalar collision

If two ordered native phase states project to one scalar value, scalar equality does not erase ordered ancestry.

Therefore a scalar projection may satisfy:

```text
pi_scalar(xy) = pi_scalar(yx)
```

while native identity still retains:

```text
xy !=_H yx.
```

## 4. Projection-local law theorem

When a projection declares target structure `S`, the laws registered for `S` are binding on admitted values in that projection.

This gives a two-direction discipline:

```text
native HARMONICODE cannot ignore a law it claims to preserve in a projection;
projection-local law cannot silently redefine native state outside the projection.
```

A failed rational-field projection is a real failure of the rational projection claim. It is not automatically a failure of a distinct native relation unless the contract claims equivalence/isomorphism.

## 5. Conservative projection criterion

A conventional projection is conservative over a declared subdomain `D` when every expression in the declared conventional language has the same result under:

```text
native evaluation -> projection
```

and:

```text
direct evaluation in the declared conventional structure.
```

Formally, for conventional operation `f_S` and native lift `f_H`:

```text
pi(f_H(h1,...,hn)) = f_S(pi(h1),...,pi(hn))
```

for every admitted tuple in `D`.

A counterexample falsifies the claimed conservative projection on that domain.

## 6. Native identity criterion

Native identity SHALL include all fields designated semantically active by the type. Depending on the type, these may include:

```text
value
ordered operands
phase orientation
position
cell/address
parent/predecessor
constraint frontier
transition identity
receipt lineage
reconstruction witness
```

Discarded fields cannot later be inferred merely because a lower-dimensional value matches.

## 7. HARMONICODE and conventional notation

Familiar symbols are lexical conveniences until typed.

For example:

```text
0^-1
xy
u^72
0 = 1
```

cannot be evaluated correctly from glyph recognition alone. The parser must determine whether the expression denotes a scalar reciprocal, ordered phase product, closure operator, residue/unit identification, or another registered type.

This is not immunity from criticism. It is the ordinary formal requirement that an operator be evaluated according to its definition.

## 8. Machine correspondence

The merged VM81 kernel supplies an executable boundary:

```text
native typed relation
→ exact ABI
→ VM81 candidate/admission
→ Hash72 transition/receipt
→ Hash216 indexed transition.
```

x86_64 remains byte-compatible ingress/egress but is a machine projection/transport surface, not the foundational HARMONICODE semantics.

## 9. Falsification obligations

The framework is falsified in the relevant scope by evidence such as:

- no model for a declared universally satisfiable constraint set;
- invalid derivation from registered axioms;
- failure of a projection preservation law;
- a collision under a projection claimed injective;
- failed round-trip under a projection claimed reversible;
- disagreement between formal rule and ABI/VM81 execution;
- nondeterministic canonical successor for identical admitted inputs;
- unauthorized projection-local law leaking into native authority;
- an external empirical correspondence failing its declared evidence test.

## 10. Conclusion

The epistemological boundary is not `HARMONICODE versus STEM`. It is an authority ordering:

```text
shared first principles
→ native HARMONICODE state algebra
→ explicit projection surfaces.
```

Conventional STEM remains fully usable and falsifiable inside the surfaces HARMONICODE claims to reproduce. It is not automatically the source semantics for every native HARMONICODE operator.
