# HHS Canonical Runtime Architecture

This document defines the current repository topology, execution authority, ownership boundaries, compatibility law, and anti-drift rules for the Holofractal Harmonicode System.

Normative companions:

- [`docs/architecture/HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION.md`](docs/architecture/HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION.md) — pre-pass state-change and kernel-protection foundation;
- [`docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md`](docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md) — cumulative single-authority and plug-in compatibility rules.

## 1. Cumulative system boundary

HHS existed before the numbered pass sequence. Every compatible pass is an additive in-place upgrade to one inherited system image.

```text
pre-pass HHS foundation
+ all compatible pass implementations
+ all validated repairs and integrations
= one cumulative HHS runtime
```

The pre-pass foundation is not Pass 000 and is not owned by any later numbered pass. Pass directories, release bundles, evidence packages, contracts, and restart records preserve development and validation boundaries. They do not define independent runtimes, products, kernels, registries, or authorities.

Architecture documentation must distinguish pre-pass foundation, pass contract authorization, implementation presence, test evidence, deployment evidence, and authoritative-main closure.

## 2. Governing invariants

All canonical computation must preserve the applicable inherited invariants, including:

```text
Δe = 0
Ψ = 0
Θ15 = true
Ω = true
xy = 1
A = P² = B
AB = P⁴
Δ = P² - pq
O != π
```

Additional binding rules:

- canonical kernel arithmetic is exact;
- floating-point values may be noncanonical display, timing, benchmark, calibration, graphics, or foreign-format witnesses only;
- ordered products, lists, bytes, phases, source spans, leading zeros, widths, grouping, and membranes retain identity;
- every canonical mutation is explicit, bounded, admitted, receipt-bound, and replay-verifiable;
- no model, API, GUI, worker, cache, database, provider, compatibility shim, or pass-scoped service becomes an alternate mutation authority;
- no numbered pass may redefine the pre-pass conditions for a valid kernel state transition.

## 3. One computational authority

HHS is plural in computation and singular in authority.

```text
many modules
many agents
many mathematical modalities
many branch trees
many cached continuations
many candidate workers
many user and machine interfaces
                ↓
one VM81/kernel admission and commit authority
```

Distributed exploration does not imply distributed truth.

A module may own a transformation method, representation, workflow, validation modality, device model, interface, or candidate-producing agent. It does not own canonical state.

The system permits parallel immutable candidate calculation. It does not permit parallel canonical mutation authorities or independent receipt clocks.

## 4. Pre-pass state-change and kernel-protection boundary

The deepest state-change protection predates the numbered pass system. It is not accurately described as one explicit security package.

The pre-pass environment combines locally narrow modules whose collective behavior provides:

- kernel protection;
- error correction and recovery;
- path-specific state continuity;
- multiple independent representation checks;
- time/epoch-sensitive state relationships;
- ordered and noncommutative transition constraints;
- lightweight prediction, lookup, reuse, or machine-learning optimization;
- automatic rollback when required representations or relations disagree.

The local modules may appear unrelated when inspected in isolation. Their global role is relational:

```text
LOCAL PURPOSE != GLOBAL SYSTEM ROLE
FILE ORGANIZATION != PROTECTION TOPOLOGY
```

The exact file-to-role map, correction topology, internal sequence, and timing constants are not specified in this overview. The normative interpretation is defined in `HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION_V1`.

## 5. Cross-format unanimity and rollback

Multiple authoritative representations may encode or project the same raw state. They may differ in format, algebra, topology, or execution method, but they may not establish competing truths.

For canonical raw state `R_n`:

```text
for every required authoritative modality m:
Normalize_m(View_m) = R_n
```

This is exact cross-format closure, not majority voting.

```text
required modality disagreement
→ closure failure
→ no canonical commit
→ retain or restore the last fully closed state
```

No mode, backend, pass, model, cache, accelerator, or interface may continue canonical execution by preferring one disagreeing required representation over another.

## 6. Explicit cryptographic security is a separate layer

HHS also contains explicit security mechanisms: hashing, signatures, capabilities, PQC/network profiles, authentication, isolation, receipts, and admission controls. Those are real security mechanisms and remain required where applicable.

They are not the same thing as the pre-pass kernel-protection/error-correction topology.

```text
EXPLICIT SECURITY / CRYPTOGRAPHY
!=
PRE-PASS KERNEL PROTECTION / ERROR CORRECTION
```

External callers submit bounded proposals. No public API may expose a path that bypasses either the applicable explicit security controls or the inherited state-change constraints.

Hash72 and Hash216 are not substitutes for the pre-pass foundation.

## 7. Python and local-module mesh

The Python layers are not the sole computational authority and are not a single wrapper around a small C application.

Across the historical and current system, Python modules may participate in exact symbolic and rational validation, tensor/manifold projection, multimodal reconstruction, error correction, recovery, timing/state tracking, prediction, caching, persistence, replay, lifecycle orchestration, provider admission, dependency scans, or test harnesses.

Some such modules are pass-era orchestration or exposure layers; some behavior is inherited from the pre-pass foundation. Documentation must not flatten those categories into one generic "Python security mesh."

A module that appears locally redundant may still participate in a path-, time-, modality-, or ordering-sensitive global relation. Refactors must therefore establish dependency-scoped equivalence before removal or collapse.

Python may harden, orchestrate, persist, test, translate, hydrate, optimize, or project the native authority. Python must not replace VM81/kernel mutation authority or redefine pre-pass validity.

## 8. Canonical transformation order

At system level, the authoritative relation is:

```text
candidate object or transformation
→ exact source / raw-state identity preservation
→ applicable pre-pass state-change compatibility and cross-format closure
→ private VM81/kernel admission and execution
→ applicable exact Harmonicode / invariant closure
→ LOCKED, CORRECTED, RECOVERED, REJECTED, or QUARANTINED decision
→ Hash72 receipt commitment for an admitted transition
```

Pass-level services may prepare, optimize, cache, rank, project, or validate candidates around this boundary. They do not redefine it.

Only a successfully admitted transformation may produce the canonical receipt block:

```text
(prev_hash72, state_hash72, receipt_hash72)
```

Hash72 records and chains an admitted transition. A Hash72-shaped value is not independently sufficient evidence of a valid state.

## 9. Hash216 begins after receipt closure

Hash216 archival and vector indexing occur only after the valid three-part Hash72 receipt block exists.

```text
prev_hash72
+ state_hash72
+ receipt_hash72
→ exact ordered 216-character block
→ character-addressed SHA-256 array
→ Hash216/vector index record
→ durable long-term storage
```

The storage layer must preserve every character position and the exact `prev, state, receipt` order. It must bind predecessor, state, transformation, dependency, replay, and recovery metadata.

Hash216 does not authorize the original transformation. It preserves, indexes, retrieves, relates, and hydrates completed proof.

A vector match is never permission to bypass current-context verification, dependency validation, pre-pass compatibility, singleton VM81 admission, or the ordered Hash72 commit.

## 10. Validated-computation cache and low-latency law

The Hash216 vector store and inherited continuation mechanisms support reusable validated computation.

A warm record may preserve exact source and machine bytes, decoder/compiler context, ordered operands and grouping, constraints, dependency roots, VM81 lowering, VM5184/G243 routes, test-vector identities, admission/rejection receipts, replay/rollback metadata, and retained native encoding.

A cache hit may eliminate redundant decoding, lowering, branch expansion, proof construction, and microcode generation. It may not eliminate foundational compatibility, admission, or commitment.

The optimization law is:

```text
DO NOT REMOVE INVARIANTS TO GET SPEED

REDUCE THE ACTIVE WORK REQUIRED
TO DEMONSTRATE THE SAME INVARIANTS
```

Thus very large global validity structure may coexist with bounded low-latency per-step work through exact caching, dependency-bounded recomputation, selective hydration, compiled representations, branch ranking, and reusable continuations.

## 11. VM5184 × G243 hydration

The permanent micro-operation address is:

```text
s = 64c + o
```

where `c ∈ [0,80]`, `o ∈ [0,63]`, and `s ∈ [0,5183]`.

The projected execution address is:

```text
q = 243s + g
```

where `g ∈ [0,242]` and `q ∈ [0,1,259,711]`.

```text
81 × 64 = 5,184
5,184 × 243 = 1,259,712
```

The fabric preserves exact state-bit position, ordered operation identity, five-trit control state, phase, grouping, dependencies, constraints, and receipt lineage.

## 12. Bidirectional native translation

The native execution path is:

```text
x86_64 bytes
→ exact decoder context
→ Hash216 instruction identity
→ VM81 intermediate representation
→ VM5184 × G243 route
→ immutable execution candidate
→ singleton VM81 admission
→ admitted state and Hash72 receipt
```

The reverse path is:

```text
validated VM81 trace
→ Hash216 instruction identity
→ retained x86_64 encoding or authorized native kernel sequence
```

Different machine-code encodings retain different identities even where their visible architectural effect is similar. Equivalent behavior does not authorize silent encoding substitution.

Unsafe, privileged, malformed, unavailable, or host-escaping operations must be trapped, modeled, rejected, or quarantined.

## 13. Full hydration branch trees

Full hydration intentionally extends through millions of nested closed and entangled branch-tree states representing valid permutations under local and global constraints.

Each valid branch binds parent state, ordered transformation, membrane depth/local constraints, inherited global invariants, phase/entanglement relationships, dependencies, resulting state, reverse/recovery path, receipt lineage, and reusable continuation identity.

Candidate branches may be explored in parallel. Invalid branches are pruned, denatured, rejected, rolled back, or quarantined without canonical mutation. Admission and commitment remain singular and deterministically ordered.

## 14. Memory register and logic are the same object

The hydrated object is not passive data beside independent logic.

```text
hydrated object
= state
+ admissible transformations
+ constraint topology
+ execution route
+ validation lineage
+ continuation address
```

A serialized VM81 circuit hydration is simultaneously memory register, executable logic, bounded specification contract, transformation history, Hash216 continuation index, VM81/VM5184/G243 circuit, program continuation, and recovery/replay image.

Serialization must preserve exact positions, order, grouping, nesting depth, branch identity, phase, constraints, predecessor/successor relations, source bytes, native bytes, and receipts. Preserving only an endpoint value while losing these relations is data loss.

## 15. Continuation and sparse hydration

The preferred reuse path is:

```text
nearest valid hydrated parent
+ authorized delta
→ affected dependency/projection frontier
→ preserve unaffected computation
→ recompute only the bounded frontier
→ compare with canonical full projection
→ foundational compatibility / singleton VM81 admission
→ new Hash72 receipt block
→ new Hash216 continuation record
```

Validated computation is reusable computational capital. Agents may consume prior continuations, calculate unresolved deltas, and contribute new validated objects, but they do not issue canonical state.

## 16. Plug-and-play object law

Anything may be built on top of HHS provided it enters as a fully backward-compatible reusable object.

A plug-and-play object must declare and preserve stable schema/object identity, exact typed inputs/outputs, source/native-byte identity where applicable, ABI/opcode bindings, ordered operations/grouping, dependencies/capabilities, local and inherited global constraints, mutation ownership/resource boundaries, lifecycle/event semantics, positive/negative/replay/rollback/recovery vectors, Hash72 receipt bindings, Hash216 archival/continuation bindings, and applicable native/Python/CLI/API/SDK/assistant/visual adapters.

The object may add operations, applications, agents, devices, optimizers, interfaces, workflows, or representations. It may not create a second kernel, receipt clock, canonical state store, identity system, backend authority, opcode authority, pre-pass-validity authority, or bypass around validation.

## 17. Backward compatibility

A valid extension satisfies:

```text
new capability works
AND inherited capabilities still work
AND inherited identities remain valid
AND shared invariants remain unchanged
AND pre-pass validity semantics remain unchanged
AND composition uses the existing authority
AND replay reproduces the same admitted result
AND no alternate authority path exists
```

Compatibility is bidirectional: inherited objects remain executable in the expanded system; new objects can consume and compose inherited validated objects; combined objects can be serialized, moved, rehydrated, replayed, and reused without hidden dependencies.

## 18. Repository ownership boundaries

| Path | Canonical responsibility |
|---|---|
| `hhs_runtime/` | Native and Python runtime substrate, kernel resolution, exact execution, C surfaces, continuation, replay, tests, and inherited/pre-pass-sensitive runtime behavior |
| `hhs_python/` | Python controller and ctypes bridge |
| `hhs_backend/` | Service lifecycle, orchestration, transport composition, assistant and route adapters |
| `hhs_graph/` | Receipt, object, branch, and continuation topology |
| `hhs_storage/` | Durable receipt, state, Hash216, vector, replay, and archival storage |
| `native_projects/` | Native implementations, ABI bindings, pass evidence, restart records, and generated artifacts |
| `hhs_gui/` and `applications/` | Human-operable projections of authoritative capabilities |
| `docs/` | Normative specifications, pass contracts, runbooks, and explanatory documents |

Root-level compatibility modules may also contain historically significant inherited behavior. Do not infer dispensability from path location alone. Moving or replacing canonical or pre-pass-sensitive logic requires coordinated dependency analysis, tests, documentation, migration, and replay evidence.

## 19. Interface and protocol rules

JSON is an internal and external protocol representation. It is not the underlying capability.

Correct flow:

```text
native or hydrated operation
→ actual computation, state, file, media, package, scene, or simulation result
→ admitted transition
→ Hash72 receipt
→ optional JSON transport, inspection, export, or replay representation
```

Interfaces must expose the capability first and the receipt as proof. Raw JSON may remain available for diagnostics and machine interoperability, but it must not replace functional application workflows.

## 20. Anti-drift rules

Prohibited:

- describing the pass system as the origin of pre-pass kernel protection;
- describing VM81 as a simple application;
- describing Python as the sole authority or as one homogeneous security wrapper;
- treating explicit hashing/PQC modules as the complete kernel-protection model;
- treating Hash72 as the mechanism that defines foundational state validity;
- treating Hash216 as the original transformation validator;
- indexing before valid receipt-chain closure;
- accepting a vector match as mutation permission;
- replacing required independent representations with one representation without equivalence proof;
- voting past disagreement among required authoritative representations;
- removing apparently redundant local modules without dependency-scoped global equivalence evidence;
- reordering path-sensitive/noncommutative transformations based only on scalar endpoint equality;
- separating hydrated memory from its executable logic and constraints;
- flattening ordered or entangled branches into untyped scalar endpoints;
- creating pass-specific parallel products or authorities;
- silently collapsing `xy` and `yx`;
- replacing exact canonical state with floats;
- direct unreceipted state mutation;
- frontend fabrication of runtime success;
- receipt-only JSON interfaces presented as complete capability integration;
- breaking inherited objects to simplify new development.

## 21. Replay and validation authority

Replay reconstructs execution and continuation identity. It must verify parent continuity, exact receipt block identity, ordered transition history, expected chain tip, invariant/witness integrity, deterministic equivalence, Hash216 archival binding, cache/hydration context, and locked/corrected/recovered/rejected/quarantined status.

A required representation or lineage mismatch produces explicit failure, quarantine, rollback boundary, repair action, or unresolved status. Silent continuation is forbidden.

Every extension must include dependency-scoped tests for inherited compatibility, positive admission, negative rejection, rollback, replay, receipt order, post-receipt Hash216 archival, cache verification, address reversibility, native-byte retention where applicable, plug-and-play discovery, and real interface behavior.

## 22. Final architectural principle

HHS is one cumulative runtime whose deepest state-change compatibility foundation predates the numbered pass system.

```text
pre-pass path/time/multimodal/noncommutative state-change compatibility
→ singleton VM81/kernel admission and execution
→ valid (prev,state,receipt) Hash72 block
→ exact 216-character concatenation
→ character-addressed SHA-256 array
→ Hash216 durable vector index
→ validated-computation cache
→ VM5184 × G243 hydrated circuit execution
→ pass-level optimization / acceleration / agents / interfaces / networking
```

Its complexity remains functional because later layers may optimize how efficiently a valid next state is found without gaining authority to redefine what constitutes a valid state transition.
