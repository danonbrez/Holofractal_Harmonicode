# Pass 219 — Lane 5 Persistent Hash216 Composition Memory 1.39

Status: **ADDITIVE / PASS174-PASS194-BOUND / AES-GCM / SQLITE-WAL-FULL / RESTART-REHYDRATABLE / CANDIDATE-ONLY**

Base authority: verified `main` at `ca11ce61861d05deed80e22b3019aec6e042eb69`, the merge of PR #450 / Lane 5 validated Hash216 composition-jump store 1.38.

## 1. Purpose

1.38 established exact registration, immutable Hash216 composition sealing, GPU/vector search, and direct candidate reuse while a process remains alive. 1.39 converts that validated jump topology into durable system memory.

A validated 1.38 jump SHALL be persistable into the inherited Pass 174/194 encrypted vector-store substrate and SHALL be recoverable after process restart without replaying every intermediate transition merely to reconstruct the known candidate destination.

Persistence remains a **data-memory authority only**. It SHALL NOT become a second VM81 transition authority, a Hash72/Hash216 minting authority, a canonical persistence authority, a PQC-key authority, or a receipt-clock authority.

## 2. Persistent object model

Each durable record binds:

```text
jump_id
parent_hash216
child_hash216
composition_hash216
metadata_hash216
vector_object_id
operation_key
operation_identity_sha256
hash216_index_root_sha256
jump_span
phase_slot
cycle_index
layer_index
ordered trace roots
1.38 native registration receipt signature
1.39 native persistence receipt signature
changed_bits
quarantine state
```

The ordered trace roots are the 1.38 sequence of:

```text
(delta_hash216, hydration_hash216, frontier_hash216, child_state_hash216)
```

The raw per-step transition program does not have to be replayed during candidate retrieval; its exact registration was already committed by the ordered Hash216 trace and immutable 1.38 composition seal.

## 3. Exact VM5184 snapshot frame

The child candidate state is persisted as the exact 5,184-bit fixed-width VM81 state:

```text
81 cells * 64 bits = 5,184 bits = 648 bytes
```

The persistent frame is exactly 81 unsigned 64-bit words in little-endian order. No floating-point representation is admitted.

The packed frame MUST round-trip exactly:

```text
VM81[81 x uint64] -> 648-byte LE frame -> VM81[81 x uint64]
```

and the recovered state MUST regenerate the stored native Pass 205 `child_hash216` exactly.

## 4. Pass 174/194 vector-store binding

1.39 SHALL use the inherited `PersistentEncryptedVectorStore` semantics:

```text
SQLite journal_mode = WAL
SQLite synchronous  = FULL
snapshot encryption = AES-GCM authenticated encryption
plaintext vector snapshot persisted = FALSE
```

The composition Hash216 itself is also admitted through the inherited Pass 194 positional indexing geometry:

```text
composition_hash216
  = Hash72_0 || Hash72_1 || Hash72_2
  -> Hash216Array.build(...)
  -> 216 positional SHA-256 indexes
  -> hash216_index_root_sha256
```

The indexed `combined` value MUST remain byte-for-byte equal to the 1.38 `composition_hash216`.

## 5. Metadata seal

Canonical persistent metadata is encoded without floats and sealed by the native Pass 205 Hash216 byte surface:

```text
metadata_hash216 = Pass205.Hash216(canonical_persistent_metadata)
```

The metadata seal binds the jump identity, parent/child/composition Hash216 values, span, 20,020-cycle phase slot, cycle index, recursive layer index, ordered trace roots, 1.38 registration receipt signature, changed-bit count, and candidate-only authority flags.

Changing any bound field MUST invalidate the persistent record.

## 6. Restart rehydration

At startup, 1.39 SHALL load the SQLite composition index and rebuild the exact parent-to-jump search index.

A persisted record whose metadata Hash216 or inherited 1.38 composition seal fails verification SHALL be quarantined and SHALL NOT participate in search or reuse.

For a valid record, direct reuse after restart SHALL perform:

```text
current native parent Hash216 == stored parent Hash216
metadata Hash216 seal valid
1.38 composition Hash216 seal valid
AES-GCM vector retrieval authenticates
vector object identity matches
vector operation identity matches
vector Hash216 combined == composition Hash216
vector Hash216 positional index root matches
parent/child Hash72 vector bindings match
648-byte child state decodes exactly
native Pass205 child state root == stored child Hash216
native 1.39 descriptor receipt closes
```

Only then may the recovered state be returned as a candidate.

## 7. Search topology

Persistent records are indexed first by exact native parent Hash216 and optionally by recursive `layer_index`. Their child Hash216 values are then ranked by the inherited 1.37 optimizer:

```text
current VM81
 -> parent Hash216
 -> persistent validated-jump subset
 -> three ordered Hash72 vector searches
 -> 20,020 phase address
 -> cycle fingerprint / consecutive-prime route
 -> ranked persistent composition candidates
```

The GPU/vector path remains candidate-only.

## 8. Native 1.39 membrane

The native authority contract SHALL report:

```text
Pass174 persistent encrypted vector store bound = TRUE
Pass194 Hash216 positional index bound          = TRUE
SQLite WAL required                             = TRUE
SQLite synchronous FULL required                = TRUE
AES-GCM authenticated snapshot encryption       = TRUE
restart rehydration supported                   = TRUE
metadata Hash216 seal required                  = TRUE
VM5184 little-endian word frame                 = TRUE
recursive layer index persisted                 = TRUE
GPU/vector search candidate-only                = TRUE
canonical VM81 mutation authority               = FALSE
canonical Hash72 authority                      = FALSE
canonical Hash216 authority                     = FALSE
canonical persistence authority                 = FALSE
floating-point canonical authority              = FALSE
signed environmental VM81 admission             = REQUIRED
```

## 9. Work-reuse interpretation

For a persisted jump of span `J`, successful restart reuse represents:

```text
represented_transitions = J
intermediate_transitions_executed_on_reuse = 0
```

This is exact state-graph work reuse after prior validation. It is not by itself a physical GPU latency measurement and does not establish nanosecond-class hardware timing.

## 10. Acceptance gates

1. Strict cumulative `make c-abi` build.
2. Export audit for 1.39 plus inherited 1.38/1.37/environmental-admission surfaces.
3. Strict native C positive/negative 1.39 descriptor test.
4. Real multi-step 1.38 registration using Pass 205.
5. 1.39 persistence into inherited `PersistentEncryptedVectorStore`.
6. SQLite metadata `WAL` + `synchronous=FULL` verification.
7. AES-GCM encrypted vector status reports `plaintext_persisted = FALSE`.
8. Close process-local objects, reopen from the same state root, recover the candidate, and prove exact child Hash216 equality.
9. Search after restart ranks an exact matching child Hash216 at distance zero through inherited 1.37/Pass207 routing.
10. Metadata tampering and persisted quarantine fail closed across restart.
11. Inherited 1.38, 1.37, Pass207, and Lane 5 1.34 authority tests remain green.
