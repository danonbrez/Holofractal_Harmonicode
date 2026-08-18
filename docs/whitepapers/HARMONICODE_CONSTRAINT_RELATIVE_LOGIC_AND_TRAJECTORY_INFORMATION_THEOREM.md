# HARMONICODE Constraint-Relative Logic and Trajectory Information Theorem

**Document class:** formal-system white paper  
**Theorem status:** native state/transition definitions + derived trajectory distinction theorem

## Abstract

HARMONICODE treats an evolving coupled transition as a first-class informational object. In profiles using `(P,s,f)`, information may be encoded in normalization/frame state `P`, internal tensor-phase state `s`, emitted substitution state `f`, and their ordered history. Apparent local contradiction is resolved only after type and active-constraint analysis; it is not admitted arbitrarily and is not rejected merely by surface-token opposition.

## 1. Coupled state

Define:

```text
Q_n = (P_n, s_n, f_n)
```

where the active profile assigns:

```text
P_n : integer normalization / address / frame / channel state
s_n : internal tensor-phase state
f_n : emitted substitution / external projection state.
```

The transition is:

```text
Gamma_n : Q_n -> Q_(n+1).
```

## 2. Constraint envelope

Let `I_G` be global invariants and `I_L` the inherited constraints active in layer `L`.

An admitted transition requires:

```text
I_G(Q_n,Gamma_n,Q_(n+1))
and
I_L(Q_n,Gamma_n,Q_(n+1)).
```

A symbolic equality chain can therefore serve as a constraint envelope defining admissible joint states rather than necessarily a request to replace every token with one untyped scalar value.

## 3. Constraint-relative contradiction classifier

Given a typed candidate containing locally opposed propositions or lanes, classify only after evaluating active constraints:

```text
FALSE                    if a required global/inherited invariant is violated
SUPERPOSED_ADMISSIBLE    if distinct typed lanes coexist without invariant violation
PHASE_OPPOSITION         if the type defines reciprocal/opposed phase ancestry
FOLD                     if opposition is resolved by a registered nesting/fold rule
MODULAR_PIVOT            if the state is a registered modular/closure pivot
UNRESOLVED               if closure/admission is not yet established.
```

This is a typed multi-valued state classifier, not a replacement for formal deduction. A state classified `FALSE` remains rejected.

## 4. Trajectory Distinction Theorem

### Statement

If state identity includes predecessor or transition lineage, equal instantaneous projection does not imply equal informational state.

Let histories `G1` and `G2` reach states with:

```text
pi_f(Q_1) = pi_f(Q_2)
```

but with distinct registered lineage:

```text
history(G1) != history(G2).
```

Then:

```text
(Q_1,history(G1)) !=_H (Q_2,history(G2)).
```

### Proof

Lineage is declared a semantically active field of the state type. Native identity requires equality of all semantically active fields. Since lineage differs, native states differ even though the selected projection is equal. QED.

## 5. Transition as carrier

A sequence:

```text
Q_0 -> Q_1 -> ... -> Q_n
```

may encode information through:

```text
selected P frames
internal s phase/tensor movement
emitted f substitutions
ordered operation classes
transition magnitudes
recurrence periods
branch/fold choices
Hash72/Hash216 receipts.
```

No single listed dimension is required to carry all information alone.

## 6. Hash216 correspondence

The inherited transition memory:

```text
(previous Hash72, change Hash72, receipt Hash72)
```

provides a natural executable witness for trajectory identity.

Pass 219 SHOULD bind `(P,s,f)` transition semantics to that inherited transition lineage instead of inventing a parallel history mechanism.

## 7. Deterministic reuse

Trajectory identity does not require recomputing all trajectory steps from Genesis after the trajectory is proven and authenticated.

After the Pass 218 gate:

```text
validated trajectory segment
→ Hash216-indexed authenticated predecessor
→ exact continuation.
```

First-principles replay remains available for proof export/audit where required.

## 8. Falsification

Claims in this model fail if:

- a transition admitted as valid violates a registered global/inherited invariant;
- two histories claimed distinct serialize to the same complete native identity without an explicit equivalence relation;
- a trajectory-dependent output changes when replayed from identical canonical predecessor and inputs;
- Hash216 lineage cannot reconstruct the claimed predecessor/change/receipt relation;
- an optimizer collapses history fields declared semantically active.
