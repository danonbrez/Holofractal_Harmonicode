# Pass 219 — Lane 5 Automatic Superedge Promotion and Routing 1.42

Status: **ADDITIVE / EXACT-CROSS-LEVEL-ROUTING / INTEGER-COST / AUTO-PROMOTION / CANDIDATE-ONLY**

Base authority: verified `main` at `e94d00d242c25e915989be0013e0124e478dc005`, the merge of PR #454 / Lane 5 Superedge Hierarchy 1.41.

## 1. Purpose

1.41 establishes a persistent recursive superedge hierarchy. Direct reuse of any authenticated superedge performs one encrypted terminal-snapshot retrieval regardless of the number of lower-level transitions represented by the node.

1.42 makes that hierarchy operational as an automatic candidate-routing layer. It adds two deterministic services:

1. **cross-level exact routing** over level-0 persistent edges and level-1..n superedges;
2. **automatic promotion** of repeatedly reused exact routes when promotion strictly reduces future persistent retrieval count.

No 1.42 decision may create canonical VM81 state, mint Hash72/Hash216 authority, or bypass signed environmental VM81 admission.

## 2. Unified candidate graph

The routing graph contains active candidate edges from both inherited stores:

```text
level 0 : Pass 219 1.39 persistent validated jumps
level n : Pass 219 1.41 persistent superedges, n >= 1
```

Each routing edge exposes only already-authenticated metadata:

```text
candidate_id
candidate_kind = LEVEL0 | SUPEREDGE
hierarchy_level
parent_hash216
child_hash216
represented_span
base_hops
layer_index
lineage_seal
```

An edge is routable only when its exact parent Hash216 equals the current graph vertex. Superedges additionally require their complete flattened level-0 dependency set to remain live.

## 3. Exact route selection

For current state `S` and requested exact goal `G`, 1.42 searches the unified graph by exact Hash216 adjacency only.

A plan is admissible iff

```text
Hash216(S) == first.parent_hash216
edge_i.child_hash216 == edge_(i+1).parent_hash216
last.child_hash216 == G
all selected dependencies are live
all selected candidates are non-quarantined
```

The optimization objective is integer and lexicographic:

```text
cost(plan) = (
    persistent_snapshot_retrievals,
    maximum_hierarchy_level,
    sum_hierarchy_levels,
    represented_span,
    ordered_candidate_ids
)
```

The first term is authoritative. A higher-level superedge is selected only when it lowers retrieval count or wins a later deterministic tie-break without changing exactness.

Floating point is forbidden from route admission and cost comparison.

## 4. Mixed-level paths

A route may mix levels:

```text
LEVEL0 -> SUPEREDGE(level 2) -> LEVEL0
```

provided every adjacency is exact. This permits 1.42 to use the best available compressed work representation without requiring the whole route to exist at one hierarchy depth.

The route planner is bounded by `max_retrievals`. It must fail closed rather than return an approximate terminal state when no exact route reaches the requested goal inside that bound.

## 5. Automatic promotion observations

1.42 stores a durable observation ledger keyed by immutable route identity:

```text
route_kind
start_hash216
goal_hash216
layer_index
ordered_component_ids
```

The ledger stores only exact authenticated reuse observations. Rejected, approximate, quarantined, or malformed routes do not increment promotion counts.

For an exact route `R`, automatic promotion is legal only when

```text
observation_count(R) >= promotion_threshold
retrieval_count(R) >= 2
promotion_gain(R) = retrieval_count(R) - 1 >= 1
```

The default promotion threshold is the exact integer `2`.

## 6. Deterministic promotion identity

Automatic promotion IDs are deterministic functions of immutable route identity:

```text
promotion_id = "auto-se-" || SHA256(route_identity)[0:32]
```

Re-observing the same immutable route therefore converges on the same promotion ID. 1.41 collision checks remain authoritative and reject any ID reuse with different immutable lineage.

## 7. Promotion classes

1.42 automatically promotes two route classes supported by 1.41:

```text
LEVEL0_PATH      -> 1.41 promote_path(...)
SUPEREDGE_CHAIN  -> 1.41 promote_superedges(...)
```

A mixed-level route may be selected and reused by 1.42, but is not recursively promoted until a later contract defines a mixed-component superedge constructor. This restriction prevents 1.42 from silently weakening 1.41 lineage semantics.

## 8. Route execution

After a plan is selected, execution reuses each selected candidate through its inherited authenticated API:

```text
LEVEL0     -> Pass219Lane5PersistentHash216CompositionMemory.reuse
SUPEREDGE  -> Pass219Lane5SuperedgeHierarchy.reuse
```

1.42 verifies the resulting child Hash216 after every retrieval. Represented VM81 transitions remain unexecuted during candidate reuse.

For a selected plan of `r` edges:

```text
persistent_snapshot_retrievals = r
intermediate_vm81_transitions_executed = 0
represented_transition_work = sum(edge.represented_span)
```

Canonical mutation still requires the inherited signed environmental VM81 admission path after candidate recovery.

## 9. Native routing membrane

Every accepted 1.42 plan is checked by the exact C ABI. The native descriptor binds:

```text
retrieval_count
base_hops
represented_span
max_hierarchy_level
phase_slot
cycle_index
layer_index
parent_hash216 signature
goal_hash216 signature
route_hash216 signature
exact adjacency
exact target closure
live dependencies
integer-cost selection
candidate-only authority
```

The native membrane rejects zero-signature plans, malformed counts, non-exact closure flags, canonical-authority escalation, or loss of signed environmental VM81 admission.

## 10. Authority boundary

```text
cross-level exact routing                         = TRUE
automatic repeated-route promotion                = TRUE
durable exact observation ledger                  = TRUE
integer-only routing cost                         = REQUIRED
exact Hash216 adjacency                           = REQUIRED
exact target closure                              = REQUIRED
mixed-level candidate routing                     = ALLOWED
mixed-level recursive promotion                   = FALSE
GPU/vector equal-cost ranking                     = OPTIONAL / NON-AUTHORITATIVE
candidate-only                                    = TRUE
canonical VM81 mutation authority                 = FALSE
canonical Hash72 authority                        = FALSE
canonical Hash216 authority                       = FALSE
canonical persistence authority                   = FALSE
PQC key authority                                 = FALSE
receipt-clock authority                           = FALSE
floating-point canonical authority                = FALSE
signed environmental VM81 admission               = REQUIRED
```

## 11. Acceptance gates

1. Exact ABI builds and exports 1.42 version, authority, and plan-validation symbols.
2. Native positive and negative routing descriptors pass strict C11 validation.
3. Six persisted level-0 edges are created and two level-1 superedges plus one level-2 superedge are available.
4. Cross-level routing selects the minimum-retrieval exact representation of the requested target.
5. A mixed route containing level-0 and superedge candidates executes with exact Hash216 adjacency and exact terminal equality.
6. Two authenticated observations of the same three-edge level-0 route trigger one deterministic level-1 promotion.
7. Restart preserves the observation count and deterministic promotion identity.
8. A repeated exact superedge chain triggers a higher-level promotion through 1.41.
9. Quarantined dependencies are excluded before routing and cannot increment observations.
10. Wrong-parent, impossible-goal, zero-retrieval, non-exact-target, and canonical-authority-escalation cases fail closed.
11. Inherited 1.41/1.40/1.39/1.38/1.37, Pass194, Pass207, and Lane 5 authority regressions remain green.
