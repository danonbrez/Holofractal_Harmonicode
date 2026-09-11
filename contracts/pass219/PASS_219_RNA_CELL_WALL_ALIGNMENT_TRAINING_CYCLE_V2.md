# Pass 219 RNA Cell-Wall Alignment Training Cycle v2

Status: implementation contract
Date: 2026-09-11

## Purpose

Cycle 2 extends the validated Cycle 1 reverse-training membrane with typed four-plane alignment objectives while preserving the exact inherited learner and all prior authority boundaries.

The four objective planes are the existing Pass 218/219 authority planes:

```text
RELATIONAL_COGNITION
NARRATIVE_EXPRESSION
AGENTIC_ACTION
TRUTH_PROMOTION
```

This cycle does not create a second learner, a second transition authority, or a second canonical state path.

## Inherited execution relation

The only weight-mutating path remains:

```text
plane-typed bounded evidence
-> exact plane-local gate
-> admitted Cycle 1 evidence subset
-> reverse chronological traversal
-> inherited RNA/four-lane exact learner
-> changed dependency frontier
-> protected historical replay
-> candidate or protected-replay rejection
```

Cycle 2 delegates every admitted update to `RNACellWallAlignmentTrainer` from Cycle 1. It does not copy or reinterpret the four-lane update equations.

## Four independently gated objectives

All planes require:

```text
relation_type_preserved = true
provenance_preserved = true
```

The plane-local requirements are:

```text
RELATIONAL_COGNITION
    relation/provenance requirements only

NARRATIVE_EXPRESSION
    relation/provenance requirements
    + narrative_modality_preserved = true

AGENTIC_ACTION
    relation/provenance requirements
    + action_capability_authorized = true
    + action_validation_satisfied = true

TRUTH_PROMOTION
    relation/provenance requirements
    + truth_evidence_satisfied = true
    + truth_validator_satisfied = true
```

Permission on one plane does not imply permission on any other plane.

Therefore the same underlying relation may be:

```text
RELATIONAL_COGNITION admitted
NARRATIVE_EXPRESSION admitted
AGENTIC_ACTION held
TRUTH_PROMOTION held
```

without contradiction and without deleting the underlying relation.

## Held objectives

A plane-local gate failure produces a held training objective. Held objectives:

```text
do not mutate the candidate learner state
do not disappear from the Cycle 2 objective accounting
do not widen another authority plane
do not mint action authority
do not promote truth
do not change historical provenance
```

If all non-protected objectives are held, the exact baseline is returned with `NO_UPDATE_REQUIRED`.

## Protected replay precedence

Protected historical replay evidence is always retained for anti-forgetting comparison even when the same sample would be held as new training under the current plane gate.

Protected replay:

```text
never trains weights
compares frozen baseline outcome to candidate outcome
can reject the complete candidate
restores the exact baseline on rejection
```

This preserves Cycle 1's anti-forgetting contract across contextual plane changes.

## Determinism and evidence identity

Cycle 2 produces an exact `objective_signature64` over:

```text
sample order
plane identity
plane-gate bits
feedback lane/trinary
protected-replay role
Hash216 transition identity
inherited Cycle 1 training signature
admitted/held/protected counts
```

Identical baseline, evidence, plane typing, and gates must replay to identical candidate bytes and identical objective/training signatures.

The signature is execution evidence only. It is not a Hash72 or Hash216 authority surface.

## Authority boundary

Cycle 2 remains candidate-only:

```text
candidate_only = true
exact_integer_only = true
canonical_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
canonical_persistence_authority = false
floating_point_authority = false
```

VM81 remains the singleton canonical mutation/admission authority.

Plane gates classify whether training evidence may influence the candidate learner; they do not authorize canonical mutation, external action, factual promotion, or receipt minting.

## Required validation

The dedicated Cycle 2 gate must prove at minimum:

1. Cycle 1 and the inherited C/C++ four-lane/RNA surfaces remain green.
2. Relational and correctly modalized narrative objectives may train while unauthorized agentic and unvalidated truth objectives are held.
3. Unlocking only the agentic capability/validation gate admits the agentic objective.
4. Unlocking only the truth evidence/validator gate admits the truth objective.
5. The same relation can be admitted on cognition/narrative planes and held on action/truth planes.
6. Cycle 2 candidate bytes equal Cycle 1 over exactly the admitted objective subset.
7. Identical evidence/gates replay to identical candidate bytes and signatures.
8. Held-only evidence returns the exact baseline with no update.
9. Protected replay remains active even when current plane gates would hold new training.
10. Unknown plane identifiers fail closed.
11. No canonical VM81, Hash72, Hash216, persistence, or floating-point authority is introduced.

## Scope

This cycle implements deterministic four-plane training-objective gating over the bounded Cycle 1 learner. It does not claim that these four booleans exhaust the full future semantic payload of each authority plane, and it does not convert candidate training quality into canonical authority.
