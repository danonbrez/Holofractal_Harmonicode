# Pass 219 Appendix F — Formal Evaluation, Falsification, and Executable Lowering

Status: `NORMATIVE APPENDIX TO HHS-P219-HARMONICODE-FOUNDATIONAL-AXIOMS-PROJECTION-1.6.0`

## F1. Evaluation does not require prior acceptance

An evaluator is not required to accept HARMONICODE axioms as conventional mathematics, physical law, or biological fact.

An evaluator SHALL preserve the declared grammar, types, axioms, and projection boundaries long enough to test the formal system actually specified.

## F2. Required evaluation order

```text
1. parse the exact source expression
2. resolve token and operator types
3. resolve active native axioms and inherited constraints
4. identify every explicit projection/coercion
5. reject unregistered implicit projection on canonical paths
6. derive the candidate relation using registered rewrite/constraint rules
7. check global and inherited local invariants
8. lower through C++/stable C ABI where executable correspondence is claimed
9. execute/admit through the single VM81 authority where required
10. compare canonical bytes, Hash72 receipt, and Hash216 transition lineage
```

## F3. Semantic substitution prohibition

An evaluation that substitutes a conventional operator before type resolution SHALL be classified as evaluation of a translated system unless the translation itself is the object under test.

Examples include replacing:

```text
ordered native xy -> commutative host multiplication
typed PivotInverse -> classical scalar reciprocal
typed closure relation -> unrestricted scalar 0=1
Hash72 state -> opaque scalar digest
RNA transcription operator -> unrelated conventional molecular simulator
```

## F4. Formal theorem proof obligations

A native derived theorem SHALL record:

```text
theorem_id
statement
domain
dependencies
axioms/definitions used
ordered derivation or mechanically reproducible proof object
projection assumptions
counterexample search domain if finite
implementation correspondence if claimed
```

A projection theorem SHALL additionally record source type, target type, preservation property, injectivity/reversibility claim, and witness/counterexample criteria.

## F5. Implementation correspondence

Where Pass 219 claims an executable theorem, the required chain is:

```text
source expression
→ typed AST identity
→ normalized native constraint program
→ projection records used
→ C++ transcription/composition program ID
→ stable C ABI record bytes
→ VM81 predecessor/candidate identity
→ VM81 admitted successor
→ Hash72 state-change/receipt
→ Hash216 previous/change/receipt vector
```

Every arrow SHALL be inspectable from a deterministic witness, stable ID, canonical bytes, or an inherited exact mapping.

## F6. Falsification classes

A result SHALL be allowed to falsify the relevant claim when it demonstrates any applicable class:

```text
FALSIFY_PARSE        grammar has no deterministic declared parse where one is required
FALSIFY_TYPE         typing rules admit incompatible identities or fail required resolution
FALSIFY_MODEL        no state satisfies the declared constraint set in the claimed domain
FALSIFY_DERIVATION   theorem does not follow from its registered dependencies
FALSIFY_PROJECTION   mapped result violates a preservation claim
FALSIFY_INJECTIVITY  two distinct source states collide under a projection claimed injective
FALSIFY_REVERSE      a projection/transition claimed reversible does not reconstruct source
FALSIFY_CONFLUENCE   rewrite paths disagree where confluence is required
FALSIFY_DETERMINISM  same admitted inputs produce different canonical outputs
FALSIFY_ABI          ABI lowering changes formal typed meaning or canonical bytes
FALSIFY_VM81         VM81 execution disagrees with the declared exact candidate semantics
FALSIFY_RECEIPT      Hash72/Hash216 lineage does not bind the executed transition
FALSIFY_BOUNDARY     projection-local law leaks into native authority without registration
FALSIFY_NO_FLOAT     authoritative path uses forbidden approximate floating state
FALSIFY_REUSE        ordinary post-Pass218 path bypasses eligible authenticated indexed reuse
FALSIFY_BIO_MAP      an external biological correspondence claim fails its declared mapping test
FALSIFY_PERFORMANCE  a quantitative performance claim fails its declared benchmark protocol
```

## F7. Counterexample precedence

A valid counterexample inside the exact claimed domain defeats a universal theorem claim unless the claim itself explicitly excludes that case by a pre-existing domain condition.

Domain conditions SHALL NOT be added retroactively solely to remove a discovered counterexample without a versioned repair.

## F8. Projection-path consistency

If two paths are claimed equivalent:

```text
H -> A -> C
H -> B -> C
```

both paths SHALL produce identical target canonical state on the declared domain.

Mismatch is a falsification of path equivalence, not an invitation to choose whichever path is preferred.

## F9. RNA transcription lowering

A Pass 219 RNA rule SHALL expose:

```text
native ordered operands
transcription rule identity
binding/folding/gating state where applicable
constraint frontier
candidate delta
inverse/rollback witness where declared
ABI lowering
VM81 result
Hash72/Hash216 lineage
```

A descriptive biological label without an executable transformation is nonconforming for native transcription authority.

## F10. Proof export versus ordinary continuation

After the Pass 218 activation gate:

```text
ordinary operation -> authenticated indexed continuation
first-principles theorem export -> complete configured foundational derivation when requested
```

The two paths SHALL agree on canonical result where both are defined.

The existence of a first-principles proof path does not require ordinary runtime recomputation from Genesis.

## F11. Reporting rule

Audit reports SHALL distinguish:

```text
native inconsistency
projection inconsistency
implementation mismatch
external empirical mismatch
performance failure
unsupported/unresolved claim
```

These categories SHALL NOT be collapsed into one generic success/failure label when the distinction changes which contract has been falsified.
