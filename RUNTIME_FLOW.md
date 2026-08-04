# HHS Runtime Flow

This document defines the canonical end-to-end execution, validation, receipt, archival, hydration, cache, replay, interface, and plug-in flow for the integrated Holofractal Harmonicode System.

Normative architecture companion:

[`docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md`](docs/architecture/HHS_SINGLE_AUTHORITY_HYDRATED_OBJECT_AND_PLUG_IN_COMPATIBILITY_SPEC.md)

## 1. Universal transition flow

```text
request, source, object, native bytes, event, or provider result
→ exact ingress capture and identity preservation
→ parsing, typing, capability, and policy checks
→ phase-locked Python security and constraint mesh
→ private VM81/kernel execution and validation
→ exact Harmonicode closure
→ tensor, entropy, phase, lineage, recovery, and replay checks
→ LOCKED, CORRECTED, RECOVERED, REJECTED, or QUARANTINED decision
```

No API, worker, cache, provider, database, GUI, or compatibility layer is an alternate authority.

## 2. Admitted transformation receipt

Only a successfully admitted transformation produces the canonical three-part Hash72 block:

```text
(prev_hash72, state_hash72, receipt_hash72)
```

The block means:

- `prev_hash72`: exact authoritative predecessor boundary;
- `state_hash72`: exact admitted resulting state;
- `receipt_hash72`: proof that the bounded transformation survived the complete applicable validation path.

A terminal value or a Hash72-shaped string without parent, state, invariant, witness, and replay agreement is not a valid transformation receipt.

Rejected or quarantined operations preserve structured evidence without changing canonical state.

## 3. Post-receipt Hash216 archival

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

Required bindings include:

- predecessor and state identity;
- transformation receipt;
- exact concatenated block;
- positional SHA-256 array;
- dependency and constraint roots;
- replay and recovery metadata;
- source, decoder, compiler, and native-byte identity where applicable.

Hash216 preserves and retrieves completed proof. It does not authorize the original transformation.

## 4. Validated-computation cache flow

```text
new request
→ derive exact lookup context
→ resolve nearest or exact Hash216 record
→ verify store root, predecessor, decoder, compiler, dependencies, constraints, and privilege context
→ retrieve validated lowering, branch, route, proof, and retained-byte records
→ reuse unchanged computation
→ calculate immutable candidate delta
→ singleton VM81 admission
→ new Hash72 receipt block
→ new Hash216 continuation record
```

A cache hit may remove redundant work. It never bypasses current-context validation, admission, or commitment.

## 5. VM5184 × G243 execution coordinates

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

## 6. Exact x86_64 ingress

```text
exact x86_64 byte sequence
→ preserve length, prefixes, opcode map, ModR/M, SIB, displacement, immediate, modes, features, and privilege class
→ resolve or construct Hash216 instruction record
→ lower into VM81 intermediate representation
→ route through VM5184 × G243
→ execute immutable candidate
→ trap faults without canonical mutation
→ singleton VM81 admission
→ Hash72 receipt commitment
```

Different encodings retain different instruction identities even when their visible architectural effects are similar.

Unsafe, malformed, unavailable, privileged, or host-escaping operations are trapped, modeled, rejected, or quarantined.

## 7. Retained native egress

```text
validated VM81 trace
→ verified Hash216 instruction identity
→ retained original encoding or explicitly authorized native kernel sequence
→ governed binary or device egress
```

Equivalent behavior does not authorize silent byte substitution. Reverse translation must preserve the exact encoding identity or record a separately admitted transformation permitting replacement.

## 8. Full hydration branch-tree flow

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
→ singleton VM81 admission
→ receipt and archival
```

Millions of nested branches may exist as reusable closed continuations. Parallel branch exploration does not create parallel canonical state authorities.

## 9. Memory and logic unification

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

## 10. Sparse continuation flow

```text
nearest valid parent state
→ validate parent receipt and Hash216 roots
→ validate bounded delta
→ derive affected dependency/projection frontier
→ copy parent state and projection
→ preserve every unaffected cell and branch
→ recompute only affected frontier
→ compare sparse result with canonical full projection
→ VM81 admission
→ new receipt block
→ new continuation token and vector record
```

Continuation roots may bind parent, content, delta, hydration, dependency, projection, learning, generation, and parent-receipt identities.

## 11. Harmonicode source flow

```text
Harmonicode source
→ preserve lexical form, widths, Lists, grouping, and membranes
→ parse typed expressions
→ preserve ordered products such as xy and yx
→ bind parameters and recursively expand macros
→ retain exact rational, reciprocal, modular, and symbolic forms
→ submit bounded transformation proposal
→ integrated validation and VM81 admission
→ receipt, archival, cache, and replay
```

No parser or macro layer may normalize away identity-bearing structure.

## 12. Agent and worker flow

Agents and workers may:

- discover prior validated objects;
- generate immutable candidate transformations;
- explore branch trees;
- compare reconstructed modalities;
- optimize schedules and hydration frontiers;
- propose files, media, applications, code, simulations, or device changes.

They may not directly mutate canonical state.

```text
agent proposal
→ typed work item
→ capability, resource, and dependency checks
→ immutable candidate computation
→ deterministic ordering barrier
→ singleton VM81 admission
→ receipt and archival
```

Worker-local queues, memory, timers, result files, and provider outputs are noncanonical.

## 13. Plug-and-play object registration

```text
new module or application
→ declare stable schema and object identity
→ declare exact inputs, outputs, dependencies, capabilities, and mutation scope
→ bind existing ABI, opcodes, services, and authority path
→ inherit local and global constraints
→ provide positive, negative, replay, rollback, and recovery vectors
→ validate backwards compatibility
→ admit representative transformations
→ bind receipts and Hash216 continuation records
→ register discoverable CLI, API, SDK, assistant, and visual surfaces
```

A plug-in is incomplete if it requires a new canonical authority, breaks inherited objects, depends on hidden conversation state, or exposes only a JSON receipt without the actual capability.

## 14. API and JSON flow

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

## 15. Visual interface flow

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

## 16. Replay flow

```text
receipt sequence and declared parent boundary
→ verify exact prev/state/receipt blocks
→ verify parent continuity
→ rederive canonical identities and witnesses
→ verify Hash216 archival binding and positional array
→ verify dependency, decoder, compiler, cache, and hydration context
→ reconstruct ordered state transitions
→ compare expected chain tip and resulting object
→ VERIFIED, MISMATCH, ROLLBACK, REPAIR_REQUIRED, or QUARANTINED
```

Replay is a canonical execution property, not optional debugging output.

## 17. Recovery flow

```text
corruption, mismatch, invalid branch, or authority failure
→ prevent canonical mutation
→ preserve evidence
→ apply bounded correction when authorized
→ otherwise denature or quarantine
→ restore last known-good state or declared recovery point
→ replay forward through validated receipts
→ emit correction, recovery, rejection, or quarantine receipt
```

No recovery path may silently weaken an invariant to make a failing state pass.

## 18. Backward-compatibility validation

Every new extension must demonstrate:

```text
new capability works
AND inherited capabilities still work
AND inherited identities remain valid
AND shared constraints remain intact
AND the existing authority path is used
AND deterministic replay agrees
AND no alternate authority exists
```

Required tests include:

- exact schema, ABI, and opcode compatibility;
- no-float authority boundaries;
- ordered operand and grouping preservation;
- positive admission and negative rejection;
- rollback without unauthorized mutation;
- correct `(prev,state,receipt)` production;
- Hash216/SHA-256 archival only after receipt closure;
- cache-hit verification without bypass;
- address reversibility where applicable;
- retained native-byte identity where applicable;
- plug-and-play discovery and interface operation;
- dependency-scoped inherited regression;
- final integrated replay.

## 19. Canonical summary

```text
proposal
→ integrated Python and native validation
→ singleton VM81 admission
→ valid Hash72 (prev,state,receipt)
→ exact 216-character archival block
→ character-addressed SHA-256 array
→ Hash216 durable vector record
→ validated-computation cache
→ VM5184 × G243 hydrated continuation
→ exact native ingress/egress
→ reusable backward-compatible object
```

The order is mandatory. Storage and caching preserve validated computation; they do not replace the authority that validates it.
