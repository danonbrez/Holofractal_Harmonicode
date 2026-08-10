# Pass 217 — Cumulative Execution Composer Restart State

## Restart identity

- Workstream: Pass 217 prerequisite — mandatory inherited execution composition and utilization reachability
- Branch: `agent/pass217-cumulative-execution-composer`
- Merge target: `main`
- Base commit: `07e514ac88b786c121d8308135fee19b9d30877d`
- Base role: authoritative `main` at workstream start
- Latest validated implementation head before this restart-record commit: `317f456a8f0d54ba51523683064e499c9c385014`
- Validation workflow: `Pass 217 Cumulative Execution Composer`
- Checkpoint 1 validation run: `31354829734` — `SUCCESS`
- Checkpoint 2 validation run: `31355052609` — dependency-scoped job `93353078780` — `SUCCESS`

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

## Validation note

An inherited `.github/workflows/pass205-repair-validation-base.yml` workflow also triggers on branch pushes and reports failure with no jobs. It is not the validation authority for this workstream. The dedicated Pass 217 cumulative-composer workflow is the dependency-scoped authority for these checkpoints and has passed both validated heads listed above.

## Deliberately not yet claimed

Checkpoints 1–2 do **not** claim that all inherited optimization authorities are already traversed in every applicable production path. Specifically still pending:

- populate live `ACTIVE_IN_PATH` witnesses from actual inherited cache/vector/continuation/delta/hydration/ROM/representation/recovery/native stages rather than synthetic test records;
- mechanically derive `NOT_APPLICABLE` from operation facts at the canonical composer boundary;
- accept `EXPLICITLY_SUPERSEDED` only from repository-bound later-pass contracts;
- route-level enforcement for `/api/runtime/services`, `/api/runtime/services/status`, and other production entrypoints that do not dispatch a service handler;
- production bypass-negative tests proving that omission of an applicable inherited authority blocks execution;
- Pass 217 closure gating on cumulative utilization reachability;
- merge to `main`.

## Exact next action

Checkpoint 3: bind the production runtime service API surfaces into kernel-derived composition so `/api/runtime/services`, `/api/runtime/services/status`, and `/api/runtime/services/dispatch` cannot bypass the composer. Prefer a shared route/IO boundary rather than hand-wiring three independent policies. Add dependency-scoped positive and bypass-negative tests, validate, and update this restart record before wiring deeper Pass 214/215 optimization stages.
