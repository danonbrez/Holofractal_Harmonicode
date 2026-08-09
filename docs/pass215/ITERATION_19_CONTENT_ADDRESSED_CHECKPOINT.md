# Pass 215 Iteration 19 — Content-Addressed Checkpoint Compaction

Iteration 19 preserves the exact bounded generation state frozen by Iteration 18 while changing only its durable storage representation.

## Frozen parent

- closure head: `d89919b1010df0dda46e18cb43b4a6ef913a5615`
- closure tree: `2a74f697278e754b44998df4d5a3598750643a4a`
- Iteration 18 checkpoint: `475300933` canonical bytes
- Iteration 18 checkpoint Hash216: `bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f`
- Iteration 18 generation-control Hash216: `309a4e102b6f78338a63c086f536f4d3d62429c77709fa4f9fa9b25d3a6ac509`
- Iteration 18 suite Hash216: `bccf558e206bc996d4647533cf310838e1f13cec1322f98c5f22ab5c1ad190d1`

## Representation

The large Iteration 18 checkpoint components are separated from the small control fields. Repeated strings of at least 16 UTF-8 bytes occurring at least twice are interned into one sorted string table. The resulting packed structure is serialized deterministically, divided into 1 MiB chunks, and compressed with zlib level 9.

Each chunk is addressed by SHA-256 of its uncompressed bytes. Compressed bytes have an independent SHA-256. The ordered chunk manifest and blob metadata receive a Hash216 content-store root, and the entire compact checkpoint receives a separate Hash216 root.

This is storage/transport compression only. It is not numerical authority and performs no floating-point canonical operation.

## Restore sequence

1. Verify compact checkpoint Hash216.
2. Verify content-store Hash216.
3. Verify compressed-blob SHA-256.
4. Decompress each referenced chunk.
5. Verify each uncompressed chunk against its content address.
6. Reassemble and verify the packed payload SHA-256.
7. Reverse string interning.
8. Reconstruct every removed Iteration 18 checkpoint component.
9. Recompute the original Iteration 18 checkpoint Hash216 and require exact equality with `bff3f18e...`.
10. Invoke the validated Iteration 18 `TerminalHeadSymbolicDAG` restore.
11. Continue generation with zero prompt forward replay and zero generated-token forward replay.

## Acceptance barrier

The compact checkpoint must be at least 2:1 smaller by canonical-byte count than the frozen 475,300,933-byte parent representation. It must still reproduce the same seven certified true-greedy token decisions, Iteration 18 generation-control root, Iteration 18 suite root, final symbolic DAG root, final interval root, and terminal token receipt.

The iteration does not authorize sampling, unbounded generation, arbitrary sequence length, floating-point authority, dense-forward replacement, runtime mutation, canonical mutation, or migration.
