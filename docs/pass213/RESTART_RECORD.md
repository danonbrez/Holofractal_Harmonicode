# Pass 213 Restart Record — Iteration 3

- Contract: `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`
- Immediate parent: Pass 212 full hydration compression and physical erasure recovery
- Base commit: `2be050264a6e9c659603100be802979bbc49bf7a`
- Branch: `agent/pass213-compiled-rom-integrity`
- Merge target: `main`
- Draft pull request: `#169`
- Iteration: `3`

## Files in Pass 213 scope

- `HHS_PASS_213_TIMESTAMP_BOUND_AUTHENTICATED_MOVING_TENSOR_COMPILED_ROM.md`
- `contracts/pass213/PASS_213_CONTRACT.json`
- `docs/pass213/README.md`
- `docs/pass213/RESTART_RECORD.md`
- `native/pass213/hhs_pass213_secure_arena.c`
- `hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py`
- `hhs_backend/runtime/hhs_pass213_recovery_admission_v1.py`
- `hhs_backend/runtime/hhs_pass213_secure_memory_v1.py`
- `hhs_backend/runtime/hhs_pass213_native_protected_rom_v1.py`
- `tests/test_pass213_compiled_rom_v1.py`
- `tests/test_pass213_recovery_admission_v1.py`
- `tests/test_pass213_secure_memory_v1.py`
- `tests/test_pass213_native_protected_rom_v1.py`
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

- Pass 212 protected-carrier integration;
- one/two-erasure physical recovery;
- recovered payload Hash216 before deserialization;
- immutable entry Hash216 after deserialization;
- keyed recovered-ROM admission proof;
- recovery-gated canonical insertion;
- intact/recovered outcome classification.

Repository-native Iteration 2 validation:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31026181234
validated implementation head: 3d021b80d9f32afdea60fef8638c66e7ebcfeae2
conclusion: SUCCESS
```

## Iteration 3 implemented state

Native C protected-memory arena:

- inaccessible `PROT_NONE` guard page before and after every arena;
- non-executable middle data pages;
- `mlock` no-swap enforcement;
- `MADV_DONTDUMP` and `MADV_DONTFORK` enforcement;
- `PR_SET_DUMPABLE` process hardening surface;
- constant-time 256-bit owner-token authorization;
- bounds-checked read/write operations;
- read-only sealing;
- explicit volatile zeroization;
- zero verification;
- zeroization before `munlock`, `PROT_NONE`, `munmap`, and release.

Runtime integration:

- `NativeSecureArena` wrapper exposes no raw address;
- keyed lifecycle receipt chain for allocation, mutation, seal, zeroization, and destruction;
- `NativeProtectedCompiledROMStore` accepts recovered admissions only;
- canonical compiled-entry bytes reside in sealed native arenas;
- the Python index retains identity and commitment metadata only;
- lookup revalidates deserialized entry Hash216;
- inventory commits admission, arena, payload-length, and memory-receipt roots;
- retirement zeroizes and destroys every arena.

## Local validation before publication

```text
native C build with -Wall -Wextra -Werror: PASS
11 secure-arena tests: PASS
4 native-protected-ROM integration tests: PASS
iteration-2 plus iteration-3 local compatibility suite: 28 tests PASS
Python compilation: PASS
```

## Repository workflow state

The dedicated workflow is configured to build the C arena and execute all Iteration 1–3 test modules against the actual repository implementations. The current Iteration 3 branch head requires repository-native workflow closure before advancement.

## Remaining work

1. Resolve the Iteration 3 repository-native workflow.
2. Implement parametric delta matching and dependency-scoped revalidation.
3. Add persistent inventory roots, authorized tombstones, and deleted-entry recovery.
4. Add ML-KEM/ML-DSA/SLH-DSA enclosure and checkpoint surfaces.
5. Add trusted external checkpoint timestamps.
6. Implement the full high-dimensional magic-square/Sudoku/Fibonacci tensor family.
7. Add API, CLI, native dispatch, performance evidence, and final main verification.

## Next exact action

If the Iteration 3 workflow passes, implement the parametric compiled-ROM lane so compatible operations validate only changed operands and affected constraints before VM81 admission. If it fails, repair the native memory or repository integration on this branch before advancing. Do not merge Pass 214 ahead of authoritative Pass 213 closure.
