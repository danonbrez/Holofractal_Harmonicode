# Pass 213 Restart Record — Iteration 6

- Contract: `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`
- Immediate parent: Pass 212 full-hydration compression and physical erasure recovery
- Base commit: `2be050264a6e9c659603100be802979bbc49bf7a`
- Branch: `agent/pass213-compiled-rom-integrity`
- Validated Iteration 5 head: `5b7a1f95ab53bdd0c47706314eac2ec1fedb5ea3`
- Validated Iteration 6 implementation head: `e9ddcb09d3af525018a9e0196d065107c00674fc`
- Validated Iteration 6 workflow-policy head: `93338a7330b480552a79ca437c77aca42e9d9cc0`
- Final validated Iteration 6 README/evidence head: `229e1fa8c6200138d5a81b42a74c20d41b829ffd`
- Merge target: `main`
- Draft pull request: `#169`
- Iteration: `6`

## Files in Pass 213 scope

- `HHS_PASS_213_TIMESTAMP_BOUND_AUTHENTICATED_MOVING_TENSOR_COMPILED_ROM.md`
- `contracts/pass213/PASS_213_CONTRACT.json`
- `docs/pass213/README.md`
- `docs/pass213/RESTART_RECORD.md`
- `requirements/pass213-pqc.txt`
- `native/pass213/hhs_pass213_secure_arena.c`
- `hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py`
- `hhs_backend/runtime/hhs_pass213_recovery_admission_v1.py`
- `hhs_backend/runtime/hhs_pass213_secure_memory_v1.py`
- `hhs_backend/runtime/hhs_pass213_native_protected_rom_v1.py`
- `hhs_backend/runtime/hhs_pass213_parametric_delta_v1.py`
- `hhs_backend/runtime/hhs_pass213_persistent_inventory_v1.py`
- `hhs_backend/runtime/hhs_pass213_pqc_enclosure_v1.py`
- `tests/test_pass213_compiled_rom_v1.py`
- `tests/test_pass213_recovery_admission_v1.py`
- `tests/test_pass213_secure_memory_v1.py`
- `tests/test_pass213_native_protected_rom_v1.py`
- `tests/test_pass213_parametric_delta_v1.py`
- `tests/test_pass213_persistent_inventory_v1.py`
- `tests/test_pass213_pqc_enclosure_v1.py`
- `scripts/run_pass213_iteration1_validation.sh`
- `.github/workflows/pass213-compiled-rom-integrity.yml`

## Inherited validated state

Iterations 1–5 provide:

- timestamp-bound noncommutative compiled-operation identity;
- Pass 212 correction before compiled-ROM interpretation;
- recovered-ROM admission proofs;
- guarded, locked, sealed, and zeroizing native memory;
- dependency-scoped parametric validation and authenticated witness reuse;
- append-only persistent inventory roots;
- root-bound authorized tombstones;
- unexplained deletion detection;
- retained-carrier and authenticated-checkpoint recovery.

Repository-native evidence:

```text
Iteration 2 workflow: 31026181234 — SUCCESS
Iteration 3 workflow: 31027325613 — SUCCESS
Iteration 4 workflow: 31028995620 — SUCCESS
Iteration 5 workflow: 31031068182 — SUCCESS
Iteration 5 validated head: 5b7a1f95ab53bdd0c47706314eac2ec1fedb5ea3
```

## Iteration 6 implemented state

Algorithm authority:

- `liboqs-python==0.16.0` is pinned in `requirements/pass213-pqc.txt`;
- the matching liboqs release is selected with `PYOQS_VERSION=0.16.0`;
- the gate requires enabled ML-KEM-768 and ML-DSA-65 mechanisms;
- the gate resolves an enabled SLH-DSA SHA2-128s mechanism by normalized family and parameter identity;
- the native liboqs installation is cached by operating system, runner architecture, and liboqs version;
- workflow artifacts retain the complete validation transcript for restartable repair.

Native key protection:

- one ML-KEM recovery keypair;
- one ML-DSA operational-signature keypair;
- one SLH-DSA archival-signature keypair;
- each secret key stored in its own sealed owner-bound native arena;
- public records retain only algorithm, role, public bytes, and Hash216 commitment;
- the public verifier bundle commits all three public records and the liboqs suite;
- authority shutdown zeroizes and destroys all three native arenas.

Dual-signature checkpoint authority:

- complete Iteration 5 checkpoint mapping bound into the signing message;
- signed sequence and prior signed-checkpoint root continuity;
- verifier-bundle root binding;
- ML-DSA-65 operational signature;
- SLH-DSA SHA2-128s archival signature;
- both signatures committed into one successor signed-checkpoint Hash216;
- verifier-only replay using public material alone.

Recovery enclosure:

- ML-KEM encapsulation to the recovery public key;
- HKDF-SHA-256 derivation from the ML-KEM shared secret;
- checkpoint-root salt and complete capsule AAD binding;
- AES-256-GCM encryption of the exact 256-bit recovery root;
- KEM ciphertext, nonce, encrypted key, AAD root, recipient key, sequence, and checkpoint root committed into the capsule Hash216;
- recovery permitted only through the protected ML-KEM secret-key arena.

Persistent signed store:

- SQLite WAL and full synchronization;
- atomic signed-envelope and recovery-capsule append;
- strict signed sequence continuity;
- strict prior signed-root continuity;
- signed-head metadata verification;
- public verifier-bundle persistence and reopen validation;
- orphan and missing capsule rejection;
- database envelope and capsule tamper detection.

## Iteration 6 test coverage

- real liboqs algorithm preflight;
- sealed native protection for all three post-quantum secret keys;
- ML-DSA and SLH-DSA verification over one canonical checkpoint message;
- checkpoint mutation and public-key substitution rejection;
- ML-KEM recovery capsule round trip;
- authenticated-encryption tamper rejection;
- integration with an actual Iteration 5 inventory checkpoint;
- verifier-only SQLite reopen and chain replay;
- signed-envelope database tamper rejection;
- recovery-capsule database tamper rejection;
- verifier-bundle tamper rejection;
- native PQC secret-key zeroization and destruction;
- all inherited Iteration 1–5 tests.

## Validation command

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

## Repository-native Iteration 6 evidence

Implementation head:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31036482697
job: 92409747663
validated head: e9ddcb09d3af525018a9e0196d065107c00674fc
algorithm preflight: PASS
Iterations 1–6 validation: PASS
workflow conclusion: SUCCESS
```

Workflow-policy head:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31037164477
job: 92412018053
validated head: 93338a7330b480552a79ca437c77aca42e9d9cc0
Iterations 1–6 validation: PASS
workflow conclusion: SUCCESS
```

Final README/evidence head:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31037308069
job: 92412545004
validated head: 229e1fa8c6200138d5a81b42a74c20d41b829ffd
Iterations 1–6 validation: PASS
workflow conclusion: SUCCESS
```

The diagnostic artifact from run `31035783049` established that 67 of 68 tests passed and isolated the only failure to punctuation-specific spelling of the enabled liboqs SLH-DSA mechanism name. The assertion was replaced with normalized family and parameter verification. The full cumulative gate then passed on the implementation, workflow-policy, and final README/evidence heads.

## Workflow state

- Workflow: `Pass 213 Compiled ROM Integrity`
- Iteration 1–6 implementation validation: complete and successful.
- Final README/evidence-head validation: complete and successful.
- Restart-record-only evidence commits are intentionally excluded from the runtime rerun path.
- Guarded Continuous Integration remains governed by its inherited path policy.
- Pull request remains draft and unmerged.

## Remaining work

1. Add trusted external timestamp checkpoint anchoring.
2. Implement the complete magic-square/Sudoku/Fibonacci moving tensor family.
3. Add API and CLI surfaces.
4. Add governed native dispatch and performance evidence.
5. Run final integration, merge, and verified-main closure.

## Next exact action

Begin the trusted external timestamp checkpoint layer while retaining every Iteration 1–6 gate. Bind external timestamp tokens to the dual-signed checkpoint root, verifier-bundle root, signed sequence, prior anchored root, and Hash216 lineage. Do not merge Pass 214 ahead of authoritative Pass 213 closure.
