# Integration Report — Pass 008

Pass 008 extends the sealed-runtime rule into the semantic-memory and vector-cache layers.

The key correction is that semantic memory is now treated as a propagation layer, not an authority layer. Before this pass, the semantic memory engine could generate fallback hashes using SHA-256 hex truncation. That produced a 64-character digest, not a canonical 72-symbol Hash72 state. Pass 008 replaces that fallback with native Hash72 normalization and commits semantic writes, vector derivations, links, searches, and vector-cache persistence to the unified receipt chain.

## Runtime effect

```text
semantic text / replay frame / attractor / query
    ↓
canonical semantic projection
    ↓
72-symbol Hash72 normalization
    ↓
semantic guard receipt
    ↓
embedding/vector derivation receipt
    ↓
validated cache/storage compatibility surface
    ↓
unified Hash72 ledger
```

## Why this matters

This closes a major shadow-propagation risk: semantic memory and embeddings can no longer act as unreceipted state. They are now downstream cached projections of receipt-chain authority.
