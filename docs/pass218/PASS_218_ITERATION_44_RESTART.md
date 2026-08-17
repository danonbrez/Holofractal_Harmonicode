# Pass 218 Iteration 44 — restart checkpoint

## Repository identity

- Frozen parent: Pass 218 Iteration 43
- Parent commit: `9fe61b41369f482de671dbabe8cbaad7e305c42e`
- Parent tree: `ccab1d8c83d0125724ff089779a6278482f5c68b`
- Branch: `agent/pass218-full-iteration44-manifest-bound-i30-atomic-promotion`
- Merge target: `main`
- Main observed before I44 work: `5cbb85ca33031e1ae2c072491271b66ec967dfde`
- Frozen I43 PR: #251 remains draft/unmerged.

## Iteration boundary

I44 may consume only an exact durable I43 authorization plus the transient frozen-I30 `Pass218I30PromotionRequest` whose deterministic fingerprints, grantor, sequence, expected I29 validation identity, validated Hash216, and exact frozen-I30 grant Hash72 equal the durable I43 authority.

Fresh execution may invoke frozen `Pass218I30AtomicSemanticPromoter.promote` exactly once. Before invocation I44 must prove the I30 store is empty. After invocation it must verify the exact durable I30 generation, atomic manifest swap, canonical root, VM5184 authoritative projection/state, candidate seal, round-trip proofs, promotion receipt, and grant identity before persisting its own I44 receipt.

Restart recovery must first inspect durable I30 state. If the exact I43-authorized I30 promotion already exists but I44 persistence was interrupted, I44 must adopt and verify that exact promotion without invoking I30 again. Any unrelated active I30 promotion fails closed.

I44 ends at `ATOMIC_PROMOTION_COMMITTED_PENDING_I31`. It must not invoke I31 verbatim purge, I32 source closure, curriculum advancement, VM81 mutation, canonical learning, truth promotion, action authority, model activation, source retention, or authoritative floating-point state.

## Planned additive files

1. `docs/pass218/PASS_218_ITERATION_44_RESTART.md`
2. `hhs_runtime/pass218/manifest_bound_i30_atomic_promotion_i44.py`
3. `hhs_backend/runtime_os_pass218_manifest_i30_atomic_promotion_i44.py`
4. `tests/pass218/test_pass218_iteration44_manifest_bound_i30_atomic_promotion.py`
5. `scripts/pass218_iteration44_manifest_i30_atomic_promotion_validation.py`
6. `.github/workflows/pass218-full-iteration44.yml`
7. `hhs_backend/runtime_os_application_server.py`

Frozen I43 and frozen I30 implementation files are not to be modified.

## Validation plan

- Python compile and AST no-authoritative-float gate.
- Focused I44 fresh invocation, restart adoption, idempotence, mismatch/conflict, and API tests.
- Frozen I43 and I30 regressions plus required I42/I29/I27 lineage regressions.
- Pass205 native bridge, Pass166, repository-native crawler, RuntimeOS production-root acceptance.
- Deterministic I44 evidence on exact head and synthetic merge; payload SHA-256 must match.
- Full TypeScript RuntimeOS/browser application acceptance.
- Final terminal check matrix and exact I43→I44 compare.

## Current state

Restart record committed first. Implementation and validation remain to be completed. No merge or deployment is authorized by this iteration request.