# Pass 219 Lane 5 Nine-Loop Large-Artifact Attestation 1.69

Pass 219 1.69 extends the 1.68 source-attested sample path to the published large representation artifacts without materializing the full weight-18 symbol.

The bounded target set is:

- both 424 x 5,431 quintuple-coordinate matrices, one for each 31-bit prime;
- the compressed 107,053-row septuple-versus-quintuple comparison record; and
- the direct-bootstrap MHV9 septuple archive.

The verifier hashes each file as a byte stream and requires membership in the upstream checksum manifest. NPZ containers are opened with `allow_pickle=False`; archive code is never executed. Each prime-lane container must independently expose the published 424 x 5,431 logical matrix geometry. Literal NPZ inventory identity is not required. The observed per-prime inventories and structure fingerprints are recorded first; only then may a separate logical-equivalence contract be frozen.

The 107,053-row comparison is streamed through gzip. The verifier records field-count and token-class fingerprints, a normalized SHA-256, endpoint row hashes, and rejects explicit mismatch markers. It never expands the comparison into a giant in-memory graph.

The septuple ZIP is checked by CRC and member metadata only. It is not extracted. Member path traversal is rejected.

1.69 exports parallel learning metadata for source identity, byte size, container structure, matrix shape, prime lane, sparse/dense representation, comparison schema, archive-member structure, representation agreement, parent Hash216 binding, and the canonical authority boundary.

No 1.69 artifact receives canonical VM81 mutation, Hash72, Hash216 lineage, persistence, or floating-point authority.

The first public-artifact run at commit `86b2a21c91534ddd38f5d25df3cb226d9b6d14c7` demonstrated that literal container equality is false for the published pair. That execution is retained as schema-discovery evidence only and is not validation of later 1.69 heads.

Discovery receipts are checkout-bound: every live receipt must carry the exact Git commit SHA and workflow-run identity that produced the observed inventories. A receipt from an earlier head may inform schema repair but cannot validate a later checkpoint.
