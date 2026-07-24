# VM81 Native Development Foundation

This module implements the first evidence-backed stages of the VM81 native-development and Hash216 elastic-vector contract without modifying the frozen VM81 or Hash216 runtime sources.

## Implemented surfaces

- deterministic architecture discovery over the inherited VM81 C runtime;
- complete binding of the 29 inherited Pass 079 direct ABI functions;
- complete binding of the eight linked Hash72/Hash216 public functions;
- a typed VM81 execution wrapper with checked integer arithmetic and typed rejection outcomes;
- byte-for-byte VM81 state preservation after rejected typed operations;
- canonical Hash216 logical addresses derived from:
  - domain;
  - role;
  - position `0..215`;
  - VM81 lane `0..80`;
  - phase `0..71`;
  - version;
  - generation;
  - content commitment;
- immutable bounded vector descriptors;
- order-independent sealed resolver candidate snapshots;
- bounded `VRESOLVE` and `VREAD` operations;
- stale-version, stale-generation, noncanonical-address, bounds, capacity, overflow, and content-tamper rejection.

## Authority boundary

The resolver constructor produces an integrity-sealed **candidate snapshot**. It does not perform authoritative VM81 publication.

The following remain separate unresolved gates:

- VM81-authorized resolver publication;
- single-use VM81 mutation capability;
- vector write, append, resize, and release operations;
- atomic frame-bundle publication;
- complete instruction encoding, program-counter, and branch semantics.

Hash216 supplies logical identity, integrity, and addressing. VM81 remains the execution and state-transition authority. Hash72 remains the receipt and witness surface. Host physical pointers and allocation addresses are excluded from logical identity and resolver-root commitments.

## Canonical resolver behavior

Resolver initialization follows:

```text
build complete candidate
→ validate every seed and descriptor
→ sort by canonical logical address
→ reject duplicates
→ commit resolver root
→ seal candidate snapshot
```

A failure leaves the output resolver zeroed. No partially initialized candidate is exposed.

Every read performs:

```text
validate resolver root
→ validate canonical address
→ resolve exact descriptor
→ re-hash stored bytes
→ validate offset and length
→ validate output capacity
→ copy requested bytes
```

## Reproducible validation

From this directory:

```bash
make verify-native
```

From an environment with the repository Python test dependencies:

```bash
make verify-python
make evidence
```

The complete local validation surface is:

```bash
make verify
```

Generated evidence is written under:

```text
reports/vm81_native_development/
```

The current implementation intentionally withholds all terminal Level 0 and Level 1 classifications.
