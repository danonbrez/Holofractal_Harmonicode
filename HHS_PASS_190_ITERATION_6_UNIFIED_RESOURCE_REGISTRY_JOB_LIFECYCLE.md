# HHS PASS 190 ITERATION 6 — UNIFIED RESOURCE REGISTRY AND JOB LIFECYCLE

## 1. Metadata

| Field | Value |
|---|---|
| Contract | `HHS-P190-I6-URR-JLC-CF-VM81-H72-H216` |
| Parent | `HHS-P190-I5-AKAC-LEASE-RECEIPT-FENCE-VM81-H72-H216` |
| Iteration | `6` |
| Baseline | `main @ 992b4e92a54d4656d66af4edfab7e03922addca6` |
| Classification | `HHS_PASS_190_ITERATION_6_UNIFIED_RESOURCE_REGISTRY_JOB_LIFECYCLE_FOUNDATION_VERIFIED` |
| Full Pass 190 completion | Not claimed |

## 2. Purpose

Iterations 1–5 established the canonical operation registry, persistent Hash72/Hash216 receipts, native ABI/compiler projection, authenticated remote authority, cross-process singleton admission, lease-transition receipts, and atomic kernel fencing.

Iteration 6 places the application-development resources that operations act upon inside that same authority:

```text
workspace
→ artifact
→ provider
→ capability definition
→ governed job
→ VM81 admission
→ Hash72 receipt and event
→ durable resource state root
```

No workspace, artifact, provider, capability, or job receives a separate mutation authority.

## 3. Governed operation registry

The inherited ten-operation native registry remains authoritative and unchanged. Iteration 6 adds twenty-one operations through an additive expanded registry:

### Workspace

```text
workspace.create
workspace.get
workspace.list
workspace.update
workspace.archive
```

### Artifact

```text
artifact.register
artifact.get
artifact.list
```

### Provider

```text
provider.register
provider.get
provider.list
provider.set_enabled
```

### Capability

```text
capability.define
capability.get
capability.list
```

### Job

```text
job.submit
job.get
job.list
job.claim
job.complete
job.fail
```

Total governed operations:

```text
10 inherited native operations
+ 21 exact authority operations
= 31 governed operations
```

Every new operation has a complete operation record, VM81 binding, HARMONICODE constructor, shell form, HTTP path, SDK symbol, capability scope, schema, and Hash216 identity.

## 4. Canonical resource state

Resources are stored in the same exact authority state used by inherited operations:

```text
state.resource_registries = {
  workspaces: {},
  artifacts: {},
  providers: {},
  capabilities: {},
  jobs: {}
}
```

The full state root remains:

```text
H_state = Hash72("pass190.state", state)
```

Each resource record has:

- a typed schema;
- canonical identity;
- positive integer version;
- exact payload;
- `record_hash72` calculated over the record without that hash field.

Startup and every distributed refresh validate the resource records inside the same atomic SQLite snapshot used for receipts, events, lease receipts, fences, and kernel witnesses.

## 5. Workspace invariants

A workspace is the root application-development scope.

Required invariants:

- canonical unique `workspace_id`;
- exact name and metadata;
- monotonic version;
- explicit archived state;
- canonical sorting by `workspace_id`;
- archived workspaces reject new artifacts and jobs;
- a workspace cannot be archived while it has queued or running jobs.

Updates replace only declared fields and produce a new record Hash72.

## 6. Artifact invariants

Artifacts are immutable registered outputs or inputs.

Required invariants:

- canonical unique `artifact_id`;
- existing active workspace;
- declared media type;
- exact integer byte size;
- 72-glyph content Hash72;
- metadata without hidden mutation authority;
- no replacement under the same artifact identity.

A job may reference only artifacts registered in its own workspace.

## 7. Provider invariants

A provider record describes a governed execution or generation provider.

Required invariants:

- canonical unique `provider_id`;
- declared provider kind;
- optional endpoint and metadata;
- explicit enabled state;
- no secret material in the canonical provider record;
- a provider cannot be disabled while it owns queued or running jobs.

Secrets remain in protected deployment configuration and are never persisted in the resource registry.

## 8. Capability-definition invariants

Capability definitions make authorization scopes discoverable and typed.

Required invariants:

- canonical non-public `namespace:action` scope;
- exact description;
- declared risk class;
- unique immutable identity;
- monotonic record version.

Capability definitions do not issue credentials. Signed credentials remain governed by the inherited capability-token authority.

## 9. Job lifecycle

A job is a durable governed request for one registered operation.

Canonical states:

```text
queued → running → completed
queued → failed
running → failed
```

Forbidden transitions fail with typed state conflict errors.

A job records:

- canonical job and workspace identities;
- target operation and operation Hash216;
- validated exact arguments;
- optional enabled provider;
- input artifact identities;
- declared required capabilities;
- request Hash72;
- worker identity after claim;
- result or error;
- output artifact identities;
- status and version;
- record Hash72.

The job must declare the target operation capability when that operation is protected. All declared scopes must already exist in the capability-definition registry.

## 10. Referential integrity

Atomic restore validates:

```text
artifact.workspace_id ∈ workspaces
job.workspace_id ∈ workspaces
job.operation_id ∈ governed operations
job.provider_id ∈ providers, when present
job.input_artifact_ids ⊆ artifacts
job.output_artifact_ids ⊆ artifacts
job.required_capabilities ⊆ capabilities
```

Any broken reference, invalid status, malformed content hash, record-hash mismatch, or unknown registry kind fails closed before the authority serves requests.

## 11. Compiler fallback

The validated native ABI remains exactly ten operations. It is not falsely expanded.

Compiler lowering is selected per operation:

```text
native operation
→ existing C ABI symbol and native value profile

resource operation
→ VM81 exact-authority fallback
→ HHSAuthorityContext.invoke
→ normal admission, receipt, fence, event, and replay path
```

Fallback VMIR declares:

```text
native_available = false
native_profile = vm81-exact-authority-fallback-v1
fallback_authority = HHSAuthorityContext.invoke
```

Compiled programs carry the expanded registry Hash216, governed/native operation counts, and Iteration 6 Hash72/Hash216 program identities.

## 12. HTTP and OpenAPI

Iteration 6 preserves all inherited routes and adds:

```text
GET /api/pass190/resource-registry
POST /api/pass190/operations/<canonical-operation-id>
```

Direct operation routes must match the operation's canonical registry path and use the same signed capability authority as `/api/pass190/invoke`.

OpenAPI reports:

- Iteration 6 contract and classification;
- 31 governed operations;
- ten native operations;
- exact VM81 fallback policy;
- all canonical direct operation paths;
- resource-registry status route.

## 13. SDK, bindings, and GUI

Generated Python and TypeScript SDKs expose all 31 operations plus `resource_registry()` / `resourceRegistry()`.

`P190_OPERATION_SURFACE_BINDINGS_V2` freezes:

- GUI action identity;
- workflow step identity;
- Python and TypeScript symbol;
- receipt channel;
- native availability for every operation.

The visual authority displays:

- governed/native/fallback operation counts;
- workspace, artifact, provider, capability, and job counts;
- active job count;
- resource-registry Hash72;
- resource-registry integrity;
- inherited receipts, events, leases, fences, kernel authority, chain head, and state root.

## 14. Deployment

Production starts:

```text
server/hhs_pass190_iteration6_server.py
```

against the inherited database:

```text
/var/lib/hhs/pass190-authority.sqlite3
```

Deployment verification requires empty-start resource registries, 31 governed operations, ten native operations, twenty-one exact fallbacks, Iteration 6 OpenAPI, and all inherited authority checks.

## 15. Validation

Iteration 6 adds tests for:

1. expanded registry order, count, and Hash216 identity;
2. capability-gated resource mutation;
3. workspace lifecycle and sorting;
4. artifact immutability and workspace binding;
5. provider and job lifecycle constraints;
6. job target-capability declaration;
7. persistence and restart hydration;
8. replay without state mutation;
9. native and fallback compiler lowering;
10. resource tamper rejection after recomputing the outer state root;
11. live direct HTTP, registry, compiler, and OpenAPI surfaces;
12. protected direct-route credential rejection.

All inherited Iterations 1–5 tests, strict native C11 tests, generated native artifact checks, SDK/binding parity, GUI/deployment verification, private-evaluation rejection, and no-float authority checks remain binding.

## 16. Remaining Pass 190 work

Iteration 6 closes the first-class resource and job-registry foundation. Still open:

- broad repository-wide hydration of legacy public operations;
- complete Python built-in and standard-library compatibility;
- broader native ABI value profiles for currently governed operations;
- migration of remaining legacy routes, GUI actions, and workflows;
- full compiler lowering beyond constructor programs;
- durable worker execution, cancellation, retry, dependency, and scheduling policies;
- provider-specific invocation adapters and live credentials;
- multi-host consensus if authority moves beyond one SQLite host;
- live DigitalOcean installation and production acceptance;
- final Pass 190 completion classification.
