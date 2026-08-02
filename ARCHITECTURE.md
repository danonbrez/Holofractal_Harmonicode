# HHS Canonical Runtime Architecture

This document defines the current repository topology, execution authority, ownership boundaries, and anti-drift rules for the Holofractal Harmonicode system.

## 1. Current state boundary

The repository contains several inherited and concurrent layers. Their status must remain explicit.

| Layer | Status on `main` |
|---|---|
| Pass 159 Harmonicode toolchain | Authoritative-main closure evidence present for the VM81 + Hash216 interpreter and C11 compiler layer. |
| Pass 161 visual assistant | Integrated visual development environment remains the default `bash start.sh` composition. |
| Pass 190 Iteration 7 | Verified durable worker and pure-operation execution layer with 42 governed operations and an inherited ten-operation native ABI. |
| Pass 190 completion | Not claimed. |
| Pass 191 universal hydration | Normative contract frozen; full repository hydration implementation and verification are not claimed merely because the contract exists. |

Architecture documentation must not promote a proposed, contracted, or partially integrated layer into a verified runtime claim without repository-visible evidence.

## 2. Governing invariants

All canonical computation must preserve:

```text
Δe = 0
Ψ = 0
Θ15 = true
Ω = true
```

Additional binding rules:

- canonical kernel arithmetic is exact;
- floating-point values may be noncanonical display, timing, benchmark, or calibration witnesses;
- state changes are explicit patches or typed transitions;
- every authoritative transition is audited and receipt-bound;
- parent receipt continuity is preserved;
- replay is a required execution property, not optional debug output;
- ordered products, lists, bytes, phases, source spans, and membranes are preserved where they carry identity;
- no model, API route, GUI event, worker-local queue, or compatibility shim becomes an alternate mutation authority.

## 3. Canonical authority chain

```text
input
→ source preservation and parsing
→ symbolic or macro expansion
→ typed state proposal
→ runtime controller or operation fabric
→ singleton VM81 admission
→ kernel and invariant audit
→ LOCKED or QUARANTINED decision
→ Hash72 receipt
→ Hash216 identity/topology witness
→ replay and persistence
→ API, SDK, WebSocket, assistant, and visual projection
```

The authority chain must remain singular. Adapters may expose it through multiple interfaces, but they must not duplicate its logic.

## 4. Repository topology

The repository is a transitional hybrid layout.

### 4.1 Canonical package paths

| Path | Canonical responsibility |
|---|---|
| `hhs_runtime/` | Runtime substrate, kernel resolution, exact execution, C surfaces, core sandbox, replay helpers, tests |
| `hhs_python/` | Python controller and ctypes bridge |
| `hhs_backend/` | FastAPI composition, lifecycle, orchestration, assistant, routes, WebSockets, service adapters |
| `hhs_graph/` | Receipt and object graph topology |
| `hhs_storage/` | Durable state, persistence, archival, and storage adapters |
| `native_projects/` | Pass-scoped native implementations, evidence, deployment, restart records, generated bindings |
| `hhs_gui/` and `applications/` | User-facing visual surfaces and application workspaces |
| `docs/` | Normative specifications, pass documentation, operational guidance, and explanatory manuscripts |

### 4.2 Root module policy

Root-level runtime modules are retained primarily for compatibility and historical imports.

Example:

```text
hhs_general_runtime_layer_v1.py
→ hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1
```

Rules:

- new canonical logic belongs in the appropriate package path;
- root compatibility modules remain thin;
- compatibility repairs must not introduce a second authority implementation;
- moving a canonical module requires updating imports, tests, documentation, and migration shims together.

## 5. Ownership boundaries

### 5.1 Authoritative kernel

Owns:

- required kernel symbols;
- exact authority functions;
- invariant evaluation;
- Hash72 security commitment implementation;
- Manifold9 and drift-gate authority where applicable.

Must not be bypassed or replaced by a local fallback authority.

### 5.2 VM81

Owns:

- semantic execution admission;
- authoritative state transitions;
- deterministic phase/tick progression;
- execution witnesses and closure relations;
- transition authority shared by higher layers.

Must not:

- delegate mutation authority to API routes, workers, providers, or GUI state;
- accept unreceipted direct mutation;
- use worker-local or provider-local state as canonical truth.

### 5.3 Hash72

Owns:

- active input, state, operation, witness, receipt, macro, expansion, and result commitments;
- parent-linked causal lineage;
- chain verification.

Hash72 receipts are append-only execution witnesses.

### 5.4 Hash216

Owns:

- ordered object identity;
- permanent indexing and historical evidence;
- operation and topology identity across broader hydrated graphs.

Hash72 and Hash216 are complementary and must not be silently collapsed.

### 5.5 General audited runtime

Canonical implementation:

```text
hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py
```

Owns:

- exact operation execution;
- pre-state and post-state capture;
- kernel gate submission;
- locked/quarantined transition recording;
- receipt commitment;
- local chain verification.

Must fail closed when the authoritative kernel is unavailable.

### 5.6 Harmonicode parser and macro layer

Owns:

- source preservation;
- symbolic normalization;
- typed expression structure;
- balanced membrane parsing;
- parameter binding;
- nested macro expansion;
- source, definition, and expansion commitments;
- submission to the audited runtime.

Canonical public files include:

```text
terminal_hhsprog_v5_macro_algebra.py
hhs_program_format_and_cli_v1.py
```

### 5.7 Runtime controller and ctypes bridge

Owns:

- lifecycle and deterministic sequencing;
- native ABI mediation;
- state ownership across Python/native boundaries;
- listener and runtime session coordination.

Must not bypass audited transition or receipt logic.

### 5.8 Backend and orchestrator

Owns:

- service lifecycle;
- composition of routes and runtime services;
- transport adaptation;
- assistant and provider proposal flow;
- WebSocket publication after authoritative transitions;
- API-visible status and evidence.

Must not:

- embed alternate business or mutation logic in routes;
- directly mutate VM81 state;
- fabricate receipts or provider success;
- treat optimistic frontend state as authoritative runtime state.

### 5.9 API routes and WebSockets

Own transport only:

- request validation;
- response serialization;
- authentication/capability extraction;
- streaming of already-governed events.

No canonical execution logic belongs in route or WebSocket handlers.

### 5.10 Graph and storage layers

Graph owns:

- receipt/object topology;
- lineage traversal;
- graph indexing and reconstruction.

Storage owns:

- durable persistence;
- state snapshots;
- replay storage;
- archival and database adapters.

Neither layer becomes an independent execution authority.

### 5.11 Visual IDE

Owns:

- user interaction;
- file and object navigation;
- editors, inspectors, previews, terminals, controls, and status surfaces;
- plain-language projection of runtime evidence.

Must not:

- fabricate backend success;
- store an alternate authoritative state;
- execute protected mutation outside the runtime path;
- hide failure, timeout, cancellation, retry, or degraded-mode conditions.

### 5.12 Language-model providers

Own capability generation only:

- text, code, plans, descriptions, and creative proposals;
- bounded tool-call proposals;
- provider invocation results.

Model output is not canonical merely because inference completed. Provider results enter HHS through policy, ingress, VM81 admission, audit, and receipt closure.

## 6. Pass 190 operation fabric

Canonical path:

```text
native_projects/hhs_pass190_operation_fabric/
```

### 6.1 Current implemented registry

```text
10 inherited native operations
+ 21 Iteration 6 exact-authority operations
+ 11 Iteration 7 execution operations
= 42 governed operations
```

The C ABI remains exactly ten operations. The remaining operations lower through the inherited exact VM81 fallback.

### 6.2 Iteration 7 execution topology

```text
registered pure operation
→ durable execution job
→ dependency and schedule admission
→ capability-matched worker
→ Hash72 claim
→ exact target evaluation
→ one outer VM81 admission
→ one receipt and event
→ completed, retry-wait, failed, or cancelled state
```

### 6.3 Single state authority

The Pass 190 service and worker share one authoritative SQLite state containing resources, workers, jobs, leases, fences, receipts, and events.

No worker-local queue, process memory, timer, or result file is authoritative.

### 6.4 Exact time

Schedules, heartbeats, retries, leases, starts, and completion use nonnegative exact integer nanoseconds.

### 6.5 Deliberate boundaries

Iteration 7 does not claim:

- provider-backed execution;
- arbitrary subprocess execution;
- mutating target execution;
- distributed multi-host consensus;
- broader native ABI parity;
- final Pass 190 completion;
- live production acceptance on DigitalOcean.

## 7. Pass 191 universal hydration target

Normative contract:

```text
docs/pass191/HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_UNIVERSAL_INVARIANT_CLOSURE.md
```

Target topology:

```text
one complete historical lineage
→ one canonical repository object graph
→ one canonical operation registry
→ one universal invariant envelope
→ one VM81 admission authority
→ one Hash72 chain
→ one Hash216 identity topology
→ consistent CLI, ABI, API, SDK, assistant, automation, and Visual IDE surfaces
```

The contract is frozen. Completion requires implementation, tests, manifests, receipts, replay evidence, integration validation, and authoritative-main verification.

Companion explanation:

```text
docs/pass191/HHS_DYADIC_QUARTIC_PHASE_LATTICE_AND_HARMONICODE_EXPLANATORY_ESSAYS.md
```

## 8. Anti-drift rules

### No execution logic in

```text
API routes
WebSocket handlers
GUI components
compatibility shims
provider adapters
storage adapters
```

### All authoritative mutation flows through

```text
registered operation or symbolic transformation
→ typed state proposal
→ VM81 admission
→ kernel audit
→ receipt emission
→ replay-verifiable persistence
```

### Prohibited

- redefining Hash72;
- bypassing Manifold9 or drift gates where required;
- introducing an alternate receipt authority;
- replacing exact canonical arithmetic with floats;
- silently collapsing `xy` and `yx`;
- stripping identity-bearing list width or leading zeros;
- direct state mutation without patch and receipt;
- frontend fabrication of backend status;
- treating contract text as proof of implementation completion;
- weakening validation to accommodate path or environment errors.

## 9. Replay authority

Replay reconstructs execution; it is not merely debugging.

Replay must verify:

- parent continuity;
- receipt identity;
- ordered transition history;
- expected chain tip;
- deterministic equivalence;
- witness integrity;
- locked/quarantined status.

A replay mismatch must produce an explicit failure, quarantine, rollback boundary, or unresolved status. Silent continuation is forbidden.

## 10. Validation entry points

Repository baseline:

```bash
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
```

Pass 190 Iteration 7:

```bash
make -C native_projects/hhs_pass190_operation_fabric validate
```

Path, environment, and deployment errors should be repaired at the adapter boundary. Canonical invariant checks must remain intact.

## 11. Final architectural principle

HHS is not a bag of unrelated utilities. It is one receipt-governed execution system exposed through multiple compatibility, native, service, assistant, and visual surfaces.

Every layer must preserve:

```text
exact meaning
ordered identity
single mutation authority
receipt continuity
replayability
bounded closure
explicit failure
restartable repository-visible state
```
