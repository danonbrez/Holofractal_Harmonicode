# Pass 217 — Cumulative Execution Composer Restart State

## Restart identity

- Workstream: Pass 217 prerequisite — mandatory inherited execution composition and utilization reachability
- Branch: `agent/pass217-cumulative-execution-composer`
- Merge target: `main`
- Base commit: `07e514ac88b786c121d8308135fee19b9d30877d`
- Base role: authoritative `main` at workstream start
- Latest validated implementation head before this restart-record commit: `1ae47ba002cd6fc704013da4d65c9cd4d0fcfa30`
- Validation workflow: `Pass 217 Cumulative Execution Composer`
- Checkpoint 1 validation run: `31354829734` — `SUCCESS`
- Checkpoint 2 validation run: `31355052609` — dependency-scoped job `93353078780` — `SUCCESS`
- Checkpoint 3 validation run: `31355330668` — dependency-scoped job `93353835996` — `SUCCESS`

## Problem being repaired

Inherited capabilities remain implemented, registered, and historically validated, but current live execution can bypass compound inherited execution layers by calling lower-level handlers directly. Capability preservation is therefore stronger than capability utilization.

The repair makes inherited execution composition mandatory rather than optional. An inherited core execution capability must resolve for each operation to exactly one of:

- `ACTIVE_IN_PATH`
- `NOT_APPLICABLE`
- `EXPLICITLY_SUPERSEDED`

`OPTIONAL_AVAILABLE` is forbidden for inherited core execution capabilities.

## Checkpoint 1 — completed and validated

Checkpoint 1 restores the Pass 043 kernel-derived runtime composer as a mandatory pre-handler gate for the production lazy service registry.

Repository-visible commits:

1. `7f07708da80a053992ab8c633bb6972249b41c34` — expose direct kernel-derived composition preflight without rebuilding the full service registry.
2. `7283d9f3495b581404564c0e73d7829bb2db9e2a` — require Pass 043 composition preflight before lazy service execution and bind the resulting composition root into the unified ledger after service dispatch.
3. `65f6994ac9cf35570ea289b757099318b2fc74ee` — add targeted positive, negative, ordering, cache, and ledger-binding tests.
4. `2246d43026bea2071c9b34ab41784b157696103d` — add dependency-scoped validation workflow.

Validated behavior:

- a kernel-derived direct surface is admitted by the inherited Pass 043 composer;
- repeated composition reuses the conformance-decision cache;
- an underived surface is rejected;
- a rejected composition prevents the service handler from running;
- admitted live dispatch order is `composition preflight -> service dispatch -> composition ledger binding`;
- expanded validation metadata is not persisted by the new preflight path;
- changed Python files compile;
- targeted checkpoint tests pass in GitHub Actions.

## Checkpoint 2 — completed and validated

Checkpoint 2 adds a fail-closed inherited optimization-authority reachability model sourced from the Pass 214-frozen Pass 215 optimization profile.

Repository-visible commits:

1. `722136b2a04e2e63831383a180e87a491e7d0b16` — add `hhs_runtime/hhs_cumulative_execution_authority_v1.py`.
2. `0bfcdc9b7ffbb11f6736c5f4fd99789dcb7a6f89` — add authority-state, negative, supersession, no-float, and no-optional tests.
3. `317f456a8f0d54ba51523683064e499c9c385014` — extend the scoped workflow over the new authority model.

The authority inventory is loaded from `contracts/pass215/PASS_215_BENCHMARK_PROFILE.json`. Runtime comparison controls (`dense_reference`, `exact_integer_reference`) are excluded from the per-operation optimization traversal set; `OPTIONAL` accelerator batching and `EXPERIMENTAL` GPU execution are not promoted into inherited core requirements.

Accepted states are exactly:

- `ACTIVE_IN_PATH`: requires an observed traversal, a path containing the exact authority id, a traversal witness, and a witness root;
- `NOT_APPLICABLE`: requires a mechanical predicate, observed facts, an explicit reason, and `mechanically_proven=true`;
- `EXPLICITLY_SUPERSEDED`: requires a later pass than the Pass 214 profile authority, a distinct replacement authority, an explicit contract, a validation root, and proven semantic equality.

Fail-closed behavior validated at exact head `317f456a8f0d54ba51523683064e499c9c385014`:

- missing authority disposition is rejected rather than inferred irrelevant;
- ambiguous dual disposition is rejected;
- weak/non-mechanical `NOT_APPLICABLE` is rejected;
- stale or unvalidated supersession is rejected;
- nested `OPTIONAL_AVAILABLE` is rejected;
- floating-point authority evidence is rejected;
- a fully witnessed accepted authority set validates successfully.

## Checkpoint 3 — completed and validated

Checkpoint 3 binds the three production service-registry API sources to kernel-derived route composition at the shared canonical IO ingress boundary:

- `GET /api/runtime/services`
- `GET /api/runtime/services/status`
- `POST /api/runtime/services/dispatch`

Repository-visible commits:

1. `24d4fbcd3845ac3c741ed518b43f38dd5f2d02eb` — add `hhs_runtime/hhs_pass217_runtime_route_composer_v1.py` with explicit source-to-route/invariant bindings.
2. `56342b02dafdfb8fa64d4590c3e753bc07d7b74a` — enforce route composition in `HHSIOGateway` before runtime access, IO receipt creation, or receipt-backed read reuse.
3. `56f56eb27aeb620b8f109f269606e30bb24b50d1` — add route derivation, mutation-policy, fail-before-runtime, and cache-reuse/no-bypass tests.
4. `1ae47ba002cd6fc704013da4d65c9cd4d0fcfa30` — extend dependency-scoped validation over route and IO enforcement.

Validated behavior:

- all three service API route bindings are Pass 042-compatible, invariant-derived API surfaces;
- service list/status routes inherit guarded-execution, invariant-derived admissibility, zero-bypass, and surface-reachability invariants;
- dispatch additionally inherits ledger-continuity and explicit-mutation-ownership invariants;
- a route-composition rejection occurs before runtime state is read and leaves IO history empty;
- receipt-backed GET reuse still traverses the route composer on the current request;
- the second identical GET may reuse its immutable IO receipt while using the current request's fresh/cached composition proof;
- expanded composition metadata is not persisted;
- exact-head dependency-scoped compile/tests pass at `1ae47ba002cd6fc704013da4d65c9cd4d0fcfa30`.

## Validation note

Inherited historical relay/base workflows also trigger on some branch pushes and may report immediate failure with no relevant jobs. They are not the validation authority for this workstream. The dedicated Pass 217 cumulative-composer workflow is the dependency-scoped authority and has passed all three validated checkpoint heads above.

## Deliberately not yet claimed

Checkpoints 1–3 do **not** claim that all inherited optimization authorities are already traversed in every applicable production path. Specifically still pending:

- publish the new service route bindings into the global Pass 042 surface-map discovery set rather than only deriving them at the shared IO boundary;
- populate live `ACTIVE_IN_PATH` witnesses from actual inherited cache/vector/continuation/delta/hydration/ROM/representation/recovery/native stages rather than synthetic test records;
- mechanically derive `NOT_APPLICABLE` from operation facts at the canonical composer boundary;
- accept `EXPLICITLY_SUPERSEDED` only from repository-bound later-pass contracts;
- production bypass-negative tests proving omission of an applicable inherited optimization authority blocks execution;
- Pass 217 closure gating on cumulative utilization reachability;
- merge to `main`.

## Exact next action

Checkpoint 4: connect the first real inherited optimization stages into the composer with observed traversal witnesses, beginning with Pass 44 semantic composition caching and Pass 111 predictive continuation caching. Preserve applicability boundaries: semantic composition is expected on derived composition planning; predictive continuation is active only when a predecessor/continuation state is mechanically present and otherwise must carry a mechanical `NOT_APPLICABLE` proof. Add these witnesses to the three-state authority record rather than declaring capabilities active merely because their modules exist.
