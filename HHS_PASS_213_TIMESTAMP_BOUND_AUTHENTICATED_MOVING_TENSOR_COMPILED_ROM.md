# HHS Pass 213 — Timestamp-Bound Authenticated Moving Tensor Compiled ROM and Runtime Memory Integrity Kernel

**Contract:** `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`  
**Status:** `CONTRACT_AUTHORIZED — IMPLEMENTATION IN PROGRESS`  
**Current iteration:** `7`

## Binding inheritance

Pass 213 is an in-place upgrade of the complete pre-pass foundation and Pass 001–212 state. It preserves Pass 212 full-hydration compression, physical erasure recovery, correction before decompression, Hash216 validation, deterministic Hash72 receipts, VM5184×G243 addressing, exact canonical serialization, and singleton VM81 admission.

## Iteration 1 — compiled-ROM nucleus

Iteration 1 established immutable compiled-operation identity, exact timestamp boundaries, noncommutative operation-group authentication, keyed one-visit closure paths, exact lookup, inventory commitments, and deterministic receipts.

```text
validated operation
→ immutable compiled-ROM record
→ Hash216 identity
→ timestamp-bound group
→ keyed closure path
→ authenticated receipt
```

## Iteration 2 — correction before interpretation

Iteration 2 integrated the Pass 212 physical recovery layer into compiled-ROM admission.

```text
compiled-entry bytes
→ Pass 212 protected shards
→ bounded reconstruction
→ reconstructed-payload Hash216
→ canonical deserialization
→ immutable entry Hash216
→ keyed RecoveredROMAdmission
```

No compiled entry reaches the canonical store before physical correction and reconstructed-payload validation complete.

## Iteration 3 — native protected compiled-ROM memory

Iteration 3 stores admitted compiled entries in native non-executable arenas:

```text
PROT_NONE guard
+ mlock / MADV_DONTDUMP / MADV_DONTFORK data pages
+ PROT_NONE guard
```

The native layer provides owner-token authorization, bounds enforcement, read-only sealing, process dump hardening, explicit zeroization, zero verification, and keyed `ALLOCATE → WRITE → SEAL → ZEROIZE → DESTROY` receipts. Canonical bytes remain in sealed arenas and are internally revalidated on lookup.

## Iteration 4 — dependency-scoped parametric admission

Iteration 4 permits one deeply validated compiled transformation to serve compatible typed invocations. Every candidate receives complete schema, type, canonical-serialization, immutable-context, lineage, route, policy, epoch, and timestamp-boundary validation. Semantic revalidation is limited to constraints whose declared dependencies intersect the changed fields.

```text
protected compiled entry
→ sealed parametric template
→ complete typed candidate validation
→ exact changed-field delta
→ affected dependency closure
→ affected-only semantic validation
→ authenticated reuse of unaffected witnesses
→ timestamp-bound VM81 admission
→ sealed native admission arena
```

Similarity alone never grants authority. The candidate must match an exact registered template and protected base entry.

## Iteration 5 — persistent inventory, tombstones, and recovery

Iteration 5 makes the compiled ROM persistent across process and deployment boundaries. `PersistentCompiledROMInventory` uses SQLite WAL mode with full synchronization and maintains:

- an append-only authenticated event chain;
- one successor inventory root per admission, recovery, or tombstone transition;
- a persistent LIVE/TOMBSTONED entry registry;
- retained authenticated Pass 212 recovery carriers;
- separate keyed deletion authorizations;
- retained tombstones and deletion evidence;
- an authenticated checkpoint chain;
- reconciliation against the native protected-memory store.

```text
validate and correct carrier
→ admit into sealed native memory
→ append ADMIT event
→ commit successor inventory root
→ retain authenticated recovery carrier
```

```text
persistent LIVE entry absent from native store
→ classify unexplained absence
→ retained carrier or authenticated checkpoint material
→ Pass 212 correction and Hash216 validation
→ restore sealed native entry
→ append RECOVER event
→ commit successor inventory root
```

```text
current inventory root
→ separately keyed deletion authorization
→ append TOMBSTONE event and successor root
→ retain carrier and authorization evidence
→ zeroize and destroy native arena
```

Every reopen verifies event continuity, event authentication, deterministic state replay, successor inventory roots, retained carriers, deletion authorizations, checkpoint continuity, and persistent LIVE identities against protected native entries.

## Iteration 6 — post-quantum signed checkpoints and recovery enclosure

Iteration 6 encloses the persistent inventory with three independent standardized post-quantum authorities executed through `liboqs`:

- **ML-KEM-768** establishes recovery shared secrets;
- **ML-DSA-65** signs operational inventory checkpoints;
- **SLH-DSA SHA2-128s** signs the same checkpoints for archival authority.

The runtime detects the enabled mechanism names from liboqs and fails the iteration gate unless all three required families and parameter sets are available.

### Native protected key authority

`PQCProtectedAuthority` creates one ML-KEM keypair and two independent signature keypairs. Each secret key is written into a distinct Iteration 3 native arena:

```text
post-quantum secret key
→ owner-bound native arena
→ locked / no-dump / no-fork pages
→ read-only seal
→ public commitment record
```

Only public keys, algorithm names, public-key Hash216 commitments, and the verifier-bundle root leave the protected authority. Signing and decapsulation read the required secret internally for one bounded operation and clear the transient mutable copy. Authority shutdown zeroizes and destroys all three arenas.

### Dual-signed checkpoint chain

Each signed checkpoint binds the complete Iteration 5 checkpoint, its inventory and event-chain roots, retained LIVE and TOMBSTONED state, the signed-checkpoint sequence, the prior signed-checkpoint root, and the verifier-bundle root.

```text
Iteration 5 authenticated checkpoint
+ prior signed root
+ signed sequence
+ verifier-bundle root
→ canonical checkpoint signing message
→ ML-DSA-65 signature
→ SLH-DSA SHA2-128s signature
→ successor signed-checkpoint Hash216
```

`PostQuantumCheckpointStore` appends the complete dual-signature envelope to SQLite WAL storage. A verifier-only process can reopen and replay the full signed chain using the public verifier bundle without access to any secret key.

### ML-KEM recovery capsule

```text
ML-KEM-768 encapsulation to recovery public key
→ shared secret
→ HKDF-SHA-256 with checkpoint-root salt and complete capsule AAD
→ AES-256-GCM wrapping key
→ encrypt exact 256-bit recovery root
→ commit KEM ciphertext, nonce, ciphertext, AAD root, and checkpoint root
```

The capsule binds its signed sequence, checkpoint root, algorithm identity, and recipient public-key Hash216. Recovery requires the protected ML-KEM secret-key arena. Any altered KEM ciphertext, nonce, encrypted recovery key, AAD, recipient key, sequence, or checkpoint root fails structural validation or authenticated decryption.

## Iteration 7 — trusted external timestamp anchoring

Iteration 7 makes the signed checkpoint chain externally time-authenticated through RFC 3161. A timestamp anchor is not a detached wall-clock label. Its message imprint is the SHA-256 digest of a canonical, domain-separated intent containing:

- the complete Iteration 6 signed-checkpoint root;
- the public verifier-bundle root;
- the exact signed and anchor sequence;
- the prior trusted timestamp-anchor root;
- the Hash216 lineage root for the anchored history;
- the local integer-nanosecond request boundary;
- the timestamp-authority identity.

```text
ML-DSA + SLH-DSA signed checkpoint
+ verifier-bundle root
+ prior external anchor root
+ Hash216 lineage root
+ local nanosecond boundary
+ TSA authority ID
→ canonical timestamp intent
→ SHA-256 RFC 3161 message imprint
→ nonce-bearing DER TimeStampReq
→ independent X.509 TSA signature
→ DER TimeStampResp
→ successor trusted timestamp-anchor Hash216
```

### RFC 3161 authority and transport

`RFC3161TimestampVerifier` uses OpenSSL's RFC 3161 implementation to create a DER request containing the message imprint, certificate request, and fresh nonce. `HTTPRFC3161Transport` submits it using the standard `application/timestamp-query` and `application/timestamp-reply` media types. `OpenSSLTSATransport` provides the same protocol boundary for isolated or offline TSA deployments and deterministic integration testing.

The response is accepted only when OpenSSL verifies it against the original request and an explicitly pinned X.509 trust bundle. The runtime retains:

- the exact DER request and response;
- request and response SHA-256 identities;
- the TSA policy identifier;
- the TSA serial number;
- the UTC generation time;
- the TSA subject;
- the request nonce;
- the trust-bundle SHA-256 identity;
- a Hash216 verification receipt and complete evidence root.

### Persistent external anchor chain

`TrustedTimestampAnchorStore` persists one externally timestamped record per signed checkpoint in SQLite WAL mode with full synchronization. Every reopen revalidates both post-quantum signatures and the RFC 3161 token against the pinned trust bundle.

```text
signed sequence n
+ prior signed checkpoint root
+ prior timestamp anchor root
→ RFC 3161 verified evidence
→ timestamp anchor n
→ atomic persistent append
→ full public reverification on reopen
```

The store rejects sequence gaps, signed-checkpoint-chain discontinuity, prior-anchor substitution, Hash216-lineage substitution, local-boundary regression, TSA-time regression, repeated TSA serials, certificate-trust substitution, nonce removal, message-imprint mismatch, and DER response alteration. Recomputing local hashes after changing a token does not create an accepted history because the independent TSA signature no longer verifies.

## Current acceptance path

```text
untrusted carrier
→ Pass 212 correction and Hash216 validation
→ recovered admission proof
→ sealed native compiled-ROM arena
→ persistent ADMIT/root chain
→ exact or parametric compiled match
→ timestamp-bound VM81 authority
→ persistent checkpoint
→ ML-DSA + SLH-DSA signed checkpoint
→ ML-KEM recovery enclosure
→ RFC 3161 external timestamp anchor
→ governed native dispatch
→ successor receipt and persistent reconciliation
```

## Validation

```bash
python -m pip install -r requirements/pass213-pqc.txt
bash scripts/run_pass213_iteration1_validation.sh
```

The dedicated gate:

1. builds the native C arena with warnings treated as errors;
2. loads the pinned liboqs Python binding and matching liboqs release;
3. verifies ML-KEM-768, ML-DSA-65, and SLH-DSA SHA2-128s are enabled;
4. verifies OpenSSL RFC 3161 command support;
5. creates an actual local X.509 timestamp authority for integration tests;
6. executes every Iteration 1–7 test module;
7. compiles every Pass 213 runtime module;
8. parses the machine-readable contract.

Validated Iteration 7 implementation evidence:

```text
head: 67e36905679fe99f883b9500ec7efbe13e4abcf4
workflow run: 31053828521
job: 92466865251
tests: 74 passed
result: SUCCESS
```

## Iteration boundary

Pass 213 remains nonterminal. Remaining work includes the full high-dimensional magic-square/Sudoku/Fibonacci moving tensor family, API and CLI surfaces, governed native dispatch, performance evidence, final integration, merge, and verified-main closure.
