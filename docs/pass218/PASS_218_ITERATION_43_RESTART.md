# Pass 218 Iteration 43 restart record

## Frozen parent

- Iteration 42 head: `b43a079c46be00cb51695cf2d8715f6b5b45ae05`
- Iteration 42 tree: `447a2da89e189825eb5fc72dea5bea45ac031b87`
- Iteration 42 branch: `agent/pass218-full-iteration42-cross-lineage-semantic-equality`
- Iteration 42 draft PR: `#250`

## Iteration 43 branch

`agent/pass218-full-iteration43-manifest-bound-i30-request-authorization`

Merge target remains `main`. This iteration is draft-only and must not merge without separate authorization.

## Boundary

Iteration 43 consumes the exact durable I42 receipt/proof plus a caller-supplied transient frozen-I30 `Pass218I30PromotionRequest`. RuntimeOS reconstructs that typed request through the existing I30 request parser but does **not** call the I30 promoter.

I43 must:

- verify the exact durable I42 receipt and cross-lineage proof;
- require the transient I29 validation request fingerprint to equal the exact I42 fingerprint;
- independently replay frozen I29 for that same typed request;
- require the replayed I29 validation Hash72 and validated Hash216 to equal both the I42 evidence and the explicit I30 request expectations;
- require the fixed frozen-I30 target scope;
- require a separate explicit caller-supplied I30 authority grant (`grantor_authority_hash72` plus exact nonnegative `grant_sequence`);
- derive the exact frozen-I30 authority-grant Hash72 from the replayed semantic witness and exact candidate identity;
- persist only nonverbatim authoritative identities, grant metadata, deterministic request fingerprints, and sealed I43 receipt/proof state.

The complete transient I29/I30 typed request is not persisted. I43 does not call `Pass218I30AtomicSemanticPromoter.promote`, does not perform VM5184 authoritative projection, does not mutate the I30 semantic store, and does not invoke I31/I32, advance curriculum, perform canonical learning, promote truth, mint action authority, activate a model, retain verbatim source, or create authoritative floating-point state.

Expected completion state:

`MANIFEST_BOUND_I30_PROMOTION_REQUEST_AUTHORIZATION_COMPLETE`

This means **AUTHORIZED_PENDING_I30_INVOCATION**, not promoted.

## Planned files

- `hhs_runtime/pass218/manifest_bound_i30_promotion_request_authorization_i43.py`
- `hhs_backend/runtime_os_pass218_manifest_i30_promotion_request_authorization_i43.py`
- `hhs_backend/runtime_os_application_server.py`
- `tests/pass218/test_pass218_iteration43_manifest_bound_i30_promotion_request_authorization.py`
- `scripts/pass218_iteration43_manifest_bound_i30_promotion_request_authorization_validation.py`
- `.github/workflows/pass218-full-iteration43.yml`
- `docs/pass218/PASS_218_ITERATION_43_RESTART.md`

## Validation commands

```bash
python -m py_compile hhs_runtime/pass218/*.py
python -m py_compile hhs_backend/runtime_os_pass218_manifest_i30_promotion_request_authorization_i43.py
python -m py_compile hhs_backend/runtime_os_application_server.py
python -m py_compile scripts/pass218_iteration43_manifest_bound_i30_promotion_request_authorization_validation.py
python -m py_compile tests/pass218/test_pass218_iteration43_manifest_bound_i30_promotion_request_authorization.py
pytest -q tests/pass218/test_pass218_iteration43_manifest_bound_i30_promotion_request_authorization.py
pytest -q tests/pass218/test_pass218_iteration42_manifest_semantic_cross_lineage_equality.py
pytest -q tests/pass218/test_pass218_iteration30_atomic_semantic_promotion.py
pytest -q tests/pass218/test_pass218_iteration29_hash216_vm5184_validation.py
PYTHONPATH="$PWD" python scripts/pass218_iteration43_manifest_bound_i30_promotion_request_authorization_validation.py
pytest -q tests/test_runtime_os_production_root.py
```

The dedicated GitHub workflow must additionally preserve the frozen I41/I40/I27/I7/I6/I33/I9 boundaries, inherited Pass205 continuation ABI, Pass166 Word2Vec behavior, repository-native creative-writing crawler boundary, RuntimeOS production-root acceptance, and deterministic evidence upload.

## Restart semantics

The I43 store is append-only/idempotent for one exact I42 receipt plus one exact typed-I30 promotion-request fingerprint. Re-entry with the same exact request returns the durable I43 receipt without repeating I29 validation or invoking I30. A different I42 receipt, different I29 request fingerprint, different I30 request fingerprint, different grant, changed expected validation identity, changed target scope, or already-active I30 promotion fails closed.

## Deployment state

No merge or production deployment is authorized by this iteration. `main` and production remain untouched.

## Next action

Implement the I43 runtime and RuntimeOS membrane, then run dependency-scoped and exact-head/synthetic validation. A later iteration may consume an exact frozen I43 authorization receipt to invoke I30 exactly once; I43 itself grants no execution beyond durable request authorization.