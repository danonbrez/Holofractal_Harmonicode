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

## P0 browser-to-SQL staging adapter (incremental)

The existing visual IDE project-lifecycle controls now include an explicit `Stage Source (Admin)` action, in addition to normal project/folder import and source editing. This action calls `stageBrowserFile` from `applications/holofractal_harmonizer/src/admin-source-stream.mjs`. It uses `File.slice()` to send binary chunks without reading the whole selected file into JavaScript memory and preserves the exact `source_name` and an immutable staging source digest returned by the existing SQL service.

The backend API `hhs_backend/api/hhs_admin_source_stream_routes_v1.py` composes the existing SQL stage methods `create`, `append`, `status`, and `finalize` with a byte-streamed PATCH request. **Important: authorization is fail-closed.** The route only accepts an already-verified, in-process `request.scope["hhs_authenticated_principal"] = {"subject": "...", "admin_source_upload": True}` supplied by separately authenticated trusted host middleware. It does **not** trust caller-supplied owner headers/JSON or grant privilege because a request passed Lane 5 candidate mediation. There is currently no verified production middleware integration establishing this specific scope object. Consequently the new controls will report an authorization rejection until such a verified authority adapter is connected. Do not invent one or relax the default denial.

This feature is **staging only**: no canonical VM81/Hash72/Hash216 admission or RAG promotion occurs, no source is silently represented as a locally editable complete copy, and existing editing/build/ingress buttons remain available. A completed source staging status or SHA-256 digest is not a canonical knowledge receipt.

Focused Python and Node tests cover spoofed identity rejection, verified owner scope, exact byte reconstruction, offset conflicts, browser slice transport, and denial/no-byte-upload behavior. End-to-end production checks must establish actual authenticated host middleware, route federation, Nginx/Lane5 hop identity and signed admission, then browser replay after service deployment.

## Reuse Pass190 signed administrator credentials

The inherited production Ubuntu Application VM control plane exposes `ApplicationVMControlPlane.authenticate_header()`, which verifies the canonical Pass190 signed `Authorization: HHS-Capability <token>` authorization format, token signature, issue/expiry time, and principal/scopes. The administrator source streaming adapter now delegates to this existing verifier and additionally requires the exact `admin.source.upload` scope. A signed credential with only general VM or read scopes cannot stage source; missing credentials and unauthenticated HTTP owner claims are rejected. The capability is **not** a replacement for VM81 admission and must be issued through the existing authorized, local Pass190 token issuer. Do not expose a token-issuing endpoint in the browser or accept user-authored unsigned scopes.

The existing visual IDE stage-source button requests this specific existing capability for the user-initiated operation. The token is used for same-origin request headers only, not serialized in the project, URL or audit response. Future integration with the established authenticated browser session may replace the temporary credential prompt, but must retain equivalent server-verified signed authorization and scope.

The Pass201 public API federation discovers the additive `hhs_backend.api.hhs_admin_source_stream_routes_v1` router alongside existing routers. A discovery presence check is not production execution evidence. Confirm the route is present and protected in the production registration report, that auth succeeds with a valid locally issued scoped token and fails without it, and that the source bytes complete a staged round trip through Lane5 before moving to signed canonical admission.

No source has been promoted to canonical Hash216 knowledge by this adapter.

## P0 signed-capability → SQL source → native candidate continuation

The private additive FastAPI router now exposes `POST /api/runtime/admin-source-stream/uploads/{upload_id}/candidate`, an authenticated, owner-scoped continuation of a finalized SQL-staged source. It uses the existing `continue_staged_to_lane5` composition, which reads exact bytes through the Pass219 unbounded bridge and requires the candidate-only authority envelope. Only sources finalized under the verified upload owner may be considered. The source SHA-256 is checked against SQL-staged metadata; no alternative integrity or native capability is introduced.

The conventional visual IDE `Stage + Lane 5 (Admin)` action first stages through `File.slice()`, then explicitly requests the native candidate receipt. A candidate failure is displayed separately and does not erase already-staged exact source bytes or pretend admission succeeded. The browser client requires `candidate_only=true`, `canonical_hash216_admitted=false`, and `signed_vm81_admission_required=true`, rejecting any response advertising authoritative promotion.

This continues the existing authenticated ingress path but **does not perform signed VM81 admission or Hash216 knowledge promotion**. Native source egress, canonical receipt/replay, and RAG require an inherited approved admission workflow; never fabricate such a receipt from SQL digests or candidate optimization. A separate Pass161 native C link error (OpenSSL EVP functions unresolved in the Pass160 executable) was also observed in the broad PR workflow and must be repaired in its existing native build ownership boundary without weakening this checkpoint.

## Actual native-library acceptance and typed canonical handoff

The native-path regression now builds the existing C ABI using `make c-abi` and calls the real `Pass219Lane5UnboundedWorkloadBridge` after durable SQL source staging. This is separate from the earlier mock-only unit tests. It requires exact original bytes for an unknown binary modality, correct source SHA-256, retained SQL ownership, successful native candidate receipt, and explicit `candidate_only=true`, `canonical_hash216_admitted=false`, and `requires_signed_environmental_vm81_admission=true`. The C-ABI test must pass in GitHub Actions before this is counted as actual native verification.

The authoritative 1.32 environmental admission symbol is defined in `hhs_runtime/include/hhs_pass219_vm81_environmental_recovery_1_32.h`: `hhs_exact_pass219_vm81_environment_admit_signed`. It requires fully typed `HHSExactUQCELInputV1`, `HHSExactVM81Frame`, `HHSExactPass219Hash216TransitionViewV1`, Lo Shu/G243/feedback fields, and emits committed frame, RNA admission, PQC firewall, PQC signature, and environmental receipts. A Lane5 route candidate, source digest, or SQL staging receipt cannot be silently cast to these types or counted as signed authority. The machine-readable contract `contracts/pass220/HHS_ADMIN_SQL_LANE5_SIGNED_VM81_HANDOFF_V1.json` records exact inputs/outputs, proof obligations, and OPEN integration states. The next implementation is to recover an existing authorized typed source constructor and admission service before any mutation.

## Read-only, typed admission prerequisite inspection

A new owner-scoped endpoint `GET /api/runtime/admin-source-stream/uploads/{upload_id}/admission-preflight` calls `hhs_backend.runtime.hhs_admin_sql_vm81_admission_preflight_v1.inspect_staged_admission_prerequisites`. It requires an existing Pass190 administrator source upload capability and a finalized owner-bound SQL source. It queries the **actual compiled** runtime for the 1.32 environmental version and state, firewall halt flag, and ML-DSA-65/SLH-DSA-SHA2-192S availability, while confirming that the signed environmental entrypoint is exported. The endpoint does not call the admission function and cannot mint a signed receipt.

The returned record always marks `typed_source_constructor_bound=false`, `authorized_parent_hash216_bound=false`, `signed_vm81_admission_performed=false`, and `canonical_hash216_admitted=false`. It does not convert SQL SHA-256 or Lane 5 route metadata to UQCEL tensors, a 648-byte VM81 frame, or a parent Hash216 reference. The positive/negative native preflight tests run after `make c-abi` with autocompilation disabled; missing native symbols fail closed.

Existing `hhs_python/runtime/hhs_uqcel_ctypes_bridge.py` provides a typed UQCEL input builder and a historical `admit_vm81` compatibility facade, but the inherited I163 probe explicitly establishes that the historical composed mutator is hidden and the unsigned/compatibility path must fail closed (status 5). The existing C `tests/pass219/test_pass219_bigint_environment_admission_native_probe.c` demonstrates a separately provisioned exact typed source and canonical environmental admission with a test root key; this probe is **not** a general-purpose conversion from arbitrary SQL source. Reuse existing authorized constructors, full parent lineage, and production key authority when implementing the next handoff; do not copy fixture root keys into runtime.

## Pass161 native link repair without upstream source drift (November 16 checkpoint)

The broad PR workflow revealed a repeatable Pass160 materialized executable-link failure: the preserved shared Hash216 implementation calls `EVP_sha256` and `EVP_Digest`, but the additive Pass160 materialization Makefile did not link OpenSSL libcrypto on the generated CLI/static executable paths. The **repair-forward Makefile only**, at `native_projects/hhs_pass160_validated_transition_runtime/assets/source_capsule/Makefile.materialized.repair-forward`, now uses `CRYPTO_LIBS ?= -lcrypto` for shared-library, CLI, native verification, performance and sanitizer link commands. The transport archive, frozen source text, checksum manifest and full native source capsule remain unchanged. An executable upstream `make all` Pass161 workflow and source-integrity/frozen-layer checks must verify the change; source-level tests cannot substitute for this native build receipt.

Signed environmental admission remains independent: the existing UQCEL ctypes builder supports explicitly typed arithmetic/witness values but must not be populated by arbitrary SQL byte-hash guesses, and the native environmental admission requires an authorized ordered parent Hash216 transition. The existing real-native staging, candidate and read-only preflight suite is successful at the preceding head; these do not establish actual signed admission.

## Pass160 materialization correction — checksum-preserving repair

The earlier attempt to modify `assets/source_capsule/Makefile.materialized.repair-forward` directly was rejected correctly by Pass161's `verify-reference-source` gate. That original file has been restored **byte-for-byte**. The executable-link repair is now implemented only in the generated `Makefile.materialized`, after `sha256sum -c` and native source archive verification complete. A guarded `apply_crypto_link_overlay.py` verifies the expected original recipe structure, adds `-lcrypto` to all five generated link commands, is idempotent, and rejects missing or partially modified source layouts. The root materialization Makefile invokes this overlay after copying the already-verified input into generated output. No upstream immutable transport hashes were altered.

This is a correction of the implementation approach, not evidence that the Pass161 workflow is green; require x86_64 and aarch64 exact-head native CI success before completing this repair.
