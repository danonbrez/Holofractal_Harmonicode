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

## P0 exact source egress for human IDE and external agent tools

A dedicated owner-scoped `GET /api/runtime/admin-source-stream/uploads/{upload_id}/source` returns verified original bytes from the privately staged SQL object. Pass190 administrator scope verification is reused; unfinalized or other-owner upload IDs are rejected. The endpoint opens a no-follow read descriptor, checks byte count and SHA-256 against the SQL receipt, and streams the same descriptor in chunks, with no intermediate whole-file output buffer. The response declares `X-HHS-Canonical-Hash216-Admitted: false`, exact source digest, exact content length and `Cache-Control: no-store`. This is source egress, not a canonical RAG retrieval or VM81 mutation.

`readStagedSource(uploadId, WritableStream, options)` in the conventional frontend streams the response into a caller-supplied sink without building a complete source buffer. It enforces the explicit noncanonical metadata and received byte count. Human IDE and authorized agent tools can consume the same original bytes without introducing new native file-size or modality restrictions. Tests cover authorized and unauthorized original-byte readback, altered staged source rejection, binary streaming into a WritableStream, and false canonical-receipt rejection.

Do not claim client-side SHA-256 verification, disk-backed browser save support, or production RAG: the frontend validates server-provided receipt and length, while the backend performs byte digest verification. A separately authorized native Hash216 admission and source-to-VM81 typed constructor are still required before this content is indexed as canonical knowledge.

## Signed Pass190 HTTP-level e2e receipt (P0)

`tests/test_hhs_admin_source_signed_asgi_roundtrip_v1.py` exercises the actual FastAPI router with `httpx.ASGITransport` and an actual token issued and verified by the inherited `ApplicationVMControlPlane` Pass190 implementation. The only signing secret is ephemeral test fixture data; it is never an operational credential. The test performs create → offset-bound multi-chunk PATCH → status → finalize with independently computed SHA-256 → byte-identical streaming GET. It then denies wrong-owner, insufficient-scope, absent and tampered signed credentials. These are real in-process HTTP request/response checks, not a stubbed authorization verifier or complete production end-to-end acceptance. The native Lane 5 integration and environmental preflight remain separate required tests; this new case does not assert canonical VM81 or Hash216 admission.

## P0 read-only typed VM81 staging recognition

The inherited `hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe` already defines a lossless 81 × 64-bit VM81 frame with 7 BigInt limbs, 72 radix-72 glyphs and exact ordered directed-lane metadata. An additive owner-scoped `GET /api/runtime/admin-source-stream/uploads/{upload_id}/typed-vm81` checks whether a **pre-existing staged source** is exactly this 648-byte typed frame and can be decoded and reencoded without change. It requires finalized SQL source SHA-256, never interprets arbitrary file bytes as VM81 instructions, never restricts the general file ingress, and does not call the signed admission mutator.

The focused regression runs all 12 inherited pq/qp lane cases, checks their phase metadata, exact BigInt identity, immutable SHA-256 source matching, and ensures malformed/opaque sources remain available through ordinary staging. The record declares `authorized_parent_hash216_bound=false`, `uqcel_math_witness_bound=false`, `signed_vm81_admission_performed=false` and `canonical_hash216_admitted=false`.

This closes only the *recognition* side for already-typed frames. The authorized UQCEL numerical witness, parent Hash216 reference, signed environmental admission, and persistent knowledge proof remain OPEN. Never synthesize them from the SQL source hash, and never turn a conventional arbitrary uploaded file into a 648-byte maximum-size file restriction.

## Exact SQL-staged VM81 frame through inherited native signed fixture (P0)

The existing Pass219 signed environmental OpenSSL-3.5/ML-DSA native probe already tests twelve BigInt/phase-qudit VM81 frames and four negative native prerequisite cases. New `tests/test_hhs_admin_sql_signed_environmental_fixture_v1.py` composes that **existing test-only** signed probe with the owner-bound SQL source staging service. For every exact 648-byte typed view it stages source in 127-byte offsets, finalizes with independently computed SHA-256, inspects the inherited typed frame decoder, loads exactly the staged original bytes, invokes the existing signed environmental C probe, requires native/PQC/environmental receipt predicates, and compares committed bytes with the staged frame and its original BigInt and opcode. The test additionally requires SQL to remain noncanonically staged after native fixture execution; negative native cases must not commit.

This is not a production arbitrary-source admission adapter. The native test probe provisions its **own deterministic test-only root**, uses the repository's genesis parent, and builds a fixture UQCEL witness independently. No staging API may invoke that probe or transfer the test fixture's claimed canonical receipt into user knowledge. A production source-bound mathematical witness, authorized current parent Hash216 registry, protected key authority, and signed receipt persistence remain OPEN. The test is wired into the **existing** `Pass 219 Fold Primitive Probe` signed-environmental job using its established OpenSSL 3.5 prerequisite; it is not allowed to imply success while that job is queued or fails.

## Test-root handoff proof separation — exact SQL→signed fixture

The queued Pass219 signed-environmental test has been strengthened with a reusable **test-only** `verify_staged_signed_fixture` handoff in `hhs_backend/runtime/hhs_admin_sql_signed_environment_fixture_handoff_v1.py`. It accepts a finalized owner-scoped source ID, verifies the inherited typed VM81 decoding and SQL SHA-256 again, reads the original exact 648-byte frame, executes the already-existing signed native fixture, checks native signature/environment/parent/child evidence, and replays exact BigInt/phase metadata. This single function centralizes the staging→native boundary rather than letting a test call the probe on unverified arbitrary bytes.

The returned receipt deliberately uses `fixture_*` keys and declares `test_root_only=true`, `production_parent_hash216_authorized=false`, `production_uqcel_witness_bound=false`, `signed_vm81_admission_performed=false`, `canonical_hash216_admitted=false`, and `production_persistence_performed=false`. The function is not exposed as an HTTP endpoint. A regular focused CI regression denies opaque source, wrong owner and any negative-mode override without executing native fixture code. The existing expensive OpenSSL-3.5 signed job runs the positive 12-case native test and negative native proofs when scheduled. No fixture root or Genesis parent may be reclassified as current production authority.

## Pass219 signed fixture CI repair-forward — uploaded receipt versus UUID

On head `938b73e05cd9fc4f1ce39917e3afd7548b037bdf`, the Pass219 Fold Primitive Probe's fast `fold-primitive-probe` job passed, while the OpenSSL-3.5 signed job reached `Prove BigInt signed environmental commit and negative closure` and failed a new owner-isolation test at `stage.append(other_owner, ...)`. The test had used `AdminStreamStaging.create(...)`'s **dict receipt**, not its `["upload_id"]` string. `AdminStreamStaging._uuid()` correctly rejected it as `INVALID_UPLOAD_ID`. The native signed probe compilation and original signed-admission test completed before this test failure; do not label the full job passed.

Repair `52e7a1f6cba4d881b8ea83774f98e0477610f0bb` extracts the actual upload ID in that negative-case setup and changes no production admission, UQCEL, Hash216, signing or source-staging code. Full OpenSSL-3.5 signed and focused CI must rerun at the new head. The production authorized-parent / witness integration is unchanged and remains OPEN.

## Pass219 signed fixture negative case follow-up — November 18

The signed-environmental job for head `c6218eb58ce9948227749ff983820038cfd2a416` compiled and executed the inherited native signing probe and proceeded through the fixture's twelve positive staged-frame cases and corrected wrong-owner test before encountering a second test setup defect: `opaque_id = stage.create(...)` was still a receipt dict. The opaque-source negative path then failed at `stage.append(opaque_id, ...)` with expected input-type rejection `INVALID_UPLOAD_ID`, not at signed admission. Commit `52a36d757be9e9e61a2c8c88c24f08bd3d0e7b3a` extracts `["upload_id"]` for that test too. All three `stage.create()` assignments in the fixture now extract the UUID. No production key, admission predicate, mathematical module, ABI, Hash216, or staging code changed. Exact-head signed-environmental CI rerun remains required.

## P0 native UQCEL witness prevalidation after green signed fixture

Exact head `3a10b81d12f9dbaf5bf0485121cd314d88710813` completed the Pass219 Fold Primitive Probe including the OpenSSL3.5 signed environmental job, Admin SQL Staging, Pass161 Finalization, Lane5 Native Capability Provider, Source Text Integrity, and frozen-layer source guard successfully.

The next additive read-only implementation is `hhs_backend/runtime/hhs_admin_sql_uqcel_witness_prevalidation_v1.py`. Given a finalized owner-bound source recognized by the inherited 81-word typed VM81 decoder and explicitly supplied exact integer values for `P,p,q,delta,A,B,cell81,left_basis8,right_basis8`, plus a 72-symbol prior Hash72 string, it calls **the existing C ABI** `HHSUQCELRuntimeBridge.validate`. This is native mathematical validation, not a Python replacement and not a signed-admission mutation. Integers are validated without floats, booleans or inferred digest-based values; original source streaming remains unrestricted.

The response records the native status/decision and whether the inherited validator reports a matched source descriptor. Crucially `source_to_witness_provenance_bound=false`, `authorized_parent_hash216_bound=false`, `signed_vm81_admission_performed=false` and `canonical_hash216_admitted=false` even if mathematical validation succeeds. A UQCEL source descriptor is not proof that a particular uploaded frame is authorized; current parent Hash216 lineage, authorized binding, production key, signed environmental commit, and canonical receipt persistence are still required.

The focused workflow now executes the actual native shared-library validator and rejects malformed/float/negative/range-invalid declarations and other-owner sources. Exact-head results remain required before treating this increment as verified.

## November 19 signed-handoff contract compatibility repair

Head `5a2790ed576879a1007803bed5bab9b3d1fda9c9` passed Pass219 signed-environmental, Pass161, source-integrity, frozen-layer and native Lane5 workflows. The focused Admin SQL workflow failed **before** the newly added UQCEL test: `tests/test_hhs_admin_signed_vm81_handoff_contract_v1.py` requires the original pending-gate label `Hash72 Hash216 canonical receipts and replay`, whereas a prior contract edit replaced that exact string with `canonical Hash72 Hash216 receipts and replay`. Commit `d0710a3d5f43f5af875bd90dbcef4690eac764f6` restores the required label and retains all newly differentiated source-provenance, authorized-parent and production-admission gates.

The existing UQCEL ctypes bridge sets `source_hash` by default to `HHS_EXACT_UQCEL_SOURCE_SHA256`, the inherited **UQCEL source-envelope descriptor**, which is not the SHA-256 of an administrator-uploaded file. The prevalidation's `source_hash_match` checks that inherited descriptor only; it must not be interpreted as upload-to-witness provenance, and the response must keep `source_to_witness_provenance_bound=false`. The authorized source-bound constructor is still an OPEN requirement. This repair does not alter the single signed environmental native mutator.

## P0 replayable exact source/UQCEL candidate association

All six required focused checks **passed** for previous exact head `fc3a49c1f4359a4c79b671de8d16773098a2ed12`, including native UQCEL prevalidation and OpenSSL3.5 signed environmental fixture.

New module `hhs_backend/runtime/hhs_admin_sql_uqcel_source_association_v1.py` composes the existing owner-scoped SQL staging, inherited exact 81-word typed VM81 decoder and native UQCEL mathematical validator. After successful native UQCEL validation, it reopens the staged original frame, recomputes exact SHA-256 from its 648 source bytes, then creates a deterministic domain-separated candidate association digest over **upload ID + source SHA-256 + explicitly supplied exact integer witness**. `replay_candidate_source_witness_association` re-verifies the owner, unchanged source, native mathematical decision, complete receipt shape and association digest. It rejects altered metadata, mismatched witness, foreign owner, source-content drift and forged admission-state flags. This module does not add an upload size limit: the 648-byte check applies exclusively to an already-typed VM81 frame.

This association is an ordinary SHA-256 candidate **identity**, not a signature or authorization. Neither an untrusted administrator choosing a witness nor recomputing the same digest establishes a source-to-witness **authorized provenance**. Its fields remain `source_to_witness_authorized_provenance=false`, `authorized_parent_hash216_bound=false`, `signed_vm81_admission_performed=false`, `canonical_hash216_admitted=false`, `canonical_persistence_performed=false`. The next production step must bind the association through the inherited authorized parent Hash216 and production 1.32 signed environmental membrane. No test key or Genesis fixture parent is usable as that authority. Exact-head CI for this new association is pending.

## Pass 220 source/UQCEL candidate replay regression repair (November 20)

At head `59db457d36287a85c9b2fcfc4681f47403a09423`, five of six relevant workflows were green: Pass219 Fold Primitive Probe (including signed environmental fixture), Pass161, Lane5 Native Capability, Source Text Integrity, and frozen-layer source guard. Focused Admin SQL failed in `test_source_tamper_and_native_reject`. The staged-source tamper check **correctly** raised `TYPED_VM81_STAGED_SOURCE_DRIFT`, but the subsequent separately intended native validator-rejection case reused the deliberately corrupted file and failed at the earlier source-integrity boundary. Commit `9272b4ddde7459d9d43c3a9a866d486e293a6e53` restores the inherited original 648-byte VM81 source after the drift assertion, before invoking the separate mocked native reject. This changes only test setup; no admission rules, digest handling or authority boundaries are weakened. CI must pass at the corrected head before freezing this regression as verified.
