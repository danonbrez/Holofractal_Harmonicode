# DigitalOcean Runtime OS Latency/Abort Repair — Start Checkpoint — 2026-09-18

## Restart identity
- Base / merge target: `main @ 63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- Branch: `repair/digitalocean-runtime-os-latency-abort-20260918`
- Production droplet: `hhs-production-01` id `598826630`
- Region: `nyc3`
- Public IPv4: `165.227.220.193`
- Size: 2 vCPU / 4 GB / 120 GB Intel
- Droplet state observed: active

## User-observed production failure
Mobile Runtime OS shell renders, but repeated production control requests fail with:

`signal is aborted without reason`

Observed interface state:
- Runtime: check
- Vector store: check
- acquisition service: not loaded
- persistent vector store: not loaded
- browser diagnostics around p95 ~41.7 s

## Initial repository diagnosis
- `ProductionMobileControlCenter.refresh()` polls `/health` at 8 s and `/api/v1/pass174/status` at 12 s using `AbortController`.
- `OpenSourceAcquisitionPanel.refresh()` polls acquisition status/history at 15 s.
- Browser abort exceptions are rendered directly, producing the opaque user-visible message.
- `hhs_backend.server.health()` is heavyweight: every request queries runtime state, exports graph summary, emulator status, websocket status, and live workflow status.
- The production droplet is active; this is not a powered-off-host failure.

## Repair scope
1. Introduce a constant-time production liveness/readiness status path and keep expensive diagnostics separate.
2. Make mobile control refresh independent/partial so one slow subsystem cannot abort the whole surface.
3. Convert browser aborts to explicit timeout classifications with endpoint identity.
4. Cache or bound status computation that does not need per-request recomputation.
5. Add mobile/server latency contract tests.
6. Extend DigitalOcean deployment verification to probe control endpoints with latency budgets.
7. Deploy only after dependency-scoped validation; preserve exact-main guarded promotion and pinned SSH trust.

## Validation remaining
- inspect production app composition and current Pass174 status implementation;
- implement;
- run focused tests/workflows;
- merge;
- verify exact-main deployment and public probes.

## Next action
Inspect `production_visual_server.py`, `runtime_os_application_server.py`, `pass174_runtime_routes.py`, and status/storage code; implement the smallest repair that removes request coupling without weakening authority boundaries.
