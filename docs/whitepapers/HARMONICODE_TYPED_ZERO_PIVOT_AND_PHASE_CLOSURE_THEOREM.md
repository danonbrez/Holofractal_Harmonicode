# HARMONICODE Typed Zero-Pivot and Phase-Closure Theorem

**Document class:** formal-system white paper  
**Theorem status:** native definitions + derived type-separation theorem  
**Scope:** HARMONICODE zero/pivot/closure semantics

## Abstract

HARMONICODE distinguishes ordinary scalar zero from modular residue, a typed phase pivot, terminal closure residue, and renewed unit state. This allows a profile to define a zero-pivot phase operation and a completed `u^72` residue/unit closure relation without asserting unrestricted scalar `0=1` or pretending that classical field division by zero has acquired an ordinary finite inverse.

## 1. Type declarations

Let:

```text
Z_s = ScalarZero
R_0(M) = ModularZeroResidue(M)
P_0(L,o) = PhasePivotZero(layer=L, orientation=o)
C_0(N) = ClosureResidue(period=N)
U_1(N) = RenewedUnit(period=N).
```

These are distinct typed states unless an explicit relation says otherwise.

## 2. Scalar separation axiom

On the ordinary scalar projection:

```text
0_scalar != 1_scalar.
```

This preserves the standard scalar boundary wherever HARMONICODE declares that projection.

## 3. Pivot inverse definition

For a registered layer `L`, define:

```text
PivotInverse(P_0(L,o)) = PhaseRotate_M_to_I(P_0(L,o),o).
```

Surface syntax MAY write the pivot operation as `0^-1` after type resolution.

It is not the ordinary field reciprocal operator.

## 4. Type-Separation Theorem

### Statement

The existence of `PivotInverse(P_0)` does not imply a scalar `q` satisfying:

```text
0_scalar * q = 1_scalar.
```

### Proof

`PivotInverse` has a phase-transition codomain, while field inversion has a scalar codomain and carries a multiplicative inverse obligation. Since the operators have different types and laws, the field inverse rule cannot be applied without an explicit coercion from phase state to scalar inverse state. The ordinary scalar projection defines no such coercion. Therefore the phase operation does not entail scalar inversion. QED.

## 5. 72-phase closure definition

Where the native phase profile defines `u` with a 72-step closure law:

```text
u^72 -> U_1(72).
```

The modular residue projection of the completed step count satisfies:

```text
72 mod 72 = 0.
```

The native closure witness may therefore bind two typed views of the same closure event:

```text
C_0(72) <-> U_1(72).
```

## 6. Closure Non-Collapse Theorem

### Statement

The typed closure relation:

```text
C_0(72) <-> U_1(72)
```

is compatible with:

```text
0_scalar != 1_scalar.
```

### Proof

The left relation equates or binds two typed representations of a closure event; the right compares elements of an ordinary scalar projection. No rule identifies `C_0(72)` with `0_scalar` and `U_1(72)` with `1_scalar` as unrestricted native identity. Therefore substitution across the type boundary is unavailable absent an explicit coercion. QED.

## 7. Orientation and reciprocal lanes

If a zero-pivot profile resolves into reciprocal phase branches, orientation is part of state identity. Conventional complex labels `+i` and `-i` may be used as projections of those branches, but a conventional label is not required to exhaust the native witness.

The native witness retains the ordered path through the pivot.

## 8. Unbounded carrier

A symbolic unbounded carrier or `ComplexInfinity` token SHALL remain symbolic and typed on authoritative paths. It is not a floating infinity value.

If a finite witness `chi_0` is registered, modular evaluation occurs only after an explicit projection:

```text
UnboundedCarrier --pi_chi0--> chi_0 --Mod_M--> residue.
```

This avoids the category error of applying a finite remainder operator directly to an unbounded symbolic carrier.

## 9. Executable correspondence

The formal zero-pivot operator is not complete as a runtime claim until its lowering is defined:

```text
typed pivot AST
→ exact phase transition record
→ exact ABI
→ VM81 operation/candidate
→ Hash72 receipt
→ Hash216 transition identity.
```

Where reversibility is claimed, reversing the admitted transition must reconstruct the source type, layer, orientation, and canonical state exactly.

## 10. Falsification

The profile fails if:

- ordinary scalar `0` and `1` collapse unintentionally;
- host division by zero is used as the implementation of `PivotInverse`;
- branch orientation is discarded;
- closure residue is admitted without the required closure witness;
- a float/NaN/infinity sentinel mutates canonical state;
- claimed reversible pivot transitions fail exact reconstruction;
- formal and VM81 results disagree.
