# Pass 177 I149 workflow-authority reconciliation

## Census

Pass 177 is not contract-only. Historical implementation was merged by commit `2aeb16e736829ec9fe64b2a0d9779bbfa147f4ec` (PR #99) and remains reachable in the principal IDE.

Repository-native historical surfaces include:

- browser Hash216 candidate identity;
- plug-and-play module registry;
- deterministic project factory;
- typed workflow registry;
- resumable workflow runner;
- browser/PWA/service source-ZIP workflows;
- IDE template integration;
- Node acceptance tests.

The historical implementation is partial relative to the terminal Pass 177 contract and had no backend VM81 admission surface.

## I149 repair

I149 preserves all historical browser workflows and adds:

- `hhs_runtime/pass177/runtime.py`;
- `hhs_backend/api/pass177_template_workflow_routes.py`;
- inherited VM81 admission for generated-project candidates;
- inherited VM81 admission for workflow checkpoints;
- post-VM81 Hash72 execution evidence;
- archival 216-character identities;
- explicit browser-identity and memory-checkpoint nonauthority markers;
- no-float canonical backend ingress.

Browser project generation remains useful and deterministic, but its `hash216-browser.mjs` output is candidate/projection identity until the backend returns a VM81-admitted project record.

## Historical truth preserved

The existing stage executors intentionally say what they actually do:

- `test-project` -> `source-validated`;
- `build-project` -> `source-preserving`;
- source ZIP -> `independentOfCompilation: true`.

I149 does not relabel those outputs as executed target compilation.

## Nonterminal debt

Pass 177 remains nonterminal. Required repair-forward categories include the complete application and creative-content family matrix, environment adapters, verified toolchain provisioning, real multi-target builds/transforms, format-specific output validation, durable project-visible checkpoints, assistant mutation parity, explicit deployment revision evidence, usability studies, performance/scale evidence, and authoritative-main/deployed closure.
