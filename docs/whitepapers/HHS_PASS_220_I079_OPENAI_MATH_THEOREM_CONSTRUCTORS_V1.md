# HHS Pass 220 I079 — OpenAI Mathematics Formal-Theorem Constructors

## Result

I079 closes the constructor gap identified by I078 for the formalized novelty
frontier.

All **54 / 54** formalized novelty sources now have distinct callable,
source-bound HHS theorem constructors. The registry binds **57**
Lean proof surfaces and has **zero unresolved proof-surface bindings**.

The frozen pre-I078 HHS tree was audited for exact dedicated constructor paths
using normalized source slugs and comparator stems. It contained **zero**
dedicated source-specific constructor matches for these 54 sources, so I079
creates 54 new constructor identities rather than silently aliasing them to
unrelated generic operators.

## Constructor contract

Each constructor preserves:

```text
immutable openai/math revision
+ source preprint tree identity
+ result-family identity
+ ComparatorChallenge contract
+ admitted Lean declaration
+ implementation Lean file
+ opaque typed theorem-assumption binding
-> deterministic HHS theorem invocation capsule
-> candidate Hash72 receipt + deterministic replay
```

The external Lean proposition remains the observable theorem contract. HHS may
later lower or optimize the internal representation, but the source proposition
and proof-declaration identity may not be weakened, reordered, or substituted.

This is deliberately stronger than creating a label or title node: each of the
54 entries has a callable constructor surface and at least one admitted formal
proof declaration.

## What the constructor does not claim

I079 does not pretend that wrapping a Lean theorem is a new independent proof.
The pinned external formalization remains the proof provenance authority. The
runtime binds and instantiates the theorem contract inside HHS and gives it
deterministic identity/replay.

```text
external_proof_rechecked_at_runtime = false
truth_promotion                     = false
canonical VM81 mutation             = false
canonical Hash72/Hash216 minting    = false
canonical persistence               = false
```

A later native algebraic lowering is permitted, but it must preserve the same
input/output theorem contract and provenance.

## Callable runtime

`hhs_runtime/hhs_pass220_i079_openai_math_theorem_constructors_v1.py`

exports:

```text
list_constructors()
get_constructor(constructor_id)
build_registry_receipt()
invoke_constructor(constructor_id, assumption_binding, proof_declaration)
```

`invoke_constructor` validates the requested proof declaration against the
source-bound allowlist, hashes the opaque assumption binding, binds the exact
source and proof identities, emits a 72-symbol candidate receipt, independently
replays the same frame, and fails closed on mismatch.

## Coverage

- Formalized novelty sources: 54.
- New source-bound constructors: 54.
- Lean proof surfaces bound: 57.
- Unresolved proof surfaces: 0.
- Preexisting dedicated source-bound matches in the frozen pre-I078 tree: 0.

Constructor domain participation:

- Analysis: 20
- Combinatorics: 10
- Geometry: 7
- Probability: 4
- NumberTheory: 2
- AlgebraicGeometry: 2
- Computability: 2
- Algebra: 1
- MeasureTheory: 1
- LinearAlgebra: 1
- RepresentationTheory: 1
- ModelTheory: 1
- GroupTheory: 1
- Topology: 1
- CategoryTheory: 1

## Relationship to existing HHS primitives

These are theorem-level constructors. They may reuse existing exact rational,
matrix, tensor, graph, probability, geometry, operator-algebra, or other HHS
primitives where compatible. Structural reuse does not collapse theorem
identity: a Euclidean-Ramsey constructor, a Falconer constructor, a
Deligne-Drinfeld constructor, and so on remain distinct source-bound objects
even when some lower-level operations already exist.

## Authority

The entire registry remains candidate-only. No constructor can self-promote an
external result to canonical truth, update model weights, mutate VM81, mint
canonical Hash72/Hash216, persist canonical state, or acquire floating-point
authority.
