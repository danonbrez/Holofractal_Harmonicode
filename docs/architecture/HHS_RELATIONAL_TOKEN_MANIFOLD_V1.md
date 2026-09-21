# HHS Relational Token Manifold v1

## Purpose

This Pass 219 surface formalizes the HARMONICODE synthesis as **both-and
relational tokenization**, not as an either-or reduction from human meaning to a
single machine identifier.

For a human, the same admitted object may remain language, mathematics, code,
data, geometry, logic, and knowledge simultaneously.

For the machine, those surfaces expose deterministic mathematical relations over
an exact character/string substrate.

```text
human semantic multiplicity
        <=>
exact source character/string identity
        <=>
relational metadata
        <=>
shared knowledge-graph topology
        <=>
machine mathematical projection
```

No arrow means that one representation deletes or replaces another.

## Canonical token law

A conventional token-to-ID mapping is insufficient for this layer.

The reference runtime binds each Unicode character to a relational object carrying:

- exact character identity;
- Unicode codepoint;
- exact UTF-8 bytes;
- exact UTF-8 BigInt projection;
- Lo Shu row/column/value address;
- prime-modular residue fingerprint;
- recursive containment path;
- bounded left/right context;
- explicit surface-role set;
- shared graph edges;
- source identity and provenance hash.

The character remains the character. The machine metadata is an additional
mathematical projection of that same source object.

## Human/machine asymmetry

```text
Human:
    language AND logic AND code AND geometry AND data AND mathematics

Machine:
    exact integer/string relations over the same admitted source state
```

This does not define language as "only numbers." It defines the runtime
representation of language as mathematically manipulable character/string state
while preserving the original human-readable source.

## Character-string meta-analysis at scale

For a source string

```text
S = c_0 c_1 ... c_(n-1)
```

the v1 runtime constructs one deterministic relational object per character.
Each character receives an index-dependent Lo Shu address and exact modular
residue fingerprint. Local context is preserved explicitly and Hash256-sealed.

The resulting graph includes at minimum:

```text
source --contains_character--> c_i
c_i   --previous_character--> c_(i-1)
c_i   --next_character------> c_(i+1)
```

Future semantic, symbolic, AST, JSON-containment, code-control-flow, tensor,
Hash72, Hash216, RNA, and Lane 5 relations are additive graph edges. They do not
require destroying the source-string identity.

## BigInt distinction

The reference implementation exposes an exact UTF-8 BigInt projection for each
character.

That field is **not** a silent replacement for the canonical HARMONICODE
fixed-width 5184-character BigInt serialization. The latter remains governed by
its inherited contract and may be attached as an additional projection when the
object reaches that admitted layer.

## No floating canonical metadata

The relational token reference surface uses only exact strings, booleans,
integers, arrays, and mappings. Floating-point metadata is rejected from
canonical serialization.

## Projection and hydration invariant

For every accepted source string:

```text
hydrate(tokenize(S)) == S
```

and the source SHA-256 must remain identical after hydration.

The contract therefore distinguishes:

```text
source identity
projection identity
context identity
knowledge-graph relation
semantic relation
canonical runtime authority
```

rather than conflating them.

## Authority boundary

This layer is relational metadata and graph projection. It does not mint:

- canonical VM81 mutation;
- canonical Hash72 receipts;
- canonical Hash216 lineage;
- independent canonical persistence authority.

Its output may feed Lane 5 candidate composition under the existing admission
chain.

## Optimization consequence

Because token identity, context, geometry, modular fingerprint, and graph
relations are explicit rather than reconstructed ad hoc at every consumer, the
same relational metadata can be reused across compatible modalities and
high-level language surfaces.

Under the existing Pass 219 multimodal optimization rule, optimizations over
this metadata are generalization candidates across compatible consumers rather
than isolated one-off accelerations.
