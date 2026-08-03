# HHS Pass 203 — Universal Hydrated Function Mainframe

## Normative metadata

| Field | Value |
|---|---|
| Contract | `HHS-P203-UNIVERSAL-HYDRATED-FUNCTION-MAINFRAME-VM81-H72-H216` |
| Classification | `HHS_PASS_203_UNIVERSAL_HYDRATED_FUNCTION_MAINFRAME_VERIFIED` |
| Pass | 203 |
| Parent version | Pass 202 guarded continuous integration and DigitalOcean deployment |
| Public prefix | `/api/runtime/mainframe` |

## Cumulative version rule

Pass 203 is a version upgrade of the complete HHS system. It inherits every prior pass, contract, service, route, compiler, interpreter, ABI, runtime, workspace, job, artifact, graphics, creative, deployment, receipt, and validation layer. It is not a feature fork and does not create an alternative runtime authority.

## Purpose

Pass 201 made every registered HTTP router publicly discoverable. Pass 203 extends that closure to the internal hydrated function system so an autonomous agent can discover and use the HHS IDE as a governed cloud-computing mainframe.

The mainframe inventory combines:

1. Pass 190 governed operations;
2. exact interpreter adapters;
3. compiler and proof-carrying artifact adapters;
4. public runtime Python functions;
5. native C ABI symbols;
6. workspace, artifact, job, scheduler, and provider operations;
7. media, game, graphics, document, vector, database, and multimodal functions;
8. bounded multi-step execution plans;
9. receipt replay and runtime status.

## Function states

Every discovered function has a stable identity and one execution state:

- `PASS190_GOVERNED`: implemented by the inherited governed operation fabric;
- `GOVERNED_ADAPTER`: explicitly connected to an authoritative runtime adapter;
- `ISOLATED_PYTHON`: bounded public top-level function executed in an isolated worker;
- `ABI_BINDING_REQUIRED`: native symbol is inventoried but lacks a governed callable binding;
- `ADAPTER_REQUIRED`: Python function is inventoried but requires an explicit authority adapter;
- `WORKSPACE_JOB_ADAPTER_REQUIRED`: mutating or long-running function must execute through workspace/job authority;
- `FORBIDDEN`: function conflicts with the public execution safety boundary.

A function is `hydrated` only when it is callable through one of the first three execution modes. The public catalog must retain unbound declarations so missing hydration remains measurable.

## Public API

- `GET /api/runtime/mainframe/status`
- `POST /api/runtime/mainframe/refresh`
- `GET /api/runtime/mainframe/functions`
- `GET /api/runtime/mainframe/functions/{function_id}`
- `POST /api/runtime/mainframe/invoke`
- `GET /api/runtime/mainframe/operations`
- `POST /api/runtime/mainframe/operations/invoke`
- `GET /api/runtime/mainframe/jobs/runtime`
- `GET /api/runtime/mainframe/replay/{receipt_hash72}`
- `POST /api/runtime/mainframe/plans/validate`
- `POST /api/runtime/mainframe/plans/execute`
- `GET /api/runtime/mainframe/studio`

## Interpreter and compiler authority

The exact interpreter remains restricted to the registered exact integer/rational expression grammar. Host-language imports, evaluation, file access, and side effects are rejected with witnessed results.

The compiler may create proof-carrying artifacts, IR, and provenance. Compilation does not automatically authorize execution, active admission, or permanent constraint promotion. Those transitions remain governed by the inherited admission passes.

## Native ABI authority

All discovered `hhs_*` C symbols are publicly indexed with their header, return type, and parameter declaration. A native symbol becomes remotely callable only when it is bound to a governed operation or explicit adapter. The API does not expose arbitrary dynamic-library symbol calls.

## Agentic plan authority

An assistant or agent may submit a typed dependency graph. The runtime validates function identities, dependency closure, cycles, schemas, capabilities, and execution modes before execution. Generation of a plan does not grant mutation authority. Each admitted step executes through its native operation or adapter and emits its own receipt; the final plan result includes the terminal VM81 receipt.

## Safety and honesty

The mainframe prohibits:

- raw Python `eval` or `exec`;
- arbitrary module import requested by a client;
- unrestricted shell or subprocess commands;
- arbitrary native symbol invocation;
- frontend-manufactured VM81 receipts;
- bypass of capability, workspace, compiler, canary, active, or rollback authority;
- fabricated success for unhydrated functions.

Rejections include a stable schema, retryability, and remediation instruction.

## Acceptance requirements

Pass 203 closes only when validation proves:

1. Pass 190 operations, Python functions, native ABI symbols, and explicit adapters are all indexed;
2. function identities are unique and deterministic;
3. every hydrated entry is callable;
4. every non-hydrated entry fails closed with an execution-mode explanation;
5. exact interpreter execution and host-eval rejection both pass;
6. compiler artifact creation passes while execution authorization remains false;
7. a governed Pass 190 operation executes and emits its inherited receipt;
8. an isolated exact Python self-test executes successfully;
9. plan cycle and missing-dependency rejection pass;
10. a valid multi-step plan executes in dependency order;
11. the hosted production FastAPI entrypoint exposes the mainframe routes before fallback/static mounts;
12. Pass 201 federation and Pass 202 deployment invariants remain intact;
13. no floating-point value becomes canonical identity, equality, admission, proof, or receipt authority.
