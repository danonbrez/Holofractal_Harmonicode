# HHS Pass 220 I080 — HOLD Claim Constructors for the Remaining OpenAI Math Novelty Frontier

## Closure target

I080 applies the constructor rule to every I078 novelty manuscript that was not
covered by the 54 I079 source-bound formal theorem constructors.

The partition is now exact:

```text
I078 novelty manuscripts             = 322
I079 formal theorem constructors     =  54
I080 HOLD claim constructors         = 268
constructor coverage gap             =   0
duplicate assignment                 =   0
```

Thus every manuscript in the currently frozen novelty frontier has a callable
HHS constructor.

## Why these 268 are HOLD constructors

The pinned OpenAI formalization catalogue does not expose a catalogued
main-result proof surface for these manuscript identities. That does not mean a
claim is false, nor does it assert that no Lean artifact can exist elsewhere in
the repository. It means I080 does not have the proof surface required to grant
the constructor theorem authority.

Each source therefore receives:

```text
HHS_SOURCE_BOUND_UNVERIFIED_CLAIM_CONSTRUCTOR_V1
status = HOLD_NO_CATALOGUED_MAIN_RESULT_PROOF
```

The constructor binds the immutable release revision, preprint tree SHA, family,
source title, source slug, date, and opaque typed claim metadata. Invocation
produces a deterministic candidate Hash72 receipt and replay capsule.

It explicitly cannot emit a theorem witness.

## Upgrade paths

A HOLD constructor can be promoted only through one of two source-preserving
paths:

1. a catalogued external Lean proof surface whose theorem statement is bound to
   the same source identity; or
2. an independent HHS proof closure that proves the source theorem under an
   exact typed statement and dependency lineage.

Both paths require source identity, theorem-statement identity, dependency
identity, deterministic replay, and preservation of the external observable
contract.

## Full frontier invariant

The runtime loads the frozen I078 and I079 registries and proves the set
partition directly:

```text
I079.source_slugs ∩ I080.source_slugs = {}
I079.source_slugs ∪ I080.source_slugs
    = I078.NOVELTY_CANDIDATE manuscript slugs
```

Any missing source, duplicate assignment, or scope drift fails closed.

## Callable surface

`hhs_runtime/hhs_pass220_i080_openai_math_hold_claim_constructors_v1.py`

exports:

```text
list_constructors()
get_constructor()
validate_frontier_coverage()
build_registry_receipt()
invoke_claim_constructor()
```

Attempting to request a theorem witness or inject a proof declaration into a
HOLD constructor is a hard failure.

## Authority

I080 grants provenance and constructor identity only. It grants no theorem
truth, proof, execution, VM81 mutation, canonical Hash72/Hash216, persistence,
model-weight mutation, learning commit, or floating-point authority.
