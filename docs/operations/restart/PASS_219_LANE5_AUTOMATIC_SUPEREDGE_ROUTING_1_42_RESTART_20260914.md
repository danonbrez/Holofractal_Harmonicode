# Pass 219 — Lane 5 Automatic Superedge Routing 1.42 Restart Record

Date: 2026-09-14

## Repository state

```text
base main: e94d00d242c25e915989be0013e0124e478dc005
branch: agent/pass219-lane5-auto-superedge-routing-1-42-20260914
merge target: main
validated implementation head: dc66b6fe18d0dd73e3f65c6e3a711dee60c349e5
dedicated green workflow: 34880050793
```

Base main is the verified merge of PR #454 / Lane 5 Superedge Hierarchy 1.41.

## Implemented target

1.42 turns the persistent 1.41 superedge hierarchy into an exact automatic candidate-routing and repeated-route promotion layer.

The unified graph contains both level-0 persistent 1.39 edges and level-1..n persistent 1.41 superedges. Routing admits only exact Hash216 adjacency and selects a route with the deterministic integer lexicographic cost:

```text
cost(plan) = (
    persistent_snapshot_retrievals,
    maximum_hierarchy_level,
    sum_hierarchy_levels,
    represented_span,
    ordered_candidate_ids
)
```

The primary objective is minimum persistent retrieval count. Mixed-level candidate routes are allowed. Mixed-level recursive promotion remains forbidden in 1.42; automatic promotion uses only the lineage-preserving 1.41 constructors.

## Implemented files

```text
contracts/pass219/PASS_219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42.md
hhs_runtime/include/hhs_pass219_lane5_automatic_superedge_routing_1_42.h
hhs_runtime/c/hhs_pass219_lane5_automatic_superedge_routing_1_42.inc
hhs_python/runtime/hhs_pass219_lane5_automatic_superedge_routing_bridge.py
hhs_backend/runtime/hhs_pass219_lane5_automatic_superedge_routing_1_42.py
hhs_runtime/include/hhs_runtime_exact_abi.h
hhs_runtime/c/hhs_runtime_exact_abi.c
tests/pass219/test_pass219_lane5_automatic_superedge_routing_1_42.c
tests/pass219/test_pass219_lane5_automatic_superedge_routing_1_42.py
.github/workflows/pass219-lane5-automatic-superedge-routing-1-42.yml
docs/operations/restart/PASS_219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42_RESTART_20260914.md
```

## Automatic promotion semantics

The restart-persistent observation ledger records only exact authenticated route reuse. The default promotion threshold is two observations.

For an exact route `R`:

```text
observation_count(R) >= 2
retrieval_count(R) >= 2
promotion_gain(R) = retrieval_count(R) - 1 >= 1
```

then 1.42 may construct the deterministic promotion identifier:

```text
promotion_id = "auto-se-" || SHA256(route_identity)[0:32]
```

and invoke one of the inherited 1.41 constructors:

```text
LEVEL0_PATH     -> promote_path(...)
SUPEREDGE_CHAIN -> promote_superedges(...)
```

The same immutable route therefore converges on the same superedge identity across restart.

## Dedicated validation — GREEN

Workflow `34880050793` completed successfully against exact implementation head `dc66b6fe18d0dd73e3f65c6e3a711dee60c349e5`.

```text
static automatic-routing contract gate                    PASS
make clean && make c-abi                                  PASS
1.42 + inherited exported-symbol audit                    PASS
strict native 1.42 C membrane                             PASS
1.42 + 1.41/1.40/1.39/1.38/1.37 + Pass207 integration   PASS
inherited Pass194 encrypted-storage regression            PASS
inherited Lane5 1.34 native authority regression          PASS
```

Native result:

```text
PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_PASS retrievals=2 base_hops=4 span=26 max_level=1 receipt=14273150116082851010
```

Primary Python integration bundle:

```text
22 passed, 1 warning in 3.57s
```

Inherited Pass194 storage regression:

```text
7 passed, 1 warning in 0.22s
```

The warning is the inherited pytest `asyncio_mode` configuration warning and does not affect the scoped tests.

## Evidence established

- six exact persistent level-0 edges are constructed in one Lane 5 layer;
- the first three-edge exact route requires three persistent retrievals before promotion;
- the first authenticated observation records count 1 and does not promote;
- the second identical authenticated observation records count 2 and creates one deterministic level-1 `auto-se-*` superedge;
- exact routing to the same target then selects that level-1 node and reduces the route to one persistent retrieval;
- process restart preserves the exact observation count and deterministic promotion identity;
- with a pre-existing `super-A`, routing to the fifth-edge target selects the exact mixed route `super-A -> edge-4 -> edge-5`, reducing five level-0 retrievals to three;
- with `super-A` and `super-B`, routing to the sixth-edge target selects two superedges instead of six level-0 edges;
- two authenticated observations of `super-A -> super-B` promote a level-2 deterministic superedge with six flattened base hops and represented span 39;
- routing to the same terminal target then selects the level-2 superedge in one persistent retrieval;
- every selected candidate is reauthenticated through the inherited 1.39 or 1.41 reuse surface and every resulting child Hash216 is regenerated and checked;
- represented intermediate VM81 transitions remain unexecuted during candidate reuse;
- quarantine of a level-0 dependency removes the dependent superedge from routing and blocks promotion observations;
- impossible goals return no exact route rather than an approximate candidate;
- wrong-parent execution fails closed;
- native descriptors reject zero retrievals, malformed base-hop accounting, non-exact closure, dead dependencies, non-integer-cost selection flags, canonical-authority escalation, and invalid phase slots.

## Work relation

For an exact selected route `R = (E_0, ..., E_(r-1))`:

```text
persistent_snapshot_retrievals(R) = r
represented_transition_work(R)    = sum(E_i.represented_span)
represented_base_hops(R)           = sum(E_i.base_hops)
intermediate_vm81_transitions      = 0
```

If repeated exact reuse promotes the route to `E*`, subsequent direct reuse has:

```text
persistent_snapshot_retrievals(E*) = 1
represented_transition_work(E*)    = represented_transition_work(R)
represented_base_hops(E*)           = represented_base_hops(R)
intermediate_vm81_transitions       = 0
```

This is deterministic state-graph work reuse and provenance compression. It is not a physical latency claim.

## Authority boundary

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

## Environment state

Repository mutations were performed directly through the authorized GitHub integration. No nested coding agent or external handoff was used. Validation used the deterministic CPU-reference semantic path for exact equality. No physical latency claim is introduced.

## Next action

Open the 1.42 PR against `main`, consume the dedicated PR-head 1.42 gate, merge after dependency-scoped validation remains green, verify the merged main SHA and aggregate exact ABI, then advance only additively from the verified automatic routing/promotion surface.

## Blockers

No known semantic or implementation blocker at the validated implementation head.
