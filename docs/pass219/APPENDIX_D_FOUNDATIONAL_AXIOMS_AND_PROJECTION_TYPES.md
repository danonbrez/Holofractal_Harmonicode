# Pass 219 Appendix D — Foundational Axioms and Projection Types

Status: `NORMATIVE APPENDIX TO HHS-P219-HARMONICODE-FOUNDATIONAL-AXIOMS-PROJECTION-1.6.0`

## D1. Native authority model

Let `H` be the typed native HARMONICODE state domain admitted by the active contract.

The automatically shared first-principles foundation is limited to four axiom classes:

```text
A_D  formal deduction
A_L  symbolic logic
A_T  higher-dimensional tensor algebra
A_E  Euclidean geometry
```

No conventional downstream formalism is automatically inherited in full.

## D2. Projection record

Every canonical projection SHALL be representable by a versioned record logically equivalent to:

```text
ProjectionRecord {
  projection_id
  version
  source_type
  target_type
  domain_predicate
  forward_rule
  reverse_rule_or_none
  preserved_invariants[]
  intentionally_lost_fields[]
  injectivity_class
  reversibility_class
  canonical_serialization
  validation_oracle
}
```

Required injectivity classes:

```text
UNKNOWN
NON_INJECTIVE
INJECTIVE_ON_DOMAIN
BIJECTIVE_ON_DOMAIN
ISOMORPHISM_ON_DOMAIN
```

Required reversibility classes:

```text
FORWARD_ONLY
PARTIAL_RECONSTRUCTION
EXACT_WITH_WITNESS
EXACT_WITHOUT_AUXILIARY_WITNESS
```

## D3. Native equality and projected equality

Native identity is typed:

```text
a ==_H b
```

Projected equality is:

```text
pi_k(a) ==_(S_k) pi_k(b).
```

The inference:

```text
pi_k(a) == pi_k(b) -> a ==_H b
```

is forbidden unless the active `ProjectionRecord` authorizes the reverse implication for `a,b` in its domain.

## D4. Examples of distinct 5,184 projections

The inherited exact cardinalities include:

```text
VM81:   81 × 64 = 5,184
Hash72: 72 × 72 = 5,184
```

These typed coordinate systems MAY be bridged by explicit reversible maps where defined.

They are not semantically interchangeable merely because both contain 5,184 addresses.

A conforming type system SHALL be able to distinguish at least:

```text
VM81CellOperationCoord(cell81, operation64)
Hash72PositionCoord(position72, glyph_or_position72)
HydrationSlot5184(slot)
```

## D5. Conventional scalar projection

An ordinary scalar projection SHALL declare its conventional laws explicitly.

At minimum, an ordinary scalar boundary SHALL retain:

```text
0_scalar != 1_scalar.
```

A typed HARMONICODE closure relation SHALL not leak into this projection as unrestricted scalar equality.

## D6. Complex / phase projections

A conventional complex-number view and a native ordered phase view are distinct types.

A projection MAY map a native phase state onto `i`, `-i`, or another conventional complex representation. Such a mapping does not authorize replacement of the native state with the conventional complex scalar unless its projection record establishes exact equivalence for the active domain.

## D7. Modular projections

A modular residue view SHALL specify:

```text
modulus
residue normalization
zero-residue typing
lift/reconstruction rule
```

A residue identity such as `72 mod 72 = 0` does not by itself define the native meaning of a completed phase closure. The phase-closure relation requires its registered native witness.

## D8. Biological projections

Pass 219 native RNA/DNA algebra is governed by amendment 1.5.0.

Conventional biological representations SHALL be explicit projections or compatibility adapters where used, including conventional nucleotide alphabets, sequence file formats, biochemical labels, or Boolean molecular-circuit abstractions.

A biological projection SHALL state which relations it claims to preserve. Failure of that correspondence is a valid failure of the projection claim; it does not rewrite the native algebra.

## D9. Machine projections

x86_64 bytecode ingress/egress is an inherited exact transport projection.

Byte equality proves byte equality. Native semantic identity requires the stronger witness declared by the active native projection/serialization contract.

Pass 175 decoding and Pass 186 SysV AMD64 mappings remain inherited compatibility authorities.

## D10. Projection composition

For projections:

```text
H --pi_a--> A --pi_b--> B
```

the composed projection is:

```text
pi_ba = pi_b o pi_a.
```

The composed projection SHALL inherit the weakest information-preservation class of the path unless a stronger property is separately proven.

A lossy intermediate projection prevents automatic reverse inference even if the final representation has the same cardinality as the source.

## D11. Commuting projection diagrams

When two projection paths are claimed equivalent:

```text
          pi_a
      H --------> A
      |            |
  pi_b|            |f
      v            v
      B -------->  C
          g
```

conformance requires:

```text
f(pi_a(h)) == g(pi_b(h))
```

for every `h` in the claimed domain.

If equality fails, the projection-equivalence claim is falsified for that witness.

## D12. Registry rule

Every projection that participates in authoritative Pass 219 lowering SHALL be registered before use. Unregistered implicit coercion is fail-closed.
