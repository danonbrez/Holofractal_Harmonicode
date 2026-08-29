# Pass 219 I141 / Pass 185 Phase 2 — degradation and negative acceptance

## Scope

Phase 2 closes the next bounded block of the historical Pass 185 production-browser contract without claiming terminal Pass 185 completion.

Validated Phase-1 nucleus:

- code head: `31a3ca0f725ac7ee14a7c2252da750536afe13ec`
- tree: `c8232474b9d15fcf847f77d4a79ba54c0aaf8eb7`
- run: `33249040294`
- job: `99091407019`
- artifact: `9713782418`
- artifact SHA-256: `21fc874daa36a94a6129de42ebc53d58f51a54f50ff8a1953d4d5055de969927`

## Phase-2 profiles

### 1. Optional provider degradation

The exact current production entrypoint is cold-booted with:

- Gemma/LiteRT-LM pointed at an unreachable loopback endpoint;
- Pass 166 Word2Vec required by the native language provider;
- Pass 166 storage pointed at an empty governed directory;
- bounded assistant-health timeout;
- C autobuild disabled;
- automatic cognition ticks disabled.

Required result:

- Runtime OS root reaches the canonical mounted IDE;
- product health reports degraded assistant authority rather than blocking boot;
- the visible Application lifecycle remains usable;
- local calculator creation, preview, test, and ZIP export remain available;
- no browser runtime authority is created.

### 2. Compiled C runtime unavailable

The CI gate temporarily removes the built `hhs_runtime/builds/libhhs_runtime.so` after first validating the inherited native build, then launches the exact production entrypoint with C autobuild disabled.

Required result:

- production web service still binds;
- the Runtime OS remains interactive;
- the source editor/application lifecycle remains available;
- local preview/test and ZIP export remain available;
- absence of the compiled C library is not mislabeled as a browser or hosting failure.

### 3. Process/socket and static/module negative acceptance

The gate executes:

- occupied production port;
- production child exit before binding caused by a missing Runtime OS asset root;
- recovery boot on a free port;
- built Runtime OS root and asset MIME inventory;
- unknown asset 404;
- unknown API JSON 404 without SPA fallback;
- required JavaScript bundle blocked;
- required JavaScript bundle returned with incorrect MIME;
- visible finite boot-failure projection;
- visible reload and interface-status recovery controls;
- reload recovery after the negative case is removed;
- corrupted Pass 185 local-storage state followed by successful Runtime OS recovery.

## Repository changes

- `hhs_gui/index.html`
  - extends the existing canonical 12-second boot watchdog with visible `Reload workspace` and `Interface status` recovery controls.
  - does not add a second bootstrap authority.
- `hhs_verification/pass185/phase2_degradation_negative_acceptance.py`
  - launches only `hhs_backend.runtime_os_application_server:app`;
  - captures profile-specific server logs and JSON evidence;
  - performs real Chromium interaction for degraded source-only profiles;
  - performs real browser module-block and wrong-MIME recovery scenarios.

## Current Phase-2 classification

`HHS_PASS_185_PHASE2_DEGRADATION_NEGATIVE_ACCEPTANCE_VERIFIED`

This is not the terminal Pass 185 classification.

The following remain mandatory after a green Phase 2:

- broader browser lifecycle matrix including offline/WebSocket/reconnect/concurrent context cases;
- multimodal workflows for document, game, graphics/image, audio, and audiovisual/video;
- performance/starvation CPU/memory/I/O/latency gates;
- remaining process/recovery and negative scenarios not covered in this phase;
- cumulative inherited Pass 185 closure receipt;
- authoritative-main verification;
- exact verified-main external deployment replay.

## Authority boundary

Phase 2 creates no new VM81 authority, Hash72 commit stream, persistence authority, C++ mutation authority, browser mutation authority, or canonical floating-point path.

Optional-provider and C-runtime degradation are availability classifications only. They do not transfer canonical authority to the browser.


## Final Phase-2 validation

Phase 2 is terminal green at:

- validated head: `2b972a66743a505937d5f819c839f5e59dda98b4`
- validated tree: `e67889f885481e0ddfd14c33a61b035af82e0bcc`
- run: `33254220079`
- job: `99105019179`
- artifact: `9715347753`
- artifact SHA-256: `c7f4ba101f0182169c1156df582e664d8befd17188d7ecd2724eee437aca2773`
- repository receipt: `evidence/pass185/i141/PASS_185_I141_PHASE2_VALIDATION_RECEIPT.json`

All Phase-2 behavioral profiles passed in the same run:

1. process/socket + static/module negative acceptance;
2. optional Gemma/Word2Vec degradation with the local application lifecycle preserved;
3. compiled-C-unavailable source-only production boot with calculator preview/test/ZIP preserved;
4. impacted inherited Pass-174 and Runtime-OS production-root regressions.

The final C-unavailable architecture is intentionally bounded at the outer production entrypoint. The cumulative application remains preserved in `runtime_os_application_server_full.py`, while `runtime_os_application_server.py` selects `runtime_os_source_only_server.py` only when C degradation is explicitly requested and the compiled library is absent. Canonical C/Hash72/VM81 modules were restored to their pre-Phase-2 blobs.

Phase 2 still does **not** claim terminal Pass 185 completion.
