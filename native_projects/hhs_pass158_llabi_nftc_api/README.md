# HHS Pass 158 Low-Level Integration API

Contract: `HHS-P158-LLABI-NFTC-API` version `1.0.0`.

This directory implements the additive Pass 158 public integration layer over the inherited Pass 157 runtime.

Implemented surfaces:

- versioned C11 ABI with opaque handles;
- canonical NFT definition and instance identities;
- exact typed bindings and validation;
- scoped capabilities;
- public VM81 opcode descriptors;
- atomic execute, commit, abort, hold, and replay;
- Hash216 identities and Hash72 receipts;
- automatic Hash216 GUI state-delta indexing and frame-budget scheduling;
- lossless authoritative projection queues with transient-event coalescing;
- VM81-admitted GUI projection packages bound to replay-verified Hash72 receipts;
- projection and Delta offset normalization;
- canonical serialization and composition;
- C++, Rust, Python, Java/Kotlin JNI, and JavaScript/WASM bindings;
- versioned local service API;
- positive, negative, replay, binding, service, scheduler, security, and inheritance validation.

The successful terminal classification is:

`HHS_PASS_158_LOW_LEVEL_ABI_NFT_CONSTRAINT_INTEGRATION_API_VERIFIED`
