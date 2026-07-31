# HHS PASS 180 — INTEGRATED APPLICATION FACTORY RUNTIME

## Normative metadata

| Field | Value |
|---|---|
| Contract identifier | `HHS-P180-IAF-VM81-H72-H216` |
| Pass number | `180` |
| Canonical name | `INTEGRATED_APPLICATION_FACTORY_RUNTIME` |
| Version | `1.0.0` |
| Authority | `HHS_VM81_SINGLETON_APPLICATION_FACTORY_AUTHORITY_V1` |
| Merge target | `main` |

## Purpose

Pass 180 converts the existing HHS workspace, visual IDE, VM81 Runtime, Hash72 receipt authority, Hash216 identity services, modality pipelines, assistant, testing, replay, and ZIP egress into one callable application-factory surface.

The factory must not create a competing execution authority. Module planning may identify independent candidate groups, but canonical project mutation and lifecycle closure remain serialized through one commit authority.

## Required capabilities

1. A repository-native plug-and-play module catalog covering project state, VM81, the visual interface, assistant workflows, exact mathematics, native graphics, interaction, audio, video, documents, storage, API services, testing, and ZIP packaging.
2. Complete workflow templates for web applications, scientific calculators, 2D games, document tools, media tools, API services, and universal multimodal applications.
3. Dependency closure and a project-scoped module graph.
4. Incremental affected-module planning from changed project paths.
5. Finite lifecycle jobs with durable IDs, checkpoints, bounded deadlines, explicit final states, cancellation, retry, and failure reasons.
6. Source ZIP export independent of compilation.
7. Hash72 roots for files, source trees, project state, module graphs, plans, checkpoints, packages, receipts, and replay.
8. Deterministic source ZIP construction and deterministic journal replay.
9. Visual-server API registration before the Pass 161 static mount.
10. No fabricated native binary, deployment, test, or provider success. Compile and test outputs that require an external executor remain explicit plans until that executor returns admitted evidence.

## Lifecycle

```text
INGRESS
→ RESOLVE_MODULES
→ BUILD_GRAPH
→ VALIDATE
→ COMPILE_PLAN
→ TEST_PLAN
→ PACKAGE
→ COMMIT_RECEIPT
```

Every lifecycle run terminates in one of:

```text
SUCCEEDED | FAILED | CANCELLED | TIMED_OUT
```

`QUEUED`, `RUNNING`, and `CANCEL_REQUESTED` are transient states only.

## Public API

Base path:

```text
/api/runtime/application-factory
```

| Method | Route | Purpose |
|---|---|---|
| GET | `/status` | Runtime and self-test status |
| GET | `/modules` | Plug-and-play module library |
| GET | `/workflows` | Complete workflow library |
| POST | `/projects` | Instantiate an application project |
| GET | `/projects/{project_id}` | Read project state |
| PUT | `/projects/{project_id}/files` | Add or replace a project file |
| POST | `/projects/{project_id}/plan` | Compute incremental affected work |
| POST | `/projects/{project_id}/lifecycle` | Execute the bounded lifecycle |
| GET | `/jobs/{job_id}` | Read durable job state and checkpoints |
| POST | `/jobs/{job_id}/cancel` | Request bounded cancellation |
| POST | `/jobs/{job_id}/retry` | Restart a final job from repository-visible inputs |
| GET | `/projects/{project_id}/source.zip` | Export source without compilation |
| GET | `/projects/{project_id}/replay` | Verify deterministic project journal replay |

## Authority rules

- Candidate groups are planning and computation units only.
- Parallel candidate planning does not imply parallel state authority.
- One application-factory commit lock serializes admitted project mutation.
- Every admitted mutation produces a Hash72 receipt.
- Source, projection, compile plan, test plan, package, execution, and deployment evidence remain distinct.
- Unknown workflows, modules, projects, jobs, and path traversal fail closed.

## Initial module library

```text
core.project
runtime.vm81
ui.web
assistant.development
math.exact
graphics.native
input.events
audio.runtime
video.runtime
documents.editor
storage.local
network.api
testing.acceptance
packaging.zip
```

## Initial workflow library

```text
web_application
scientific_calculator
game_2d
document_studio
media_studio
api_service
universal_multimodal
```

## Acceptance criteria

Pass 180 is accepted only when all of the following are demonstrated by executable tests:

- module and workflow catalogs are callable;
- dependency closure succeeds for valid workflows;
- unknown workflow and path traversal requests fail closed;
- incremental planning returns impacted and unaffected modules;
- candidate groups are topologically ordered;
- lifecycle jobs execute all eight checkpoints and terminate;
- source ZIP export succeeds before any compilation executor runs;
- ZIP bytes are deterministic for identical project state;
- project replay verifies ordered journal sequence and roots;
- the visual server registers the application-factory routes before mounting the static interface;
- dependency-scoped CI passes.

## Restartability record

The authoritative repository state contains:

- this contract;
- `hhs_backend/runtime/hhs_application_factory_v1.py`;
- `hhs_backend/api/application_factory_routes.py`;
- visual-server route composition;
- `tests/test_pass180_application_factory.py`;
- `.github/workflows/pass180-application-factory.yml`.

No private local state is required to resume implementation or validation.
