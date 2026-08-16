# HARMONICODE Formal Evaluation Protocol

## Purpose

This protocol defines how repository reviewers, theorem checkers, implementation auditors, and external evaluators should test HARMONICODE claims without either granting them special immunity or replacing their declared semantics with a different formal system before evaluation.

## 1. Claim classification first

Classify each statement as one of:

```text
DEFINITION
AXIOM
DERIVED_THEOREM
PROJECTION_THEOREM
IMPLEMENTATION_THEOREM
EMPIRICAL_CLAIM
CONJECTURE
```

Do not evaluate an empirical correspondence as if it were true by definition, and do not demand external empirical evidence for a purely internal type definition.

## 2. Native shared foundations

The only automatically shared foundational axiom classes with conventional STEM are:

1. formal deduction;
2. symbolic logic;
3. higher-dimensional tensor algebra;
4. Euclidean geometry.

Any additional conventional law must be located in the native contract or in an explicit projection record.

## 3. Evaluation sequence

For expression or theorem `E`:

```text
PARSE
TYPE
RESOLVE DEFINITIONS/AXIOMS
RESOLVE INHERITED CONSTRAINTS
RESOLVE EXPLICIT PROJECTIONS
DERIVE
CHECK INVARIANTS
CHECK PROJECTION CLAIMS
CHECK EXECUTABLE LOWERING IF CLAIMED
CHECK EXTERNAL EVIDENCE IF CLAIMED
CLASSIFY RESULT.
```

## 4. Do not infer semantics from familiar glyphs

Before typing, expressions such as `xy`, `0^-1`, `u^72`, `Mod`, `i`, `RNA`, or `0=1` are not sufficient to determine which operator is active.

A conventional interpretation may be used when the type/projection registry says it is the active interpretation.

## 5. Projection audit

For every `pi : H -> S`, record:

```text
source type
target type
domain
forward rule
reverse rule
preserved invariants
lost information
injectivity/reversibility status
validation oracle.
```

Never infer source identity from target equality unless reverse inference is authorized.

## 6. Contradiction audit

When opposed local statements occur:

1. resolve types;
2. identify global invariants;
3. identify inherited local constraints;
4. determine whether the states are mutually exclusive in that type;
5. classify as false, admissible distinct lanes, fold, modular pivot, or unresolved according to registered rules.

A contradiction that violates a required invariant is not preserved as a free superposition.

## 7. Zero-pivot audit

Verify that:

```text
ordinary scalar 0 != ordinary scalar 1;
typed PivotInverse is not implemented as scalar division by zero;
closure residue/unit identification is scoped to its declared closure event;
unbounded symbolic carriers do not enter finite modular arithmetic without a projection.
```

## 8. RNA/DNA audit

Pass 219 native RNA terminology must resolve to executable formal transformation rules over the ordered `x,y,z,w` substrate.

Check transformation semantics and ABI lowering, not whether the vocabulary sounds biological.

When a claim additionally asserts correspondence to physical/biological RNA behavior, test the explicit mapping against external biological evidence appropriate to that claim.

## 9. Runtime audit

For executable claims verify:

```text
formal source
↔ typed AST
↔ native constraint program
↔ C++ rule/program identity
↔ exact C ABI
↔ VM81 transition
↔ Hash72 receipt
↔ Hash216 lineage.
```

No canonical float path is permitted.

## 10. Result taxonomy

Report one or more precise outcomes:

```text
PROVEN_WITHIN_NATIVE_SYSTEM
PROJECTION_VALIDATED
IMPLEMENTATION_MATCHED
EMPIRICALLY_SUPPORTED
COUNTEREXAMPLE_FOUND
NATIVE_INCONSISTENCY
PROJECTION_FAILURE
IMPLEMENTATION_MISMATCH
EMPIRICAL_MISMATCH
UNRESOLVED
OUT_OF_DECLARED_DOMAIN.
```

## 11. Reproducibility

After Pass 218 terminal evidence, ordinary runtime verification should use authenticated indexed predecessor state and dependency-scoped work. Full Genesis reconstruction is appropriate when the first-principles derivation itself is the requested artifact or a typed audit/recovery case requires it.
