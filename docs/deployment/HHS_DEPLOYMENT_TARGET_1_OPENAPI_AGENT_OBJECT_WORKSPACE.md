# HHS Deployment Target 1 — OpenAPI Remote Agent Object Workspace

## Status

`BINDING_FIRST_POST_220_DEPLOYMENT_TARGET — NOT IMPLEMENTED — NOT PASS 219 OR PASS 220 CLOSURE`

This document defines the first production deployment target after terminal Pass 219 and terminal Pass 220 closure.

It does **not** claim that the target is implemented, deployed, externally reachable, production-secure, or accepted. It does not add work to the Pass 219 terminal gate and it does not bypass the existing Pass 220 implementation gate.

The admission relation is:

```text
PASS 219 TERMINAL CLOSURE + EXACT-HEAD VERIFICATION
    -> PASS 220 TERMINAL CLOSURE + EXACT-HEAD VERIFICATION
    -> DEPLOYMENT TARGET 1 IMPLEMENTATION ADMISSION
```

The target's canonical product identity is:

```text
HHS_REMOTE_AGENT_OBJECT_WORKSPACE_V1
```

The target SHALL use the repository's pinned OpenAPI 3.2.0 profile unless the cumulative standards registry explicitly upgrades that profile before implementation.

## 1. Purpose

Deployment Target 1 SHALL make HHS remotely useful to external AI agents without requiring those agents to understand repository paths, pass numbers, VM81 internals, Hash72 fields, native ABI symbols, or the legacy browser interface.

Given only:

1. the authenticated service origin;
2. its OpenAPI description;
3. an authorized agent credential; and
4. a user's requested outcome and supplied inputs,

an external AI agent SHALL be able to discover available HHS capabilities and use them to create, inspect, revise, validate, build where applicable, export, retrieve, and verify user-requested HHS objects and artifacts.

The remote tool is an agent-access projection of inherited HHS functionality. It SHALL NOT implement a second object engine, application factory, operation registry, mutation authority, database authority, or receipt system.

## 2. Inherited implementation foundation

Deployment Target 1 SHALL reuse rather than replace these inherited surfaces:

- Pass 170 public API port authority, canonical public gateway, authentication/authorization lifecycle, exact transport, and route/operation parity;
- Pass 187 composable object/application authority;
- Pass 189 repository-wide template-object registry, object discovery, materialization, build/test/export workflows, and searchable modality tree;
- Pass 190 canonical operation registry, OpenAPI/HTTPS/WebSocket projection, capability registry, job service, artifact service, workspace service, Hash72 receipts, Hash216 operation identity, and replay;
- Pass 219 exact reusable runtime/ABI closure;
- Pass 220 common action/workspace model, native Linux execution/tooling, packaging, and agent/API parity;
- the cumulative deployment end-state in `docs/pass219/PASS_219_CUMULATIVE_DEPLOYMENT_END_STATE.md`.

The governing equivalence remains:

```text
ONE REGISTERED OPERATION
-> ONE CANONICAL CONSTRUCTOR
-> ONE SEMANTIC IMPLEMENTATION
-> ONE VM81 ADMISSION PATH
-> ONE RECEIPT / REPLAY MODEL
-> MANY INTERFACE PROJECTIONS
```

An OpenAPI route SHALL therefore resolve to existing registered semantics rather than own them.

## 3. User-requested object model

The central remote work unit SHALL be a governed **user object request**.

A user object request expresses the user's requested outcome plus structured constraints and desired deliverables. It MAY target an existing object/template identity or request that HHS select a compatible registered object/template from the Pass 189 catalog.

The remote object model SHALL be registry-driven, not a hard-coded list. At minimum, when the corresponding registered implementation exists, an agent SHALL be able to request or manipulate objects in families such as:

```text
PROJECT / WORKSPACE
APPLICATION / SERVICE / CLI TOOL
FILE / DIRECTORY / MODULE / SOURCE PACKAGE
DOCUMENT / TEXT / PUBLISHING ARTIFACT
IMAGE / GRAPHICS / VECTOR ASSET
AUDIO / MUSIC / PCM ARTIFACT
VIDEO / ANIMATION / STORY ARTIFACT
3D ASSET / SCENE / SIMULATION
GAME / INTERACTIVE PROJECT
DATASET / TABLE / GRAPH / DATA ARTIFACT
WORKFLOW / AUTOMATION / BUILD PIPELINE
MODEL-COMPATIBLE OR REGISTERED INTELLIGENCE ARTIFACT
PACKAGE / RELEASE / DOWNLOADABLE ARTIFACT
ANY OTHER EXECUTABLE OR MATERIALIZABLE PASS 189 TEMPLATE OBJECT
```

Specification-only, unresolved, deprecated, or non-materializable templates SHALL be labeled honestly and SHALL NOT be presented to an agent as executable generation capability.

## 4. Canonical architecture

```text
USER REQUEST
     |
     v
EXTERNAL AI AGENT
     |
     | HTTPS + OpenAPI-described operations
     v
HHS REMOTE AGENT GATEWAY
     |
     +-> authentication / workload identity
     +-> tenant + workspace isolation
     +-> schema + size validation
     +-> capability + authorization gate
     +-> idempotency / expected-version gate
     |
     v
AGENT SESSION / USER OBJECT REQUEST
     |
     v
PASS 220 COMMON ACTION MODEL
     |
     v
PASS 190 CANONICAL OPERATION REGISTRY
     |
     v
PASS 187/189 OBJECT + APPLICATION FACTORY
     |
     v
PASS 219 EXACT RUNTIME / ABI
     |
     v
SINGLETON VM81/KERNEL ADMISSION
     |
     v
HASH72 RECEIPT -> HASH216 IDENTITY / REPLAY
     |
     +-> JOB SERVICE
     +-> ARTIFACT / CONTENT SERVICE
     +-> GOVERNED DATA SERVICES
     |
     v
INSPECT / REVISE / EXPORT / DOWNLOAD / VERIFY
```

The AI agent is a caller and planner. It is **not** canonical HHS authority.

## 5. Minimum remote lifecycle

An agent using only the published remote contract SHALL be able to execute this lifecycle:

```text
DISCOVER OPENAPI
-> AUTHENTICATE
-> DISCOVER CAPABILITIES + OBJECT/TEMPLATE TYPES
-> CREATE OR RESUME AGENT SESSION
-> CREATE OR SELECT WORKSPACE
-> SUBMIT USER OBJECT REQUEST
-> RECEIVE DURABLE REQUEST/JOB ID
-> OBSERVE STATUS / EVENTS
-> INSPECT MATERIALIZED OBJECT + VERSION
-> APPLY ONE OR MORE TYPED REVISIONS
-> BUILD / TEST / VALIDATE where the object supports them
-> EXPORT REQUESTED FORMAT(S)
-> RETRIEVE ARTIFACT(S)
-> VERIFY DIGEST + PROVENANCE + RECEIPT
-> RESUME / RETRY / REPLAY when required
```

No step may require an interactive browser frontend.

## 6. Minimum OpenAPI surface

The implementation SHALL expose versioned operations under the canonical public API model. Exact implementation may compose existing registered routes, but the effective agent surface SHALL provide equivalents of:

```text
GET    /openapi.json
GET    /v1/capabilities
GET    /v1/templates
GET    /v1/templates/{template_id}

POST   /v1/agent/sessions
GET    /v1/agent/sessions/{session_id}

POST   /v1/workspaces
GET    /v1/workspaces/{workspace_id}

POST   /v1/agent/object-requests
GET    /v1/agent/object-requests/{request_id}
POST   /v1/agent/object-requests/{request_id}/actions

GET    /v1/objects/{object_id}
GET    /v1/objects/{object_id}/versions

GET    /v1/jobs/{job_id}
POST   /v1/jobs/{job_id}/cancel
POST   /v1/jobs/{job_id}/retry

POST   /v1/objects/{object_id}/export
GET    /v1/artifacts/{artifact_id}
GET    /v1/receipts/{receipt_id}
```

Status/event streaming MAY use a registered WebSocket or SSE projection, but streaming semantics SHALL remain tied to the same durable job/request identity.

The route names above are the required effective capability families, not authorization for a second private semantic implementation. Where an inherited registered route already satisfies the operation, the deployment SHALL reuse or alias it with parity verification.

## 7. User object request schema

The canonical request SHALL include or resolve at least:

```text
request_id or idempotency_key
agent_session_id
workspace_id
user_request_identity
user_intent
object_type and/or template_id
source_object_id / source_version when revising
inputs[] / attachments[] / references[]
constraints[]
desired_outputs[]
desired_formats[]
capability_request
resource_bounds
expected_object_version or expected_state when applicable
delivery_mode
metadata
```

`user_intent` MAY be natural language. Natural language SHALL be interpreted into typed registered actions before authoritative mutation.

Canonical exact numeric fields SHALL use inherited exact tagged transport and SHALL NOT acquire authority from JSON floating-point values.

## 8. Action model

An AI agent SHALL NOT obtain an unrestricted generic mutation endpoint. Agent changes SHALL be expressed as typed actions resolved through the Pass 220 common action model and Pass 190 canonical operation registry.

Required action classes include, where supported by the target object:

```text
CREATE
INSPECT
EDIT / TRANSFORM
ADD / REMOVE / CONNECT / NEST
PLAN
BUILD
RUN
TEST
VALIDATE
PREVIEW
EXPORT
PACKAGE
REPLAY
ROLLBACK / RESTORE where authorized
```

An agent MAY perform multiple actions in one user task, but every authoritative effect SHALL retain operation identity, capability decision, version lineage, durable status, and receipt/replay evidence required by the underlying operation.

## 9. Agent authentication and security boundary

Production acceptance SHALL require authenticated agent/workload identity and explicit user/tenant authorization.

At minimum the remote surface SHALL enforce:

1. scoped, revocable agent credentials or workload identity;
2. tenant and workspace isolation;
3. per-operation capability scopes;
4. request-size, upload-size, compute, time, concurrency, and storage quotas;
5. idempotency protection for retried mutations;
6. optimistic version/expected-state conflict detection where applicable;
7. path traversal and filesystem-boundary rejection;
8. SSRF and unintended private-network egress rejection;
9. shell/command injection rejection at API adapters;
10. secret and credential redaction in responses, logs, artifacts, and diagnostics;
11. cross-tenant object/artifact/database access denial;
12. explicit authorization for external publication, destructive actions, and privileged egress;
13. no raw VM81 memory/register mutation API;
14. no direct database superuser credential exposure;
15. no unrestricted host or VM shell capability by default;
16. fail-closed behavior when identity, capability, integrity, schema, or expected-version validation is unresolved.

If a shell or arbitrary-code execution capability is later offered to agents, it SHALL be an explicitly registered, sandboxed, resource-bounded capability with its own security contract. It SHALL NOT be implicit in object-generation access.

## 10. Database and artifact boundary

Object metadata, job state, uploads, versions, generated content, indexes, and artifacts MAY be persisted in the secure data plane.

Those stores SHALL NOT independently authorize semantic mutation. Database writes implementing an admitted HHS action remain downstream persistence of the authoritative action outcome.

Agents SHALL receive opaque governed object, job, artifact, workspace, and receipt identities rather than privileged storage credentials or direct uncontrolled database access.

Artifact retrieval SHALL provide integrity metadata sufficient to verify the downloaded bytes against the artifact record.

## 11. Durability and restartability

Long-running generation, compilation, rendering, validation, packaging, or export SHALL use durable jobs.

A server/worker restart SHALL not require the external AI agent to reconstruct the task from private conversation memory. The service SHALL persist sufficient request/action/job state to support:

```text
STATUS
RESUME
RETRY
CANCEL
INSPECT FAILURE
REPLAY where supported
RETRIEVE COMPLETED ARTIFACTS
```

Idempotent retry SHALL not silently create duplicate authoritative mutations or duplicate releases.

## 12. Agent discoverability requirement

The remote product SHALL be usable without a bespoke agent integration manual for ordinary supported tasks.

The published OpenAPI document SHALL contain stable operation IDs, meaningful descriptions, request/response schemas, authentication requirements, capability/error classes, examples where useful, and machine-readable links or IDs sufficient for an agent to discover the normal workflow.

The deployment SHALL not require knowledge of repository file paths or internal pass architecture for normal remote use.

## 13. First production acceptance scenario

Deployment Target 1 SHALL NOT be accepted until executable external evidence demonstrates that an AI agent, operating as a remote client and given only the service OpenAPI contract, valid credentials, and user intent, can complete at least the following:

1. discover supported capabilities and materializable object/template types;
2. create or resume a tenant-scoped workspace/session;
3. submit a natural-language user request plus structured constraints;
4. materialize a real registered object through the inherited object/application factory;
5. inspect the resulting object/version;
6. make at least one subsequent typed revision;
7. build/test/validate the object when its registered profile supports those operations;
8. export a requested standard or native format;
9. download at least one resulting artifact and verify its cryptographic digest;
10. retrieve receipt/provenance/version lineage for the mutating workflow;
11. survive a worker or service interruption and resume or retrieve durable work without duplicating authoritative mutation;
12. reject an unauthorized operation;
13. reject a cross-tenant object/artifact access attempt;
14. reject an invalid/stale expected-version mutation;
15. demonstrate that every admitted mutation still reaches the singleton inherited VM81/kernel authority.

Acceptance SHALL include representative breadth across at least:

```text
ONE SOFTWARE/APPLICATION OBJECT
ONE CREATIVE OR DOCUMENT/MEDIA OBJECT
ONE DATA OR STRUCTURED PROJECT OBJECT
```

when executable registered implementations for those families are available.

Documentation-only objects do not satisfy acceptance.

## 14. Non-goals of Deployment Target 1

Deployment Target 1 is intentionally the first remote production slice. Its acceptance does not by itself claim completion of:

- the full native Linux VM fleet;
- every standalone application platform target;
- the complete creative-content distribution/catalog product;
- every secure database backend/profile;
- unrestricted third-party plugin execution;
- general-purpose arbitrary shell/root access for agents;
- all future multi-region/high-availability deployment objectives.

Those remain cumulative downstream work.

## 15. Promotion law

This target SHALL remain specification/preimplementation while Pass 219 or Pass 220 is nonterminal.

After Pass 220 terminal closure, implementation SHALL begin by reconciling the then-authoritative repository rather than copying an old API snapshot. It SHALL inventory and reuse current operation IDs, template/object identities, workspace/job/artifact services, authentication surfaces, deployment topology, and accepted security contracts.

The first deployment target is therefore:

```text
POST-219/220 DEPLOYMENT TARGET 1
= AUTHENTICATED OPENAPI REMOTE ACCESS
+ EXTERNAL AI AGENT DISCOVERY
+ GOVERNED USER OBJECT REQUESTS
+ REAL OBJECT MATERIALIZATION / REVISION
+ DURABLE JOBS
+ ARTIFACT EXPORT / DOWNLOAD
+ RECEIPT / PROVENANCE / REPLAY
+ SINGLETON HHS AUTHORITY PRESERVED
```
