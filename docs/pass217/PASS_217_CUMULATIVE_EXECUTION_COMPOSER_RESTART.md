# Pass 217 — Cumulative Execution Composer Restart State

## Restart identity

- Workstream: Pass 217 prerequisite — mandatory inherited execution composition and utilization reachability
- Current iteration: Pass 217 Iteration 5 — Cumulative Execution Composer, Checkpoint 9
- Branch: `agent/pass217-cumulative-execution-composer`
- Merge target: `main`
- Workstream base / merge base: `07e514ac88b786c121d8308135fee19b9d30877d`
- Current live `main` observed before this restart update: `191c36164425ed263b940f551409f9404c7c3fd8`
- Latest validated implementation head before this restart-record update: `221ffc516ba1be6b4a840da875a62ae118645761`
- Validation workflow: `Pass 217 Cumulative Execution Composer`
- Checkpoint 9 validation run: `31556963841` — job `93991247483` — `SUCCESS`

At validated implementation head `221ffc51...`, comparison against current `main @ 191c3616...` is intentionally `diverged`: 53 workstream commits ahead, 113 current-main commits behind, with merge base still `07e514ac88b786c121d8308135fee19b9d30877d`. No rebase or merge was attempted because final integration remains a later bounded action after cumulative closure prerequisites.

The restart-record commit itself is documentation-only. The exact implementation authority remains the validated head above.

## Binding execution rule

Inherited capabilities are not considered utilized merely because their modules are present or importable. Every required inherited execution capability must resolve mechanically for the current operation to exactly one of:

- `ACTIVE_IN_PATH` — the inherited callable actually traversed and emitted a concrete witness/root;
- `NOT_APPLICABLE` — operation facts mechanically prove the capability has no applicable execution domain;
- `EXPLICITLY_SUPERSEDED` — a repository-bound later-pass contract explicitly replaces the authority and proves the replacement.

`OPTIONAL_AVAILABLE` is forbidden for inherited core execution capabilities. Partial or malformed applicability context fails closed; it is not downgraded to `NOT_APPLICABLE`.

## Preserved validated foundation — Checkpoints 1–8

Checkpoint 1 made the Pass 043 kernel-derived runtime composer a mandatory pre-handler gate for the production lazy service registry. Validation run `31354829734` succeeded.

Checkpoint 2 added the fail-closed cumulative execution authority model sourced from the Pass 214-frozen Pass 215 optimization profile. Validation run `31355052609`, job `93353078780`, succeeded.

Checkpoint 3 bound production service routes at the shared IO boundary:

- `GET /api/runtime/services`
- `GET /api/runtime/services/status`
- `POST /api/runtime/services/dispatch`

Validation run `31355330668`, job `93353835996`, succeeded.

Checkpoint 4 connected `conformance_decision_cache`, `semantic_composition_cache`, and mechanical `predictive_continuation_cache` applicability. Validation run `31355776730`, job `93355060485`, succeeded.

Checkpoint 5 activated the actual Pass 111 predictive-continuation path. Exact implementation head `d2004ebcf54ad20736d7d1a3fea05af55c8a634c` validated in run `31356115574`, job `93356017137`. Stop/restart commit: `f4117f23bdb13e32539802323076ec9e85bf09e9`.

Checkpoint 6 connected:

```text
reusable_pattern_cache
→ vector_shortlist
→ exact_compatibility_filtering
→ exact_delta_cost_reranking
```

Pass 086 supplies reusable pattern admission; one Pass 205 `retrieve()` traversal supplies the three retrieval witnesses. Exact implementation head `bea55a0a481aaee56e7253f656cb26faceddc8b0` validated in run `31486763564`, job `93763831800`. Restart commit: `edb976b06072bef1fd12c827a01d42034402cd61`.

Checkpoint 7 connected `content_addressed_source_reuse` through the real Pass 165 committed-source reuse branch and preserved the incremental-tokenization boundary. A changed-region incremental tokenizer callable has not been proven; explicit incremental context therefore still fails closed rather than being mislabeled active. Exact implementation head `71a827d55da4774031ec493a93d97ba5e051790e` validated in run `31493307824`, job `93784769816`. Restart commit: `6fcf15a1d5de64c822a44f2ff1d3c121a9ad6716`.

Checkpoint 8 connected:

```text
sparse_5184_projection
→ dependency_complete_frontier
→ residual_only_processing
```

Pass 165 `MultimodalLearningService.project_5184` supplies the exact 81×64 / 5,184-coordinate projection. One Pass 215 Iteration 4 `execute_continuation_delta` traversal supplies dependency-frontier and residual-only witnesses. Exact implementation head `c6055c4258ce193ae089258a9fbfc5b6ec172309` validated in run `31556155721`, job `93988896468`. Restart commit: `7bf7b0540a107fb5a4dab1101e93b1cf892bb726`.

## Checkpoint 9 — completed and validated

Checkpoint 9 connects the next frozen authority slice:

```text
parametric_admission
    → compiled_rom_reuse
    → generator_exception_compression
```

### `parametric_admission`

Repository-native operational authority:

- origin: Pass 213 Iteration 4;
- module: `hhs_backend.runtime.hhs_pass213_parametric_delta_v1`;
- callable: `create_parametric_admission`;
- runtime authority: true.

The inherited callable binds a candidate to an authenticated compiled-ROM base entry and exact opening timestamp boundary, computes exact changed fields, re-evaluates only constraints depending on those fields, reuses authenticated baseline witnesses for unaffected constraints, computes a delta root, and emits a boundary-bound VM81 admission root plus authentication tag.

Checkpoint 9 admits `ACTIVE_IN_PATH` only after:

- request template Hash216 matches the supplied template;
- request base-entry Hash216 matches the supplied compiled-ROM entry;
- request opening-boundary Hash216 matches the supplied exact boundary;
- validation key is present and sufficiently sized;
- the inherited `create_parametric_admission` call succeeds;
- the returned admission validates against the same template, base entry, opening boundary, and key;
- VM81 admission root and authentication tag are concrete.

The validated test changes only `operands.x`, proving constraint `c_x` is re-evaluated while unchanged `context.mode` constraint `c_mode` reuses its authenticated baseline witness.

### `compiled_rom_reuse`

Repository-native operational authority:

- origin: Pass 213 Iteration 1;
- module: `hhs_backend.runtime.hhs_pass213_compiled_rom_v1`;
- callable: `CompiledROMStore.lookup_operation`;
- runtime authority: true.

This is explicitly distinct from the Pass 215 Iteration 4 immutable compiled-block descriptor benchmark analog. Checkpoint 9 does not promote the benchmark analog into runtime authority.

The bridge requires exact binding of:

- operation ID;
- expected compiled-ROM entry Hash216;
- expected compiled-ROM inventory root Hash216.

The inherited store is measured before and after lookup. `ACTIVE_IN_PATH` requires that lookup returns the expected authenticated entry while entry count and inventory root remain unchanged. The traversal witness records VM81 cell, opcode slot, G243 control, and native dispatch identity from the inherited compiled record.

### `generator_exception_compression`

Repository-native operational authority:

- origin: Pass 212;
- module: `hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1`;
- compression callable: `FullHydrationRecoveryRuntime._compress`;
- replay callable: `FullHydrationRecoveryRuntime._decompress`;
- runtime authority: true.

The inherited codec operates over the complete hydration envelope:

```text
40 × 243 × 5,184 = 50,388,480 bits = 6,298,560 bytes
```

There are 9,720 local 5,184-bit leaves. The strict affine codec stores two generator bits per leaf — 19,440 bits / 2,430 seed bytes — plus exact sparse XOR exception positions. If the state is outside that efficient domain, the inherited runtime falls back to raw packed bytes rather than making a false compression claim.

Checkpoint 9's authority path constructs an exact inherited affine-generated hydration state from a declared uniform seed, applies declared exact exception positions through the inherited exception operator, calls the real `_compress`, then calls the real `_decompress` and requires bit-exact state replay.

`ACTIVE_IN_PATH` is admitted only when:

- exception positions are exact integers, in range, and strictly ascending;
- the inherited codec selects `AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR`;
- raw fallback is not used;
- decompression reproduces the exact original 50,388,480-bit state;
- recovered codec and exception count match;
- exception count exactly matches the declared positions;
- compressed payload is strictly smaller than the raw hydration state.

The validated real route case used three exact exceptions and proved the 2,430-byte affine seed basis, strict compression, and replay equality. No float authority or approximate compression path was introduced.

### Mechanical applicability and fail-closed behavior

For each Checkpoint 9 class:

- no exact request domain → `NOT_APPLICABLE` with operation facts;
- a present but malformed request → applicable and fail closed;
- missing internal authority binding for an applicable request → fail closed, not `NOT_APPLICABLE`.

Validated negative cases include:

- parametric request without a bound template/base/boundary/key;
- compiled-ROM request without a bound store;
- out-of-range generator/exception position.

### Checkpoint 9 repository-visible commits

1. `4be01397c2a700dba0d939d97d696b38a8a97464` — add `hhs_runtime/hhs_pass217_checkpoint9_rom_compression_v1.py`.
2. `6c0c238c9fca03eada07a93386207a330f3a0f0f` — wire Checkpoint 9 into the production route composer.
3. `24a72d033f0b70bf3498357b2b44052d6e4a8d47` — add dedicated Checkpoint 9 traversal and negative tests.
4. `221ffc516ba1be6b4a840da875a62ae118645761` — extend the dependency-scoped workflow over Checkpoints 8/9 plus inherited Pass 212/213 runtime authority; exact validated implementation head.

### Checkpoint 9 validation

Hosted validation authority:

- workflow: `Pass 217 Cumulative Execution Composer`;
- run: `31556963841`;
- job: `93991247483` (`dependency-scoped-validation`);
- exact head: `221ffc516ba1be6b4a840da875a62ae118645761`;
- conclusion: `SUCCESS`;
- checkout: success;
- Python setup and targeted pytest dependency: success;
- compile stage: success;
- cumulative-composer pytest stage: success.

The workflow now directly compiles and/or exercises:

- Checkpoint 8 and Checkpoint 9 bridges;
- Pass 212 full hydration generator/exception codec;
- Pass 213 compiled-ROM runtime;
- Pass 213 parametric delta/admission runtime;
- dedicated Checkpoint 8 and Checkpoint 9 test files;
- all prior cumulative-composer dependency-scoped tests.

No exact pytest count is claimed here because the workflow job summary was used as validation authority and no test-count extraction was required.

## Files added or modified by Checkpoint 9

Added:

- `hhs_runtime/hhs_pass217_checkpoint9_rom_compression_v1.py`
- `tests/test_hhs_pass217_checkpoint9_rom_compression_v1.py`

Modified:

- `hhs_runtime/hhs_pass217_runtime_route_composer_v1.py`
- `.github/workflows/pass217-cumulative-execution-composer.yml`
- this restart record

The inherited Pass 212 and Pass 213 runtime sources were exercised as-is and were not modified.

## Current cumulative connected authority scope

The production route composer now mechanically disposes these fifteen required inherited classes on every bound service-route operation:

```text
conformance_decision_cache
semantic_composition_cache
predictive_continuation_cache
reusable_pattern_cache
vector_shortlist
exact_compatibility_filtering
exact_delta_cost_reranking
content_addressed_source_reuse
incremental_tokenization
sparse_5184_projection
dependency_complete_frontier
residual_only_processing
parametric_admission
compiled_rom_reuse
generator_exception_compression
```

An admitted operation has no `OPTIONAL_AVAILABLE` state in this scope.

## Deliberately not yet claimed

Checkpoint 9 does **not** claim full Pass 217 cumulative closure. Still pending:

- continue remaining Pass 214/215 authority traversal after `generator_exception_compression`;
- preserve the unresolved incremental-tokenization fail-closed boundary unless an inherited callable or explicit supersession is proven;
- publish production service route bindings into global Pass 042 surface-map discovery rather than deriving them only at the shared IO boundary;
- add systematic bypass-negative tests proving omission of every applicable inherited authority blocks execution;
- gate Pass 217 closure on complete cumulative utilization reachability;
- perform final integration against then-current `main`, resolve both lineages without discarding either, merge, and verify `main`.

## Exact next bounded action

Continue Pass 217 Iteration 5 with the next frozen authority slice after `generator_exception_compression`:

```text
physical_recovery
    → receipt_vector_indexing
    → sql_context_graph
```

Map each class to exact inherited repository-native authority first. Distinguish operational recovery/index/context-graph callables from benchmark observations. Implement one real traversal wherever inherited authority is proven; emit mechanical `NOT_APPLICABLE` only from operation facts; fail closed on partial applicable context; preserve repository-bound `EXPLICITLY_SUPERSEDED` semantics; run only dependency-scoped validation; commit the bounded slice; update this restart record before proceeding to encrypted-vector-store/snapshot/learning/routing/native-dispatch authorities.

Do not rerun unchanged historical proof suites merely because `main` advances. Final current-main integration remains a later bounded stage after cumulative closure prerequisites are complete.
