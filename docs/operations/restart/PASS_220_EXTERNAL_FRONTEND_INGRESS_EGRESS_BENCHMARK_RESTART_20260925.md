# Pass 220 External Frontend Ingress/Egress Benchmark — Restart Record

Date: 2026-09-25

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `156d4138f2640c6fd8937f96ffb5c030ae9b7952`
- branch: `pass220-lane5-global-tool-hydration-1-0`
- pull request: `#588`
- merge target: `main`
- current task: full external frontend ingress -> computation -> egress lossless/nonblocking validation
- Lane 5 selector replacement: forbidden / unchanged

## Implemented in this cycle

Added:

```text
contracts/pass220/PASS_220_EXTERNAL_FRONTEND_INGRESS_EGRESS_LOSSLESS_NONBLOCKING_V1.md
hhs_verification/pass220/external_frontend_ingress_egress_benchmark_v1.py
tests/pass220/test_hhs_pass220_external_frontend_ingress_egress_v1.py
.github/workflows/pass220-external-frontend-ingress-egress-benchmark.yml
docs/operations/restart/PASS_220_EXTERNAL_FRONTEND_INGRESS_EGRESS_BENCHMARK_RESTART_20260925.md
```

Modified:

```text
hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx
hhs_backend/runtime_os_pass220_lane5_tool_hydration.py
```

## Repairs made before benchmarking

### Frontend admission limit

The deployment-facing file-ingress UI previously admitted files up to 24 MiB
while canonical Pass 165 rejects sources above 16 MiB.

The frontend bound is now exactly:

```text
16 * 1024 * 1024 bytes
```

so an impossible 16–24 MiB request is rejected before base64 transport and
backend computation.

### Lane 5 warm hydration startup

The Pass 219/220 warm-tool deployment lifecycle previously awaited full
repository/vector hydration before application lifespan yielded.

It is now a post-start `asyncio.create_task(asyncio.to_thread(...))` warm job.

While warming:

```text
state = WARMING_NONBLOCKING
available_to_lane5 = false
candidate_only = true
lane5_selection_changed = false
```

The public frontend therefore starts without waiting for warm candidate-memory
population. Tool availability remains fail-closed until the warm graph seals.

## Benchmark matrix

The real deployment-facing entrypoint:

`hhs_backend.production_visual_server:app`

is exercised in headless Chromium through the actual public Runtime OS file
ingress control.

Fixtures:

```text
HARMONICODE source
JSON
PDF
PNG
RIFF/WAVE
MP4/ISO-BMFF signature
arbitrary binary
exact 648-byte raw5184 carrier
256 KiB deterministic binary stress object
```

For each fixture the runner requires:

```text
input SHA-256
== Pass174 source identity
== Pass165 source hash
== lifecycle egress source hash
== SHA256(decoded egress source_b64)

decoded egress source_b64 == original frontend bytes
snapshot == 5184 bits / 648 bytes
Hash216 vector object == 72 + 72 + 72 characters
vector readback == HHS_PASS_174_VECTOR_QUERY_HIT
mutation_authority == false
plaintext_exposed == false
```

The exact backend egress source is then re-ingressed from browser fetch and must
reproduce the same source identity and deterministic Pass 165 projection
Hash72.

The HARMONICODE fixture additionally requires all computation stages:

```text
PLAN -> GENERATE -> INTERPRET -> COMPILE -> RUN -> VALIDATE -> RECEIPT
```

to close as `COMPLETED`.

## Nonblocking benchmark

A one-MiB browser-originated binary ingress runs while:

- browser `requestAnimationFrame` heartbeat is sampled;
- `/api/interface/status` is repeatedly requested from outside the browser;
- at least one status probe must complete while the ingress is still in flight;
- status probes have a five-second hard timeout;
- browser maximum sampled frame gap must remain below 1500 ms.

A separate browser `Promise.all` batch submits three exact concurrent binary
ingress requests. Every request must close and preserve its own exact source
identity.

An oversized 16 MiB + 1 byte synthetic browser File is injected into the real
frontend control. The benchmark requires zero `/api/v1/pass174/sdlc/run`
requests from that attempt.

Negative transport checks require media-type spoofing to return 422 and unknown
API paths to return structured JSON 404 rather than SPA HTML.

## Full impacted validation suite

The dedicated workflow performs:

1. base/selector immutability check;
2. exact compiled C runtime build;
3. I149 raw5184 native ingress/egress C test;
4. RNA native frame round-trip C test;
5. exact ctypes 648-byte VM81 and x86_64 round trips;
6. I150 Python compatibility/hydration tests;
7. Pass 165 multimodal regressions;
8. Pass 174 lifecycle route reachability;
9. Pass 220 external frontend contract tests;
10. Pass 220 global Lane 5 warm-tool tests;
11. Pass 220 I042 multimodal shared-root tests;
12. Pass 220 I028 G3 registry tests;
13. Runtime OS TypeScript typecheck;
14. Runtime OS production build;
15. live GUI source verification;
16. real Chromium external lossless/nonblocking benchmark;
17. prior Pass 185 Phase-4 production multimodal Chromium suite;
18. production-root/public-app/mobile-control regressions;
19. repository-identifiable evidence seal and artifact upload.

## Validation state

Implementation is committed and restartable. The dedicated GitHub Actions run
must provide the measured benchmark evidence. If it fails, repair only the
demonstrated dependency-scoped failure and rerun the focused gate.

Do not reinterpret a benchmark failure as a change to HHS equations or Lane 5
selection semantics.

## Next action

Inspect the dedicated workflow on PR #588. Repair-forward any exact failure.
After focused green, merge PR #588, verify exact main, and run the post-merge
workflow so the merged PR itself is hydrated into the authoritative Pass
219/220 warm-history tool graph.
