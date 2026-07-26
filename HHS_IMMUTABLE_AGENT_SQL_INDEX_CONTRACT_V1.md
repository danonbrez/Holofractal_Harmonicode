# HHS Immutable Agent SQL Index and Protected Decision-Narrative Contract

Contract ID: `HHS-IMMUTABLE-AGENT-SQL-INDEX-V1`  
Runtime classification: additive inherited-nucleus integration  
Authority boundary: committed-state observation and append-only evidence only  

## 1. Purpose

This contract wires the HHS knowledge, semantic-memory, replay, goal, cognition,
research, toolchain, consensus, and API-transport layers into one immutable SQL
evidence index. The index records database-layer identities, snapshots,
accumulated constraints, bindings between constraints and API geometries,
agent sessions, execution events, and protected natural-language decision
narratives.

The narrative is an execution-derived account of observable decisions and
state transitions. It is not raw hidden chain-of-thought, private scratchpad
content, model activations, or undeclared internal reasoning.

## 2. Canonical topology

```text
Committed VM81/runtime state
        +
Pass 145 semantic propositions, rules, contracts, and objects
        +
Live semantic memory, goals, replay, cognition, research, and consensus
        +
FastAPI method/path/schema/endpoint geometry
        ↓
Writer-only immutable SQLite authority
        ↓
Hash-chained agent events
        ↓
Protected hash-chained decision-narrative records
```

## 3. Indexed database layers

The runtime shall register at least the following layers:

- deterministic runtime-state continuity;
- semantic vector memory;
- deterministic replay;
- adaptive goals;
- agentic cognition;
- autonomous research;
- recursive toolchains;
- distributed consensus;
- multinode goal consensus;
- live cognition coordination;
- API geometry;
- discovered Pass 145 knowledge databases.

Each layer identity shall include its module, storage class, authority class,
schema identity, schema version, and a commitment to its source locator.
Mutable databases shall be represented by append-only state snapshots rather
than by changing an earlier layer record.

## 4. Accumulated constraint ingress

When a Pass 145 database is configured or discovered, the index shall import
without deleting or rewriting the source database:

- `semantic_rules`;
- `semantic_propositions`;
- objects classified as constraints, rules, contracts, propositions, or
  invariants;
- security boundary contracts.

Every imported constraint shall preserve source type, source reference,
authority level, provenance commitments, and database-layer identity.
Duplicate commitments shall not create duplicate canonical constraints.

## 5. API geometry

Every boot-reachable FastAPI operation shall be indexed as immutable geometry
containing:

- HTTP method;
- path template;
- route name;
- endpoint module and qualified name;
- route tags;
- request schema;
- response schema;
- authority classification;
- geometry commitment.

Core authority, immutability, disclosure, evidence, and geometry constraints
shall be explicitly bound to each indexed API surface.

## 6. Agent event chain

Each observed operation shall append an event containing only bounded,
execution-derived facts and commitments:

- session identity;
- ordered sequence;
- event classification;
- originating API geometry when known;
- input commitment;
- output commitment;
- active constraint-set commitment;
- bounded factual summary;
- previous-event commitment;
- current-event commitment.

Events shall cover committed runtime ticks, semantic-memory ingestion and
linking, goals, cognition tasks, predictions, research, toolchains, consensus,
multinode synchronization, initialization, and classified failures.

## 7. Protected narrative chain

Every event shall produce one corresponding narrative record. The narrative
shall:

- describe observable decisions and transitions in natural language;
- avoid raw private chain-of-thought;
- avoid exposing unrestricted prompt or output bodies when commitments are
  sufficient;
- be marked `EXECUTION_DERIVED_DECISION_NARRATIVE`;
- be marked `PROTECTED_AUDIT_ONLY`;
- form an independent append-only hash chain;
- remain inaccessible to the writer connection and generating API tools.

The runtime API shall expose only counts, chain tips, integrity state, and
access-policy classifications. It shall expose no narrative text, narrative
query route, update route, or delete route.

## 8. Immutability controls

The SQLite implementation shall enforce:

- `UPDATE` denial triggers on canonical evidence tables;
- `DELETE` denial triggers on canonical evidence tables;
- foreign-key restriction;
- write serialization;
- WAL journaling;
- full synchronous durability;
- trusted-schema disabling;
- file permission restriction where supported;
- writer-authorizer denial of protected narrative reads;
- writer-authorizer denial of schema dropping, attachment, and immutable-row
  modification.

The following tables are canonical append-only evidence:

```text
database_layers
database_snapshots
api_surfaces
constraints
constraint_bindings
agent_sessions
agent_events
narrative_log
```

## 9. Audit separation

A local audit reader may exist only as an out-of-band, read-only capability. It
shall:

- require a token whose SHA-256 commitment is supplied outside the generating
  API runtime;
- open SQLite in read-only URI mode;
- enable `query_only`;
- provide no mutation operation;
- remain unregistered with FastAPI;
- verify both event and narrative chains.

Possession of the runtime writer object shall not grant audit-reader authority.

## 10. Failure behavior

A failure to write the immutable index shall be observable and classified. It
shall not silently promote a cognition result or grant VM81 mutation authority.
The existing runtime and pass terminal conditions remain inherited and
independent; this integration is additive.

## 11. Acceptance gates

Completion requires evidence that:

1. the index initializes and records its core constraints;
2. known runtime database layers are registered;
3. Pass 145 accumulated constraints are backfilled;
4. API geometries and constraint bindings are committed;
5. concurrent event writes remain ordered;
6. event and narrative chains verify;
7. writer-side narrative reads fail;
8. direct update and delete attempts fail;
9. no FastAPI narrative read, update, or delete route exists;
10. the local audit reader rejects invalid tokens and is query-only;
11. existing cognition, route, server, replay, and kernel tests remain green;
12. native inherited validation remains green.

The terminal classification is:

```text
HHS_IMMUTABLE_AGENT_SQL_INDEX_AND_PROTECTED_DECISION_NARRATIVE_VERIFIED
```
