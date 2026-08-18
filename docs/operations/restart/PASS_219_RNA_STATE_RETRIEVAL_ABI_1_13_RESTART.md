# Pass 219 RNA State Retrieval ABI 1.13 Restart Record

Status: implementation complete; exact documentation-inclusive validation must be terminal green before this head is treated as frozen.

## Repository identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen I112 parent: `becac3cd957ddba2b485cd49002aadb89d59c125`
- Branch: `agent/pass219-iteration113-authenticated-indexed-prior-state-retrieval`
- Merge target: no merge authorized by this iteration.
- Deployment: not authorized.
- History policy: append-only repair-forward; no rebase, force-push, or rewrite.

## Iteration 113 boundary

I113 implements amendment 1.5.0 E15/E16 authenticated indexed predecessor-state retrieval while preserving the frozen I112 admission boundary.

The stable C-compatible identity binds:

- `program_hash216`
- `predecessor_state_hash216`
- predecessor Hash72
- predecessor Hash216 SHA-256 digest
- retrieval-source SHA-256 identity
- authenticated cache/index SHA-256 identity
- `checkpoint_counter`
- dependency-frontier SHA-256
- exact predecessor VM81 frame

Retrieval classification is typed as exactly:

- `HHS_EXACT_RNA_STATE_RETRIEVAL_OK`
- `HHS_EXACT_RNA_STATE_RETRIEVAL_UNAVAILABLE`
- `HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH`

## Reference authentication and optimized continuation

`hhs_exact_pass219_rna_reference_seal_from_replay` accepts two independently produced canonical/reference predecessor frames and refuses to seal them unless they are byte-exact equal. The resulting pointer-free reference seal records the exact predecessor frame and all cryptographic-grade identity bindings.

`hhs_exact_pass219_rna_state_retrieval_authenticate` then authenticates indexed predecessor material against that replay-verified seal. A cache/index byte hit alone is never sufficient: identity and exact VM81 frame equality are both required.

The ordinary continuation path after the seal exists is:

```text
indexed predecessor
  -> identity + dependency-frontier verification
  -> exact reference-seal comparison
  -> HHS_EXACT_RNA_STATE_RETRIEVAL_OK
  -> hhs_exact_pass219_rna_admission_candidate_from_retrieval
  -> frozen I112 candidate reconstruction/rollback boundary
  -> inherited C-only VM81 admission authority
```

No Genesis/reference frame is an input to `hhs_exact_pass219_rna_admission_candidate_from_retrieval`. Genesis/reference replay remains outside the hot path and is retained for proof, audit, recovery, missing evidence, or foundational dependency change.

`UNAVAILABLE` requires fallback without invalidation. `MISMATCH` requires fallback and marks the indexed record for deterministic invalidation. `hhs_exact_pass219_rna_indexed_prior_state_invalidate` clears only the non-authoritative cached frame and availability bit; it cannot mutate VM81 canonical state.

## Authority boundary

I113 introduces no new VM81 mutation authority.

- C++ `AuthenticatedPriorState` can authenticate/read retrieval results and prepare a non-authoritative I112 candidate.
- It exposes no `commit` member.
- It exposes no `admit` member.
- Canonical mutation remains behind the inherited C function `hhs_exact_pass219_rna_admit_composed` reached through frozen I112 lowering.

## Complexity declaration

I113 does not claim a complexity bound for the external storage backend lookup because the backend is not defined by this ABI.

Once an indexed record and replay-verified reference seal are supplied, authentication is fixed-size with respect to repository/history length: it compares bounded identity material plus one 81-word VM81 frame. Equivalently, the ABI work is O(81) frame words and therefore O(1) with respect to prior transition-history length. Normal candidate continuation is likewise bounded by the inherited fixed 81-cell frame operations and does not replay unchanged history from Genesis.

## Intended nine-path delta

1. `hhs_runtime/include/hhs_pass219_rna_state_retrieval_1_13.h`
2. `hhs_runtime/include/hhs_pass219_rna_state_retrieval_1_13.hpp`
3. `hhs_runtime/c/hhs_pass219_rna_state_retrieval_1_13.inc`
4. `hhs_runtime/include/hhs_runtime_exact_abi.h`
5. `hhs_runtime/c/hhs_runtime_exact_abi.c`
6. `tests/pass219/test_pass219_rna_state_retrieval_1_13.c`
7. `tests/pass219/test_pass219_rna_state_retrieval_1_13.cpp`
8. `.github/workflows/pass219-rna-state-retrieval-1-13.yml`
9. `docs/operations/restart/PASS_219_RNA_STATE_RETRIEVAL_ABI_1_13_RESTART.md`

Frozen 1.10-1.12 implementation files are not modified.

## Validation and repair-forward record

Initial implementation head `e04a8f92cfff828a2d1dae1a42cdcea9eea785f2`:

- dedicated run: `32050615806`
- strict C ABI compile: PASS
- 1.13 C test: FAIL in the new fixture before retrieval assertions
- failure: the fixture selected `HHS_EXACT_PASS219_RNA_RULE_ACTIVATION` without establishing its activation precondition
- inherited regressions: skipped because the focused step failed first

Repair-forward commit:

- `d215fd94ef2a0ea28f1f10a97af6a32020d43439`
- changed only the I113-owned witness fixture to the frozen inhibition rule semantics already proven in I112
- no implementation or inherited file was rewritten

The documentation-inclusive head created by this restart-record commit must pass the dedicated workflow before freeze classification.

## Dedicated validation contract

`.github/workflows/pass219-rna-state-retrieval-1-13.yml` requires:

- no `float`/`double` authority tokens in the I113 ABI surface
- strict C11 aggregate compilation with `-Wall -Wextra -Werror -pedantic`
- I113 C authenticated retrieval conformance
- I113 C++17 non-authority conformance
- frozen I112 C/C++ lowering regression
- frozen I111 C rule regression
- frozen I110 C admission regression

The I113 C test proves replay-seal equality, authenticated indexed success, direct candidate continuation without Genesis inputs, frame mismatch classification, index-identity mismatch classification, deterministic invalidation, unavailable fallback, and reference-replay divergence rejection.

## Exact next action after green freeze

Implement E17 inherited-capability utilization as the next additive Pass 219 boundary: register the authenticated indexed continuation path with the canonical execution composer as the default when its preconditions match, add typed bypass reasons (`FIRST_PRINCIPLES_EXPORT`, `DEPENDENCY_CHANGED`, `CORRUPTION_RECOVERY`, `REFERENCE_ORACLE`, `ABLATION_OR_BENCHMARK_CONTROL`, `UNAVAILABLE_AUTHENTICATED_PREDECESSOR`, `EXPLICITLY_AUTHORIZED_AUDIT`), and preserve the selected bypass reason in evidence without adding C++ mutation authority.
