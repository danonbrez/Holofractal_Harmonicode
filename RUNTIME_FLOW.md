# HHS Runtime Flow

This document defines the canonical end-to-end execution, validation, receipt, archival, hydration, cache, replay, interface, and plug-in flow for the integrated Holofractal Harmonicode System.

Normative architecture companions:

- [`docs/architecture/HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION.md`](docs/architecture/HHS_PRE_PASS_KERNEL_PROTECTION_STATE_CHANGE_CONSTITUTION.md)
- [`docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md`](docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md)

## 1. Universal transition flow

The system-level flow begins beneath the numbered pass system:

```text
request, source, object, native bytes, event, or provider result
→ exact ingress capture and identity preservation
→ parsing, typing, capability, and policy checks where applicable
→ pre-pass path/time/multimodal/noncommutative state-change compatibility
→ required cross-format equality and error-correction closure
→ private VM81/kernel execution and admission
→ exact Harmonicode / inherited invariant closure
→ LOCKED, CORRECTED, RECOVERED, REJECTED, or QUARANTINED decision
→ Hash72 receipt commitment for an admitted transition
```

The pre-pass protection layer is not a numbered pass and is not accurately reduced to a generic "Python security mesh." Individual Python/native/local modules may participate in state protection, error correction, prediction, reconstruction, timing, caching, rollback, or pass-level orchestration according to their inherited role.

No API, worker, cache, provider, database, GUI, pass, or compatibility layer is an alternate authority.

## 2. Cross-format closure and rollback

Required authoritative representations may differ structurally while describing the same raw state.

For canonical raw state `R_n`:

```text
for every required authoritative modality m:
Normalize_m(View_m) = R_n
```

The rule is unanimity, not voting.

```text
required representation disagreement
→ candidate closure failure
→ no canonical mutation
→ preserve evidence as applicable
→ retain or restore the last fully closed state
```

Rollback at this boundary is part of normal state-machine behavior, not only disaster recovery.

## 3. Path, ordering, temporal, and lineage dependence

A candidate is evaluated in its applicable state-history context. Local endpoint similarity does not establish global equivalence.

The applicable relation may bind:

```text
Genesis continuity
+ exact predecessor
+ execution path
+ temporal / epoch position
+ modality
+ ordered / noncommutative context
+ hash / receipt lineage
+ correction closure
```

A stale transition or witness does not become valid for another state merely because its bytes were valid previously. Exact implementation-specific timing constants and internal transition sequences are not published by this overview.

## 4. Admitted transformation receipt

Only a successfully admitted transformation produces the canonical three-part Hash72 block:

```text
(prev_hash72, state_hash72, receipt_hash72)
```

The block means:

- `prev_hash72`: exact authoritative predecessor boundary;
- `state_hash72`: exact admitted resulting state;
- `receipt_hash72`: proof that the bounded transformation survived the complete applicable validation/admission path.

Hash72 chains admitted state. It does not independently define whether a pre-pass-incompatible state is valid.

A terminal value or a Hash72-shaped string without parent, state, invariant, cross-format, witness, and replay agreement is not a valid transformation receipt.

Rejected or quarantined operations preserve structured evidence without changing canonical state.

## 5. Post-receipt Hash216 archival

Hash216 storage begins only after the valid receipt block exists.

```text
prev_hash72
+ state_hash72
+ receipt_hash72
→ exact ordered 216-character concatenation
→ preserve every character position
→ derive configured character-addressed SHA-256 array
→ bind metadata and lineage
→ store durable Hash216/vector index record
```

Required bindings include predecessor/state identity, transformation receipt, exact concatenated block, positional SHA-256 array, dependency/constraint roots, replay/recovery metadata, and source/decoder/compiler/native-byte identity where applicable.

Hash216 preserves and retrieves completed proof. It does not authorize the original transformation and cannot bypass the pre-pass/kernel boundary.

## 6. Validated-computation cache flow

```text
new request
→ derive exact lookup context
→ resolve nearest or exact validated record
→ verify store root, predecessor, decoder, compiler, dependencies, constraints, privilege, and applicable state context
→ retrieve validated lowering, branch, route, proof, and retained-byte records
→ reuse unchanged computation
→ calculate immutable candidate delta
→ pre-pass compatibility / required cross-format closure
→ singleton VM81 admission
→ new Hash72 receipt block
→ new Hash216 continuation record
```

A cache hit may remove redundant work. It never bypasses foundational compatibility, current-context validation, admission, or commitment.

## 7. Low-latency optimization law

HHS performance work SHALL optimize the amount of active work rather than weaken the state-validity rules.

```text
GLOBAL VALIDITY STRUCTURE = LARGE
PER-STEP AUTHORITATIVE WORK = BOUNDED
```

Compatible acceleration includes validated continuations, exact caches, vector indexing, dependency-bounded recomputation, selective hydration, compiled representations, branch prediction/ranking, and candidate parallelism.

```text
HOW FAST CAN WE FIND A VALID NEXT STATE?
```

may be optimized aggressively.

```text
WHAT COUNTS AS A VALID NEXT STATE?
```

is not a pass-level optimization variable.

## 8. VM5184 × G243 execution coordinates

Permanent address:

```text
s = 64c + o
```

- `c`: VM81 cell, `0..80`;
- `o`: ordered operation position, `0..63`;
- `s`: permanent address, `0..5183`.

Projected control address:

```text
q = 243s + g
```

- `g`: ordered five-trit control, `0..242`;
- `q`: projected execution coordinate, `0..1,259,711`.

Every applicable route preserves state-bit position, operation order, phase, grouping, dependencies, constraints, source identity, and receipt lineage.

## 9. Exact x86_64 ingress

```text
exact x86_64 byte sequence
→ preserve length, prefixes, opcode map, ModR/M, SIB, displacement, immediate, modes, features, and privilege class
→ resolve or construct Hash216 instruction record
→ lower into VM81 intermediate representation
→ route through VM5184 × G243
→ execute immutable candidate
→ trap faults without canonical mutation
→ applicable foundational compatibility / singleton VM81 admission
→ Hash72 receipt commitment
```

Different encodings retain different instruction identities even when their visible architectural effects are similar.

Unsafe, malformed, unavailable, privileged, or host-escaping operations are trapped, modeled, rejected, or quarantined.

## 10. Retained native egress

```text
validated VM81 trace
→ verified Hash216 instruction identity
→ retained original encoding or explicitly authorized native kernel sequence
→ governed binary or device egress
```

Equivalent behavior does not authorize silent byte substitution. Reverse translation must preserve the exact encoding identity or record a separately admitted transformation permitting replacement.

## 11. Full hydration branch-tree flow

```text
validated parent hydrated object
→ enumerate locally admissible operations and controls
→ enforce membrane depth and local constraints
→ enforce inherited global constraints
→ preserve phase, ordering, dependencies, and entanglement links
→ calculate branch candidates
→ prune invalid branches
→ close valid branches
→ deterministically order mutation candidates
→ foundational compatibility / singleton VM81 admission
→ receipt and archival
```

Millions of nested branches may exist as reusable closed continuations. Parallel branch exploration does not create parallel canonical state authorities.

## 12. Memory and logic unification

A hydrated object is loaded and stored as one circuit object:

```text
state
+ admissible transformations
+ constraint topology
+ execution route
+ validation lineage
+ continuation address
```

The serialized block is simultaneously memory, logic, contract, history, program continuation, index, and recovery image.

Loading a hydrated object restores both values and the validated relationships required to continue computation.

## 13. Sparse continuation flow

```text
nearest valid parent state
→ validate parent receipt and Hash216 roots
→ validate bounded delta
→ derive affected dependency/projection frontier
→ copy parent state and projection
→ preserve every unaffected cell and branch
→ recompute only affected frontier
→ compare sparse result with canonical full projection
→ foundational compatibility / VM81 admission
→ new receipt block
→ new continuation token and vector record
```

Continuation roots may bind parent, content, delta, hydration, dependency, projection, learning, generation, and parent-receipt identities.

## 14. Harmonicode source flow

```text
Harmonicode source
→ preserve lexical form, widths, Lists, grouping, and membranes
→ parse typed expressions
→ preserve ordered products such as xy and yx
→ bind parameters and recursively expand macros
→ retain exact rational, reciprocal, modular, and symbolic forms
→ submit bounded transformation proposal
→ inherited state compatibility and VM81 admission
→ receipt, archival, cache, and replay
```

No parser or macro layer may normalize away identity-bearing structure.

## 15. Agent and worker flow

Agents and workers may discover prior validated objects, generate immutable candidates, explore branch trees, compare reconstructed modalities, optimize schedules/hydration frontiers, and propose files, media, applications, code, simulations, or device changes.

They may not directly mutate canonical state or redefine foundational state validity.

```text
agent proposal
→ typed work item
→ capability, resource, and dependency checks
→ immutable candidate computation
→ deterministic ordering barrier
→ foundational compatibility / cross-format closure
→ singleton VM81 admission
→ receipt and archival
```

Worker-local queues, memory, timers, result files, and provider outputs are noncanonical.

An optimizer must not remove apparently unrelated or redundant pre-pass-sensitive modules merely because their local function seems unnecessary. Dependency-scoped global equivalence is required.

## 16. Plug-and-play object registration

```text
new module or application
→ declare stable schema and object identity
→ declare exact inputs, outputs, dependencies, capabilities, and mutation scope
→ bind existing ABI, opcodes, services, and authority path
→ inherit local, global, and foundational state-change constraints
→ provide positive, negative, replay, rollback, and recovery vectors
→ validate backwards compatibility
→ admit representative transformations
→ bind receipts and Hash216 continuation records
→ register discoverable CLI, API, SDK, assistant, and visual surfaces
```

A plug-in is incomplete if it requires a new canonical authority, breaks inherited objects, depends on hidden conversation state, redefines foundational validity, or exposes only a JSON receipt without the actual capability.

## 17. API and JSON flow

```text
HTTP/WebSocket/SDK request
→ transport validation
→ authoritative runtime call
→ actual computational or application result
→ admitted receipt-bearing state
→ response serialization
```

Routes and WebSocket handlers transport already-governed requests and events. They do not implement canonical business logic or fabricate success.

JSON is protocol representation for request, result, status, receipt, export, diagnostics, and replay. It is not the native capability itself.

## 18. Visual interface flow

```text
user action
→ registered capability binding
→ backend/native authoritative execution
→ actual file, scene, package, media, simulation, editor, calculator, device, or workflow result
→ receipt and lifecycle evidence
→ human-readable visual projection
```

The UI must derive from the complete user-facing capability registry. A capability is either visible and operable or has an explicit machine-readable exclusion reason.

The UI must not reduce native functionality to raw JSON or repeatedly expose only a manually chosen subset of demos.

## 19. Replay flow

```text
receipt sequence and declared parent boundary
→ verify exact prev/state/receipt blocks
→ verify parent continuity
→ rederive canonical identities and witnesses
→ verify Hash216 archival binding and positional array
→ verify dependency, decoder, compiler, cache, hydration, and applicable representation context
→ reconstruct ordered state transitions
→ compare expected chain tip and resulting object
→ VERIFIED, MISMATCH, ROLLBACK, REPAIR_REQUIRED, or QUARANTINED
```

Replay is a canonical execution property, not optional debugging output.

## 20. Recovery flow

```text
corruption, required representation mismatch, invalid branch, or authority failure
→ prevent canonical mutation
→ preserve evidence
→ apply bounded correction when authorized
→ otherwise denature or quarantine
→ restore last fully closed state or declared recovery point
→ replay forward through validated receipts
→ emit correction, recovery, rejection, or quarantine receipt
```

No recovery path may silently weaken an invariant or choose a disagreeing representation merely to make a failing state pass.

## 21. Backward-compatibility validation

Every new extension must demonstrate:

```text
new capability works
AND inherited capabilities still work
AND inherited identities remain valid
AND shared constraints remain intact
AND foundational state-change semantics remain intact
AND the existing authority path is used
AND deterministic replay agrees
AND no alternate authority exists
```

Required tests include exact schema/ABI/opcode compatibility, no-float authority boundaries, ordered operand/grouping preservation, positive admission/negative rejection, rollback without unauthorized mutation, correct `(prev,state,receipt)` production, Hash216 archival only after receipt closure, cache-hit verification without bypass, address reversibility where applicable, retained native-byte identity where applicable, plug-and-play discovery/interface operation, dependency-scoped inherited regression, and final integrated replay.

## 22. Canonical summary

```text
proposal
→ pre-pass path/time/multimodal/noncommutative compatibility
→ required cross-format closure / rollback on disagreement
→ singleton VM81 admission
→ valid Hash72 (prev,state,receipt)
→ exact 216-character archival block
→ character-addressed SHA-256 array
→ Hash216 durable vector record
→ validated-computation cache
→ VM5184 × G243 hydrated continuation
→ pass-level optimization, agents, interfaces, and networking
```

Storage and caching preserve validated computation; explicit security protects applicable boundaries; neither replaces the pre-pass state-change constitution or singleton kernel authority.
