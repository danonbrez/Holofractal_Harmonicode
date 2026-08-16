# Pass 218 Iteration 46 — restart checkpoint

## Repository identity

- Frozen parent: Pass 218 Iteration 45
- Parent commit: `64f3a8acea92775f015400eac7e1e07f0707acfb`
- Parent tree: `9757f3648b6b07b52a62dddba719096f973aaf59`
- Branch: `agent/pass218-full-iteration46-manifest-bound-i32-source-closure`
- Merge target: `main`
- Main observed before I46 work: `5cbb85ca33031e1ae2c072491271b66ec967dfde`
- Frozen I45 PR: #255 remains the unmerged predecessor boundary.
- Pre-checkpoint implementation head: `f5f73c4480f4d67da5cad6cfa0c4d9a29a906cb1`

## Iteration boundary

I46 consumes only the exact durable I45 manifest-bound I31 purge receipt/proof, the exact frozen-I31 receipt that I45 sealed, and the already durable nonverbatim manifest identity proven earlier in the frozen I34→I42 lineage. The I45→I44→I43→I42 receipt chain must remain exact, and I42's six shared identity fields — curriculum identity and position, source id and SHA-256, source authority, and rights class — must equal the active frozen-I34 manifest source-ingress receipt before I32 can run.

The frozen-I32 `Pass218I32ClosureRequest` is derived internally. Its purge roots and Hash216 come from the exact durable I31 receipt; its source/curriculum identity, source stage, and previous closure come from the exact durable I34 receipt. The I46 HTTP membrane accepts only an empty intent object and exposes no field with which a caller can replace these identities.

Fresh execution requires an empty frozen-I32 closure store and invokes frozen `Pass218I32SourceCloser.close` exactly once. I46 verifies the durable I32 closure receipt, source-closure Hash72, closure Hash216, and closure-chain root, then verifies the complete I30 semantic generation and canonical root are byte-for-byte unchanged across closure.

Restart recovery inspects durable I32 state first. If frozen I32 committed the exact manifest-bound closure but I46 persistence was interrupted, I46 adopts and verifies that durable closure without a duplicate I32 invocation. An unrelated I32 closure, broken predecessor receipt chain, mismatched I34/I42 source identity, or changed I30 generation fails closed.

I46 ends at exact frozen-I32 status `SOURCE_CLOSED_PENDING_CURRICULUM_ADVANCE`, wrapped by `MANIFEST_BOUND_I32_SOURCE_CLOSURE_COMPLETE`. It must not invoke I33, advance the curriculum cursor or stage, mutate VM81, perform canonical learning, promote truth, mint action authority, activate a model, retain verbatim source content, claim physical-memory/external-storage erasure, or create authoritative floating-point state.

## Additive/modified files

1. `hhs_runtime/pass218/manifest_bound_i32_source_closure_i46.py`
2. `hhs_backend/runtime_os_pass218_manifest_i32_source_closure_i46.py`
3. `hhs_backend/runtime_os_application_server.py`
4. `tests/pass218/test_pass218_iteration46_manifest_bound_i32_source_closure.py`
5. `scripts/pass218_iteration46_manifest_i32_source_closure_validation.py`
6. `.github/workflows/pass218-full-iteration46.yml`
7. `docs/pass218/PASS_218_ITERATION_46_RESTART.md`

Frozen I45, I44, I43, I42, I34, I32, I31, I30, and I33 implementation files are not modified by I46.

## Implementation commits before this checkpoint

1. `7e1919dfec0b246eb9d398922b8cc5d17f694b14` — I46 runtime and durable proof/receipt store.
2. `9d533f6d30e7e478747060b44701934792722c76` — RuntimeOS I46 no-override closure membrane.
3. `262f1e27f97cc72c78d7c55e68e60736a3d4f8e1` — cumulative RuntimeOS application composition through I46.
4. `469e01b6d0aaffa26298d7264dea60cfec18bdb8` — focused I46 exactly-once, restart, mismatch, non-persistence, and API tests.
5. `140c210a21c576ff2d3b4823e1d1c09c1db308ba` — deterministic I46 evidence generator.
6. `f5f73c4480f4d67da5cad6cfa0c4d9a29a906cb1` — dependency-scoped I46 GitHub Actions validation workflow.

## Validation plan

- Python compile of cumulative Pass 218 plus I45/I46 RuntimeOS bindings, application server, tests, and evidence script.
- Global Pass 218 and I45/I46 no-authoritative-float AST gate.
- Focused I46 fresh exactly-one-I32 invocation, restart adoption without duplicate I32, durable replay, unrelated manifest-source rejection, source-payload non-persistence, erasure-claim boundary, and API override rejection.
- Frozen I45/I44/I43/I42/I41/I40/I34/I33/I32/I31/I30/I29/I27/I7/I6/I9 regressions.
- Pass205 native continuation, Pass166 Word2Vec, repository-native crawler, and RuntimeOS production-root acceptance.
- Deterministic I46 evidence on exact head and synthetic merge; payload SHA-256 must match before freeze.
- Full TypeScript RuntimeOS/browser application acceptance and final terminal check matrix.
- Exact I45→I46 compare must retain merge base `64f3a8acea92775f015400eac7e1e07f0707acfb`, report zero behind, and contain only the seven listed files.

## Current state

The complete seven-file I46 candidate is now repository-visible and restartable. Validation is the remaining gate: inspect exact-head CI, repair forward only if a new I46 defect is proven, create/maintain a draft PR against `main`, validate the synthetic merge candidate, compare deterministic evidence payloads, and freeze only after all executable checks are terminal green. No merge to `main` or production deployment is authorized by this iteration request.
