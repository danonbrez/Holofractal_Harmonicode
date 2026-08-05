# Pass 213 Restart Record — Iteration 2

- Contract: `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`
- Immediate parent: Pass 212 full hydration compression and physical erasure recovery
- Base commit: `2be050264a6e9c659603100be802979bbc49bf7a`
- Branch: `agent/pass213-compiled-rom-integrity`
- Merge target: `main`
- Draft pull request: `#169`
- Iteration: `2`

## Files in Pass 213 scope

- `HHS_PASS_213_TIMESTAMP_BOUND_AUTHENTICATED_MOVING_TENSOR_COMPILED_ROM.md`
- `hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py`
- `hhs_backend/runtime/hhs_pass213_recovery_admission_v1.py`
- `tests/test_pass213_compiled_rom_v1.py`
- `tests/test_pass213_recovery_admission_v1.py`
- `contracts/pass213/PASS_213_CONTRACT.json`
- `docs/pass213/README.md`
- `docs/pass213/RESTART_RECORD.md`
- `scripts/run_pass213_iteration1_validation.sh`
- `.github/workflows/pass213-compiled-rom-integrity.yml`

## Iteration 1 implemented state

- timestamp boundary records and pair validation;
- exact ordered-operation chaining;
- domain-separated state-local derivation;
- keyed full-cycle closure mapping and inverse;
- immutable compiled-ROM entries and exact lookup;
- authenticated inventory root;
- deterministic group receipt.

## Iteration 2 implemented state

- canonical compiled-entry serialization;
- Pass 212 `ProtectedPayload` carrier integration;
- keyed Pass 213 carrier authentication;
- inherited physical-shard validation and one/two-erasure reconstruction;
- recovered payload Hash216 validation before deserialization;
- immutable compiled-entry Hash216 validation after deserialization;
- keyed `RecoveredROMAdmission` proof;
- canonical `RecoveryGatedCompiledROMStore` insertion surface;
- admission-root inclusion in the compiled-ROM inventory root;
- intact/recovered outcome receipts;
- fail-closed rejection of corrupted and over-budget carriers.

## Validation performed before repository publication

```text
new runtime module Python compilation: PASS
new test module Python compilation: PASS
12 iteration-2 interface tests against a Pass 212 API-compatible local harness: PASS
```

The local harness validated the Pass 213 integration logic and public Pass 212 call contract. Repository-native execution against the inherited Pass 212 implementation is delegated to:

```bash
bash scripts/run_pass213_iteration1_validation.sh
```

The branch workflow `.github/workflows/pass213-compiled-rom-integrity.yml` runs both Pass 213 test modules against the repository implementation.

## Iteration 2 test coverage

- intact carrier recovery and admission;
- one missing data shard correction;
- one data plus one parity erasure correction;
- three-erasure fail-closed behavior;
- corrupted present-shard rejection;
- carrier metadata tamper rejection;
- carrier authentication tamper rejection;
- wrong-key rejection;
- carrier mapping round trip;
- raw non-admission object rejection;
- admission-token tamper rejection;
- atomic inspect-correct-admit behavior.

## Remaining work

1. Add protected-memory allocation, zeroization, no-dump, and no-swap native enforcement.
2. Implement parametric delta matching and dependency-scoped revalidation.
3. Add persistent inventory roots, authorized tombstones, and deleted-entry recovery.
4. Add ML-KEM/ML-DSA/SLH-DSA enclosure and checkpoint surfaces.
5. Add trusted external checkpoint timestamps.
6. Implement the full high-dimensional magic-square/Sudoku/Fibonacci tensor family.
7. Add API, CLI, native dispatch, performance evidence, and final main verification.

## Next exact action

After the repository-native Pass 213 workflow validates iteration 2, implement the protected kernel-memory arena with explicit allocation ownership, page locking, no-dump/no-swap controls, guard regions, and zeroization receipts. Do not merge Pass 214 ahead of authoritative Pass 213 closure.
