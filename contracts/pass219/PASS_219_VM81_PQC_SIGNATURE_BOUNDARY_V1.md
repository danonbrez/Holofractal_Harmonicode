# PASS 219 — VM81 Post-Quantum Signature Boundary v1

## 1. Purpose

This contract is the asymmetric cryptographic successor to:

```text
PASS_219_VM81_PQC_FIREWALL_EXTERNAL_AUTHORITY_CLOSURE_V1
PASS_219_POST_219_COMPOSITIONAL_DEVELOPMENT_ABI_V1
```

It preserves Pass 220+ compositional development while making the Pass 219
VM81 firewall the only production path by which a post-219 candidate can reach
hidden RNA/VM81 canonical mutation authority.

The 1.30 HMAC-SHA-512 record is retained as an internal symmetric provenance
seal. It is not a public-key signature and MUST NOT be represented as one.
The 1.31 successor adds an actual post-quantum asymmetric signature gate.

Normative production predicate:

```text
VM81_MUTATE(candidate) ⇒
    pass(candidate) >= 220
∧   parent_hash216_reference_complete(candidate)
∧   all_216_positional_sha256_records_rederived(candidate)
∧   parent_receipt_lineage_matches(candidate)
∧   RNA219_CPP_CELL_WALL(candidate)
∧   exact_648_byte_frame_bound(candidate)
∧   internal_HMAC_SHA512_root_seal_valid(candidate)
∧   PQ_SIGNATURE_VERIFIED(candidate)
∧   inherited_canonical_revalidation(candidate)
∧   child_hash216_reference_complete(candidate)
```

where:

```text
PQ_SIGNATURE_VERIFIED :=
    ML-DSA-65 verified
    OR
    SLH-DSA-SHA2-192s verified
```

No unsigned production fallback is permitted.

---

## 2. Authority split

The caller MAY choose one of the two fixed signature profiles:

```text
ML-DSA-65
SLH-DSA-SHA2-192s
```

The caller MUST NOT provide:

```text
private signing key
public-key replacement
signature bytes
signature verifier callback
Hash216 positional resolver callback
canonical receipt
VM81 mutation capability
```

The kernel derives the selected signature keypair from the already-required
512-bit firewall root through a domain-separated deterministic expansion.
Therefore the caller selects an algorithm profile but never possesses signing
authority merely by invoking the ABI.

The resulting signature receipt is diagnostic provenance evidence only:

```text
signature_is_canonical_receipt = false
external_key_authority         = false
external_signature_authority   = false
```

Canonical Hash72 / Hash216 receipt ownership remains with the inherited
singleton VM81 authority.

---

## 3. Hash216 restore/reference invariant

A Hash216 reference is admissible only if the kernel independently proves all
of the following:

```text
three Hash72 lanes present in fixed order
transition identity rederived from those lanes
resolved_index_count == 216
for every absolute position i in [0,215]:
    lane_role == floor(i / 72)
    lane_position == i mod 72
    glyph == transition_word216[i]
    sha256_index_present == true
    sha256_index_record == KernelDerive(previous_index, identity, i, glyph)
```

An external resolver cannot participate in this production predicate.

A failure is a provenance/security failure, not a semantic candidate failure:

```text
invalid Hash216 reference ⇒ VM81_HALT
```

before hidden RNA authority is invoked.

---

## 4. Signed instruction message

The asymmetric signature covers a deterministic message containing at least:

```text
signature-domain/version
post-219 pass number
selected PQ signature profile
monotonic anti-replay instruction sequence
candidate Hash72
RNA cell-wall path Hash216
parent Hash216 transition identity
SHA-256 root over all 216 positional SHA-256 records
exact 648-byte little-endian VM81 candidate frame
cell-wall graph signature
cell-wall tensor signature
cell-wall decision signature
selected routing lane
internal HMAC-SHA-512 provenance tag
```

Thus a valid signature cannot be transplanted to another candidate frame,
another Hash216 parent, another cell-wall route, or another instruction
sequence without verification failure.

---

## 5. Signature profiles

### 5.1 ML-DSA-65

The primary profile is ML-DSA-65 as standardized by FIPS 204.

The kernel derives the deterministic 32-byte ML-DSA seed from the 512-bit
firewall root with a domain-separated HMAC-SHA-512 expansion, constructs the
keypair internally, signs the exact instruction message, and verifies the
signature before VM81 mutation authority is invoked.

### 5.2 SLH-DSA-SHA2-192s

The alternate profile is SLH-DSA-SHA2-192s as standardized by FIPS 205.

The deterministic key-generation seed has length `3*n = 72` bytes for the
192-bit parameter family and is derived by the same domain-separated kernel
expansion. The keypair, signature, and verification remain internal.

---

## 6. Provider law

The implementation uses the OpenSSL provider interface for these standardized
algorithms.

Provider availability is part of the executable security precondition:

```text
requested_algorithm_unavailable
    ⇒ VM81_HALT
    ⇒ committed_frame = 0
    ⇒ inherited_rna_authority_invoked = false
```

There is no automatic downgrade from an unavailable ML-DSA/SLH-DSA provider to
HMAC-only admission.

The HMAC seal may still be computed as an internal layer, but it is not
sufficient for production mutation after this contract.

---

## 7. HALT versus semantic rejection

Security/provenance failure:

```text
InvalidPassPath
∨ InvalidCellWallPath
∨ InvalidHash216Reference
∨ InvalidHashLineage
∨ InvalidCandidateHash
∨ InvalidHMACAuthenticator
∨ InvalidPQSignatureProfile
∨ PQSignatureProviderUnavailable
∨ PQSignatureGenerationFailure
∨ PQSignatureVerificationFailure
∨ ChildHash216InvariantFailure
⇒ VM81_HALT
```

HALT requires:

```text
committed_frame = ZERO
canonical receipt issuance = false
persistence = false
subsequent requests in process = fail closed
```

A mathematical admission failure after every provenance/signature check passes
remains distinct:

```text
ValidProvenance
∧ ValidPQSignature
∧ CanonicalConstraintReject
⇒ REJECT
∧ committed_frame = ZERO
∧ VM81_HALT = false
```

This separation prevents malformed provenance from being treated as an ordinary
candidate while preserving legitimate negative mathematical results.

---

## 8. Dynamic ABI closure

After 1.31, the intended production dynamic mutation surface is:

```text
hhs_exact_pass219_vm81_pqc_admit_signed
```

The following mutation primitives MUST NOT be exported as independent
production dynamic ABI authorities:

```text
hhs_exact_vm81_admit_uqcel
hhs_exact_pass219_admit_composed
hhs_exact_pass219_rna_admit_composed
hhs_exact_pass219_vm81_pqc_admit
```

Non-mutating Hash216 reference construction/verification and capability queries
may remain public.

---

## 9. Pass 220+ development preservation

This signature boundary does not freeze the pass system.

For every pass `P_n`, `n >= 220`:

```text
P_n MAY:
    define
    compose
    lower through Pass 219 RNA
    optimize
    validate
    cache candidate state
    request signed canonical admission
    observe canonical result
```

but:

```text
P_n MUST NOT:
    sign with an externally supplied canonical key
    choose a caller-defined resolver
    bypass the RNA cell wall
    bypass the Hash216 reference proof
    bypass the asymmetric signature gate
    directly mutate VM81 canonical state
    directly issue canonical Hash72/Hash216 receipts
```

The high-level pass remains development authority; Pass 219 remains lowering
and cryptographic membrane; the singleton kernel remains canonical authority.

---

## 10. Environment and trust statement

The canonical admission policy is designed to be self-contained and
fail-closed with respect to its software-defined invariants. This does not
claim that software can become physically independent of the machine executing
it.

The trusted computing assumptions remain explicit:

```text
correct kernel/runtime binary
protected 512-bit firewall root
correct CPU/memory execution
correct cryptographic provider implementation
correct operating-system process isolation for secret material
```

Within those assumptions, host applications, plugins, remote callers, API
clients, later passes, GPU candidates, vector caches, and distributed workers
cannot acquire canonical mutation authority merely by controlling invocation
or supplying validation material.

---

## 11. Closure equation

The resulting post-219 production path is:

```text
Pass 220+ candidate
    ↓
Pass 219 exact composition
    ↓
Pass 219 RNA C++ cell wall
    ↓
kernel-owned Hash216[216] parent verification
    ↓
exact 648-byte candidate + route + anti-replay binding
    ↓
internal HMAC-SHA-512 provenance seal
    ↓
ML-DSA-65 OR SLH-DSA-SHA2-192s sign+verify
    ↓
hidden RNA canonical admission
    ↓
child Hash216[216] revalidation
    ↓
COMMIT + inherited canonical receipt
```

Any broken security edge before the hidden canonical admission step is a
latched VM81 HALT, not a recoverable caller exception or a normal semantic
rejection.
