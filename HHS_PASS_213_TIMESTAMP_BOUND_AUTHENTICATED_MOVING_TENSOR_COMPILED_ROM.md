# HHS Pass 213 — Timestamp-Bound Authenticated Moving Tensor Compiled ROM and Runtime Memory Integrity Kernel

**Contract:** `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`  
**Status:** `CONTRACT_AUTHORIZED — IMPLEMENTATION IN PROGRESS`  
**Current iteration:** `9`

## Binding inheritance

Pass 213 is an in-place upgrade of the complete pre-pass foundation and Passes 001–212. Iteration 9 inherits every validated Pass 213 Iteration 1–8 authority without replacement: compiled-ROM identity, correction before interpretation, native protected memory, dependency-scoped parametric admission, persistent inventory and tombstones, post-quantum signed checkpoints, RFC 3161 external timestamp anchoring, and exact moving-tensor authority.

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
→ governed API/CLI projection
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

Every tensor state binds the complete Iteration 7 trusted timestamp-anchor root, signed-checkpoint and verifier-bundle roots, Hash216 lineage, RFC 3161 evidence root, local integer-nanosecond request boundary, TSA serial and UTC generation time, Genesis epoch, tensor sequence, prior tensor root, and declared domain.

These fields and the protected root key derive one domain-separated 256-bit tensor seed. Any change to history, time boundary, lineage, epoch, sequence, domain, or prior state derives a different tensor.

### Exact geometry and closure

The runtime validates all eight Lo Shu dihedral orientations with magic sum 15, exact Sudoku row/column/region invariants, exact Fibonacci residues over all eleven axes, reversible logical-to-physical coordinate maps, and affine one-visit closure proofs over `5,184`, `1,259,712`, and `50,388,480` positions.

The trusted boundary, seed commitment, Lo Shu tensor, Sudoku tensor, Fibonacci phase, coordinate map, and closure proof are committed into one immutable moving-tensor Hash216 root. A canonical Hash72 receipt is emitted over that root.

`MovingTensorStore` uses SQLite WAL mode and `synchronous=FULL`. Every reopen rederives each state from the protected root key and rejects wrong keys, changed anchors or lineage, timestamp regression, altered tensor evidence, substituted chain links, and direct database mutation.

Canonical tensor authority contains no floating-point values. Derived geometry may encode exact phase ratios as committed IEEE-754 binary64 projections, but cannot redefine identity, path membership, receipts, counters, keys, or addresses.

## Iteration 9 — governed API and CLI projection authority

Iteration 9 exposes bounded operational visibility without creating an alternate execution or mutation path.

### Shared transport authority

HTTP and CLI commands call one `Pass213GovernedSurface` dispatcher. Transport formatting cannot alter operation semantics, required capability scope, projection identity, response Hash216, or Hash72 receipt.

The HTTP surface uses FastAPI and inherited canonical runtime response envelopes. The CLI uses `argparse` and emits the same governed payload or a structured fail-closed rejection.

### Scoped capabilities

Protected projection queries require short-lived HMAC-SHA-256 capabilities bound to:

- subject;
- exact sorted scopes;
- issue and expiry boundaries in integer nanoseconds;
- capability epoch;
- unique nonce;
- capability Hash216 identity.

The permitted scopes are:

```text
compiled.read
inventory.verify
tensor.read
tensor.verify
timestamp.read
integrity.verify
receipt.read
```

HTTP accepts either a Bearer token or `X-HHS-Capability`; conflicting headers are rejected. Capability issuance is local CLI authority only and has no network route.

### Append-only public projection chain

Only already validated commitments are published into a separate SQLite WAL projection store. Every projection event binds:

- kind and opaque object identity;
- canonical source Hash216 root;
- bounded sanitized public data;
- exact publication boundary;
- prior projection event root;
- projection event Hash216;
- keyed authentication tag;
- projection-domain Hash72 receipt.

Canonical source receipts remain committed public data but are never substituted for the projection chain's own receipt.

### Protected-state non-exposure

The sanitizer rejects:

- cryptographic keys, owner tokens, authentication tags, capability tokens, and native arena identities;
- protected carriers, payload bytes, exact state bytes, shard payloads, and recovery material;
- tensor seeds, coordinate permutations, physical addresses, physical maps, and vector topology;
- RFC 3161 DER requests, DER responses, and nonces;
- floating-point values in canonical public projections;
- unknown binary objects, excessive depth, excessive collection size, and overlong text.

The surface publishes commitments, counts, invariant results, sanitized TSA metadata, Hash216 roots, and Hash72 receipts only.

### Governed routes

```text
GET  /api/runtime/pass213/status
GET  /api/runtime/pass213/catalog
GET  /api/runtime/compiled-rom/status
POST /api/runtime/compiled-rom/lookup
GET  /api/runtime/memory-integrity/status
POST /api/runtime/memory-integrity/scan
GET  /api/runtime/timestamp-boundary/status
POST /api/runtime/timestamp-boundary/lookup
GET  /api/runtime/tensor-lattice/status
POST /api/runtime/tensor-lattice/lookup
POST /api/runtime/tensor-lattice/verify
GET  /api/runtime/inventory/status
POST /api/runtime/inventory/verify
GET  /api/runtime/pass213/receipts/{object_id}
```

Pass 201's API federation discovers and attaches the router before the static visual root mount.

### Governed CLI

```text
hhs-pass213 status
hhs-pass213 catalog
hhs-pass213 compiled-rom status|lookup
hhs-pass213 memory-integrity status|scan
hhs-pass213 timestamp-boundary status|lookup
hhs-pass213 tensor-lattice status|lookup|verify
hhs-pass213 inventory status|verify
hhs-pass213 receipt get
hhs-pass213 capability issue
```

### Explicitly unexposed operations

Iteration 9 does not expose:

- compiled-ROM compilation or execution;
- physical memory reads;
- repair or recovery mutation;
- deletion or tombstone creation;
- tensor physical mapping;
- recovery-carrier reads;
- RFC 3161 DER reads;
- network capability issuance;
- uncommitted candidate state.

Those operations remain inside their existing canonical authorities until governed native dispatch is implemented and validated.

## Validation

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

The cumulative gate builds the native C arena with warnings as errors, verifies real liboqs mechanisms and OpenSSL RFC 3161 support, executes all 102 Iteration 1–9 tests, compiles every Pass 213 runtime/API/CLI module, parses the machine-readable contract, and retains the complete validation transcript.

Iteration 9 validation includes capability scope/expiry/tamper tests, append-only projection replay, protected-field rejection, source/projection receipt separation, FastAPI OpenAPI and credential behavior, HTTP/CLI parity, local-only capability issuance, mutation-route exclusion, and SQLite tamper detection.

## Iteration boundary

Pass 213 remains nonterminal and unmerged. Remaining implementation work is governed native compiled dispatch, full-hydration performance and recovery evidence, and final integration/verified-main closure.
