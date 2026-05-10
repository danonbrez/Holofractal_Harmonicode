# ARCHITECTURE.md
# Holofractal Harmonicode (HHS)
# Canonical Runtime Architecture Specification

---

# PURPOSE

This document defines the canonical architectural topology of the
Holofractal Harmonicode (HHS) runtime substrate.

This file exists to prevent:

- architectural drift,
- replay fragmentation,
- execution bypassing,
- semantic divergence,
- runtime duplication,
- compatibility confusion,
- distributed inconsistency.

This document is part of the execution substrate itself.

---

# CORE PRINCIPLE

```text
ALL EXECUTION MUST BE:

deterministic
audited
receipt-linked
replay-verifiable
graph-ingested
consensus-compatible
```

---

# CANONICAL RUNTIME GEOMETRY

```text
Frontend / GUI
        ↓
FastAPI / Transport Layer
        ↓
Runtime Orchestrator
        ↓
Runtime Controller
        ↓
Audited Runtime Layer
        ↓
VM81 / ABI / Receipt System
        ↓
Graph + Persistence + Replay
        ↓
Distributed Consensus Runtime
        ↓
Adaptive Cognition Layers
```

---

# REPOSITORY TOPOLOGY

## Canonical Runtime Layers

| Path | Purpose |
|---|---|
| `hhs_runtime/` | VM81 substrate, ABI, deterministic runtime |
| `hhs_backend/` | orchestration, replay, distributed cognition |
| `hhs_python/` | ctypes bridge, runtime control |
| `hhs_graph/` | graph topology + receipt memory |
| `hhs_storage/` | persistence + replay storage |
| `gui/` | visualization only |
| `docs/` | canonical specifications |

---

# ROOT MODULE POLICY

## Root-Level Files

Root-level modules are:

```text
compatibility shims only
```

Root files MUST NOT become the canonical execution layer.

All new runtime implementation work belongs in:

```text
hhs_runtime/
hhs_backend/
hhs_python/
hhs_graph/
hhs_storage/
```

---

# EXECUTION OWNERSHIP BOUNDARIES

## VM81

### Responsibility

- deterministic execution substrate
- receipt generation
- closure mechanics
- witness propagation
- transport/orientation/constraint fields
- orbit detection
- replay-compatible execution

### MUST NOT

- perform network operations
- perform websocket operations
- mutate semantic memory
- bypass receipt emission

---

## ABI LAYER

### Responsibility

- canonical memory layouts
- runtime struct compatibility
- ctypes compatibility
- websocket packet consistency
- replay serialization stability

### MUST NOT

- contain runtime logic
- contain adaptive cognition
- mutate runtime state

---

## RUNTIME CONTROLLER

### Responsibility

- stepping
- lifecycle
- execution coordination
- runtime state ownership
- deterministic sequencing

### MUST NOT

- bypass audited runtime
- mutate graph memory directly
- perform distributed consensus

---

## RUNTIME ORCHESTRATOR

### Responsibility

- subsystem coordination
- event routing
- graph ingestion routing
- websocket propagation
- replay coordination
- semantic synchronization

### MUST NOT

- directly mutate VM state
- bypass runtime controller
- mutate ABI structures

---

## AUDITED RUNTIME LAYER

### Responsibility

- invariant enforcement
- receipt continuity
- replay verification
- quarantine semantics
- lock enforcement
- fail-closed execution

### MUST NOT

- permit silent mutation
- allow receipt bypass
- allow replay divergence

---

## GRAPH LAYER

### Responsibility

- receipt topology
- replay linkage
- graph persistence
- semantic topology
- distributed graph synchronization

### MUST NOT

- execute runtime logic
- mutate VM state
- bypass replay verification

---

## STORAGE LAYER

### Responsibility

- durable persistence
- replay storage
- vector persistence
- event archival
- sandbox overlays

### MUST NOT

- perform execution logic
- mutate replay ordering
- bypass graph ingestion

---

## REPLAY ENGINE

### Responsibility

- deterministic reconstruction
- replay verification
- replay equivalence
- branch replay
- predictive replay

### MUST NOT

- mutate live runtime
- alter receipts
- bypass persistence

---

## PREDICTION ENGINE

### Responsibility

- trajectory scoring
- attractor detection
- convergence prediction
- replay prioritization

### MUST NOT

- mutate runtime invariants
- directly modify replay history
- override governance layers

---

## ADAPTIVE GOAL ENGINE

### Responsibility

- directional cognition
- goal persistence
- attractor reinforcement
- entropy suppression
- adaptive replay routing

### MUST NOT

- override deterministic invariants
- bypass replay verification
- mutate VM execution

---

## SELF-MODIFICATION GOVERNOR

### Responsibility

- mutation sandboxing
- replay-safe validation
- rollback certification
- semantic drift detection
- invariant preservation

### MUST NOT

- apply unvalidated mutations
- bypass consensus
- bypass rollback certification

---

## DISTRIBUTED CONSENSUS RUNTIME

### Responsibility

- quorum validation
- federated replay reconciliation
- consensus-certified mutations
- distributed rollback authority
- global semantic coherence

### MUST NOT

- permit unilateral mutation authority
- bypass replay reconciliation
- mutate runtime state directly

---

## SEMANTIC MEMORY ENGINE

### Responsibility

- searchable cognition
- semantic indexing
- replay-memory association
- symbolic retrieval
- vector cognition

### MUST NOT

- execute runtime logic
- mutate replay state
- bypass persistence

---

## MULTIMODAL EMBEDDING ROUTER

### Responsibility

- modality projections
- replay-aware embeddings
- cross-modal routing
- semantic transport

### MUST NOT

- execute runtime logic
- mutate replay history
- bypass semantic memory

---

## WEBSOCKET LAYER

### Responsibility

- streaming transport only

### MUST NOT

- contain runtime logic
- contain replay logic
- contain mutation logic
- bypass orchestrator

---

## FASTAPI ROUTES

### Responsibility

- transport only

### MUST NOT

- contain business logic
- mutate runtime directly
- bypass orchestrator
- bypass replay validation

---

# ANTI-DRIFT RULES

## HARD RULES

```text
NO EXECUTION LOGIC IN:
- websocket handlers
- API routes
- GUI layers
- compatibility shims
```

---

## ALL EXECUTION FLOWS THROUGH

```text
runtime controller
↓
audited runtime
↓
receipt emission
↓
graph ingestion
↓
replay validation
```

---

## NO BYPASS POLICY

The following MUST NEVER be bypassed:

- receipt emission
- replay verification
- audited runtime layer
- mutation governance
- rollback certification
- consensus validation

---

# REPLAY AUTHORITY MODEL

## Replay Is Canonical

Replay is NOT:

```text
debug tooling
```

Replay IS:

```text
canonical execution reconstruction
```

---

## Replay Guarantees

Replay must preserve:

- receipt continuity
- parent linkage
- deterministic ordering
- replay equivalence
- graph topology
- invariant continuity

---

## Replay Failure Policy

Replay mismatch MUST trigger:

```text
quarantine
rollback
lock
or consensus arbitration
```

Never silent continuation.

---

# RECEIPT TOPOLOGY

## Receipts Are Immutable

Receipts represent:

```text
audited execution witnesses
```

Receipts MUST remain:

- append-only
- replay-verifiable
- graph-ingested
- parent-linked

---

## Receipt Chain

```text
receipt(n)
    ↓
parent_receipt(n-1)
    ↓
replay continuity
    ↓
graph topology
```

---

# DISTRIBUTED CONSENSUS MODEL

## Distributed Nodes

Nodes MUST synchronize through:

- replay reconciliation
- receipt continuity
- quorum validation
- semantic coherence

---

## Mutation Governance

All distributed mutations MUST be:

```text
sandboxed
↓
replay-validated
↓
drift-scored
↓
consensus-approved
↓
rollback-certified
```

---

# SEMANTIC COGNITION MODEL

## Semantic Memory

Semantic memory is:

```text
searchable cognition
```

NOT:

```text
execution authority
```

---

## Prediction Engine

Prediction is:

```text
trajectory inference
```

NOT:

```text
mutation authority
```

---

## Goals

Goals are:

```text
adaptive routing bias
```

NOT:

```text
invariant override authority
```

---

# MULTIMODAL COGNITION MODEL

## Multimodal Routing

Multimodal routing is:

```text
semantic transport
```

NOT:

```text
runtime execution
```

---

## Modality Isolation

Modality projections MUST NOT:

- mutate runtime state
- alter replay ordering
- bypass semantic memory
- override consensus

---

# GOVERNED RECURSION MODEL

## Recursive Adaptation

Recursive adaptation MUST remain:

```text
replay-safe
consensus-certified
rollback-capable
semantically bounded
```

---

## Self-Modification Policy

All runtime mutations MUST:

1. generate proposal
2. enter sandbox
3. replay validation
4. drift analysis
5. quorum approval
6. rollback certification
7. controlled application

---

# STABLE EXECUTION BASELINES

## VM81

Current authoritative deterministic substrate:

```text
hhs_vm81_runtime_v7_2.c
```

---

## ABI

Canonical ABI layer:

```text
hhs_runtime/c/hhs_runtime_abi.h
```

---

## Runtime Coordination

Canonical orchestration layer:

```text
hhs_backend/runtime/runtime_orchestrator.py
```

---

# ARCHITECTURAL INVARIANTS

## Primary Runtime Invariants

```text
determinism
receipt continuity
replay equivalence
append-only persistence
consensus-certified mutation
rollback recoverability
semantic coherence
distributed replay stability
```

---

# FINAL PRINCIPLE

The HHS runtime is NOT:

```text
a collection of utilities
```

It IS:

```text
a deterministic replay-governed cognitive operating substrate
```

Every layer MUST preserve:

- replay continuity,
- invariant coherence,
- semantic topology,
- deterministic reconstruction,
- distributed recoverability.