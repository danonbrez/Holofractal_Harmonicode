# Pass 213 Restart Record — Iteration 8

- Contract: `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`
- Immediate parent: Pass 212 full-hydration compression and physical erasure recovery
- Base commit: `2be050264a6e9c659603100be802979bbc49bf7a`
- Branch: `agent/pass213-compiled-rom-integrity`
- Final validated Iteration 7 head: `ff6d0e70504a86c6906573d0cffbbffc131048b9`
- Iteration 8 implementation/workflow head: `92d506674b529e4a27a14daf997dd61e0006fba6`
- Final validated Iteration 8 contract/documentation head: `891fc461a698b4a8385a3dc5da6d40adac3c625e`
- Merge target: `main`
- Draft pull request: `#169`
- Iteration: `8`

## Cumulative runtime state

Iterations 1–8 are implemented and repository-validated. The current chain includes:

- immutable timestamp-bound Hash216 compiled-ROM identity;
- Pass 212 correction before interpretation;
- guarded, locked, sealed, and zeroizing native memory;
- dependency-scoped parametric validation and authenticated witness reuse;
- persistent inventory roots, tombstones, unexplained-deletion detection, and recovery;
- ML-KEM-768 recovery enclosure;
- ML-DSA-65 and SLH-DSA SHA2-128s checkpoint signatures;
- RFC 3161 external timestamp anchoring;
- exact trusted-anchor-bound moving tensor authority.

## Iteration 8 files

Added:

- `hhs_backend/runtime/hhs_pass213_tensor_geometry_v1.py`
- `hhs_backend/runtime/hhs_pass213_tensor_closure_v1.py`
- `hhs_backend/runtime/hhs_pass213_tensor_boundary_v1.py`
- `hhs_backend/runtime/hhs_pass213_moving_tensor_v1.py`
- `hhs_backend/runtime/hhs_pass213_tensor_store_v1.py`
- `tests/test_pass213_moving_tensor_v1.py`

Extended:

- `HHS_PASS_213_TIMESTAMP_BOUND_AUTHENTICATED_MOVING_TENSOR_COMPILED_ROM.md`
- `contracts/pass213/PASS_213_CONTRACT.json`
- `docs/pass213/README.md`
- `docs/pass213/RESTART_RECORD.md`
- `scripts/run_pass213_iteration1_validation.sh`
- `.github/workflows/pass213-compiled-rom-integrity.yml`

## Iteration 8 authority

### Trusted anchor binding

Each tensor state binds the complete Iteration 7 timestamp anchor, signed-checkpoint root, verifier-bundle root, Hash216 lineage, RFC 3161 evidence root, local nanosecond boundary, TSA serial, UTC generation time, Genesis epoch, tensor sequence, prior tensor root, and declared domain.

### Exact geometry

- all eight exact Lo Shu dihedral orientations;
- magic sum 15 over rows, columns, and diagonals;
- exact Sudoku band, stack, row, column, digit, and transpose transformations;
- exact Sudoku row, column, and 3×3 region uniqueness;
- exact Fibonacci residues over moduli `9,9,4,4,4,3,3,3,3,3,40`;
- reversible logical/physical mapping over `1,259,712` and `50,388,480` positions;
- exact operation-axis, G243-control-axis, and hydration-lane permutations.

### Exact closure

The closure proof uses:

```text
C(i) = (a·i + b) mod N
gcd(a, N) = 1
```

It retains the modular inverse, endpoints, closing successor, sample commitment, path root, and proof root for the `5,184`, `1,259,712`, and `50,388,480` domains.

### State and persistence

- immutable moving-tensor Hash216 root;
- canonical Hash72 receipt;
- SQLite WAL with `synchronous=FULL`;
- append-only tensor root continuity;
- complete trusted-anchor retention;
- protected-key rederivation on every reopen;
- rejection of key, anchor, lineage, timestamp, coordinate, closure, receipt, chain, or database substitution;
- root-key zeroization on close or failed reopen.

### Floating projection boundary

Canonical authority contains no floating-point values. The optional projection is IEEE-754 binary64, big-endian, nearest-even, FMA-forbidden, NaN-forbidden, and commits the exact source ratios and exact bit patterns.

## Validation command

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

## Repository-native Iteration 8 evidence

Implementation/workflow head:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31055983254
job: 92473465106
validated head: 92d506674b529e4a27a14daf997dd61e0006fba6
Iterations 1–8 validation: PASS
result: SUCCESS
```

Final contract/documentation head:

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31056363508
job: 92474616663
validated head: 891fc461a698b4a8385a3dc5da6d40adac3c625e
cumulative tests: 83 passed
result: SUCCESS
artifact: pass213-iteration8-validation-31056363508
artifact digest: sha256:df16684790a37e0ed5c7097be5b36c9a2ad738a3a02b10940223dadfafdc7f47
```

The gate builds the native C arena with warnings as errors, verifies real liboqs mechanisms and OpenSSL RFC 3161 support, executes all 83 cumulative tests, compiles every Pass 213 runtime module, parses the Iteration 8 contract, and retains the complete transcript.

## Workflow state

- Iteration 1–8 implementation validation: complete and successful.
- Final Iteration 8 contract/documentation validation: complete and successful.
- Guarded Continuous Integration remains governed by its inherited path policy.
- Pull request remains draft and unmerged.

## Remaining work

1. Add API and CLI parity for compiled ROM, recovery, inventory, PQC checkpoints, trusted timestamps, and moving tensors.
2. Add governed native compiled dispatch.
3. Produce full-hydration performance and recovery evidence.
4. Run final integration, merge, and verified-main closure.

## Next exact action

Begin Iteration 9 with governed API and CLI surfaces while retaining every Iteration 1–8 gate. The public interfaces must expose only sanitized commitments, status, receipts, and authorized operations; they must not expose protected memory addresses, state-local keys, internal vector topology, tensor seeds, private recovery material, or uncommitted transitions. Pass 214 must not merge ahead of authoritative Pass 213 closure.
