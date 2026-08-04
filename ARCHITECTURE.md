# HHS Canonical Runtime Architecture

This document defines the current repository topology, execution authority, ownership boundaries, compatibility law, and anti-drift rules for the Holofractal Harmonicode System.

The detailed normative companion is:

[`docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md`](docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md)

## 1. Cumulative system boundary

HHS existed before the numbered pass sequence. Every compatible pass is an additive in-place upgrade to one inherited system image.

```text
pre-pass HHS foundation
+ all compatible pass implementations
+ all validated repairs and integrations
= one cumulative HHS runtime
```

Pass directories, release bundles, evidence packages, contracts, and restart records preserve development and validation boundaries. They do not define independent runtimes, products, kernels, registries, or authorities.

Architecture documentation must distinguish contract authorization, implementation presence, test evidence, deployment evidence, and authoritative-main closure. It must not erase inherited implementation merely because a later document focuses on a narrower pass.

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
- no model, API, GUI, worker, cache, database, provider, compatibility shim, or pass-scoped service becomes an alternate mutation authority.

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

## 4. Internal security boundary

The post-quantum security construction is internal to the kernel and integrated runtime. It is not exposed as a set of independently callable public cryptographic operations.

External callers submit bounded proposals. Internal runtime layers perform the applicable joined validation, including:

- exact no-float Harmonicode algebra;
- higher-dimensional tensor checks;
- ordered and noncommutative phase computation;
- high-entropy validation;
- Golay-style toroidal corruption detection, correction, denaturing, and recovery;
- local and global constraint closure;
- phase, identity, lineage, and mutation-ownership preservation;
- rollback and last-known-good recovery;
- deterministic replay.

The security model is cumulative: formal specifications became equations, equations became operations, operations became native gates, native gates were tested, and interconnected Python implementations expanded the enforcement and test surface.

No public API may expose a path that reorders, weakens, selectively bypasses, or substitutes these internal stages.

## 5. Python phase-locked enforcement mesh

The Python layers are not the sole computational authority and are not a single wrapper around a small C application.

They form an interconnected phase-locked mesh that hardens, orchestrates, tests, persists, hydrates, translates, and projects the same governing constraints through multiple methods, including:

- symbolic and rational validation;
- tensor and manifold projection;
- semantic and proposition-identity preservation;
- entropy, corruption, recovery, and quarantine;
- storage and ledger integrity;
- replay reconstruction;
- provider-output admission;
- workflow lifecycle and deployment hardening;
- repository-wide hydration and dependency scans;
- multimodal reconstruction comparison.

Python must remain bound to the native object identity, predecessor lineage, VM81 admission boundary, invariant envelope, and receipt semantics.

## 6. Canonical transformation order

The authoritative order is:

```text
candidate object or transformation
→ exact source and identity preservation
→ Python phase-locked enforcement mesh
→ private VM81/kernel validation and execution
→ exact Harmonicode closure
→ correction, recovery, entropy, tensor, lineage, and replay checks
→ LOCKED, CORRECTED, RECOVERED, REJECTED, or QUARANTINED decision
```

Only a successfully admitted transformation may produce the canonical receipt block:

```text
(prev_hash72, state_hash72, receipt_hash72)
```

Hash72 is the receipt that the transformation survived the complete applicable validation path. A Hash72-shaped value is not independently sufficient evidence of a valid state.

## 7. Hash216 begins after receipt closure

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

Hash216 does not authorize the original transformation. VM81 and the integrated validation fabric already did so. Hash216 preserves, indexes, retrieves, relates, and hydrates the completed proof.

A vector match is never permission to bypass current-context verification, dependency validation, singleton VM81 admission, or the ordered Hash72 commit.

## 8. Validated-computation cache

The Hash216 vector store also supports a buffer/cache optimizer for reusable validated computation.

A warm record may preserve:

- exact source and machine bytes;
- decoder and compiler context;
- ordered operands and grouping;
- local and global constraints;
- dependency roots;
- VM81 lowering graph;
- VM5184 routes and G243 controls;
- expected faults and privilege classes;
- test-vector identities;
- admission and rejection receipts;
- replay, rollback, repair, and retained native encoding.

A cache hit may eliminate redundant decoding, lowering, branch expansion, proof construction, and microcode generation. It may not eliminate admission or commitment.

## 9. VM5184 × G243 hydration

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

## 10. Bidirectional native translation

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

## 11. Full hydration branch trees

Full hydration intentionally extends through millions of nested closed and entangled branch-tree states representing valid permutations under local and global constraints.

Each valid branch binds:

- parent state;
- ordered transformation;
- membrane depth and local constraints;
- inherited global invariants;
- phase and entanglement relationships;
- dependencies;
- resulting state;
- reverse and recovery path;
- receipt lineage;
- reusable continuation identity.

Candidate branches may be explored in parallel. Invalid branches are pruned, denatured, rejected, rolled back, or quarantined without canonical mutation. Admission and commitment remain singular and deterministically ordered.

## 12. Memory register and logic are the same object

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

A serialized VM81 circuit hydration is simultaneously:

- memory register;
- executable logic;
- bounded specification contract;
- transformation history;
- Hash216 continuation index;
- VM81/VM5184/G243 circuit;
- program continuation;
- recovery and replay image.

Serialization must preserve exact positions, order, grouping, nesting depth, branch identity, phase, constraints, predecessor/successor relations, source bytes, native bytes, and receipts. Preserving only an endpoint value while losing these relations is data loss.

## 13. Continuation and sparse hydration

The preferred reuse path is:

```text
nearest valid hydrated parent
+ authorized delta
→ affected dependency/projection frontier
→ preserve unaffected computation
→ recompute only the bounded frontier
→ compare with canonical full projection
→ singleton VM81 admission
→ new Hash72 receipt block
→ new Hash216 continuation record
```

Validated computation is reusable computational capital. Agents may consume prior continuations, calculate unresolved deltas, and contribute new validated objects, but the runtime remains the sole issuer of canonical state.

## 14. Plug-and-play object law

Anything may be built on top of HHS provided it enters as a fully backward-compatible reusable object.

A plug-and-play object must declare and preserve:

- stable schema and object identity;
- exact typed inputs and outputs;
- source and native-byte identity where applicable;
- ABI and opcode bindings;
- ordered operations and grouping;
- dependencies and capabilities;
- local and inherited global constraints;
- mutation ownership and resource boundaries;
- lifecycle and event semantics;
- positive, negative, replay, rollback, and recovery vectors;
- Hash72 receipt bindings;
- Hash216 archival and continuation bindings;
- native, Python, CLI, API, SDK, assistant, and visual adapters where applicable;
- explicit machine-readable exclusion reasons for intentionally unsupported surfaces.

The object may add new operations, applications, agents, devices, optimizers, interfaces, workflows, or representations. It may not create a second kernel, receipt clock, canonical state store, identity system, backend authority, opcode authority, or bypass around validation.

## 15. Backward compatibility

A valid extension satisfies:

```text
new capability works
AND inherited capabilities still work
AND inherited identities remain valid
AND shared invariants remain unchanged
AND composition uses the existing authority
AND replay reproduces the same admitted result
AND no alternate authority path exists
```

Compatibility is bidirectional:

- inherited objects remain executable in the expanded system;
- new objects can consume and compose inherited validated objects;
- combined objects can be serialized, moved, rehydrated, replayed, and reused without hidden dependencies.

## 16. Repository ownership boundaries

| Path | Canonical responsibility |
|---|---|
| `hhs_runtime/` | Native and Python runtime substrate, internal security, exact execution, C surfaces, continuation, replay, tests |
| `hhs_python/` | Python controller and ctypes bridge |
| `hhs_backend/` | Service lifecycle, orchestration, transport composition, assistant and route adapters |
| `hhs_graph/` | Receipt, object, branch, and continuation topology |
| `hhs_storage/` | Durable receipt, state, Hash216, vector, replay, and archival storage |
| `native_projects/` | Native implementations, ABI bindings, pass evidence, restart records, and generated artifacts |
| `hhs_gui/` and `applications/` | Human-operable projections of authoritative capabilities |
| `docs/` | Normative specifications, pass contracts, runbooks, and explanatory documents |

Root-level compatibility modules remain thin. Moving or replacing canonical logic requires coordinated import, test, documentation, migration, and replay updates.

## 17. Interface and protocol rules

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

The interface should derive from the complete authoritative capability registry rather than a manually curated demonstration subset. Every integrated user-facing capability must be discoverable or carry an explicit exclusion reason.

## 18. Anti-drift rules

Prohibited:

- describing VM81 as a simple application;
- describing Python as the sole authority;
- treating Hash72 as the entire security algorithm;
- treating Hash216 as the original transformation validator;
- indexing before valid receipt-chain closure;
- accepting a vector match as mutation permission;
- separating hydrated memory from its executable logic and constraints;
- flattening ordered or entangled branches into untyped scalar endpoints;
- exposing internal security as bypassable public helpers;
- creating pass-specific parallel products or authorities;
- silently collapsing `xy` and `yx`;
- replacing exact canonical state with floats;
- stripping identity-bearing width, order, grouping, bytes, or membranes;
- direct unreceipted state mutation;
- frontend fabrication of runtime success;
- receipt-only JSON interfaces presented as complete capability integration;
- breaking inherited objects to simplify new development.

## 19. Replay and validation authority

Replay reconstructs execution and continuation identity. It must verify:

- parent continuity;
- exact receipt block identity;
- ordered transition history;
- expected chain tip;
- invariant and witness integrity;
- deterministic equivalence;
- Hash216 archival binding;
- cache and hydration context;
- locked, corrected, recovered, rejected, or quarantined status.

A mismatch produces explicit failure, quarantine, rollback boundary, repair action, or unresolved status. Silent continuation is forbidden.

Every extension must include dependency-scoped tests for inherited compatibility, positive admission, negative rejection, rollback, replay, receipt order, post-receipt Hash216 archival, cache verification, address reversibility, native-byte retention where applicable, plug-and-play discovery, and real interface behavior.

## 20. Final architectural principle

HHS is one evolutionary modular entangled thermodynamic phase-logic runtime and agentic knowledge economy.

```text
formal specifications and equations
→ native kernel operations and internal security
→ phase-locked Python enforcement mesh
→ singleton VM81 admission
→ valid (prev,state,receipt) Hash72 block
→ exact 216-character concatenation
→ character-addressed SHA-256 array
→ Hash216 durable vector index
→ validated-computation cache
→ VM5184 × G243 hydrated circuit execution
→ exact native ingress and retained egress
→ reusable backward-compatible plug-and-play objects
```

Its complexity remains functional because every module, object, branch, agent, cache, interface, and future pass composes through one computational authority and one cumulative system history.
