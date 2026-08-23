# HHS Glossary

This glossary stabilizes the principal terms used across source code, pass contracts, receipts, runtime services, APIs, visual surfaces, and explanatory documentation.

## Admission

The governed act by which a proposed operation or state transition is accepted into canonical runtime state through VM81 and the applicable kernel gates. Admission does not override foundational pre-pass state compatibility.

## AuditedRunner

The exact runtime component that resolves registered operations, captures pre-state and post-state, derives witnesses, submits the transition to the kernel gate, and commits a locked or quarantined Hash72 receipt.

## Canonical

The representation or authority path that defines identity and state for HHS. A display value, provider result, local cache, GUI state, worker-local queue, or compatibility wrapper is not canonical merely because it exists.

## Canonical raw state

The single underlying authoritative state to which all required authoritative representations or modalities must normalize at a closed transition boundary. Different formats may encode it differently; they may not define competing truths about it.

## Canonicalization

Deterministic conversion of values into exact identity-bearing structures before commitment. Canonicalization preserves semantic distinctions such as exact fractions, list order, nesting, ordered products, phase tags, and identity-bearing lexical structure.

## Capability

A bounded permission or declared worker/provider ability used to determine which operations may be proposed, claimed, or executed. A capability does not independently confer mutation authority.

## Claim token

A Hash72 identity binding a governed job claim to the job, worker, attempt, claim time, lease, and preclaim state root.

## Closed state

A state boundary at which all required foundational, representational, lineage, ordering, and applicable invariant relations agree. A candidate with unresolved required disagreement is not a partially closed authoritative state.

## Closure

Completion of a transformation cycle under its governing relations. Closure restores required coherence while preserving the fact and lineage of the completed transformation.

## Constraint join

A typed relation that combines witnesses from different semantic domains without destructively coercing them into one untyped scalar equality.

## Cross-format unanimity

The requirement that every required authoritative representation or modality normalize to the same canonical raw state. It is equality enforcement, not majority voting. Required disagreement blocks commitment and invokes the applicable rollback/recovery behavior.

## Contract

A normative repository document defining required behavior, inheritance, claim boundaries, implementation obligations, and validation conditions. Contract presence is distinct from implementation presence and implementation verification.

## Drift gate

An authority membrane that detects or blocks transitions that violate inherited invariants or permitted state movement.

## Dyadic level

The exact scale coordinate `level` in a state represented by `2^level`.

## Exact authority

Canonical computation performed with integers, rationals, symbolic roots, prime-exponent forms, tagged phases, ordered bytes, and other identity-preserving structures rather than silent floating-point replacement.

## Explicit security layer

The HHS mechanisms intentionally serving security functions such as hashing, signatures, authentication, capabilities, PQC/network profiles, isolation, receipts, and access/admission controls. This layer is distinct from the pre-pass kernel-protection/error-correction substrate even when both contribute to integrity or recovery.

## Gate status

The admission result attached to a transition. Primary values include `LOCKED` and `QUARANTINED`; inherited paths may also preserve corrected, recovered, rejected, or other explicit states.

## Genesis continuity

The exact ancestry relation connecting a state or transition to its admitted Genesis/root history. Current validity may depend on predecessor and historical path, not only endpoint bytes.

## Harmonicode

The algebra-oriented HHS source and execution language connecting preserved source, typed expressions, exact arithmetic, macros, membrane structure, ordered transformations, VM81 admission, kernel audit, receipts, and replay.

## Hash72

The canonical active commitment and causal receipt mechanism for admitted HHS state transitions and their parent-linked lineage. Hash72 records/chains states that survived the applicable authority path; a Hash72-shaped value does not independently make a pre-pass-incompatible state valid.

## Hash216

The ordered identity, indexing, topology, historical evidence, and durable object/vector identity surface used across hydrated repository and runtime structures after valid Hash72 receipt closure. It does not originate foundational state validity or canonical mutation authority.

## Hydration

The process of discovering, binding, validating, and making repository objects or runtime state fully available through the canonical graph, operation registry, invariant envelope, authority path, receipts, replay, and user/machine surfaces.

## Ingress

The governed entry of external, provider-generated, uploaded, or transport-delivered data into HHS for parsing, policy evaluation, identity assignment, admission, and receipt commitment.

## Invariant

A relation that must remain preserved across an admitted transition. Core HHS invariants include `Δe = 0`, `Ψ = 0`, `Θ15 = true`, and `Ω = true`.

## Kernel protection

The foundational preservation of valid kernel state continuity. In HHS this includes pre-pass path-, time-, modality-, ordering-, correction-, and representation-dependent behavior. It is broader than and architecturally distinct from the explicit security layer.

## Local-purpose/global-role distinction

The rule that a module's apparent isolated purpose, directory, filename, or immediate output does not determine its complete system role. A small error-correction, prediction, normalization, cache, timing, algebra, or reconstruction module may participate in a larger path-dependent state relation.

## LOCKED

A gate state indicating that a proposed transition satisfied the required authority, integrity, and invariant conditions and may enter canonical state.

## Macro

A named Harmonicode algebra transformation with parameters, preserved source, canonical definition identity, parameter bindings, nested expansion trace, and optional execution receipt.

## Manifold9

An inherited kernel authority surface used in applicable transitions for structural admission and invariant enforcement. It must not be bypassed when required by the governing pass or runtime path.

## Membrane

A nesting and scope boundary whose interior order, lexical structure, depth, semantic domain, and witness identity are preserved.

## Native ABI

The stable C-level callable boundary connecting exact HHS native operations to higher runtime layers. The current cumulative Pass 219 work extends inherited ABI exposure without making the ABI a second mutation authority.

## Operation registry

The canonical collection of named operations, effects, schemas, capabilities, implementation availability, identities, and authority bindings exposed by the cumulative system. Historical pass-specific counts remain evidence for those pass checkpoints rather than a permanent system-wide cardinality.

## Ordered product

A product or composition whose operand order may carry identity or semantics, such as `xy` and `yx`. Ordered products must not be silently collapsed into commutative equality.

## Parent receipt

The immediately preceding receipt identity named by a new receipt. Parent continuity forms the causal receipt chain.

## Pass

A numbered additive HHS development layer containing contracts, implementation, tests, receipts, evidence, manifests, deployment or interface surfaces, and inherited authority. The pre-pass foundation is not a numbered pass.

## Path-specific state relation

A state relation whose meaning depends on the history, ordering, modality, temporal position, predecessor, or other contextual coordinates by which the state was reached. Local endpoint equality alone does not prove path-specific equivalence.

## Phase

A discrete or symbolic orientation coordinate carried by a state or transition. In the dyadic–quartic explanatory model, the quartic phase belongs to `Z/4Z`.

## PhaseState

A pair `(dyadic_level, quartic_phase) ∈ Z × Z/4Z` used by the dyadic–quartic explanatory formalization.

## Pre-pass foundation

The HHS state-change and kernel-protection environment that predates Pass 001. It is not Pass 000 and is not owned by a later pass. It includes the inherited path-specific multimodal/error-correction behavior that constrains what kernel transitions can become canonical.

## Pre-pass state-change constitution

The system-wide rule that numbered passes, optimizers, agents, and interfaces may propose or accelerate candidate computation but may not redefine the foundational conditions under which raw state, history, ordering, modalities, and correction relationships form a valid kernel transition.

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

## Rollback

Rejection of an invalid candidate followed by retention or restoration of a previously fully closed state. At the pre-pass boundary, rollback is normal state-machine behavior when required representations or relations disagree; it is not limited to administrative disaster recovery.

## Runtime controller

The Python/native coordination layer that owns deterministic stepping, lifecycle, session state, and ABI mediation while preserving the audited authority path. It does not define the pre-pass state-validity law.

## State patch

An explicit bounded representation of a proposed state mutation. Direct invisible mutation is prohibited.

## State root

A canonical commitment to the complete authoritative state at a transition boundary.

## Symbolic normalization

The conversion of preserved source into a deterministic symbolic representation without erasing identity-bearing order, membranes, values, or source distinctions.

## Temporal validity

The property that a state transition, witness, lease, or relation is valid only in the exact applicable temporal/epoch context defined by the runtime. System-wide documentation does not publish private timing constants or transition sequences.

## U72

The 72-position HHS phase wheel. Offset `36` is the discrete half-turn.

## VM81

The semantic execution, admission, and authoritative state-transition substrate. VM81 remains the singleton mutation authority across native, API, SDK, worker, assistant, and visual surfaces, while inheriting the pre-pass state-change compatibility boundary beneath the numbered pass system.

## Witness

Structured evidence describing what was evaluated, which conditions were checked, and why a transition was locked, corrected, recovered, rejected, or quarantined.

## Worker

A restartable execution process that participates in governed scheduling and candidate work. Worker-local memory, queues, timers, and files are not canonical authority.
