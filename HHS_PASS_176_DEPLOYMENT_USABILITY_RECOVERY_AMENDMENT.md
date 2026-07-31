# HHS PASS 176 — DEPLOYMENT USABILITY RECOVERY AMENDMENT

## Normative identity

- Contract: `HHS-P176-DURA-FSLJ-SPX-PB-AWR`
- Parent: `HHS_PASS_176_FROZEN_PRODUCTION_MULTIMODAL_IDE_STABILIZATION_PERFORMANCE_RECOVERY`
- Baseline: authoritative `main`
- Scope: deployed browser IDE reliability and progressive disclosure

## Binding inheritance

This amendment is additive. It does not replace, weaken, normalize, reinterpret, or bypass any prior pass invariant, VM81 authority rule, Hash72 receipt rule, Hash216 indexing rule, exact-source preservation rule, canonical no-float authority rule, ingress/egress rule, or restartable-agent closure rule.

The browser remains a non-authoritative control and packaging surface. Governed execution remains on the canonical backend authority path. Local preview and ZIP construction may package source and browser artifacts but may not claim VM81, Hash72, Hash216, compiler, or runtime authority.

## Required corrections

1. Every user-visible test lifecycle is represented as a finite job with `job_id`, `correlation_id`, state, timestamps, active file, last successful checkpoint, timeout, terminal reason, and retry metadata.
2. A lifecycle must terminate as `succeeded`, `failed`, `cancelled`, or `timed_out`; a browser reload converts an orphaned `running` job to a recoverable failure.
3. Active tests are bounded to ten seconds at the client boundary. Timeout or cancellation must restore editing and export controls immediately.
4. Source project export is always available and is independent of compilation or lifecycle success.
5. Runnable web export is identified separately from source, receipt/evidence, and governed compiler artifacts.
6. Preview must expose explicit `loading`, `ready`, and runtime-error behavior and a stable postMessage test bridge for query, click, type, key, snapshot, and accessibility inspection operations.
7. The default workspace is Application IDE: canonical Save, Build & Preview, Test, Export, Cancel, and Retry controls with project editing and preview as the primary surface.
8. VM81, Hash216, receipts, pass lineage, global registries, terminal hardware, and processor internals remain available without loss under Advanced Runtime.
9. Generated starter files are clean at creation and receive an explicit starter checkpoint.
10. Existing duplicate controls are rebound to the canonical command model; source export is never disabled by a running or failed governed lifecycle.

## Acceptance gates

- Preview reaches explicit ready or actionable error within five seconds.
- A governed active-path test completes within ten seconds or reaches an actionable terminal failure.
- Cancellation aborts the active client request and restores controls without waiting for the original backend timeout.
- Source ZIP export remains callable before, during, and after test failure.
- The test bridge can deterministically drive a generated calculator interaction without direct iframe DOM access.
- Application and Advanced Runtime workspaces are reversible and preserve all advanced controls.
- Dependency-scoped static tests and ECMAScript syntax validation pass.

## Terminal classification

`HHS_PASS_176_DEPLOYMENT_USABILITY_RECOVERY_IMPLEMENTED`
