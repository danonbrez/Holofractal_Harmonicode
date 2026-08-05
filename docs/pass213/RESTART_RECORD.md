# Pass 213 Restart Record — Iteration 4

- Contract: `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`
- Immediate parent: Pass 212 full hydration compression and physical erasure recovery
- Base commit: `2be050264a6e9c659603100be802979bbc49bf7a`
- Branch: `agent/pass213-compiled-rom-integrity`
- Published implementation and restart head before final workflow receipt: `6e87dab5262f539722f795553b0332ef078c241d`
- Merge target: `main`
- Draft pull request: `#169`
- Iteration: `4`

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
- `hhs_backend/runtime/hhs_pass213_parametric_delta_v1.py`
- `tests/test_pass213_compiled_rom_v1.py`
- `tests/test_pass213_recovery_admission_v1.py`
- `tests/test_pass213_secure_memory_v1.py`
- `tests/test_pass213_native_protected_rom_v1.py`
- `tests/test_pass213_parametric_delta_v1.py`
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

- guarded native C protected-memory arena;
- non-executable, locked, no-dump, no-fork data pages;
- process dumpability hardening;
- constant-time owner-token authorization;
- bounds-checked access and read-only sealing;
- explicit zeroization and zero verification;
- keyed memory lifecycle receipts;
- native sealed backing for recovered compiled-ROM entries;
- internal Hash216 revalidation and zeroizing retirement.

Repository-native Iteration 3 validation:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31027325613
validated implementation head: b02f5a0694fe7c4eadcf5c8bb0af6bf4a4ade5a4
validate job: 92379008538
conclusion: SUCCESS
```

## Iteration 4 implemented state

Parametric template authority:

- immutable template identity bound to one protected compiled-ROM entry;
- exact operand and context field registry;
- exact field type and mutability declarations;
- deterministic finite semantic-constraint bytecode;
- explicit dependency paths for every constraint;
- complete authenticated baseline constraint-witness set.

Dependency-scoped candidate admission:

- complete field-set validation on every invocation;
- complete type validation on every invocation;
- exact canonical comparison against the baseline;
- immutable context mutation rejection;
- sorted changed-field delta;
- union of constraints whose dependencies intersect the changed fields;
- semantic execution only for that affected set;
- authenticated baseline-witness reuse for unaffected constraints;
- candidate, delta, evaluated witnesses, reused-witness root, compiled route, kernel policy, parent, epoch, group sequence, and opening timestamp boundary bound into the VM81 admission root;
- keyed deterministic admission authentication.

Native-memory integration:

- templates stored in sealed owner-bound native arenas;
- parametric admission bytes stored in separate sealed owner-bound native arenas;
- public records retain identity, delta, count, arena, length, and receipt commitments only;
- protected lookup requires the original timestamp boundary and revalidates the complete admission;
- identical candidate and boundary admissions are idempotent;
- template and admission arenas are zeroized before destruction.

## Iteration 4 validation

Local pre-publication checks:

```text
new runtime Python compilation: PASS
new test Python compilation: PASS
7 isolated core dependency-selection tests against API-compatible stubs: PASS
```

Repository-native validation:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31028844237
validated branch head: a1c8fb3f7b149f1d23090321f7512ee182c7960a
validate job: 92384100388
native build and Iteration 1–4 validation step: SUCCESS
workflow conclusion: SUCCESS
```

Iteration 4 repository coverage includes:

- complete baseline witness set;
- exact invocation with complete witness reuse;
- one-field dependency selection;
- multi-field dependency union;
- immutable-context rejection;
- complete type validation;
- affected-constraint failure;
- timestamp-boundary-specific authority;
- wrong-key and altered-admission rejection;
- baseline-witness tamper rejection;
- sealed template and admission storage;
- idempotent admission;
- original-boundary lookup enforcement;
- protected-base-entry requirement;
- zeroizing retirement.

Guarded Continuous Integration remained skipped under its inherited guard policy. The dedicated Pass 213 workflow is the authoritative dependency-scoped validation for this slice.

## Remaining work

1. Add persistent inventory roots, authorized tombstones, and deleted-entry recovery.
2. Add ML-KEM/ML-DSA/SLH-DSA enclosure and checkpoint surfaces.
3. Add trusted external checkpoint timestamps.
4. Implement the full high-dimensional magic-square/Sudoku/Fibonacci tensor family.
5. Add API, CLI, governed native dispatch, performance evidence, and final main verification.

## Next exact action

Implement the persistent compiled-ROM inventory and deletion-transition layer. Every authorized retirement must retain an authenticated tombstone, while unexplained absence must fail inventory continuity and recover the protected entry from authenticated carrier or checkpoint material. Preserve the Iteration 2 correction gate, Iteration 3 protected-memory gate, and Iteration 4 dependency-scoped admission gate. Do not merge Pass 214 ahead of authoritative Pass 213 closure.
