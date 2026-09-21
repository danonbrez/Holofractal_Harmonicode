# Pass 219 Acquisition Job Service v1 — Restart Checkpoint — 2026-09-16

## Base and branch

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base `main`: `c64f38dd0f99864fd042890afeb6f6d55ad0be16`
- Branch: `pass219/acquisition-job-service-v1`
- Pull request: `#482`
- Validated implementation head: `cf08caf34d4854ccde0f5e2b2e470d4866b7dfcc`
- Latest pre-checkpoint operational head: `e1a4234e674b19de9d90cf04f38eebc5e5a9d172`
- Merge target: `main`

## Implemented

This cycle closes the first production application-service control plane above the merged Pass 219 live acquisition/replay worker.

### Persistent application jobs

`hhs_backend/pass219_acquisition_job_service.py` adds:

- SQLite job persistence under the Pass 174 state root;
- lifecycle `QUEUED → RUNNING → COMPLETED/FAILED`;
- durable failed-job inspection;
- bounded job history;
- job receipt Hash72;
- exact replay bundles containing verified source bytes and projection-evidence bytes;
- network-free archived replay with expected replay-closure verification;
- restart-safe job lookup and replay.

### Approved adapters

v1 permits exactly:

- `SOURCE_ONLY_V1`: verified immutable source acquisition with no semantic projection, producing an inherited semantic HOLD rather than fabricated meaning;
- `EXTERNAL_EVIDENCE_V1`: exact caller-supplied external projection evidence, sealed through the already validated Pass 219 acquisition worker before ingress.

Unknown projector IDs fail before job creation.

### HTTP application surface

`hhs_backend/api/pass219_acquisition_routes.py` adds:

```text
GET  /api/v1/pass174/acquisition/status
GET  /api/v1/pass174/acquisition/projectors
POST /api/v1/pass174/acquisition/jobs
GET  /api/v1/pass174/acquisition/jobs
GET  /api/v1/pass174/acquisition/jobs/{job_id}
GET  /api/v1/pass174/acquisition/jobs/{job_id}/receipt
POST /api/v1/pass174/acquisition/jobs/{job_id}/replay
```

`hhs_backend/pass174_server.py` registers this router before the inherited unknown-API fallback and static-root mount and includes the route in readiness checks.

### Mobile production control

`hhs_gui/runtime_os/workspace/OpenSourceAcquisitionPanel.tsx` adds a first-class production mobile panel with:

- GitHub/Hugging Face provider choice;
- immutable repository revision;
- expected SHA-256 and exact byte length;
- media type, source language, license and source URL;
- acquisition submission;
- persistent job history;
- job/receipt inspection;
- one-click offline replay.

`ProductionMobileControlCenter.tsx` mounts this panel while preserving the existing local-file → Pass 174 SDLC → persistent Hash216 vector-store workflow.

### Deployment gate inheritance

`.github/workflows/digitalocean-mobile-control-ingress.yml` now directly watches `OpenSourceAcquisitionPanel.tsx` and the Pass 219 UI source-verification script, and checks the built bundle for:

- `/api/v1/pass174/acquisition/jobs`;
- `Acquire + verify`;
- `Replay offline`.

This prevents future changes to the child acquisition panel from bypassing the DigitalOcean mobile control gate merely because the parent component did not also change.

## Authority boundary

The service and UI remain control-plane/candidate surfaces only.

They do not mint truth, action authority, canonical learning commits, VM81 mutations, canonical Hash72 receipts, or canonical 216-symbol Hash216 state. SQLite job IDs and replay bundles are not canonical runtime identities. Downstream Lane 5 / I29-equivalent / VM81 admission remains distinct.

## Validation completed

Dedicated workflow:

- Workflow: `Pass 219 Acquisition Job Service v1`
- Successful run: `35165737978`
- Exact validated head: `cf08caf34d4854ccde0f5e2b2e470d4866b7dfcc`
- Conclusion: `success`

Successful steps:

1. checkout;
2. Python setup;
3. Node setup;
4. Python dependency installation;
5. Python compilation of service, routes, production server, and tests;
6. persistent acquisition/replay tests;
7. production source/route-order verification;
8. Runtime OS dependency installation;
9. strict TypeScript typecheck;
10. Vite production build.

The first dedicated run (`35165689140`) failed only in `actions/setup-node` because the workflow incorrectly requested npm caching for a nonexistent `hhs_gui/package-lock.json`; no substantive test ran. The workflow was repaired to avoid the nonexistent lockfile and the successor run passed completely.

Additional deployment evidence:

- `DigitalOcean Mobile Control and Vector Ingress` run `35165737865` completed `success` on the implementation head before the gate-inheritance amendment.
- The deployment workflow amendment triggers a successor DigitalOcean gate; under the repository forward-progress policy, a queued external gate does not invalidate already completed dependency-scoped implementation validation.

## Changed files

- `.github/workflows/pass219-acquisition-job-service-v1.yml`
- `.github/workflows/digitalocean-mobile-control-ingress.yml`
- `contracts/pass219/PASS_219_ACQUISITION_JOB_SERVICE_V1.md`
- `hhs_backend/api/pass219_acquisition_routes.py`
- `hhs_backend/pass174_server.py`
- `hhs_backend/pass219_acquisition_job_service.py`
- `hhs_gui/runtime_os/workspace/OpenSourceAcquisitionPanel.tsx`
- `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
- `hhs_gui/scripts/pass219-acquisition-job-ui-source-verify.mjs`
- `tests/pass219/test_hhs_pass219_acquisition_job_service_v1.py`
- this restart record.

## Remaining / next action

After merge and verified-main closure, the next Pass 219 boundary is a real approved projector execution adapter: execute a revision-pinned open-source multilingual/text-image model outside canonical authority, emit exact projection evidence into `EXTERNAL_EVIDENCE_V1`, then exercise a public DigitalOcean acquisition → job persistence → receipt → offline replay workload through the mobile/API surface.
