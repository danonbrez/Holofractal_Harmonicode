# Pass 218 Iteration 30 Restart Record

## Scope

Pass 218 Iteration 30 is the bounded **atomic semantic promotion** stage over the
frozen Iteration 29 validated Hash216/VM5184 transition candidate.

The governing Pass 218 order is:

```text
formal/analogical differentiation
    -> Hash72/Hash216/VM5184 transition
    -> validation
    -> atomic promotion
    -> verbatim purge
    -> purge receipt / closure progression
```

I30 implements only atomic promotion. It does not perform the subsequent
verbatim purge, issue a purge receipt, advance the curriculum, or close the Pass.

The contract's commit-before-purge order is preserved explicitly:

```text
validate
    -> durable candidate commit
    -> verify prospective roots + semantic round trip
    -> atomic promotion
    -> [I31: verbatim purge]
    -> [I31: purge receipt / quarantine on failure]
```

## Frozen parent

- Frozen I29 head:
  `ec45c89bcb95384f3eda5075659c5ebc2e686c43`
- I29 branch:
  `agent/pass218-full-iteration29-hash216-vm5184-transition-validation`
- I29 draft PR:
  `#237`
- I29 freeze checkpoint:
  `5300615060`
- `main` at I29 freeze:
  `5cbb85ca33031e1ae2c072491271b66ec967dfde`

## Iteration 30 branch

`agent/pass218-full-iteration30-atomic-semantic-promotion`

The branch was created directly from the exact frozen I29 head.

## Implemented promotion boundary

I30 consumes an I29 state only when all of the following remain exact:

- schema is the frozen I29 validated-candidate schema;
- status is `VALIDATED_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE`;
- Hash216 continuation is verified;
- semantic transition validation is complete;
- VM5184 candidate projection is verified;
- candidate semantic binding is verified;
- atomic-promotion candidate readiness is true;
- promoted-object round-trip has not already been claimed;
- authoritative VM5184 projection has not already been invoked;
- VM81 authorization/mutation remains closed;
- atomic promotion has not already been invoked;
- truth/action/canonical-learning/model/verbatim/float authority remains closed.

The caller must provide a separate exact I30 promotion grant containing:

- a valid grantor authority Hash72;
- a non-negative grant sequence;
- the exact expected I29 validation Hash72;
- the exact expected I29 validated Hash216;
- the fixed I30 target scope
  `PASS218_VALIDATED_HASH216_VM5184_SEMANTIC_PROMOTION`.

The grant is bound after I29 revalidation to the exact semantic-witness Hash72.
No candidate may self-authorize promotion.

## Canonical writer fence

I30 does not introduce an independent writer authority. Every promotion calls
the inherited Pass218 lifecycle `require_ingestion_ready()` before any candidate
commit or canonical swap.

That reuses the existing I9/I10/I11 local/distributed writer fence and therefore
keeps browser/API promotion behind the same canonical ownership membrane used by
other Pass218 durability paths.

The RuntimeOS store lives beneath the resolved Pass218 state root at:

`cognition/atomic-semantic-promotion-i30`

## Promoted semantic object

I30 deliberately does **not** treat the one-way 64-bit relation-cell digests as
standalone reversible meaning. Instead it promotes an exact nonverbatim semantic
object containing enough derived structure to prove the contract's grounded and
perspective round trips.

The object retains only allowed derived/identity material, including:

- exact I29 validation identity and validated Hash216;
- exact I28/I27 lineage identities;
- semantic validation witness identity;
- normalized grounded relation graph with source/target Hash72 identities;
- exact relation direction, type, family, mode, trinary status, exact rational
  strength where present, provenance, and perspective order;
- grounding/curriculum identity metadata and upstream semantic roots;
- relation taxonomy and family layers;
- accepted perspective profile identity and rule witnesses;
- hashed active-context and attention-configuration witnesses rather than their
  token streams;
- exact 81 x 64-bit VM5184 state words;
- inherited native state/projection/continuation root216 values;
- validation, authority, and promotion receipts.

It does not retain source paragraphs, raw source bytes, raw source text, token
streams, narrative source excerpts, or source/target token presentation fields.

## Formal semantic round trip

Before the manifest can become authoritative, I30 reconstructs the exact I27
semantic state and independently re-derives the VM5184 state and inherited
Pass205 native state/projection roots.

It then creates two canonical nonverbatim decoded views:

1. `DecodeGrounded(promoted_object)` — normalized grounded graph, relation
   taxonomy/layers, exact identity/status/provenance/order data, grounding
   identity, conservation record, and upstream semantic roots.
2. `DecodePerspective(promoted_object)` — accepted perspective identity/rule
   witnesses, active-context and attention Hash72 witnesses, perspective order,
   relation-family/type/status sequences, and I24/I25 semantic roots.

The atomic swap is impossible unless both decoded views equal the exact expected
views derived from the current I27 state. Therefore successful I30 promotion may
set `formal_semantic_round_trip_verified = true` without claiming that the
relation-cell digest alone is reversible.

## Atomic durability protocol

I30 uses content-sealed files and a single atomic manifest replacement:

1. Validate and re-derive the exact candidate under the current writer fence.
2. Build the nonverbatim promoted semantic object and prove both round trips.
3. Write/fsync a content-addressed **candidate commit** under `candidates/`.
4. Re-read the candidate and verify its exact canonical bytes/SHA-256.
5. Compute and seal the prospective canonical semantic root.
6. Emit a root-verification Hash72.
7. Write/fsync a content-sealed promotion generation under `generations/`.
8. Atomically replace `manifest.json` to make that generation authoritative.
9. Re-read the manifest/generation and verify their root/object linkage.

An injected failure before step 8 leaves no authoritative promotion and cannot
partially move the canonical root. Candidate/generation files may remain as
non-authoritative recovery evidence, but the manifest remains the sole active
pointer.

Exact replay of the same I29 candidate under the same exact grant is idempotent.
A conflicting grant/candidate while a promotion is pending purge fails closed.
This prevents a second semantic promotion from silently advancing the curriculum
before I31 completes the purge gate.

## Successful I30 state

A successful I30 promotion has status:

`ATOMICALLY_PROMOTED_PENDING_VERBATIM_PURGE`

and may truthfully mark:

- `formal_semantic_round_trip_verified = true`;
- `grounded_round_trip_verified = true`;
- `perspective_round_trip_verified = true`;
- `candidate_commit_verified = true`;
- `prospective_root_verified = true`;
- `vm5184_authoritative_projection_invoked = true`;
- `vm5184_authoritative_state_committed = true`;
- `atomic_promotion_authorized = true`;
- `atomic_promotion_invoked = true`;
- `atomic_manifest_swap = true`.

The following remain false/closed:

- `vm81_authorization_invoked`;
- `verbatim_purge_invoked`;
- `purge_receipt_issued`;
- `curriculum_advance_permitted`;
- `closure_invoked`;
- `truth_promotion`;
- `action_authority_minted`;
- `canonical_learning_commit_invoked`;
- `model_activation_invoked`;
- `verbatim_corpus_source_retained`;
- `authoritative_float_weights_created`.

I30 therefore promotes validated semantic state, not truth claims, action
permissions, learning authority, or model authority.

## Implemented files

1. `hhs_runtime/pass218/atomic_semantic_promotion_i30.py`
   - exact I29 grant binding and validation
   - writer-fenced semantic promotion
   - nonverbatim semantic object construction
   - VM5184/native re-projection verification
   - grounded/perspective round-trip proof
   - content-sealed candidate commit
   - prospective-root verification
   - atomic durable manifest swap
   - idempotent replay / pending-purge conflict rejection

2. `hhs_backend/runtime_os_pass218_atomic_semantic_promotion_i30.py`
   - browser-safe status endpoint
   - explicit-authority promotion endpoint
   - no purge or curriculum-advance endpoint

3. `hhs_backend/runtime_os_application_server.py`
   - installs I30 after I29
   - supplies the existing Pass218 lifecycle fence and resolved state root
   - preserves I15-I19 maintenance compatibility aliases

4. `tests/pass218/test_pass218_iteration30_atomic_semantic_promotion.py`
   - atomic successful promotion
   - grounded/perspective round trip
   - token-bearing presentation data exclusion
   - durable restart/idempotent exact replay
   - conflicting pending-purge promotion rejection
   - injected pre-swap failure/no partial root movement
   - canonical writer-fence enforcement
   - exact I29 authority binding
   - browser-safe promotion-only RuntimeOS surface

5. `scripts/pass218_iteration30_atomic_semantic_promotion_validation.py`
   - reconstructs the exact frozen I29 evidence candidate
   - requires exact frozen I29 validation Hash72 and validated Hash216
   - uses the real inherited Pass205 native bridge
   - acquires a real I9 filesystem writer fence in an isolated state root
   - performs atomic promotion and exact replay
   - proves purge/curriculum advance remain closed

6. `.github/workflows/pass218-full-iteration30.yml`
   - cumulative compile/no-float enforcement
   - focused I30 tests
   - frozen I29/I28 regression
   - inherited Pass205 ABI
   - canonical I9 writer-fence regression
   - I27 -> I20, Genesis, Pass166, crawler preservation
   - real I30 evidence
   - RuntimeOS production-root acceptance
   - evidence artifact upload

7. `docs/pass218/PASS_218_ITERATION_30_RESTART.md`
   - this restart record

## Commit chain and validation repair

From frozen I29 `ec45c89bcb95384f3eda5075659c5ebc2e686c43`:

1. `2b17fec047409657cc4d51a30c59ce2e23a2be50`
   - atomic semantic promotion runtime
2. `171f38d793e3d628d4918ab777206b8ebc3f876f`
   - RuntimeOS promotion membrane
3. `41b128a776d6809948a43a86653da69c5767f311`
   - application composition
4. `b1b86996569962ccb6195553c1c05ef006b0df97`
   - focused tests
5. `8c812a27e1cfcb2bbaf5cf1ecb2ee10f3dbb2dd0`
   - repository-native evidence harness
6. `a1e2fb4c24e31f9e0190f80e355510bd75dc6231`
   - bounded I30 workflow
7. `9b573679335e38c56e5a1561f115df21e8d0d49a`
   - initial restart record / first exact-head validation candidate
8. `f5a4150da5e165676f4a5c15e269a3ef22289c04`
   - repair the focused-test fixture to use the exact frozen I28 mapping version
     `HHS-P218-I28-VM5184-RELATION-CELL-MAP-V1` rather than a stale duplicated
     literal. The runtime correctly rejected the stale fixture with
     `P218_I30_NATIVE_STATE_ROOT_MISMATCH`; no production promotion semantics
     were weakened or reinterpreted.
9. this restart-record update records that bounded repair before the next exact
   validation candidate is frozen.

The bounded I30 file set remains exactly seven files. Repair-forward history may
therefore contain nine commits while preserving the same seven-file iteration
scope.

## Validation required before freeze

Do not freeze I30 until one exact branch head satisfies all of the following:

1. draft I30 PR is open, draft, mergeable, and unmerged;
2. exact-head I30 workflow is terminal green;
3. synthetic-merge I30 workflow is terminal green;
4. focused I30 promotion/failure/restart tests are green;
5. global Pass218/cognition authoritative-float literal scan is green;
6. frozen I29 and I28 regression tests are green;
7. inherited Pass205 native continuation ABI is green;
8. canonical I9 writer-fence regression is green;
9. frozen I27 -> I20 regression chain is green;
10. I1 Genesis, Pass166, and repository-native crawler preservation is green;
11. repository-backed real I30 evidence reconstructs the exact frozen I29
    validation identity before promotion;
12. real evidence proves 14 relations, exact native roots, semantic round trip,
    exact writer fence, candidate commit, root verification, and atomic swap;
13. injected pre-swap failure proves no authoritative partial promotion;
14. exact replay is idempotent;
15. purge remains pending and no purge receipt exists;
16. curriculum advance remains prohibited;
17. VM81/truth/action/learning/model/verbatim/float authority remains closed;
18. RuntimeOS production-root acceptance is green;
19. evidence artifact ID/archive SHA-256 and evidence-file SHA-256 are recorded;
20. exact I29 -> I30 delta and exact merge base are recorded;
21. synthetic merge candidate identity is recorded;
22. broader applicable PR matrix is terminal green or explicitly skipped by
    configured applicability;
23. `main` remains unchanged;
24. a terminal freeze comment is recorded without moving the validated head.

## Restart procedure

A restarting agent should:

1. read this record and I29 freeze checkpoint `5300615060`;
2. inspect the exact I30 branch head;
3. compare it to frozen I29
   `ec45c89bcb95384f3eda5075659c5ebc2e686c43`;
4. confirm the seven-file bounded delta and exact merge base;
5. inspect the I30 draft PR and exact-head/synthetic-merge workflows;
6. if a check fails, inspect only the relevant logs and repair forward;
7. rerun impacted checks plus the final bounded I30 workflow;
8. freeze only one exact green head and record its artifact/evidence identities;
9. leave the PR draft/unmerged and leave `main` unchanged.

## Next bounded stage

Only after I30 is frozen green does the contract proceed to **verbatim purge**.
A later I31 should verify that the promoted semantic authority is durable, purge
or prove absence of remaining verbatim source buffers, issue the purge receipt,
and quarantine rather than silently advance if purge confirmation fails.

I30 itself grants no authority to skip that stage or advance the curriculum.
