# Pass 074 — Unified HHS IDE Workspace and Bidirectional Runtime API

Pass 074 is the first shared workspace product built above the frozen Pass 072 HHS v1.0-alpha platform and the Pass 073 context-independent native-development substrate.

It establishes the common Runtime boundary through which later editors, interpreters, compilers, emulators, testing systems, self-healing loops, human developers, LLM coding agents, CI agents, and external clients must operate.

## Governing architecture

```text
ONE RUNTIME
ONE AUTHORITY CHAIN
ONE PROJECT MODEL
ONE INGRESS CONTRACT
ONE EGRESS CONTRACT
ONE REPOSITORY-NATIVE AGENT EXCHANGE PROTOCOL
MANY CLIENT AND AGENT PROJECTIONS
```

Every request resolves through `HHS_UNIFIED_RUNTIME_REQUEST_V1`; every result exits through `HHS_UNIFIED_RUNTIME_RESPONSE_V1`.

```text
client or agent intent
→ canonical request envelope
→ operation registration
→ authority and lease validation when effectful
→ Pass 072 foundation-alignment gate
→ native project dispatch
→ receipt and chained Runtime event
→ canonical response envelope
→ GUI / CLI / API / agent projection
```

## Product boundary

- One Runtime dispatcher receives every GUI, CLI, API, replay, human-agent, LLM-agent, tool-agent, and CI-agent request.
- Editor buffers remain presentation objects rather than committed source artifacts.
- Product mutations require a role contract, task assignment, capability lease, and admitted alignment decision.
- Foundation-directed mutation is rejected by this product. A Pass 072 change requires a separately classified, justified, minimal, witnessed, reversible alignment patch.
- Console output never replaces an execution receipt.
- Runtime events are chained committed projections.
- Interpreter, compiler, and emulator routes remain typed unavailable reservations for later native products.

## Development-agent networking protocol

Pass 074 adds `HHS_OPEN_ENDED_NATIVE_DEVELOPMENT_PROTOCOL_V1` and executable objects for:

- `HHS_DEVELOPMENT_AGENT_IDENTITY_V1`
- `HHS_REPOSITORY_CHANGE_PROPOSAL_V1`
- `HHS_POST_FREEZE_ALIGNMENT_DECISION_V1`
- `HHS_TEST_EVIDENCE_RECORD_V1`
- `HHS_AGENT_HANDOFF_CAPSULE_V1`
- `HHS_BOUNDED_SELF_HEALING_PLAN_V1`

Agent registration confers no authority. A human, LLM, tool, or CI agent must still use the same role, task, lease, and alignment chain as every other client.

A proposed repository change is admitted to testing only when it declares:

- a reachable native program;
- a reusable capability;
- a new capability statement;
- affected product paths;
- requested tests;
- no unclassified foundation mutation.

This enforces the reciprocal post-freeze constraints:

```text
FOUNDATION CONSERVATION
↔
CAPABILITY-BEARING PRODUCT CLOSURE
```

## Bounded self-healing boundary

Pass 074 can derive a bounded product-local repair plan from failed test evidence. The plan requires reproduction, cause isolation, a minimal reversible patch, test rerun, an iteration receipt, authority revalidation, and rollback support.

It does not automatically apply the repair and cannot target the frozen Pass 072 foundation. Automated repair execution belongs to later passes after the interpreter and test-execution surfaces exist.

## API

- `POST /api/hhs/v1/ingress`
- `POST /api/hhs/v1/execute`
- `POST /api/hhs/v1/mutate`
- `POST /api/hhs/v1/query`
- `POST /api/hhs/v1/compile`
- `POST /api/hhs/v1/emulate`
- `GET /api/hhs/v1/artifacts/{id}`
- `GET /api/hhs/v1/receipts/{id}`
- `GET /api/hhs/v1/state/{id}`
- `WS /api/hhs/v1/events`

## Implemented operations

```text
workspace.project.create
workspace.session.open
workspace.buffer.open
workspace.agent.register
workspace.change.propose
workspace.state.get
workspace.project.index
workspace.buffer.update
workspace.source.commit
workspace.test.record
workspace.handoff.create
workspace.source.inspect
workspace.alignment.evaluate
workspace.healing.plan
```

Reserved operations remain typed unavailable:

```text
workspace.interpreter.execute
workspace.compiler.compile
workspace.emulator.run
```

## Workspace surfaces

```text
WorkspaceShell
ProjectExplorer
EditorPanel
RuntimeConsole
ArtifactPanel
ReceiptPanel
ExecutionPanel
AgentNetworkPanel
AlignmentPanel
IterationPanel
StatusBar
```

Every surface is a projection over Runtime state. No surface owns a private authority or execution path.

## Native program entrypoints

```text
API:    native_projects.hhs_ide_workspace.hhs_unified_runtime_api_v1:app
CLI:    python -m native_projects.hhs_ide_workspace.hhs_workspace_cli_v1
Replay: native_projects.hhs_ide_workspace.hhs_workspace_replay_runner_v1:replay_workspace
GUI:    native_projects/hhs_ide_workspace/workspace_ui/index.html
```

## Open-ended development rule

There is no fixed terminal pass above Pass 072. Development may continue indefinitely through reusable native products while both reciprocal constraints remain satisfied.

```text
PASS_072 = frozen platform foundation
PASS_073 = context-independent native-development proof
PASS_074 = unified workspace, API, agent exchange, and alignment gate
PASS_075 = Harmonicode parser / typed IR / agent-coordinated test acceleration
PASS_076+ = interpreter-driven bounded repair, compiler, emulator, and open-ended products
```

## Frozen-platform result

Pass 074 adds a native product only. It does not modify any Pass 072 foundation file or any Pass 073 parent file.
