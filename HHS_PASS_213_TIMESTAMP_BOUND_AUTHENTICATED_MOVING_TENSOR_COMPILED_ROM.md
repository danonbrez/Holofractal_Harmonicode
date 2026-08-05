# HHS Pass 213 — Timestamp-Bound Authenticated Moving Tensor Compiled ROM and Runtime Memory Integrity Kernel

**Contract:** `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`  
**Status:** `CONTRACT_AUTHORIZED — IMPLEMENTATION IN PROGRESS`  
**Current iteration:** `8`

## Binding inheritance

Pass 213 is an in-place upgrade of the complete pre-pass foundation and Passes 001–212. Iteration 8 inherits every validated Pass 213 Iteration 1–7 authority without replacement: compiled-ROM identity, correction before interpretation, native protected memory, dependency-scoped parametric admission, persistent inventory and tombstones, post-quantum signed checkpoints, and RFC 3161 external timestamp anchoring.

## Cumulative acceptance path

```text
untrusted carrier
→ Pass 212 correction and reconstructed Hash216 validation
→ immutable compiled-ROM admission
→ sealed native memory
→ exact or dependency-scoped parametric match
→ persistent inventory and authorized transition root
→ ML-DSA + SLH-DSA checkpoint signatures
→ ML-KEM recovery enclosure
→ RFC 3161 trusted external timestamp anchor
→ exact moving-tensor derivation
→ singleton VM81 admission and governed native dispatch
```

## Iterations 1–7 retained authority

1. **Compiled-ROM nucleus:** immutable Hash216 operations, integer timestamp boundaries, noncommutative order chains, exact lookup, closure paths, and receipts.
2. **Correction before interpretation:** Pass 212 shard recovery and recovered-payload Hash216 validation precede compiled-entry deserialization.
3. **Native protected memory:** guarded, locked, non-executable, dump-excluded, fork-excluded, owner-bound arenas with read-only sealing and verified zeroization.
4. **Parametric admission:** typed immutable templates, exact changed-field deltas, dependency-scoped revalidation, authenticated witness reuse, and timestamp-bound VM81 authority.
5. **Persistent inventory:** SQLite WAL append-only `ADMIT`, `RECOVER`, and `TOMBSTONE` chains, native reconciliation, unexplained absence detection, and retained recovery material.
6. **Post-quantum enclosure:** ML-KEM-768 recovery, ML-DSA-65 operational signatures, SLH-DSA SHA2-128s archival signatures, native secret-key arenas, and verifier-only replay.
7. **Trusted external time:** RFC 3161 DER requests and responses bound to signed checkpoints, verifier roots, prior anchors, Hash216 lineage, local boundaries, TSA identity, nonce, serial, policy, and UTC generation time.

## Iteration 8 — exact moving-tensor authority

Iteration 8 turns the timestamped tensor lattice into an executable canonical authority rather than descriptive metadata.

### Canonical tensor domain

The exact coordinate basis is:

```text
(row, column, a, b, d, t0, t1, t2, t3, t4, lane)
```

with axis moduli:

```text
(9, 9, 4, 4, 4, 3, 3, 3, 3, 3, 40)
```

After VM5184×G243 projection:

```text
9² × 4³ × 3⁵ = 1,259,712
```

After forty hydration lanes:

```text
9² × 4³ × 3⁵ × 40 = 50,388,480
```

The logical address remains canonical. The tensor supplies a reversible physical placement for the same logical state.

### Trusted boundary derivation

Every tensor state binds:

- the complete Iteration 7 trusted timestamp-anchor root;
- signed-checkpoint and verifier-bundle roots;
- Hash216 lineage;
- RFC 3161 evidence root;
- local integer-nanosecond request boundary;
- TSA serial and UTC generation time;
- Genesis epoch, tensor sequence, prior tensor root, and declared domain.

These fields and the protected root key derive one domain-separated 256-bit tensor seed. Any change to history, time boundary, lineage, epoch, sequence, domain, or prior state therefore derives a different tensor.

### Lo Shu authority

The runtime selects one of all eight exact dihedral orientations of:

```text
4 9 2
3 5 7
8 1 6
```

Every accepted orientation proves:

- exact symbols 1–9;
- row sums equal 15;
- column sums equal 15;
- both diagonal sums equal 15.

### Sudoku authority

The 9×9 tensor is generated only through legal exact transformations:

- band and stack permutations;
- row permutations inside bands;
- column permutations inside stacks;
- digit permutation;
- optional transpose.

Every row, column, and 3×3 region must contain the exact symbols 1–9.

### Fibonacci phase

Exact Fibonacci residues are computed for the eleven axis moduli. These residues participate in operation-axis offsets, G243 control-axis offsets, and hydration-lane phase without introducing floating-point authority.

### Reversible coordinate movement

The moving coordinate map applies:

- exact row and column permutations;
- operation-axis permutation and modular offsets over three base-4 axes;
- control-axis permutation and modular offsets over five base-3 axes;
- a coprime affine permutation over forty hydration lanes.

Both `map_index` and `unmap_index` are exact inverses over `1,259,712` and `50,388,480` positions.

### Full-domain closure proof

For domain size `N`, the closure path is:

```text
C(i) = (a·i + b) mod N
```

with:

```text
gcd(a, N) = 1
```

The proof stores the modular inverse of `a`, first and last cells, closing successor, sample commitment, inherited closure-path root, and proof root. This proves a one-to-one traversal and exact wrap without materializing all 50,388,480 cells. The 5,184-cell domain is additionally materialized in tests to prove unique visitation directly.

### State and receipt authority

The trusted boundary, seed commitment, Lo Shu tensor, Sudoku tensor, Fibonacci phase, coordinate map, and closure proof are committed into one immutable moving-tensor Hash216 root. A canonical Hash72 receipt is emitted over that root.

### Persistent replay

`MovingTensorStore` uses SQLite WAL mode and `synchronous=FULL`. It stores the complete tensor state and trusted timestamp anchor. Every reopen rederives every state from the protected root key and rejects:

- wrong keys;
- changed anchors or lineage;
- timestamp or anchor-sequence regression;
- altered Lo Shu, Sudoku, Fibonacci, coordinate, closure, tensor-root, or Hash72 evidence;
- missing or substituted chain links;
- direct database mutation.

### Derived floating projection

Canonical tensor authority contains no floating-point values. A separate projection may encode exact phase ratios as IEEE-754 binary64 with:

- big-endian serialization;
- nearest-even rounding;
- FMA forbidden;
- NaN forbidden;
- exact source ratios and exact 64-bit patterns committed into a projection root.

The projection cannot redefine canonical identity, path membership, receipts, counters, keys, or addresses.

## Validation

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

The cumulative gate builds the native C arena with warnings as errors, verifies real liboqs mechanisms and OpenSSL RFC 3161 support, runs all Iteration 1–8 tests, compiles every Pass 213 runtime module, parses the machine-readable contract, and retains the complete validation transcript.

## Iteration boundary

Pass 213 remains nonterminal and unmerged. Remaining implementation work is API/CLI parity, governed native compiled dispatch, full-hydration performance and recovery evidence, and final integration/verified-main closure.
