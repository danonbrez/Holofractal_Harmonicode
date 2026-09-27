# Pass 220 — External Frontend Ingress/Egress Lossless Nonblocking Benchmark

**Schema:** `HHS_PASS_220_EXTERNAL_FRONTEND_INGRESS_EGRESS_LOSSLESS_NONBLOCKING_V1`  
**Status:** additive validation/benchmark contract  
**Parent delivery:** Pass 220 global Lane 5 Pass219/220 tool hydration  
**Selector rule:** Lane 5 route selection remains unchanged.

## 1. Objective

The deployment-facing Runtime OS SHALL prove that externally supplied frontend
bytes can traverse the real browser/API/runtime computation path and return in
egress evidence without byte loss, source/projection substitution, silent
frontend fabrication, or avoidable request-path blocking.

The tested path is:

```text
browser File / Uint8Array
-> exact base64 transport
-> POST /api/v1/pass174/sdlc/run
-> Pass 165 source-preserving multimodal ingress
-> exact 5,184-bit / 648-byte projection
-> workspace ingress
-> interpreter/compiler/VM81 where applicable
-> Pass 174 VM81 continuation
-> Hash72 receipt / Hash216 indexed vector object
-> HTTP response
-> inherited lifecycle egress manifest
-> exact source_b64 recovery
-> browser-side re-ingress
```

Browser preview, JSON transport, vector retrieval, and egress presentation do
not become canonical mutation authority.

## 2. Exact information-preservation gate

For every admitted benchmark fixture:

```text
SHA256(frontend input bytes)
==
source_identity_sha256
==
inherited lifecycle source_sha256
==
SHA256(Base64Decode(egress.manifest.source_b64))
```

and:

```text
Base64Decode(egress.manifest.source_b64)
== frontend input bytes
```

The VM projection MUST remain distinct from source bytes and MUST satisfy:

```text
snapshot_bits  = 5184
snapshot_bytes = 648
len(Base64Decode(projection_b64)) = 648
original_source_preserved = true
projection_replaces_source = false
```

The Pass 174 continuation MUST expose a validated vector object whose ordered
Hash216 representation is exactly three 72-character lanes / 216 characters.

Re-ingressing the exact egress source through browser fetch MUST reproduce the
same source SHA-256 and the same deterministic Pass 165 projection Hash72.

## 3. External fixture matrix

The real production frontend/API path SHALL exercise at minimum:

- UTF-8 HARMONICODE source with non-ASCII symbols and exact lexical bytes;
- JSON with escaped and Unicode content;
- PDF signature payload;
- PNG image bytes;
- RIFF/WAVE audio bytes;
- MP4/ISO-BMFF video signature bytes;
- arbitrary binary with NUL and non-UTF-8 octets;
- exact 648-byte raw5184-compatible binary;
- a larger deterministic binary stress object.

The fixture bytes themselves are test authority. No decoded preview, OCR,
renderer output, or semantic projection may substitute for byte identity.

## 4. Computation gate

For the HARMONICODE/source fixture, the public Pass 174 response MUST close:

```text
PLAN
GENERATE
INTERPRET
COMPILE
RUN
VALIDATE
RECEIPT
```

with a Pass 174 VM81 continuation receipt.

For non-text modalities, interpretation/compilation may remain
`NOT_APPLICABLE_OR_REJECTED` according to the existing lifecycle contract,
but ingress, exact projection, workspace registration, Pass 174 continuation,
receipt closure, vector persistence, and exact egress source recovery remain
mandatory.

## 5. Persisted-vector readback

Every completed browser ingress MUST expose the Pass 174 operation key.

The same visible frontend SHALL use:

```text
POST /api/v1/pass174/hash216/query
```

to retrieve the persisted vector record.

The query MUST report:

```text
classification = HHS_PASS_174_VECTOR_QUERY_HIT
mutation_authority = false
plaintext_exposed = false
```

and retain the exact 216-character ordered Hash216 object.

## 6. Nonblocking gate

The external pipeline is not allowed to turn a long ingress computation into a
frontend or server event-loop freeze.

During a deterministic large browser-originated ingress:

1. browser animation-frame heartbeat continues;
2. deployment-facing lightweight status requests complete while the ingress is
   still in flight;
3. the ingress itself completes within the bounded request deadline;
4. no relevant request is silently dropped;
5. multiple concurrent browser-originated ingress requests close without
   starvation;
6. vector/tool warming remains candidate-only and executes as a nonblocking
   post-start background task.

Timing measurements are observational, runner-dependent benchmark evidence.
They are not canonical arithmetic or route-selection authority.

## 7. Frontend admission bound

The public file ingress bound MUST equal the canonical Pass 165 source limit:

```text
16 MiB
```

A file larger than that bound MUST be rejected by the frontend before
`/api/v1/pass174/sdlc/run` is issued. This prevents avoidable transport,
allocation, and backend work for a request the canonical ingress must reject.

The Quick Build text-only path may retain a stricter local bound.

## 8. Negative cases

The suite SHALL also prove:

- declared-media spoofing is rejected rather than coerced;
- malformed ingress never produces a success egress;
- over-limit frontend files produce no SDLC network request;
- unknown API paths do not fall through to SPA HTML;
- vector retrieval has no mutation authority;
- frontend result fabrication remains false;
- no source bytes are replaced by the 5,184-bit projection.

## 9. Inherited native exactness

The benchmark gate MUST retain the existing native exact-boundary regressions:

- I149 raw5184 public frame ingress/egress hydration;
- I150 compatibility serialization;
- RNA frame export/import round trip;
- exact 648-byte x86_64 frame round trip.

## 10. Acceptance

Acceptance requires one evidence bundle proving:

```text
all modality fixtures lossless
AND exact 5184 projection on every fixture
AND Hash216 vector structure valid
AND persisted vector readback valid
AND browser egress -> browser re-ingress source identity stable
AND source-code computation stages closed
AND status probes serviced during in-flight ingress
AND browser heartbeat remains live
AND concurrent requests complete without starvation
AND oversize frontend request is blocked before POST
AND native 648-byte ingress/egress regressions pass
AND Runtime OS typecheck/build passes
AND production Chromium acceptance passes
AND Lane 5 selector files remain unchanged
```

No benchmark result may be used to grant vector memory, browser code, frontend
state, or benchmark timing canonical authority.
