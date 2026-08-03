# Agentic Development Findings After Pass 201

## Verified strengths

The existing HHS architecture already provides several capabilities that are unusually useful to autonomous development agents:

1. receipt-chained provenance through Hash72 tips, VM81 ticks, and gate status;
2. honest capability and degradation flags rather than fabricated success;
3. structured tool registries and machine-correctable validation responses;
4. evidence-grounded assistant output with explicit proposal-versus-runtime-admission boundaries.

## Discovery gap closed by Pass 201

Pass 201 directly addresses the previous lack of a machine-readable API manifest:

- `/api/public/status` reports federation closure;
- `/api/public/catalog` returns the complete route, service, pass-module, and documentation index;
- `/api/public/routes` enumerates directly callable native routes;
- `/api/public/services` groups registered services;
- `/api/public/passes` publishes every discovered pass module, including modules without native routers;
- `/api/public/openapi` returns the generated OpenAPI document;
- `/api/public/tools` and `/api/public/tools/invoke` provide bounded catalog discovery.

The production validator requires zero hidden registered router routes and zero missing OpenAPI operations.

## Remaining agentic creative-platform gaps

### Native media capability

The storybook-reel path requires an operational host media toolchain, including `ffmpeg`, `ffprobe`, and the repository-native reel CLI. Capability flags must remain honest when those dependencies are absent.

### Durable asynchronous jobs

Long operations must use a restartable job contract:

- submit job;
- receive durable job identity;
- inspect status and bounded progress;
- cancel or retry without duplicate ambiguity;
- retrieve receipts, logs, and artifacts;
- recover interrupted work after process restart.

The integration-scan work in PR #141 is an existing partial implementation of this pattern but is outside the Pass 201 merge scope.

### Content-addressed workspace artifacts

The workspace authority needs governed object and artifact routes for:

- source upload;
- object registration;
- content-addressed storage;
- artifact metadata and lineage;
- binary retrieval;
- project attachment;
- receipt-chain binding;
- deterministic export and replay.

### Admitted executable assistant plans

The assistant should be able to return a structured action plan against the public tool registry. Execution must remain separate:

1. assistant proposes a typed plan;
2. runtime validates schemas, capabilities, dependencies, and authority requirements;
3. an audited runner admits or rejects the plan;
4. admitted steps execute through native routes;
5. each step emits receipts and artifact references;
6. the final root binds the complete workflow lineage.

The assistant must never acquire direct mutation authority merely by generating the plan.

## Recommended next bounded pass

A subsequent pass should combine these requirements as an **Agentic Creative Work Authority** with three integrated but separately governed substrates:

1. durable asynchronous job queue;
2. content-addressed workspace artifact store;
3. admitted executable assistant plans.

A target end-to-end acceptance path is:

`declare intent → assistant proposes plan → runtime admits plan → native creative job executes → artifacts are stored content-addressed → final receipt root proves plan, execution, and artifact lineage`.

This document records the next architecture boundary only. Pass 201 remains limited to complete public API federation and discovery.
