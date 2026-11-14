# Administrator Resumable SQL Staging v1 — additive native integration record

## Scope

This change adds an **untrusted, administrator-private SQL intake library**, not a replacement for Pass 194, Hash216, or VM81. It permits arbitrary byte lengths and formats through incremental `append(upload_id, authenticated_owner, offset, bytes)` calls, writes exact source bytes to a private spool, and persists SQL offset/state metadata. Once finalized, source files become content-addressed blobs with SHA-256 identity. Hash216 admission is always **false** at this layer.

The caller, **not** a payload field, must supply a host-verified administrator identity. This library is not directly HTTP-exposed. The HTTP host must implement authentication, session scope, CSRF/origin requirements, chunk admission, and bounded concurrency without introducing a whole-file size or modality cap.

## Native composition

`existing nginx :443 -> Lane 5 gateway :8715 -> private authenticated upload entry -> SQL stage -> Pass 174/194 and Lane 5 BIOS/C coprocessor hydration -> signed environmental VM81 admission -> Hash216`

The repository's current `hhs_backend/lane5_ingress_gateway.py` uses `body = await request.body()` and materializes the full HTTP envelope before mediation. Therefore this new SQL staging library is **not yet end-to-end arbitrary-size production transport**. Before deploying the HTTP interface, add an independently validated, memory-bounded ingress streaming composition that preserves byte-exact Lane 5 candidate mediation across all chunks and their verified full-source manifest. Do **not** circumvent the gateway with a direct public staging endpoint. The current `hhs_backend/api/pass194_storage_training_routes.py` retains an inherited 16 MiB JSON/base64 endpoint; do not silently rewrite its frozen historical contract. Add an explicit streaming successor and maintain old compatibility until governed migration.

## Recovery and lifecycle

- SQLite WAL and FULL sync persist committed offsets.
- After a crash between spool fsync and SQL commit, the next append truncates uncommitted tails before resuming.
- Duplicate committed chunks are replay-idempotent only when their exact bytes match.
- Finalization streams through SHA-256 verification and creates a content-addressed source file.
- Novel and unknown formats remain staged. They are never marked as canonical Hash216 knowledge merely because source SHA-256 exists.
- Private SQL source metadata is not authorization, native tokenization, or a signed VM81 receipt.
- This is **single-process** serialized staging. A production multi-worker implementation must introduce a verified shared file lock, lease, and object-store consistency/retention policy; it must not assume threading locks coordinate multiple processes.

## Validation to complete

1. Run focused PR CI tests and review main-branch source-integrity checks.
2. Independently validate limits of OS filesystem, nginx, upstream timeouts and backpressure without converting physical limits to arbitrary input eligibility policy.
3. Integrate a trusted private admin host identity, CSRF/origin checks and Lane 5 streaming admission (not bypass).
4. Connect the existing Pass 174/194 native hydration and signed VM81/PQC admission, using authentic receipts.
5. Prove exact source upload -> SQL recovery -> native hydration -> Hash216 graph and RAG readback on the DigitalOcean exact-main deployment.

No stage in this PR claims production admission, native egress, or deployed reachability.

## Existing native Lane 5 continuation (additive)

`hhs_backend/runtime/hhs_admin_sql_lane5_continuation_v1.py` composes the existing Pass 219 1.48 unbounded workload bridge with finalized private SQL source files. It uses `Lane5WorkloadEnvelope.from_file(..., chunk_bytes=648)` and submits the resulting exact byte-count/digest/provenance envelope to `Pass219Lane5UnboundedWorkloadBridge.optimize`. This preserves the existing candidate-only semantics and verifies the bridge receipt before exposing a noncanonical candidate outcome.

The 648-byte read granularity is 81 × 64 bits, not a maximum object or upload size. Hash216 canonical ingestion still requires independent signed environmental VM81 authorization and Pass 174/194 authoritative persistence. This continuation does **not** call that canonical admission or claim a full hydration/RAG result.

The existing HTTP gateway full-body buffering remains an unresolved transport integration defect; never route uploads around the existing Lane 5 membrane to bypass it.


## Gateway exact-byte streaming integration

The PR now contains an additive repair to `hhs_backend/lane5_ingress_gateway.py`: HTTP bodies are spooled through `request.stream()` into a private temporary file, then hashed incrementally in **648-byte native reads** by `Lane5WorkloadEnvelope.from_chunks()`. The exact original request framing is reproduced using the request metadata prefix and the source byte length; the existing Pass219 1.48 native candidate optimizer is invoked before any HTTP bytes are forwarded upstream. A denied native candidate aborts forwarding. After acceptance, `httpx` streams the original staged bytes to the existing private upstream. The temporary spool is not the persistent administrator SQL staging database.

The regression test compares the new streaming envelope hash and byte count against the historical `serialize_environmental_ingress(...,payload=...)` representation for empty, short, cross-frame, and larger binary bodies.

This is an HTTP ingress **memory-buffering repair**, not the completed administrator uploader. The existing Pass194 JSON/base64 API still imposes its own 16 MiB limit, and no signed VM81/Hash216 promotion or RAG readback is claimed. Production must also verify reverse-proxy buffering, timeout and filesystem behavior, and multi-worker resource pressure.
