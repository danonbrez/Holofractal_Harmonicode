# Pass 217 — Cumulative Execution Composer Restart State

## Restart identity

- Workstream: Pass 217 prerequisite — mandatory inherited execution composition and utilization reachability
- Branch: `agent/pass217-cumulative-execution-composer`
- Merge target: `main`
- Base commit: `07e514ac88b786c121d8308135fee19b9d30877d`
- Base role: authoritative `main` at workstream start
- Latest validated implementation head before this restart-record commit: `5a088ec739b28c8778395f23a23f2773636673be`
- Validation workflow: `Pass 217 Cumulative Execution Composer`
- Checkpoint 1 validation run: `31354829734` — `SUCCESS`
- Checkpoint 2 validation run: `31355052609` — dependency-scoped job `93353078780` — `SUCCESS`
- Checkpoint 3 validation run: `31355330668` — dependency-scoped job `93353835996` — `SUCCESS`
- Checkpoint 4 validation run: `31355776730` — dependency-scoped job `93355060485` — `SUCCESS`

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

## Checkpoint 4 — completed and validated

Checkpoint 4 connects the first real inherited optimization stages into the mandatory composer instead of merely proving that their modules exist.

Repository-visible commits:

1. `5a163c21b178feaad20fa4bfab78b8cec2406b2a` — add `hhs_runtime/hhs_inherited_execution_stage_bridge_v1.py`.
2. `76169e1479cf4fa93f9810934cceaa1746bd5fb0` — add real-stage traversal and continuation-applicability tests.
3. `1297af9ac6a79fefabed6b3ad1eedf2fc6c4ccb4` — require the real inherited authority slice on production service API routes.
4. `044ea3d240133ddd82299b39538c7435e7cb839a` — require the same authority slice before direct lazy service-handler execution and ledger-bind its reachability root.
5. `991ba4b809568066514e14ec6750bd00674a0c57` — add service-handler authority rejection/order/binding tests.
6. `90bd06d5dd0f1ddb6bffd7fa66589c89af7c5e60` — extend route tests over real inherited optimization reachability.
7. `5a088ec739b28c8778395f23a23f2773636673be` — extend the dependency-scoped workflow over the stage bridge and all updated production gates.

Validated live authority slice:

- `conformance_decision_cache` — `ACTIVE_IN_PATH` using the actual Pass 043 `get_or_build_decision` cache entry and its Hash72 cache-entry root;
- `semantic_composition_cache` — `ACTIVE_IN_PATH` by actually traversing the inherited Pass 044 dependency-rooted semantic composition cache, validating hits, replacing stale entries, preserving the compact reconstruction recipe, and retaining `expanded_payload_persisted=false`;
- `predictive_continuation_cache` — `NOT_APPLICABLE` only when the operation payload contains no exact Pass 111 continuation-contract marker.

Continuation-bearing requests are deliberately fail-closed at this checkpoint. If any exact Pass 111 continuation marker is observed, `predictive_continuation_cache` is considered applicable but remains without a disposition, so the three-state gate rejects the route/service before execution. No synthetic `ACTIVE_IN_PATH` witness is fabricated.

Checkpoint 4 dependency-scoped validation at exact head `5a088ec739b28c8778395f23a23f2773636673be` passed compilation and all four scoped test suites in workflow run `31355776730`, job `93355060485`.

## Validation note

Inherited historical relay/base workflows also trigger on some branch pushes and may report immediate failure with no relevant jobs. They are not the validation authority for this workstream. The dedicated Pass 217 cumulative-composer workflow is the dependency-scoped authority and has passed all four validated checkpoint heads above.

## Deliberately not yet claimed

Checkpoints 1–4 do **not** claim that all inherited optimization authorities are already traversed in every applicable production path. Specifically still pending:

- wire the real Pass 111 predictive-continuation resume/admission path so continuation-bearing requests can become `ACTIVE_IN_PATH` rather than intentionally blocked;
- publish the new service route bindings into the global Pass 042 surface-map discovery set rather than only deriving them at the shared IO boundary;
- continue populating live `ACTIVE_IN_PATH` witnesses from the remaining Pass 214/215 cache/vector/delta/hydration/ROM/representation/recovery/native stages;
- mechanically derive `NOT_APPLICABLE` only from operation facts at the canonical composer boundary;
- accept `EXPLICITLY_SUPERSEDED` only from repository-bound later-pass contracts;
- add production bypass-negative tests proving omission of any applicable inherited optimization authority blocks execution;
- gate Pass 217 closure on complete cumulative utilization reachability;
- merge to `main`.

## Exact next action

Checkpoint 5: attach the actual Pass 111 predictive continuation machinery when a continuation contract is present. Reuse the existing `PredictiveContinuationEngine`, `ContinuationLease`, cache validation, one-ninth-tail replay, and resume admission rather than creating a parallel continuation implementation. The composer must emit `ACTIVE_IN_PATH` only after a real Pass 111 cache/lease validation and replay/admission witness succeeds. Requests with no continuation context remain mechanically `NOT_APPLICABLE`; malformed/incomplete continuation context must fail closed. Validate, then update this restart record again before broadening to the remaining Pass 214/215 authorities.
