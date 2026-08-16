# Pass 218 Iteration 45 — restart checkpoint

## Repository identity

- Frozen parent: Pass 218 Iteration 44
- Parent commit: `6f04e8504010f634a14a2b3412959aaf5913458b`
- Parent tree: `2217bbcef4c93bf1729b795c0c0c3b62c3ba5c65`
- Branch: `agent/pass218-full-iteration45-manifest-bound-i31-verbatim-purge`
- Merge target: `main`
- Main observed before I45 work: `5cbb85ca33031e1ae2c072491271b66ec967dfde`
- Frozen I44 PR: #253 remains draft/unmerged.

## Iteration boundary

I45 may consume only the exact durable I44 manifest-bound I30 atomic-promotion receipt/proof and the exact durable frozen-I30 generation that I44 verified. I45 must derive the frozen-I31 `Pass218I31PurgeRequest` internally from those durable identities; callers may not supply or override I30/I29 roots, receipts, hashes, purge scope, source payload, or managed-buffer data through the I45 HTTP membrane.

Fresh execution requires an empty frozen-I31 purge store, invokes frozen `Pass218I31VerbatimPurger.purge` exactly once, and verifies that the resulting durable I31 receipt binds the exact I44/I30 promotion. I45 must prove the I30 durable semantic generation and canonical root are byte-for-byte unchanged across I31 execution, managed HHS buffers are absent afterward, the durable nonverbatim store remains valid, and no physical-memory or external-source erasure claim is invented.

Restart recovery must inspect durable I31 state first. If the exact I44-bound I31 purge receipt already exists but I45 persistence was interrupted, I45 may adopt and verify that exact receipt without invoking I31 again. Any quarantine record or unrelated active I31 receipt fails closed.

I45 ends at the exact frozen-I31 status `VERBATIM_PURGE_RECEIPTED_PENDING_CLOSURE`, wrapped by `MANIFEST_BOUND_I31_VERBATIM_PURGE_COMPLETE`. It must not invoke I32 source closure, advance curriculum, mutate VM81, perform canonical learning, promote truth, mint action authority, activate a model, retain source payload, or create authoritative floating-point state.

## Planned additive files

1. `docs/pass218/PASS_218_ITERATION_45_RESTART.md`
2. `hhs_runtime/pass218/manifest_bound_i31_verbatim_purge_i45.py`
3. `hhs_backend/runtime_os_pass218_manifest_i31_verbatim_purge_i45.py`
4. `tests/pass218/test_pass218_iteration45_manifest_bound_i31_verbatim_purge.py`
5. `scripts/pass218_iteration45_manifest_i31_verbatim_purge_validation.py`
6. `.github/workflows/pass218-full-iteration45.yml`
7. `hhs_backend/runtime_os_application_server.py`

Frozen I44, I31, and I30 implementation files are not to be modified.

## Validation plan

- Python compile and global Pass 218 no-authoritative-float AST gate.
- Focused I45 fresh single-purge, restart adoption, durable replay, mismatch/conflict/quarantine, I30-state-preservation, non-persistence, and API-bypass tests.
- Frozen I44/I43/I42/I41/I40/I31/I30/I29/I27/I7/I6/I33/I9 regressions.
- Pass205 native continuation, Pass166 Word2Vec, repository-native crawler, RuntimeOS production-root acceptance.
- Deterministic I45 evidence on exact head and synthetic merge; payload SHA-256 must match.
- Full TypeScript RuntimeOS/browser application acceptance.
- Final terminal check matrix and exact I44→I45 compare.

## Current state

Restart record committed first. Implementation and validation remain to be completed. No merge or deployment is authorized by this iteration request.
