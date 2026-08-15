# Pass 218 Iteration 38 restart record

## Repository checkpoint

- Frozen parent: Pass 218 Iteration 37 head `17489c131ddad84caad8826569b9ab8df7f11d7a`
- Branch: `agent/pass218-full-iteration38-manifest-bound-promotion-authority-authorization-ingress`
- Merge target: `main`
- Main at iteration start: `5cbb85ca33031e1ae2c072491271b66ec967dfde`
- Iteration 38 must remain draft/unmerged until a later explicit merge instruction.

## Bounded purpose

Iteration 38 consumes only the exact durable I37 manifest-bound promotability proof and enters the remaining frozen-I5 authority half of the protocol. It does not execute the frozen I6 canonical target.

The intended boundary is:

```text
frozen I37 binding receipt
        +
exact manifest-bound I5 promotability proof
        +
propagated manifest/curriculum/source/rights/ordinal lineage
        ↓
validate exact active I37 state
        ↓
derive grantor = frozen manifest authority_root_hash72
derive grant_sequence = frozen curriculum_position
        ↓
frozen PromotionAuthorityGrant.bind(...)
        ↓
frozen PromotionAuthorizationJournal.authorize(...)
        ↓
AUTHORIZED_PENDING_CANONICAL_COMMIT
        +
canonical_mutation_permitted = true
        +
all actual canonical mutation flags = false
        ↓
durable manifest-bound I38 authorization envelope + receipt
        ↓
MANIFEST_BOUND_PROMOTION_AUTHORIZATION_INGRESS_COMPLETE
```

`canonical_mutation_permitted=true` is a precondition produced by frozen I5. It is not evidence that a canonical mutation happened. I38 deliberately leaves the I6 target untouched.

## Authority derivation

The RuntimeOS request cannot provide the I5 grant identity. I38 derives the grant exclusively from frozen inherited state:

- `grantor_authority_hash72 = manifest_binding.authority_root_hash72`
- `grant_sequence = manifest_binding.curriculum_position`
- `target_scope = PASS217_VECTOR_VM5184_PROMOTION`
- candidate identity and projection identity come from the exact frozen I37/I5 proof.

The explicit authorization act is the distinct I38 authorize operation. A request cannot replace the grantor, sequence, candidate, manifest binding, I37 receipt, or I5 proof.

## Files changed in this iteration

1. `hhs_runtime/pass218/manifest_bound_promotion_authorization_i38.py`
2. `hhs_backend/runtime_os_pass218_manifest_promotion_authorization_i38.py`
3. `hhs_backend/runtime_os_application_server.py`
4. `tests/pass218/test_pass218_iteration38_manifest_bound_promotion_authorization.py`
5. `scripts/pass218_iteration38_manifest_promotion_authorization_validation.py`
6. `.github/workflows/pass218-full-iteration38.yml`
7. `docs/pass218/PASS_218_ITERATION_38_RESTART.md`

Frozen I5, I6, I37, and earlier pass-specific runtime modules remain unchanged.

## RuntimeOS surface

Status:

`GET /api/runtime/pass218/cognition/manifest-promotion-authorization/status`

Authorization:

`POST /api/runtime/pass218/cognition/manifest-promotion-authorization/authorize`

The authorization action accepts no grantor, sequence, proof, candidate, source, or manifest authority payload.

## Durable state / restartability

The I38 store persists only nonverbatim authorization evidence:

- I38 binding receipt
- exact frozen-I5 authority grant
- exact frozen-I5 authorization receipt
- manifest-bound authorization envelope
- active state pointer/root

Same-process replay of an already-persisted exact I37 binding returns the same I38 receipt without constructing a second grant or authorization. Restart replay loads the same persisted state and likewise does not invoke the I5 grant/authorization path again.

## Explicitly closed after I38

The following remain false after successful I38 authorization:

- source payload persistence
- verbatim corpus retention
- I6 canonical commit invocation
- I30 canonical semantic promotion
- I31 later verbatim purge
- I32 later source closure
- curriculum cursor advance
- curriculum stage advance
- VM81 authorization/commit invocation
- truth promotion
- action-authority minting
- authoritative vector-store promotion
- canonical vector-store mutation
- canonical VM81 commit
- canonical learning commit
- model activation
- authoritative floating-point state

## Validation contract

Dependency-scoped validation for I38 includes:

- compile cumulative Pass 218 and RuntimeOS bindings through I38
- global no-authoritative-float literal scan
- focused I38 tests
- frozen I37 preservation
- frozen I5 grant/authorization preservation
- frozen I6 commit-boundary preservation without invocation
- frozen I36/I35/I4/I34/I3/I2 preservation
- I33/I32/I31/I30 and I20-I29 regression gates
- I9 writer-fence preservation
- I1 curriculum preservation
- Pass205 continuation ABI
- Pass166 Word2Vec
- repository-native creative-writing crawler
- deterministic I38 evidence
- RuntimeOS production-root acceptance
- exact-head and synthetic-merge evidence equality
- broader integration and full application/browser acceptance before freeze

## Environment / deployment state

No deployment or main-branch mutation is authorized by this iteration. The repository branch/PR evidence is the authoritative checkpoint. The separate Vercel preview is outside the HHS repository/runtime acceptance boundary.

## Next bounded action after freeze

Inspect frozen I6 in detail before Iteration 39. I6 itself separates `prepare -> atomic commit -> receipt`; the next iteration must decide its bounded boundary from the frozen API rather than assuming authorization implies execution. Do not reconstruct I5 authorization or mutate the canonical target outside frozen I6.
