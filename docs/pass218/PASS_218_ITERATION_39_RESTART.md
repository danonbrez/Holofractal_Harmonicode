# Pass 218 Iteration 39 — Restart Record

## Repository checkpoint

- Frozen parent: Pass 218 Iteration 38 head `6a90fa54a5cfbd589051378cf8d989e711214b29`.
- Branch: `agent/pass218-full-iteration39-manifest-bound-canonical-prepare-ingress`.
- Merge target: `main`.
- Main was `5cbb85ca33031e1ae2c072491271b66ec967dfde` when I39 began.
- This branch must remain draft/unmerged until exact-head and synthetic-merge validation are terminal.

## I39 purpose

Iteration 39 binds the exact durable I38 promotion authorization and exact frozen I36 staged VM5184 candidate to the **prepare half only** of the frozen Iteration-6 canonical commit boundary.

Frozen I6 already defines canonical admission as:

```text
active exact I5 authorization
        +
exact I4 staged candidate
        ↓
I6 prepare
        ↓
64-lane shadow VM81 image = exact 648-byte / 5,184-bit projection
        ↓
I6 atomic canonical commit
        ↓
I6 canonical receipt
```

I39 intentionally stops after `I6 prepare`.

The reason is restartability: frozen I7 is the durable canonical persistence boundary. Performing the I6 atomic canonical mutation in I39 without simultaneously establishing the exact durable I7 restart state would create a canonical state change whose persistence boundary has not yet been bound into the current manifest lineage.

## Frozen boundary established by I39

```text
frozen I38 durable authorization receipt/envelope
        +
exact frozen I37 promotability proof
        +
exact frozen I36 manifest-bound I4 stage
        ↓
revalidate I36→I38 identity and manifest lineage
        ↓
read-only durable I38 authorization-journal view
        +
exact frozen I4 staged candidate
        ↓
frozen I6 Pass218CanonicalCommitBoundary.prepare()
        ↓
64 VM81 shadow lane commits
        +
exact 648-byte / 5,184-bit shadow image
        +
VM81_ADMITTED shadow entry
        +
I6 prepare Hash72 / validation Hash72 / Hash216
        ↓
noncanonical durable I39 prepare envelope + binding receipt
        ↓
MANIFEST_BOUND_CANONICAL_PREPARE_INGRESS_COMPLETE
```

## Authority boundary

I39 may establish:

- exact I38 receipt bound;
- exact I37 proof bound;
- exact I36 stage bound;
- exact I5 authorization bound;
- frozen I6 `prepare` invoked;
- complete 64-lane VM81 **shadow** preparation;
- exact I6 prepare and validation receipts;
- a deterministic target-root-before-commit identity.

I39 must not establish or claim:

- frozen I6 `commit` invocation;
- canonical Pass-217 vector mutation;
- canonical VM81 commit;
- I7 durable canonical persistence;
- canonical learning;
- truth promotion;
- action authority;
- Pass 218 I30 semantic promotion;
- I31 purge or I32 source closure;
- curriculum cursor or stage advancement;
- model activation;
- source/verbatim persistence;
- authoritative floating-point state.

`vm81_prepare_commit_count == 64` refers only to the isolated frozen-I6 shadow runtime. It is not canonical VM81 authority or a canonical VM81 commit.

## I5 authorization handling

I38 already performed the explicit frozen-I5 grant and authorization. I39 does not mint another grant and does not call `PromotionAuthorizationJournal.authorize()` again.

Instead, `DurableI38AuthorizationJournalView` exposes the exact already-persisted I38 authorization through the frozen I6 journal protocol. Before that view is used, I39 independently validates the frozen I5 proof, grant, authorization identity, Hash72/Hash216 lanes, candidate binding, projection binding, scope, and pending-canonical-commit state.

## Durable I39 state

The I39 store persists only:

- the I39 receipt;
- the manifest-bound serialized frozen-I6 prepare record;
- the state pointer/root.

It does **not** persist:

- source text or source bytes;
- the frozen I4 `vm5184_projection_b64` payload;
- a canonical Pass-217 target mutation;
- a canonical VM81 image;
- I7 checkpoint state.

The serialized frozen-I6 prepare record contains hashes, entry identities, the deterministic pre-commit target root, VM81 shadow state/snapshot hashes, the 64-lane receipt root, and the I6 prepare Hash216. It is sufficient to prove what I39 prepared without pretending the canonical target has changed.

## Replay behavior

- Same-process replay returns the durable I39 receipt without invoking frozen I6 prepare again.
- Restart replay from the same durable I39 store returns the same receipt without invoking frozen I6 prepare again.
- A different/stale I38 receipt, different I36 stage, different manifest binding, tampered authorization/proof/stage, or stale predecessor status fails closed before frozen I6 prepare.

## RuntimeOS surface

Status:

`GET|HEAD /api/runtime/pass218/cognition/manifest-canonical-prepare/status`

Prepare:

`POST /api/runtime/pass218/cognition/manifest-canonical-prepare/prepare`

The POST action is parameterless. Caller JSON cannot provide or override source content, manifest binding, I38 authorization, I37 proof, I36 stage, projection bytes, canonical target root, canonical commit, I7 persistence, VM81 canonical authority, learning authority, or curriculum advancement.

## Files changed in I39

1. `hhs_runtime/pass218/manifest_bound_canonical_prepare_i39.py`
2. `hhs_backend/runtime_os_pass218_manifest_canonical_prepare_i39.py`
3. `hhs_backend/runtime_os_application_server.py`
4. `tests/pass218/test_pass218_iteration39_manifest_bound_canonical_prepare.py`
5. `scripts/pass218_iteration39_manifest_canonical_prepare_validation.py`
6. `.github/workflows/pass218-full-iteration39.yml`
7. `docs/pass218/PASS_218_ITERATION_39_RESTART.md`

Frozen I5, I6, and I7 source files are not modified.

## Validation required before freeze

1. Exact I38→I39 comparison: seven commits, seven files, zero behind, merge base exactly frozen I38.
2. Focused I39 tests.
3. Frozen I38/I37/I7/I6/I5/I36 preservation tests.
4. Cumulative dependency-scoped Pass218 regressions in the I39 workflow.
5. Global Pass218/cognition no-authoritative-float literal scan.
6. Deterministic I39 evidence generation.
7. Exact-head GitHub workflow success.
8. Draft PR synthetic-merge workflow success against the computed merge candidate.
9. Exact-head and synthetic-merge evidence payload SHA-256 equality.
10. Broader Pass217/218/219 integration success.
11. Full RuntimeOS/application/browser acceptance success.
12. Terminal current-head check matrix with failures/pending states resolved; non-applicable skips remain skips.
13. Freeze review anchored to the exact I39 head.
14. Reverify `main` unchanged.

## Next action after a successful I39 freeze

Inspect the exact frozen I7 persistence API together with the frozen I6 commit preconditions. The next bounded iteration should bind the durable I39 prepare proof to an atomic I6 canonical commit **only if** that same iteration can durably seal/restore the resulting canonical state through frozen I7 without widening semantic-learning, truth/action, curriculum, or later source lifecycle authority.
