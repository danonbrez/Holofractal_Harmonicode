# HHS PASS 185 — PRODUCTION COLD-BOOT BROWSER ACCEPTANCE AND INHERITED VERIFICATION CLOSURE

## Exact Production-Root Boot, Finite Runtime Startup, Browser Module-Graph Closure, Mobile/Desktop Interaction Proof, Native C and Optional Model Degradation, Full Application Workflow Acceptance, Inherited Contract Accountability, Deterministic Evidence, and Non-Waivable Completion Gates

# 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P185-PCBAVC-IVC-VM81-H72-H216` |
| Pass number | `185` |
| Canonical pass name | `PRODUCTION_COLD_BOOT_BROWSER_ACCEPTANCE_AND_INHERITED_VERIFICATION_CLOSURE` |
| Short name | `P185 Production Browser Closure` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative baseline | Authoritative `main` after Pass 184 closure. Pass 185 implementation must not be based on an unmerged Pass 184 branch. |
| Merge target | `main` |
| Completion classification | `HHS_PASS_185_PRODUCTION_BROWSER_AND_RUNTIME_CLOSURE_VERIFIED` |

# 2. Purpose

Pass 185 repairs and permanently closes the inherited verification failure exposed by a real production deployment of the full HHS Application IDE.

The deployment proved that prior pass contracts, module tests, route tests, health checks, and browser harnesses could all report success while the actual public application remained partially rendered, never completed browser startup, and exposed buttons that did not work.

This pass therefore establishes the following binding rule:

```text
A PASS THAT DELIVERS A USER-FACING APPLICATION IS NOT COMPLETE
UNTIL THE EXACT PRODUCTION ROOT HAS COLD-BOOTED IN A REAL BROWSER,
BECOME INTERACTIVE, COMPLETED ITS REQUIRED USER WORKFLOW,
AND CLOSED ALL SERVER, CLIENT, RUNTIME, AND RECOVERY EVIDENCE.
```

Unit tests, isolated module imports, static HTML rendering, route existence, API health, parser-only checks, mock browser tests, and decorative controls are supporting evidence only. None can substitute for the required full production-root acceptance.

# 3. Inherited authority

Pass 185 inherits all compatible requirements from Passes 001–184. No prior verified capability may be removed, bypassed, hidden, or weakened to make this pass succeed.

The following inherited principles remain mandatory:

1. The Visual IDE is the principal product surface and a primary contractual deliverable.
2. The interface must support real application creation, editing, preview, execution, testing, export, recovery, and multimodal workflows.
3. Static shells, disconnected buttons, placeholder projections, raw API viewers, decorative panels, and detached command submitters are not completion.
4. Runtime authority remains in the inherited singleton VM81, Hash72, Hash216, constraint membrane, and exact canonical execution path.
5. All long-running work must be finite, cancellable, timed, restartable, and recoverable from repository-visible state.
6. Completion requires dependency-scoped validation, commit, merge or ready PR, verification on authoritative `main`, and a user-facing completion report.
7. Optional providers may degrade capability, but must never prevent the base IDE from loading and becoming interactive.

# 4. Production incident evidence carried forward

Pass 185 must preserve the July 31, 2026 deployment evidence as a regression nucleus.

## 4.1 Server-side evidence

A production Ubuntu service launched:

```text
uvicorn hhs_backend.application_ide_server:app
```

The process initially consumed one full logical CPU and failed to bind or answer port 8080. Stack capture showed synchronous kernel tick and Hash72 ledger work on the Uvicorn main thread through:

```text
hash72_digest
append_filesystem_ledger_entry
commit_receipt
authorized_tick
tick_kernel
emit_tick_event
tick_once
_run_loop
```

After bounded deployment patches, the server bound to `127.0.0.1:8080`, `/api/health` returned HTTP 200 in milliseconds, and static JavaScript assets returned correct MIME types.

## 4.2 Browser-side evidence

The full public root still failed to complete `DOMContentLoaded` and remained non-interactive.

Observed browser isolation results included:

```text
NO_JAVASCRIPT: DOM_READY
BLOCK_ALL_MJS: DOM_READY
BLOCK_VISUAL_IDE: DOM_READY
BLOCK_NOTHING: TIMEOUT
```

Every direct Visual IDE dependency imported successfully in isolation after DOM readiness, and every dependency also completed when loaded as an individual parser module. The unresolved failure occurred only in the composed production-root boot graph.

This evidence proves that isolated module success does not establish integrated browser boot closure.

## 4.3 Accountability classification

This incident is classified as:

```text
INHERITED_PASS_VERIFICATION_FAILURE
PRODUCTION_BOOT_GRAPH_NOT_PROVEN
APPLICATION_INTERACTIVITY_NOT_PROVEN
HOSTING_PROVIDER_NOT_CAUSAL
```

DigitalOcean, Nginx, C compilation, Gemma, Word2Vec, and external model availability must not be used to excuse a browser boot failure when the base HTML, API, and static assets are reachable.

# 5. Mandatory implementation scope

## 5.1 Repository-native correction

All final fixes must exist in the repository and be reproducible from a clean clone.

Temporary server edits, manual `sed` patches, ad hoc environment changes, local-only files, browser cache workarounds, and uncommitted deployment modifications are diagnostic evidence only and cannot satisfy Pass 185.

The implementation must identify and repair the exact integrated boot dependency causing the production-root stall. The fix must not simply remove `visual-ide.mjs`, disable the IDE, suppress errors, shorten a timeout, or mark a partial shell ready.

## 5.2 Finite server startup

The production service must:

- bind its configured socket within a bounded deadline;
- expose separate liveness, readiness, authority, and optional-provider status;
- never perform unbounded or repeated canonical hashing on the main ASGI event loop;
- move CPU-heavy canonical work to an explicit bounded worker or governed job;
- allow automatic kernel ticks to be disabled by deployment profile;
- preserve explicit API- and GUI-authorized runtime ticks;
- publish startup phase, elapsed time, current operation, timeout, and failure reason;
- terminate or degrade cleanly instead of remaining active without a listener;
- avoid continuous idle disk writes and receipt generation when no governed work is requested.

## 5.3 Browser boot graph

The public application must have one explicit boot coordinator with a finite state machine.

Required states:

```text
DOCUMENT_RECEIVED
STATIC_ASSETS_LOADING
CORE_MODULES_READY
DOM_READY
WORKSPACE_BOUND
EDITOR_READY
PREVIEW_READY
INTERACTIVE
DEGRADED_INTERACTIVE
FAILED
```

Requirements:

- no circular dependency between module evaluation and DOM readiness;
- no parser-loaded module may await an event whose dispatch depends on completion of that same module graph;
- every boot promise must have a deadline and failure projection;
- optional services must initialize after the editable workspace is interactive;
- errors must be visible in the page with retry, reload, diagnostics, and recovery actions;
- the UI must never remain indefinitely in a generic loading or processing state;
- duplicate static and dynamic imports must be idempotent;
- all event bindings must be installed once and remain functional after recovery and reload;
- mobile pane selection must expose a visible editor by default.

## 5.4 Native C runtime

The production package must compile and verify the inherited C runtime before claiming full runtime readiness.

Required commands must be repository-owned and deterministic. A failed C build must produce a clear degraded or failed runtime state without preventing the base source editor and export functions from loading.

C compilation is required for final Pass 185 completion but is not a prerequisite for basic HTML/JavaScript interactivity.

## 5.5 Gemma and assistant provider

The base IDE must cold-boot and remain usable when Gemma/LiteRT-LM is:

- disabled;
- absent;
- downloading;
- configured to an unreachable external endpoint;
- present but missing the requested model;
- present but unable to use GPU/Vulkan;
- slow to answer;
- returning an error.

Assistant status must be explicit and actionable. Optional-provider initialization must not block `DOMContentLoaded`, workspace readiness, file editing, preview, testing, or ZIP export.

A local 12B model must not be required on a low-memory CPU-only production host. External provider mode and assistant-degraded mode remain valid deployment profiles.

## 5.6 Word2Vec

Pass 166 Word2Vec installation and activation remain governed, separate capabilities.

The IDE must remain interactive when Word2Vec is absent, inactive, quarantined, corrupt, or awaiting license acceptance. Word2Vec readiness may enable language-vector functions but cannot own the browser boot barrier.

# 6. Non-waivable acceptance matrix

Every scenario below must be executed against the exact production application composition, not a substitute static server or reduced test app.

## 6.1 Process and socket scenarios

1. Clean process start with empty runtime caches.
2. Warm restart with valid persisted runtime state.
3. Restart with incomplete prior ledger tail.
4. Configured port free.
5. Configured port occupied.
6. Child process exits before binding.
7. TCP listener opens but HTTP health is not ready.
8. Required startup phase exceeds its deadline.
9. SIGTERM during startup.
10. Recovery restart after startup failure.

For successful startup, liveness and lightweight HTTP health must answer within the declared deadline. The service must not consume a full CPU core continuously while idle.

## 6.2 Static asset and module scenarios

1. Every required `.mjs`, `.js`, `.css`, font declaration, image, worker, and source map route returns the intended status and MIME type.
2. Cold cache with no service worker cache.
3. Warm cache.
4. Cache-busting query parameters.
5. One top-level module blocked at a time.
6. All JavaScript blocked.
7. One direct Visual IDE dependency blocked at a time.
8. Wrong MIME type.
9. HTTP 404.
10. HTTP 500.
11. Delayed asset response.
12. Truncated module response.
13. Duplicate module inclusion.
14. Dynamic import rejection.
15. Root static mount and explicit `/src` mount ordering.

Negative cases must reach a finite, visible, recoverable failure state. They must not hang indefinitely.

## 6.3 Browser lifecycle scenarios

The following must run in Chromium at minimum, with desktop and mobile viewports:

- initial navigation;
- hard reload;
- normal reload;
- back/forward navigation;
- restored tab;
- second concurrent tab;
- private/incognito context;
- JavaScript disabled;
- offline transition after shell load;
- slow network;
- temporary API unavailability;
- WebSocket unavailable;
- WebSocket reconnect;
- local storage unavailable;
- corrupted recoverable browser state;
- empty browser state.

Required assertions:

```text
HTTP root success
DOMContentLoaded bounded
load event bounded or explicitly non-blocking
boot state reaches INTERACTIVE or DEGRADED_INTERACTIVE
editor visible
mobile dock functional
no uncaught pageerror
no unresolved required boot promise
no permanent loading overlay
no required request left indefinitely pending
```

## 6.4 Required end-to-end application workflow

The minimum acceptance workflow remains:

```text
Create Calculator
→ Edit HTML
→ Save
→ Preview
→ Calculate 7 + 8
→ Assert 15
→ Run Test
→ Export ZIP
→ Validate ZIP contents
→ Reload
→ Reopen project
→ Confirm persisted source and runnable preview
```

The workflow must use real pointer/touch and keyboard events against visible controls. Direct JavaScript function calls, synthetic state mutation, hidden API shortcuts, or DOM injection cannot substitute for user interaction.

The test must also verify:

- New File;
- upload ingress;
- Explorer selection;
- editor typing;
- Save;
- Build;
- Run;
- Preview ready/error bridge;
- Test;
- Export;
- terminal open/close;
- mobile pane switching;
- assistant panel opening in degraded and ready states;
- actionable error and retry behavior;
- cancellation of a running lifecycle job;
- recovery after cancellation or failure.

## 6.5 Multimodal inherited scenarios

At least one real workflow must be completed for each inherited application modality:

- text/document;
- calculator or general application;
- 2D game;
- image/graphics;
- audio;
- video or audiovisual reel.

Each workflow must produce a user-visible result and a real exported artifact or source package. Placeholder cards and static demonstrations do not count.

## 6.6 Optional-provider scenarios

The complete matrix must run with:

1. C runtime verified, Gemma disabled, Word2Vec absent.
2. C runtime verified, external assistant unavailable, Word2Vec inactive.
3. C runtime verified, external assistant ready, Word2Vec active.
4. C runtime build failure, source-only degraded IDE.
5. Assistant timeout during an already interactive session.
6. Word2Vec activation failure during an already interactive session.

The base editor and source ZIP export must remain available in every degraded scenario unless a specific action genuinely requires the missing provider.

# 7. Browser test architecture

## 7.1 Required real-browser runner

Pass 185 must add a repository-owned Playwright acceptance runner that:

- launches the exact production server command generated by Pass 184;
- waits separately for socket, liveness, readiness, and browser interactivity;
- uses a clean temporary HOME, runtime directory, cache, and browser profile;
- captures console messages, `pageerror`, request failures, response status, WebSocket events, and boot-state transitions;
- records screenshots at every boot phase and workflow milestone;
- retains Playwright traces and network evidence;
- tests mobile touch and desktop pointer input;
- kills all child processes within a bounded cleanup phase;
- fails on leaked jobs, listeners, browsers, or temporary servers.

## 7.2 Prohibited substitutions

The following cannot satisfy the production acceptance gate:

- importing modules after `DOMContentLoaded` in an artificial page;
- loading one module per page without the complete production graph;
- checking only that a module returns HTTP 200;
- checking only Python route tests;
- checking only static HTML selectors;
- checking only API health;
- checking only that buttons exist;
- invoking internal functions instead of clicking controls;
- running against a different server entry point;
- accepting a screenshot without interaction proof;
- manually declaring the interface usable.

These tests remain useful diagnostics but are not completion evidence.

# 8. Performance and starvation gates

The test harness must sample process CPU, memory, disk I/O, event-loop responsiveness, and HTTP latency during startup, idle, workflow execution, and recovery.

Minimum gates:

- the listener must bind within the declared startup deadline;
- lightweight health p95 must remain below 250 ms while idle on the reference 2-vCPU host;
- the ASGI main loop must not execute synchronous canonical hashing or ledger traversal for longer than 100 ms without yielding;
- an idle server must not sustain one full logical CPU for more than 10 seconds;
- no background tick may continuously append ledger entries without an authorized workload;
- browser main-thread long tasks above 200 ms must be recorded and bounded;
- editor input must remain responsive while optional capability probes execute;
- no boot stage may remain unresolved beyond its configured deadline.

A performance gate failure is a functional failure when it prevents interaction.

# 9. Required negative tests

The suite must prove rejection or recovery for:

- circular browser boot dependency;
- boot promise that never resolves;
- parser module that waits on its own completion-dependent DOM event;
- missing required DOM element;
- duplicate control binding;
- malformed recovery payload;
- corrupted local storage;
- source asset shadowed by root mount;
- incorrect JavaScript MIME;
- API route collision;
- unavailable runtime authority;
- duplicate VM81 commit authority;
- more than one Hash72 commit stream;
- runtime tick executed synchronously on the event loop;
- uncontrolled background kernel loop;
- assistant provider required for base boot;
- Word2Vec required for base boot;
- C build failure mislabeled as browser failure;
- browser failure mislabeled as hosting failure;
- server process active with no listening socket;
- UI reports ready while required controls are unbound;
- export reports success without a valid ZIP.

# 10. CI and evidence requirements

Pass 185 must add a dedicated required workflow, proposed name:

```text
Pass 185 Production Cold-Boot Browser Acceptance
```

The workflow must execute on every change to:

- production server composition;
- startup scripts or systemd generation;
- public HTML;
- `/src` modules;
- Visual IDE modules;
- Pass 176 stability code;
- application lifecycle code;
- assistant bootstrap code;
- C runtime build surfaces;
- Word2Vec activation surfaces;
- Nginx or reverse-proxy templates;
- packaging and deployment profiles.

Required evidence artifacts:

- exact base and tested commit SHA;
- environment manifest;
- production launch command;
- process tree;
- socket and health timeline;
- browser console log;
- page errors;
- failed requests;
- response/MIME inventory;
- screenshots;
- Playwright trace;
- workflow action log;
- exported ZIP and manifest;
- CPU/memory/I/O samples;
- recovery and replay receipts;
- Hash72 completion receipt;
- Hash216 evidence-set identity;
- final scenario matrix with pass/fail status.

# 11. Completion prohibition

Pass 185 must remain incomplete when any required scenario is skipped, mocked, manually waived, hidden behind an optional CI job, or classified as an external deployment concern without proof.

The following classifications are prohibited before complete evidence closure:

```text
PRODUCTION_READY
IDE_COMPLETE
PASS_185_COMPLETE
BROWSER_VERIFIED
DEPLOYMENT_VERIFIED
```

A green unit-test suite cannot override a failed real-browser test.

A healthy API cannot override a frozen UI.

A rendered shell cannot override unbound controls.

A successful module import cannot override a composed production-root timeout.

A local diagnostic patch cannot override an unfixed repository.

# 12. Required closure sequence

```text
PRESERVE INCIDENT REPRODUCTION
→ REPAIR SERVER STARTUP STARVATION
→ REPAIR INTEGRATED BROWSER BOOT GRAPH
→ ADD REAL PRODUCTION-ROOT PLAYWRIGHT ACCEPTANCE
→ ADD DESKTOP AND MOBILE WORKFLOW TESTS
→ ADD C / GEMMA / WORD2VEC DEGRADATION MATRIX
→ RUN DEPENDENCY-SCOPED REGRESSION
→ RUN COMPLETE PASS 185 ACCEPTANCE
→ COMMIT
→ MERGE OR OPEN READY-TO-MERGE PR
→ VERIFY AUTHORITATIVE MAIN
→ DEPLOY EXACT VERIFIED MAIN SHA
→ REPEAT EXTERNAL COLD-BOOT ACCEPTANCE
→ ISSUE COMPLETION RECEIPT
```

No Pass 185 implementation may remain stranded on an agent branch after validation.

# 13. Durable operating rule

This contract records the following project-wide directive for all subsequent passes:

```text
EVERY USER-FACING PASS MUST TEST THE EXACT PRODUCTION COMPOSITION,
EVERY REQUIRED INTERACTION, EVERY DECLARED DEGRADATION MODE,
AND EVERY RELEVANT FAILURE SCENARIO BEFORE COMPLETION.

INHERITED CONTRACTS AND PRIOR TESTS ARE MINIMUM INPUTS,
NOT PROOF THAT THE CURRENT INTEGRATED APPLICATION WORKS.
```

This rule is binding until explicitly superseded by a later authoritative contract that provides equal or stronger production acceptance.

# 14. Terminal acceptance statement

Pass 185 may emit its terminal completion classification only when all required evidence is present and verified:

```text
HHS_PASS_185_PRODUCTION_BROWSER_AND_RUNTIME_CLOSURE_VERIFIED
EXACT_PRODUCTION_ROOT_COLD_BOOT_VERIFIED
DESKTOP_AND_MOBILE_INTERACTIVITY_VERIFIED
CALCULATOR_CREATE_EDIT_SAVE_PREVIEW_TEST_EXPORT_VERIFIED
MULTIMODAL_APPLICATION_WORKFLOWS_VERIFIED
SERVER_EVENT_LOOP_AND_BACKGROUND_WORK_BOUNDED
C_RUNTIME_VERIFIED
GEMMA_DEGRADATION_AND_READY_MODES_VERIFIED
WORD2VEC_DEGRADATION_AND_ACTIVE_MODES_VERIFIED
INHERITED_VERIFICATION_FAILURE_REPAIRED
AUTHORITATIVE_MAIN_AND_EXTERNAL_DEPLOYMENT_REPLAY_VERIFIED
```
