# Post-220 OpenAPI Agent Object Workspace — Restart Record

## Status

`BINDING_TARGET_SPECIFICATION — NOT IMPLEMENTED — NOT DEPLOYED`

This is a repository-visible restart record for the first deployment target intended after terminal Pass 219 and terminal Pass 220 closure.

## Repository boundary

- Repository: `danonbrez/Holofractal_Harmonicode`
- Development branch: `agent/pass220-linux-vm-bootstrap-preimplementation`
- Existing stacked PR: `#320`
- Immediate PR base: `agent/pass219b-i7-exact-selective-projection-optimization`
- Validated Pass 219B I7 base: `6df75bc39fd7c58108b8cf7aee3758341fe345a5`
- Branch head observed immediately before this target specification: `3a051417c3cf4a91d83e147a4336981179ec586a`
- That observed head was an evidence-only Pass 172/173 hosted-validation commit; it did not change the Pass 220 VM/API implementation.
- Deployment Target 1 specification commit: `b1700f40d0da91452006aaf75c1b4f9f4c9a9620`
- Dedicated contract-workflow commit: `48e0f0d81494f77a7a99f2bb1fc478f6fabe0dd3`

Automated hosted-evidence workflows have previously appended evidence-only commits to this branch. Before any later promotion, compare the intended implementation/specification checkpoint against the branch tip and classify unrelated evidence-only movement rather than treating all tip movement as Deployment Target 1 source changes.

## Governing files

- `docs/pass219/PASS_219_CUMULATIVE_DEPLOYMENT_END_STATE.md`
- `HHS_PASS_220_HARMONICODE_UNIVERSAL_POLYGLOT_NATIVE_LINUX_VISUAL_IDE_PORTABLE_VM_COMPILER_CONTRACT.md`
- `docs/deployment/HHS_DEPLOYMENT_TARGET_1_OPENAPI_AGENT_OBJECT_WORKSPACE.md`
- `.github/workflows/post220-openapi-agent-object-target-contract.yml`
- this restart record

Inherited semantic sources include Pass 170, Pass 187, Pass 189, and Pass 190 contracts/implementations. The remote target must reuse their public-port, object/application, template/materialization, operation-registry, workspace, job, artifact, receipt, and replay semantics rather than implement route-owned alternatives.

## Target identity

```text
HHS_REMOTE_AGENT_OBJECT_WORKSPACE_V1
```

Classification:

```text
FIRST POST-219/220 DEPLOYMENT TARGET
= authenticated OpenAPI remote access
+ external AI-agent capability discovery
+ governed user object requests
+ registered object/application materialization
+ typed iterative revisions
+ durable jobs
+ build/test/validate where supported
+ artifact export and download
+ receipt/provenance/replay
+ singleton HHS authority preserved
```

## Admission gate

```text
PASS 219 TERMINAL CLOSURE + EXACT-HEAD VERIFICATION
    -> PASS 220 TERMINAL CLOSURE + EXACT-HEAD VERIFICATION
    -> DEPLOYMENT TARGET 1 IMPLEMENTATION ADMISSION
```

Nothing in this specification changes the current Pass 219 closure requirement or prematurely authorizes Pass 220 promotion.

## Specification completed

The target contract now defines:

1. OpenAPI 3.2.0 as the currently pinned agent-facing API profile, subject to the cumulative standards registry at implementation time;
2. a registry-driven user-object model covering software, documents/media, data, workflows, packages, and any other materializable Pass 189 object/template;
3. OpenAPI discovery, capabilities/templates, agent sessions, workspaces, object requests, typed actions, jobs, objects/versions, exports, artifacts, and receipts as minimum effective operation families;
4. natural-language user intent as ingress that must lower to typed registered actions before authoritative mutation;
5. explicit reuse of Pass 170/190 public operation semantics and Pass 187/189 object/application materialization;
6. full separation between AI-agent caller/planner role and singleton VM81/kernel authority;
7. scoped credentials, tenant/workspace isolation, quotas, idempotency, expected-version conflicts, SSRF/path/shell-injection protection, secret redaction, cross-tenant denial, and fail-closed behavior;
8. no raw VM81 mutation, no database-superuser exposure, and no unrestricted host/VM shell by default;
9. durable restartable jobs and artifact integrity/provenance requirements;
10. external-agent acceptance using only the service OpenAPI contract, valid credentials, and user intent;
11. acceptance breadth across a software/application object, creative/document/media object, and data/structured-project object when executable registered implementations exist.

## Validation state

A dedicated exact/synthetic GitHub Actions contract workflow has been added:

`.github/workflows/post220-openapi-agent-object-target-contract.yml`

It is required to verify:

- Pass 219/220 gates remain intact;
- target identity/status and OpenAPI profile;
- inherited registry/object/runtime reuse;
- singleton authority boundary;
- minimum agent lifecycle;
- minimum remote capability families;
- fail-closed security requirements;
- external-agent executable acceptance requirements.

At creation of this restart record, the workflow has been committed but its newest run may still be queued or in progress. Do not record it as green until terminal GitHub Actions evidence confirms both exact and synthetic jobs.

## Environment/deployment state

No production remote agent gateway has been deployed by this task.

No live external AI agent, production authentication provider, cloud database, artifact store, VM worker, or internet-facing OpenAPI service has been claimed or exercised by this target specification.

The existing historical DigitalOcean deployment documentation is inherited context only and does not count as Deployment Target 1 acceptance.

## Blockers

The implementation admission blockers are intentionally upstream:

1. Pass 219 is not yet terminally closed on authoritative main.
2. Pass 220 is therefore not yet admitted/promoted to terminal implementation.
3. Deployment Target 1 cannot honestly begin production implementation before both gates close.

## Next valid action

Continue Pass 219 to terminal closure and preserve this target specification.

After terminal Pass 219 and Pass 220 closure:

1. reconcile the then-current public operation registry and OpenAPI application;
2. inventory current template/object/application factory, workspace, job, artifact, authentication, data, and receipt services;
3. freeze the production authentication/tenant/resource model;
4. implement the smallest externally reachable agent workflow end-to-end;
5. run negative security and cross-tenant tests;
6. execute real external-agent object generation/revision/export/download acceptance;
7. freeze receipts, deployment identity, and restart evidence.

Do not implement a parallel generic agent backend when inherited registered HHS operations can satisfy the action.
