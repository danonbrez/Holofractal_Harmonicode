# Pass 219 — Acquisition Job Service v1

## Status

Implementation contract for the persistent application-service boundary above the merged translation-invariant ingress, real-source calibration, and live acquisition/replay worker.

## Required result

The production Pass 174 application server SHALL expose a durable, mobile-accessible job surface for immutable GitHub/Hugging Face acquisition and replay without giving the HTTP/UI layer canonical runtime authority.

The service path is:

```text
mobile/API request
→ approved projector adapter id
→ immutable repository/source validation
→ persistent QUEUED/RUNNING record
→ Pass 219 live acquisition worker
→ exact source verification
→ optional sealed external projection evidence
→ translation-invariant candidate ingress
→ persistent result + replay bundle
→ job receipt
→ network-free archived replay
```

## Persistent state

The default service state root is nested beneath the Pass 174 runtime state root:

```text
.hhs/pass174/pass219_acquisition/
  jobs.sqlite3
  bundles/<job_id>.json
```

`HHS_PASS219_ACQUISITION_STATE_DIR` MAY override this location.

The SQLite ledger SHALL preserve:

- job id;
- creation/update time;
- lifecycle state;
- approved projector id;
- normalized request identity;
- result or failure record;
- job receipt Hash72.

Lifecycle states are:

```text
QUEUED → RUNNING → COMPLETED
                 ↘ FAILED
```

A failed acquisition SHALL remain inspectable. It SHALL NOT disappear from history.

## Approved projector adapters

v1 registers exactly:

### `SOURCE_ONLY_V1`

Acquires and verifies source bytes but supplies no semantic projection. The existing ingress therefore produces `HOLD_NO_SEMANTIC_PROJECTION`. This is a valid acquisition result, not an error.

### `EXTERNAL_EVIDENCE_V1`

Accepts externally produced projection evidence only when the request includes exact output bytes, vector-identity bytes, immutable model repository identity, source/pivot languages, modality, exact rational similarity, labels, and translation chain.

The service seals those bytes through the existing Pass 219 worker before ingress.

An unknown adapter id MUST fail before job creation.

## Source requirements

Every live acquisition request MUST supply:

- provider (`GITHUB` or `HUGGING_FACE`);
- repository id;
- immutable 40-hex revision;
- production-allowlisted license;
- repository kind and HTTPS source URL;
- artifact path;
- expected SHA-256;
- exact expected byte length;
- declared media type when known;
- source language when known.

The application service SHALL NOT accept `main`, `latest`, branch names, moving tags, or an arbitrary unbound fetch URL in place of an immutable revision.

## Replay bundle

A successful job persists a bounded local replay bundle containing:

- validated source specification;
- exact source bytes encoded as base64;
- exact external projection evidence bytes when present;
- the expected replay-closure Hash72.

Replay MUST invoke `LiveAcquisitionReplayWorker.replay_archived()` and MUST NOT perform network acquisition or external model execution.

A modified source or projection bundle cannot replay to the same expected closure.

## HTTP surface

The authoritative server exposes:

```text
GET  /api/v1/pass174/acquisition/status
GET  /api/v1/pass174/acquisition/projectors
POST /api/v1/pass174/acquisition/jobs
GET  /api/v1/pass174/acquisition/jobs
GET  /api/v1/pass174/acquisition/jobs/{job_id}
GET  /api/v1/pass174/acquisition/jobs/{job_id}/receipt
POST /api/v1/pass174/acquisition/jobs/{job_id}/replay
```

These routes MUST be registered before the inherited unknown-API fallback and static-root mount.

## Mobile control surface

`ProductionMobileControlCenter` mounts `OpenSourceAcquisitionPanel` as a first-class production control surface.

The v1 mobile form supports `SOURCE_ONLY_V1` because it can be operated without pasting arbitrary external model payloads into a small-screen form. The API simultaneously exposes `EXTERNAL_EVIDENCE_V1` for model-backed workers and future dedicated projector UI.

The panel provides:

- service/adapter status;
- immutable provider/repository/revision fields;
- exact SHA-256 and byte-length fields;
- source media/language fields;
- submit/refresh controls;
- persistent job history;
- job detail and receipt inspection;
- one-click network-free replay for completed jobs.

## Authority boundary

This service is application control plane state, not canonical execution state.

It MUST NOT:

- mint truth;
- mint action authority;
- mutate VM81;
- mint canonical Hash72;
- mint canonical 216-symbol Hash216;
- commit canonical learning;
- authorize permanent pruning;
- treat a service job id or SQLite row as canonical state identity.

All acquisition and projection results remain candidate-only. Lane 5 / VM81 admission remains a distinct later boundary.

## Validation

Dependency-scoped validation SHALL include:

1. Python compilation of the service, router, and tests;
2. persistent source-only job + offline replay;
3. external-evidence sealing + service restart + replay;
4. failed digest persistence;
5. rejection of unknown projector ids before job creation;
6. route inventory checks;
7. production server route registration before fallback;
8. TypeScript typecheck and Vite build for the mobile control surface;
9. source checks for acquisition endpoints and replay controls.

External hosting availability is not part of deterministic CI. Real HTTPS acquisition remains an operator/runtime workload through the already validated bounded transport.
