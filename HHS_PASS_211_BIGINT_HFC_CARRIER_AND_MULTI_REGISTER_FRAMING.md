# HHS Pass 211 — BigInt HFC Carrier and Multi-Register Framing

**Contract:** `HHS-P211-P133-BIGINT-HFC-MULTIREGISTER-H72-H216`  
**Classification target:** `HHS_PASS_211_BIGINT_HFC_CARRIER_RUNTIME_VERIFIED`

## 1. Objective

Turn the observed Pass 133 × Pass 210 composition into a replayable cumulative runtime guarantee. The Pass 133 palindromic SECDED carrier remains the sole canonical BigInt serialization. Pass 211 adds only deterministic framing across one or more Pass 210 registers.

## 2. Exact dimensional bridge

```text
Pass 210 register       = 5184 Boolean cells
packed register capacity = 5184 / 8 = 648 bytes
bit mapping              = register[8*b+i] = (payload[b] >> (7-i)) & 1
```

The final shard records its exact payload bit length. Every bit after that boundary must be zero. Non-final shards are exactly 648 bytes.

## 3. Package identity

Each shard commits:

- shard index and total count;
- exact payload byte and bit lengths;
- payload Hash216;
- Pass 210 register Hash216;
- Hash72, Hash216, phase, and frame projection identities;
- Pass 210 frame receipt;
- all 36 snapshot witness roots;
- strict-domain admission or exact rejection classification.

The package root commits the ordered shard roots, carrier identity, source identity, Pass 133 Hash72 witness, shard count, and final-shard bit length. One deterministic package-level Hash72 receipt binds the package root and the ordered roots.

## 4. Decode order

```text
package structure
→ ordered shard roots
→ HFC frame/projection/snapshot anchors
→ optional one-snapshot recovery
→ exact carrier byte concatenation
→ Pass 133 palindrome and center validation
→ SECDED correction/fail-closed behavior
→ canonical TLV and digest validation
→ source BigInt identity
```

Structural palindrome rejection precedes ECC correction when the mirror shape itself is invalid. This is intentional layered behavior.

## 5. Agreement semantics

`hfc_agree` compares the projections supplied to it. If every projection is freshly generated from the same uniformly changed register, the projections can self-agree. That result is contemporaneous consistency only.

Historical integrity requires at least one independently retained minted anchor. Pass 211 stores those anchors at package creation and compares every fresh read against them. The anchored result is classified as either:

- `ANCHORED_WITNESSES_VERIFIED`; or
- `ANCHORED_DISAGREEMENT_LOCATED`.

No repair is performed by the agreement operation.

## 6. Compression honesty boundary

For every carrier shard, Pass 211 guarantees exact framing, reconstruction, double witness coverage, one-snapshot erasure recovery, ordered package integrity, and anchored corruption localization.

Strict-size compression remains restricted to the Pass 210 declared domain:

```text
HFC_ADMISSIBLE_AFFINE_FIBONACCI_MOD2_V1
a[n] = (a[n-1] + a[n-2] - 1) mod 2
```

A carrier shard outside that recurrence is recorded as `STRICT_DOMAIN_REJECTED` with `HFC_STRICT_COMPRESSION_DOMAIN_WITNESS_REQUIRED`. It is never described as compressed.

## 7. Required negative behavior

The runtime rejects:

- zero and negative Pass 133 source values;
- missing or duplicated shards;
- reordered shard lists;
- payload substitution;
- wrong final-shard bit length;
- non-zero padding;
- altered projection, snapshot, package-root, receipt, metric, or Pass 133 witness data;
- an ambiguous or uncorrectable Pass 133 carrier.

## 8. Conformance workload

The evidence workload contains:

- 11 independent Pass 133 exact round trips;
- 512 sampled single-bit SECDED corrections and two fail-closed double-error drills;
- four one-register Pass 133 carriers;
- all 36 erasure positions for each fitting carrier, totaling 144 recoveries;
- a deterministic 1024-bit source requiring multiple HFC registers;
- stacked HFC erasure recovery followed by one Pass 133 ECC correction;
- affine-Fibonacci strict admission and ordinary carrier strict rejection;
- anchored localization of exactly register cell 1000;
- missing, duplicate, reordered, substituted, zero, and negative cases;
- deterministic clean-runtime replay.

## 9. Authority surfaces

- Runtime: `hhs_backend/runtime/hhs_pass211_bigint_hfc_carrier_v1.py`
- API: `/api/runtime/bigint-hfc-carrier`
- Contract: `contracts/pass211/PASS_211_CONTRACT.json`
- Evidence: `evidence/pass211/PASS_211_BIGINT_HFC_REFERENCE_VECTORS.json`
- Gate: `scripts/run_pass211_bigint_hfc_validation.sh`
