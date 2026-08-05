# Pass 211 — BigInt HFC Carrier and Multi-Register Framing

Pass 211 composes two already verified exact layers:

- Pass 133: positive BigInt → canonical TLV → SECDED half → palindromic carrier.
- Pass 210: one 5,184-cell Boolean register → exact two-witness holographic frame.

The bridge packs each 648-byte carrier shard into one register using MSB-first bit order. It preserves the original carrier byte stream exactly and records the final shard's exact bit length. Each shard carries retained Hash72, Hash216, phase, frame, 36 snapshot, and HFC receipt anchors. One package root and one ordered Hash72 receipt bind the complete shard sequence.

## Integrity order

1. Validate package structure and ordered shard roots.
2. Rebuild each Boolean register from its retained packed payload.
3. Verify HFC identities, frame receipts, and all 36 snapshot witnesses.
4. Recover any declared single missing snapshot.
5. Reassemble the exact Pass 133 carrier bytes.
6. Validate the palindrome, center, TLV, digest, and SECDED layer.
7. Reconstruct the original positive BigInt and verify source identity.

## Agreement boundary

Fresh projections generated from one uniformly corrupted source can agree with each other. They prove contemporaneous consistency, not historical integrity. Pass 211 therefore compares fresh reads against independently retained anchors minted at package creation. The API returns both the fresh self-agreement result and the anchored disagreement cells.

## Size reporting

The runtime keeps these quantities separate:

- source BigInt byte length;
- Pass 133 carrier byte length and expansion ratio;
- canonical HFC storage: 5,184 bytes per shard;
- native packed capacity: 648 bytes per shard;
- packed-capacity occupancy;
- multi-register requirement.

Strict compression is not claimed for ordinary carrier shards. It is reported only when Pass 210 admits the individual register under its declared affine-Fibonacci domain witness.

## Public API

`/api/runtime/bigint-hfc-carrier`

- `GET /status`
- `POST /encode`
- `POST /decode`
- `POST /recover`
- `POST /anchored-compare`

The Pass 201 public API federation automatically discovers the router before the visual static mount.

## Validation

```bash
bash scripts/run_pass211_bigint_hfc_validation.sh
```

The gate runs the inherited Pass 133 suite, inherited Pass 210 suite, Pass 211 runtime and API suites, and deterministic evidence equality.
