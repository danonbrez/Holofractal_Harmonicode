# Pass 219 I14 — Multi-Source Convergence Evidence

## Purpose

I14 consumes the verified I13 PQC speculative-hydration membrane and defines when two or more frozen external sources may be treated as one reusable native route. It does **not** infer convergence from model agreement, architecture labels, logits, embedding proximity, or floating-point similarity.

The admissible convergence relation is:

```text
independent frozen source manifests
        -> independently verified I13 evidence bundles
        -> identical committed VM81 frame serialization
        -> identical admitted child Hash216 identity
        -> multi-source convergence receipt
        -> candidate deduplication authorization
```

Deduplication is therefore downstream of VM81/Hash216 equality, never a substitute for it.

## I14-C1 — independent provenance

At least two source manifests are required. Every source must retain a distinct immutable `source_hash`; architecture diversity is allowed but is not required. The original source hash, source architecture, projection-root Hash216, five-lane roots, H2 coordinate, H5 index, exact constraint surface, and projection proof remain part of the per-source evidence.

## I14-C2 — post-I13 admission evidence only

Every source evidence bundle must satisfy the I13 exact projection contract and must carry a committed VM81 result plus the inherited RNA admission, PQC firewall receipt, PQC signature receipt, and environmental receipt. The I14 verifier rejects non-committed, halted, unsigned, externally authoritative, non-VM81, or structurally inconsistent evidence.

I14 does not re-sign or re-admit a source. It verifies and composes evidence that is already downstream of I13. `hhs_exact_pass219_vm81_environment_admit_signed` remains the sole public mutation successor.

## I14-C3 — source-route cryptographic binding

For each admitted source, I14 derives a deterministic project-native Hash216 binding over:

- immutable source hash and architecture ID;
- source projection-root Hash216;
- all five projection-lane roots;
- exact H2 and H5 coordinates;
- exact constraint-surface and projection-proof digests;
- committed candidate Hash72;
- admitted child Hash216 identity;
- signed-message digest;
- environmental witness digest.

The binding is evidence only. It creates no Hash216 mutation authority and does not replace the inherited transition identity.

## I14-C4 — convergence predicate

For `N >= 2` independently sourced evidence bundles, deduplication is authorized only when all of the following are true:

1. every bundle passes I14 post-I13 evidence validation;
2. all source hashes are distinct;
3. the committed VM81 frames are byte-identical under the inherited 648-byte serialization;
4. their canonical frame Hash72 values are identical;
5. their admitted child Hash216 identities are identical.

If the sources are valid but the admitted identity or committed frame differs, the result is `NOT_CONVERGED` and deduplication remains forbidden.

## I14-C5 — authority membrane

The I14 API is `static inline` and non-mutating. It creates no dynamic ABI, no canonical mutation authority, no canonical Hash216 authority, and no persistence authority. H5 remains candidate-only and the four inherited Holo4 lanes remain canonical.

## Validation semantics

The executable gate includes deterministic logic fixtures for positive convergence, divergent-route rejection, duplicate-source rejection, provenance-binding separation, and tamper rejection. It also attempts a live two-source I13 admission/convergence when the runtime exposes the required PQC signature provider. When the provider is unavailable, the test records `I14_LIVE_MULTISOURCE_NOT_CLAIMED_PQC_PROVIDER_UNAVAILABLE`; that condition is not reported as live convergence evidence and the inherited I13 fail-closed behavior remains authoritative.
