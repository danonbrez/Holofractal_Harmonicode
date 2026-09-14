# Pass 219 — Lane 5 Superedge Hierarchy 1.41

Status: **ADDITIVE / RECURSIVE-SUPEREDGE / HASH216-SEALED / RESTART-REHYDRATABLE / CANDIDATE-ONLY**

Base authority: verified `main` at `7aec75207b3baa4c760325c98c3452ed190cfee5`, the merge of PR #452 / Lane 5 Recursive Hash216 Composition Graph 1.40.

## 1. Purpose

1.40 can recover and reuse an ordered route of persistent 1.39 edges without re-executing the represented VM81 transitions, but reuse still performs one authenticated persistent retrieval per route edge.

1.41 promotes a validated route into one **superedge** with its own encrypted terminal VM5184 snapshot and immutable recursive lineage. A superedge may itself become a component of a higher-level superedge.

For a validated route

```text
E_0 -> E_1 -> ... -> E_(h-1)
```

promotion constructs

```text
E* = Compose(E_0, E_1, ..., E_(h-1))
```

such that

```text
E*.parent_hash216 = E_0.parent_hash216
E*.child_hash216  = E_(h-1).child_hash216
E*.total_span     = sum(E_i.total_span)
E*.base_hops      = sum(E_i.base_hops)
```

and direct reuse of `E*` requires exactly one authenticated encrypted snapshot retrieval.

## 2. Hierarchy

Level zero is the inherited persistent 1.39 edge set:

```text
level(E_i) = 0
base_hops(E_i) = 1
```

A promoted superedge has

```text
level(E*) = 1 + max(level(component_i))
```

with at least two ordered components.

The recursive hierarchy is therefore

```text
level 0: persistent validated jumps
level 1: superedges over level-0 jumps
level 2: superedges over level-1 and/or lower superedges
...
level n: recursively sealed work-compression edges
```

Each promoted record stores both its immediate ordered component list and its flattened level-0 leaf jump list.

## 3. Exact promotion admission

Promotion is legal only after the represented route has already passed the inherited exact membranes.

For a level-1 promotion, 1.40 `reuse_path` SHALL authenticate every 1.39 edge, prove exact Hash216 adjacency, recover the exact terminal VM5184 candidate, and validate the 1.40 path seal.

For a level >1 promotion, every component superedge SHALL be authenticated by 1.41 reuse, and adjacent components SHALL satisfy exact Hash216 equality:

```text
component_i.child_hash216 == component_(i+1).parent_hash216
```

Promotion does not infer a route from approximate vector similarity and does not mint a child state that has not already been established by lower-level validated candidate memory.

## 4. Immutable recursive lineage

Every superedge stores

```text
superedge_id
level
parent_hash216
child_hash216
route_hash216
hierarchy_hash216
metadata_hash216
component_ids[]
component_levels[]
leaf_jump_ids[]
total_span
base_hops
phase_slot
cycle_index
layer_index
```

The hierarchy seal is

```text
hierarchy_hash216 = Hash216(
  domain ||
  superedge_id ||
  level ||
  parent_hash216 ||
  child_hash216 ||
  route_hash216 ||
  total_span ||
  base_hops ||
  ordered(component_id, component_level, component_seal) ||
  ordered(leaf_jump_ids)
)
```

Changing component order, hierarchy level, endpoint, span, flattened leaves, or any component seal invalidates the hierarchy seal.

## 5. Encrypted terminal snapshot

A promoted superedge receives a dedicated inherited Pass174/194 encrypted vector object containing exactly the terminal 648-byte VM5184 frame.

The vector object SHALL bind

```text
parent Hash72
child Hash72
route/hierarchy operation identity
Hash216 positional index
terminal VM5184 snapshot
represented direct-cost units = total_span
```

The superedge record is restart-rehydratable from durable storage.

## 6. Direct reuse

Given canonical candidate state `S` with

```text
Hash216(S) == E*.parent_hash216
```

1.41 reuse performs:

1. superedge metadata Hash216 verification;
2. hierarchy Hash216 verification;
3. dependency-liveness verification over all flattened level-0 leaf jumps;
4. native 1.41 descriptor verification;
5. one AES-GCM persistent vector retrieval;
6. vector-object identity and Hash216 positional-index verification;
7. terminal VM5184 frame -> child Hash216 regeneration.

The work relation is

```text
represented_transition_work = E*.total_span
base_hops_represented = E*.base_hops
persistent_snapshot_retrievals = 1
intermediate_vm81_transitions_executed = 0
component_snapshot_retrievals = 0
```

## 7. Dependency revocation

A superedge is not allowed to outlive invalidated provenance.

If any flattened level-0 leaf jump becomes quarantined or unavailable, the superedge SHALL fail closed and be quarantined before candidate reuse succeeds.

Higher-level superedges therefore inherit revocation transitively through their flattened leaf set.

## 8. Search integration

Superedges are ordinary **candidate destinations** for inherited 1.37/Pass207 Hash216 vector ranking, but they are not ordinary transition authority.

For a current parent Hash216, active superedges may be ranked by

```text
query_hash216 = target
candidate.hash216 = superedge.child_hash216
candidate.jump_span = superedge.total_span
candidate.lineage_signature = superedge.hierarchy_hash216
```

Exact parent equality remains a precondition before ranking.

## 9. Canonical-authority boundary

```text
recursive superedge hierarchy                    = TRUE
restart-rehydratable superedges                  = TRUE
one-snapshot direct superedge reuse              = TRUE
transitive flattened provenance                  = REQUIRED
Hash216 hierarchy seal                           = REQUIRED
exact component adjacency                        = REQUIRED
leaf quarantine propagation                      = REQUIRED
GPU/vector superedge ranking                     = ALLOWED
candidate-only                                   = TRUE
canonical VM81 mutation authority                = FALSE
canonical Hash72 authority                       = FALSE
canonical Hash216 authority                      = FALSE
canonical persistence authority                  = FALSE
PQC key authority                                = FALSE
receipt-clock authority                          = FALSE
floating-point canonical authority               = FALSE
signed environmental VM81 admission              = REQUIRED
```

## 10. Acceptance gates

1. Cumulative exact ABI builds and exports 1.41 symbols.
2. Native positive and negative superedge descriptor tests pass under strict C11.
3. Build three real persistent 1.39 edges and promote their 1.40 route into one level-1 superedge.
4. Close/reopen the process and reuse the level-1 superedge through exactly one encrypted snapshot retrieval.
5. The level-1 child VM5184 state and Hash216 equal the 1.40 terminal candidate exactly.
6. `total_span` and `base_hops` equal the flattened route sums.
7. Promote two independently valid lower-level superedges into a level-2 superedge and reuse it through one encrypted snapshot retrieval.
8. Level-2 flattened leaf provenance is exact and ordered.
9. Quarantining one underlying level-0 leaf causes dependent superedge reuse to fail closed.
10. Wrong parent, tampered hierarchy metadata, wrong component order, and invalid level fail closed.
11. Inherited 1.40, 1.39, 1.38, 1.37, Pass207, Pass194, and Lane5 1.34 dependency-scoped regressions remain green.
