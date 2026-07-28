# HHS Pass 163 implementation status

## Scope

This change implements the first executable Pass 163 reference runtime and repairs the blocking Hash72 dependency identified by the independent Pass 163 / Pass 150 / Pass 158 verification report.

## Dependency repairs

### Hash72 closure

The prior validator evaluated:

```python
sum(range(72)) % 72 == 0
```

That expression is permanently false because `sum(range(72)) = 2556` and `2556 mod 72 = 36`.

The repaired validator now checks:

- exact 72-symbol population;
- membership in the canonical 72-symbol alphabet;
- one ordered traversal of the complete `u(k) = k mod 72` phase ring;
- closure from phase 71 back to phase 0.

### Canonical Hash72(D || S)

`hhs_runtime/core/hash72_digest_v1.py` now defines a callable construction with:

- `HHS-HASH72-DIGEST-V1` domain separation;
- explicit 64-bit big-endian length framing for `D` and `S`;
- canonical JSON for structured values;
- SHAKE-256 expansion;
- rejection sampling into the 72-symbol alphabet without modulo bias;
- constant-time verification;
- a Pass 158/163 Hash216 projection-receipt bridge.

## Pass 163 implementation

The Python reference runtime implements:

- the position-major `81 × 64 = 5184` Boolean snapshot;
- exact 648-byte expanded state;
- exact 864-symbol unpadded full-snapshot Base64;
- strict canonical decoding by decode/re-encode equality;
- thread-major and position-major transpose projections;
- zero- and one-background sparse polarity compression;
- immutable parameter identities and dictionary roots;
- bounded deterministic phase-gear propagation;
- exact rational, path-dependent virtual-memristor edges;
- exact continuation keys with stale invalidation;
- capability-zero rejection and foreign-lane mutation rejection;
- singleton VM81 kernel and singleton permanent index construction;
- candidate validation followed by atomic commit;
- inherited Pass 150 Hash216 operation identity;
- Hash72 snapshot identity and Hash72(D||S) state identity;
- append-only journals and permanent Hash216 index records;
- deterministic replay with tamper detection;
- canonical Base64 ABI envelopes with integrity and Hash216 identity.

The C11 reference surface implements:

- fixed-width versioned snapshot storage;
- explicit position/thread bounds;
- authority-token-gated writes;
- exact 648-byte / 864-symbol Base64 encode/decode;
- strict canonical decode;
- `-std=c11 -Wall -Wextra -Werror -pedantic` compilation.

The FastAPI composition entrypoint is:

```text
hhs_backend.pass163_server:app
```

The governed route prefix is:

```text
/api/runtime/vmrc
```

## Executed validation

```text
Python: 18 passed
C11: compile succeeded; native test executable returned 0
```

The Python matrix covers geometry, transpose closure, Base64 geometry, sparse polarity, Hash72 determinism and tamper rejection, parameter immutability, candidate admission, stale roots, expected-output mismatch, bounds, foreign-lane rejection, bounded gear propagation, path-dependent exact memristor state, continuation key exactness, ABI envelope tamper rejection, and replay-journal tamper rejection.

## Classification

```text
HHS_PASS_163_CONTRACT_BOUND
HHS_PASS_163_LOW_LEVEL_VIRTUAL_MEMRISTOR_RAM_CACHE_IMPLEMENTED
HHS_PASS_163_LOW_LEVEL_VIRTUAL_MEMRISTOR_RAM_CACHE_VALIDATED
```

The following classifications are intentionally not claimed in this change:

```text
HHS_PASS_163_LOW_LEVEL_VIRTUAL_MEMRISTOR_RAM_CACHE_CROSS_ARCHITECTURE_VERIFIED
HHS_PASS_163_LOW_LEVEL_ABI_BASE64_VIRTUAL_MEMRISTOR_RAM_CACHE_VERIFIED
```

They remain gated on independent cross-architecture replay, GPU adapter equivalence, durable crash-interruption testing, and full repository CI.
