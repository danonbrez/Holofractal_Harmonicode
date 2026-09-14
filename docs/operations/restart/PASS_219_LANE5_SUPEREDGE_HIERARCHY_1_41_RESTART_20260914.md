# Pass 219 — Lane 5 Superedge Hierarchy 1.41 Restart Record

Date: 2026-09-14

## Repository state

```text
base main: 7aec75207b3baa4c760325c98c3452ed190cfee5
branch: agent/pass219-lane5-superedge-hierarchy-1-41-20260914
merge target: main
validated implementation head: 40a5da3d8ee8c600c5035d3504476780b953e4fe
dedicated green workflow: 34837270128
```

Base main is the verified merge of PR #452 / Lane 5 Recursive Hash216 Composition Graph 1.40.

## Implemented target

1.41 promotes authenticated 1.40 routes into restart-rehydratable persistent superedges. A level-1 superedge represents an ordered route of persistent 1.39 edges. Higher levels recursively compose lower superedges while retaining an ordered flattened list of all level-0 leaf jumps.

For a promoted superedge `E*`:

```text
E*.parent_hash216 = first component parent
E*.child_hash216  = final component child
E*.total_span     = sum(component total_span)
E*.base_hops      = sum(component base_hops)
level(E*)         = 1 + max(level(component_i))
```

Every superedge owns a dedicated Pass174/194 encrypted terminal 648-byte VM5184 snapshot. Direct reuse therefore performs one authenticated snapshot retrieval and zero component snapshot retrievals or represented intermediate VM81 transitions.

## Implemented files

```text
contracts/pass219/PASS_219_LANE5_SUPEREDGE_HIERARCHY_1_41.md
hhs_runtime/include/hhs_pass219_lane5_superedge_hierarchy_1_41.h
hhs_runtime/c/hhs_pass219_lane5_superedge_hierarchy_1_41.inc
hhs_python/runtime/hhs_pass219_lane5_superedge_hierarchy_bridge.py
hhs_backend/runtime/hhs_pass219_lane5_superedge_hierarchy_1_41.py
hhs_runtime/include/hhs_runtime_exact_abi.h
hhs_runtime/c/hhs_runtime_exact_abi.c
tests/pass219/test_pass219_lane5_superedge_hierarchy_1_41.c
tests/pass219/test_pass219_lane5_superedge_hierarchy_1_41.py
.github/workflows/pass219-lane5-superedge-hierarchy-1-41.yml
docs/operations/restart/PASS_219_LANE5_SUPEREDGE_HIERARCHY_1_41_RESTART_20260914.md
```

## Repair-forward history

Dedicated workflow `34836753091` established that the initial implementation had one fail-closed defect: an existing `superedge_id` was treated as idempotent without comparing the immutable requested route identity. The gate result was `1 failed, 18 passed` and identified only `test_superedge_wrong_parent_and_id_collision_fail_closed`.

Repair commit `40a5da3d8ee8c600c5035d3504476780b953e4fe` now:

- computes the complete requested hierarchy/metadata identity before existing-ID acceptance;
- returns idempotently only when all immutable hierarchy fields match exactly;
- rejects an ID collision with a different route, endpoint, hierarchy, component lineage, flattened leaf set, span, phase/cycle, or layer;
- admits VM5184 words through exact integer `operator.index` semantics and rejects fractional or overflowing words instead of truncating them;
- preserves empty-search candidate behavior without relaxing exact parent selection.

## Dedicated validation — GREEN

Workflow `34837270128` completed successfully against exact implementation head `40a5da3d8ee8c600c5035d3504476780b953e4fe`.

```text
static superedge hierarchy contract gate                  PASS
make clean && make c-abi                                  PASS
1.41 + inherited symbol audit                             PASS
strict native 1.41 C membrane                             PASS
real persistent recursive superedge integration           PASS
inherited Pass194 encrypted-storage regression            PASS
inherited Lane5 1.34 native authority regression          PASS
```

Native result:

```text
PASS219_LANE5_SUPEREDGE_HIERARCHY_PASS level=2 components=2 base_hops=6 span=39 receipt=4371393688048492118
```

Primary Python integration bundle:

```text
19 passed, 1 warning in 2.63s
```

Inherited Pass194 storage regression:

```text
7 passed, 1 warning in 0.23s
```

The warning is the inherited pytest `asyncio_mode` configuration warning and does not affect the scoped tests.

## Evidence established

- six exact Pass205-validated persistent level-0 edges are constructed with spans `4,6,8,5,7,9`;
- `super-A` promotes the first three edges into level 1 with span 18 and three flattened base hops;
- `super-B` promotes the next three edges into level 1 with span 21 and three flattened base hops;
- process restart reconstructs both level-1 superedges from durable encrypted storage;
- level-1 direct reuse retrieves one encrypted terminal snapshot, no component snapshots, and executes zero represented intermediate VM81 transitions;
- inherited 1.37/Pass207 Hash216 vector ranking finds the exact `super-A` child with distance zero from the exact parent state;
- `super-A + super-B` promote into `super-AB`, a level-2 superedge with span `18 + 21 = 39` and six ordered flattened level-0 leaves;
- second process restart reconstructs and directly reuses the level-2 superedge through one encrypted snapshot retrieval;
- the recovered terminal 81-word VM5184 state equals the exact sixth-edge terminal candidate;
- quarantining underlying `edge-2` transitively revokes dependent `super-AB` reuse and quarantines the dependent superedge;
- wrong parent state fails exact Hash216 admission;
- a reused `superedge_id` with a different immutable hierarchy identity fails closed as a collision;
- tampered stored component order is isolated/quarantined on restart without taking down an unrelated valid superedge;
- fractional VM5184 words are rejected as non-exact rather than silently truncated;
- inherited 1.40/1.39/1.38/1.37, Pass207, Pass194, and Lane5 1.34 behavior remains green.

## Work relation

For a superedge hierarchy node `E*` reused `r` times:

```text
represented_transition_work(E*, r) = E*.total_span * r
represented_base_hops(E*, r)       = E*.base_hops * r
persistent_snapshot_retrievals      = r
component_snapshot_retrievals       = 0
intermediate_vm81_transitions        = 0
```

At hierarchy depth `n`, the stored node remains a one-snapshot candidate retrieval regardless of the number of recursively represented lower-level edges, while the complete ordered level-0 provenance remains bound into the hierarchy and metadata Hash216 seals.

This is deterministic state-graph work reuse and provenance compression. It is not a physical latency claim.

## Authority boundary

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
signed environmental VM81 admission              = REQUIRED
```

## Environment state

Repository mutations were performed directly through the authorized GitHub integration. No nested coding agent or external handoff was used. Validation used the deterministic Pass207 CPU-reference backend for semantic equality; no physical nanosecond latency claim is introduced.

## Next action

Open the 1.41 PR against `main`, consume the dedicated PR-head 1.41 gate, merge when dependency-scoped validation remains green, verify the merged main SHA and aggregate exact ABI, then advance to automatic superedge promotion/routing policy only as an additive candidate-search layer.

## Blockers

No known semantic or implementation blocker at the validated implementation head.
