# HHS Glossary

This glossary stabilizes the principal terms used across source code, pass contracts, receipts, runtime services, APIs, visual surfaces, and explanatory documentation.

## Admission

The governed act by which a proposed operation or state transition is accepted into canonical runtime state through VM81 and the applicable kernel gates.

## AuditedRunner

The exact runtime component that resolves registered operations, captures pre-state and post-state, derives witnesses, submits the transition to the kernel gate, and commits a locked or quarantined Hash72 receipt.

## Canonical

The representation or authority path that defines identity and state for HHS. A display value, provider result, local cache, GUI state, worker-local queue, or compatibility wrapper is not canonical merely because it exists.

## Canonicalization

Deterministic conversion of values into exact identity-bearing structures before commitment. Canonicalization preserves semantic distinctions such as exact fractions, list order, nesting, ordered products, phase tags, and identity-bearing lexical structure.

## Capability

A bounded permission or declared worker/provider ability used to determine which operations may be proposed, claimed, or executed. A capability does not independently confer mutation authority.

## Claim token

A Hash72 identity binding a Pass 190 job claim to the job, worker, attempt, claim time, lease, and preclaim state root.

## Closure

Completion of a transformation cycle under its governing relations. Closure restores required coherence while preserving the fact and lineage of the completed transformation.

## Constraint join

A typed relation that combines witnesses from different semantic domains without destructively coercing them into one untyped scalar equality.

## Contract

A normative repository document defining required behavior, inheritance, claim boundaries, implementation obligations, and validation conditions. Contract presence is distinct from implementation presence and implementation verification.

## Drift gate

An authority membrane that detects or blocks transitions that violate inherited invariants or permitted state movement.

## Dyadic level

The exact scale coordinate `level` in a state represented by `2^level`.

## Exact authority

Canonical computation performed with integers, rationals, symbolic roots, prime-exponent forms, tagged phases, ordered bytes, and other identity-preserving structures rather than silent floating-point replacement.

## Gate status

The admission result attached to a transition. Primary values are `LOCKED` and `QUARANTINED`.

## Harmonicode

The algebra-oriented HHS source and execution language connecting preserved source, typed expressions, exact arithmetic, macros, membrane structure, ordered transformations, VM81 admission, kernel audit, receipts, and replay.

## Hash72

The canonical active commitment and causal receipt authority for inputs, pre-states, operations, post-states, witnesses, programs, macros, expansions, claims, results, and parent-linked transition lineage.

## Hash216

The ordered identity, indexing, topology, historical evidence, and permanent object identity authority used across hydrated repository and runtime structures.

## Hydration

The process of discovering, binding, validating, and making repository objects or runtime state fully available through the canonical graph, operation registry, invariant envelope, authority path, receipts, replay, and user/machine surfaces.

## Ingress

The governed entry of external, provider-generated, uploaded, or transport-delivered data into HHS for parsing, policy evaluation, identity assignment, admission, and receipt commitment.

## Invariant

A relation that must remain preserved across an admitted transition. Core HHS invariants include `Δe = 0`, `Ψ = 0`, `Θ15 = true`, and `Ω = true`.

## LOCKED

A gate state indicating that a proposed transition satisfied the required authority, integrity, and invariant conditions and may enter canonical state.

## Macro

A named Harmonicode algebra transformation with parameters, preserved source, canonical definition identity, parameter bindings, nested expansion trace, and optional execution receipt.

## Manifold9

An inherited kernel authority surface used in applicable transitions for structural admission and invariant enforcement. It must not be bypassed when required by the governing pass or runtime path.

## Membrane

A nesting and scope boundary whose interior order, lexical structure, depth, semantic domain, and witness identity are preserved.

## Native ABI

The stable C-level callable boundary connecting exact HHS native operations to higher runtime layers. In Pass 190 Iteration 7, the inherited native ABI remains ten operations.

## Operation registry

The canonical collection of named operations, effects, schemas, capabilities, native/fallback availability, and Hash216 identities. Pass 190 Iteration 7 exposes 42 governed operations.

## Ordered product

A product or composition whose operand order may carry identity or semantics, such as `xy` and `yx`. Ordered products must not be silently collapsed into commutative equality.

## Parent receipt

The immediately preceding receipt identity named by a new receipt. Parent continuity forms the causal receipt chain.

## Pass

A numbered additive HHS development layer containing contracts, implementation, tests, receipts, evidence, manifests, deployment or interface surfaces, and inherited authority.

## Phase

A discrete or symbolic orientation coordinate carried by a state or transition. In the dyadic–quartic explanatory model, the quartic phase belongs to `Z/4Z`.

## PhaseState

A pair `(dyadic_level, quartic_phase) ∈ Z × Z/4Z` used by the dyadic–quartic explanatory formalization.

## Proposal

A requested or generated operation, state patch, model output, artifact, or transition that has not yet completed the HHS authority path.

## Provider

An external or local capability service, including a language model, that can generate results or proposals. A provider is not the canonical HHS mutation authority.

## QUARANTINED

A gate state indicating that an attempted operation is preserved as evidence but is blocked from authoritative mutation.

## Receipt

A parent-linked committed transition record binding input, pre-state, operation, post-state, witness, phase/tick, integrity, result status, and reason.

## Replay

Deterministic reconstruction and verification of execution from receipts, parent linkage, witnesses, and expected chain identity. Replay is a canonical execution property, not merely debugging.

## Restart record

A repository-visible handoff artifact recording base commit, branch or merge target, changed files, executed commands, validations completed and remaining, environment state, blockers, and next action.

## Runtime controller

The Python/native coordination layer that owns deterministic stepping, lifecycle, session state, and ABI mediation while preserving the audited authority path.

## State patch

An explicit bounded representation of a proposed state mutation. Direct invisible mutation is prohibited.

## State root

A canonical commitment to the complete authoritative state at a transition boundary.

## Symbolic normalization

The conversion of preserved source into a deterministic symbolic representation without erasing identity-bearing order, membranes, values, or source distinctions.

## U72

The 72-position HHS phase wheel. Offset `36` is the discrete half-turn.

## VM81

The semantic execution, admission, and authoritative state-transition substrate. VM81 remains the singleton mutation authority across native, API, SDK, worker, assistant, and visual surfaces.

## Witness

Structured evidence describing what was evaluated, which conditions were checked, and why a transition was locked or quarantined.

## Worker

A restartable Pass 190 execution process that heartbeats, participates in scheduling, claims eligible jobs, and executes registered pure operations. Worker-local memory, queues, timers, and files are not canonical authority.
