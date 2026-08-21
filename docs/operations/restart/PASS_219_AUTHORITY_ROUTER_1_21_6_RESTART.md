# Pass 219 I121.6 — Exact Authority Router Restart Record

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Canonical `main`: `f5d8fdc014d888f93c0d85d40d2a2c0c198eefdf`
- Branch: `agent/pass219-orthogonal-glyph-parallel-membrane-1-21`
- PR: `#315`
- Merge target: `main`
- Merge authorization: **NOT GRANTED**
- I121.5 frozen parent: `93074bbfb353b093b21eca0a642f5497f71656cf`
- Delivery model: additive repair-forward; no frozen-history rewrite.

## Repair classification

`AUTHORITY_ROLE_AMBIGUITY — FAIL_CLOSED_RUNTIME_ROUTING_REPAIR`

I121.5 proved that canonical main already contains frozen Pass191 exact-context execution/manifold evidence for the exact I120 native source. That discovery creates a new downstream hazard if later native code treats the strongest available evidence as canonical whole-expression authority.

I121.6 therefore makes the evidence/authority distinction compiler-visible in the cumulative exact C ABI.

## Exact authority roles

The router recognizes these roles in increasing evidence depth:

```text
NONE
PASS159_SOURCE_PIPELINE
I1213_CANDIDATE_DIAGNOSTIC
I1214_UNRESOLVED_COMPOSITION
PASS191_INHERITED_MANIFOLD
PASS169_WHOLE_EXPRESSION
```

The last role is the canonical authority target, not a decision that this router can grant.

The router has only one successful route decision:

`HHS_EXACT_PASS219_AUTHORITY_ROUTE_PASS169_REQUIRED`

There is deliberately no `CANONICAL_PROVEN` route decision in the public enum.

## Fail-closed evidence dependencies

The router rejects malformed or logically impossible evidence bundles:

- downstream evidence without exact source identity;
- a Pass159 VMIR identity without verified Pass159 source pipeline;
- candidate execution without exact replay, or replay without execution;
- I121.4 composition without Pass159 source/VMIR identity and I121.3 execution/replay;
- Pass191 manifold evidence without all of:
  - exact-context scope preservation;
  - singleton VM81 authority evidence;
  - deterministic replay evidence;
- any Boolean evidence field outside `{0,1}`.

Even a complete Pass191 bundle yields:

```text
selected_evidence_role = PASS191_INHERITED_MANIFOLD
pass191_canonical_monolithic_authority = false
pass169_whole_expression_authority_required = true
whole_expression_semantics_resolved = false
canonical_monolithic_proof = false
floating_point_authority = false
vm81_mutation_authority = false
hash72_commit_authority = false
```

## Source binding

The router descriptor obtains its native source SHA-256 from the inherited I120 monolithic descriptor rather than defining an independent source identity.

## Files

Added:

- `hhs_runtime/include/hhs_pass219_authority_router_1_21_6.h`
- `hhs_runtime/c/hhs_pass219_authority_router_1_21_6.inc`
- `tests/pass219/test_pass219_authority_router_1_21_6.c`
- `tests/pass219/test_pass219_authority_router_1_21_6.cpp`
- `.github/workflows/pass219-authority-router-1-21-6.yml`
- `docs/operations/restart/PASS_219_AUTHORITY_ROUTER_1_21_6_RESTART.md`

Modified additively:

- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`

The root Makefile's existing dynamic exact-aggregate dependency census includes the new `.inc` and header through these aggregate registrations.

## Commit checkpoints

- `74dadf46a199f59cc48a88ab863f2fea590ebe90` — public exact authority-router ABI
- `9b5e0aaff154572172f455e755183789125e8f4e` — fail-closed routing implementation
- `dbaa1f709076a221ab51209095d22b9b91dc47da` — cumulative exact header registration
- `a5850062ab228ef762ad2e101d27ca1109b9f235` — cumulative exact implementation registration
- `a7823593126f790a804312e7ce4160e4adc59e0d` — C positive/negative conformance
- `82f51600a0567266f4b4b70e89731c80596d1d39` — C++ ABI conformance
- `85f87edfd96b458962b5042ec9774bcb94078a53` — exact/synthetic workflow

## Validation state

I121.5 Actions run `32459705059` was observed on the I121.5 head. Both exact and synthetic jobs terminated failure with `steps=null` and no logs, matching the repository-wide runner failure affecting unrelated Pass159, VM81, UQCEL, RNA, Pass217, and Pass218 jobs in the same batch. This is infrastructure evidence, not a code verdict.

I121.6 requires:

1. canonical-main ancestry for Pass169/186/189/191 evidence;
2. no floating-point fields or operations in the authority router;
3. no public `CANONICAL_PROVEN` route decision;
4. cumulative exact ABI compilation;
5. C evidence-tier and malformed-bundle tests;
6. C++ ABI consumption;
7. fresh I121.5 frozen Pass191 evidence verification;
8. Pass169 whole-expression contract lock.

Do not mark I121.6 validated until an exact and synthetic job executes these steps successfully.

## Next semantic boundary

The remaining problem is not authority selection. It is exact correspondence:

```text
Pass159 ordered constraint graph / VMIR
        ↕  [must be independently proven]
frozen Pass191 source/manifold execution effects
        ↓
Pass169 exact whole-expression VM81 admission
```

The next repair may add only a thin correspondence witness over inherited artifacts. It must not introduce a replacement equation evaluator, reinterpret the 837 Pass191 exact-context hits as whole-expression proofs, or promote the I121.3 candidate-completion circuit into Pass159 VMIR semantics.

Do not merge PR #315 into canonical `main` without separate explicit authorization.
