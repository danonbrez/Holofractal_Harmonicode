# HHS Pass 203 — Universal Hydrated Function Mainframe and High-Fidelity Native Creative Runtime

## Normative metadata

| Field | Value |
|---|---|
| Primary contract | `HHS-P203-UNIVERSAL-HYDRATED-FUNCTION-MAINFRAME-VM81-H72-H216` |
| Primary classification | `HHS_PASS_203_UNIVERSAL_HYDRATED_FUNCTION_MAINFRAME_VERIFIED` |
| Native render subauthority | `HHS-P203-HIGH-FIDELITY-NATIVE-RENDER-PARAMETER-AUTHORITY-VM81-H72-H216` |
| Native render classification | `HHS_PASS_203_HIGH_FIDELITY_NATIVE_RENDER_SUBAUTHORITY_VERIFIED` |
| Pass | 203 |
| Parent version | Pass 202 guarded continuous integration and DigitalOcean deployment |
| Mainframe prefix | `/api/runtime/mainframe` |
| Storybook/game prefix | `/api/runtime/storybook-reel` |

## Cumulative version rule

Pass 203 is a version upgrade of the complete HHS system. It inherits every prior pass, contract, service, route, compiler, interpreter, ABI, runtime, workspace, job, artifact, graphics, creative, deployment, receipt, and validation layer. It is not a feature fork and does not create an alternative runtime authority.

A higher pass archive represents the complete integrated system through that version. New functionality must attach to inherited modules and authority chains. Prior functions do not become optional plugins merely because a later pass adds a new surface.

## Purpose

Pass 201 made every registered HTTP router publicly discoverable. Pass 203 extends that closure to the internal hydrated function system so an autonomous agent can use the HHS IDE as a governed cloud-computing mainframe for complex task management, exact logic, software development, artifact production, and creative workflows.

The integrated inventory combines:

1. Pass 190 governed operations;
2. exact interpreter adapters;
3. compiler and proof-carrying artifact adapters;
4. public runtime Python functions;
5. native C ABI symbols;
6. workspace, artifact, job, scheduler, and provider operations;
7. media, game, graphics, document, vector, database, and multimodal functions;
8. bounded multi-step execution plans;
9. receipt replay and runtime status;
10. the complete native storybook/game renderer, shader, sprite-map, texture, palette, typography, composition, codec, and output parameter authority.

## Function states

Every discovered function has a stable identity and one execution state:

- `PASS190_GOVERNED`: implemented by the inherited governed operation fabric;
- `GOVERNED_ADAPTER`: explicitly connected to an authoritative runtime adapter;
- `ISOLATED_PYTHON`: bounded public top-level function executed in an isolated worker;
- `ABI_BINDING_REQUIRED`: native symbol is inventoried but lacks a governed callable binding;
- `ADAPTER_REQUIRED`: Python function is inventoried but requires an explicit authority adapter;
- `WORKSPACE_JOB_ADAPTER_REQUIRED`: mutating or long-running function must execute through workspace/job authority;
- `FORBIDDEN`: function conflicts with the public execution safety boundary.

A function is `hydrated` only when it has an executable governed binding. Every hydrated entry must be callable through the public mainframe. The public catalog retains unbound declarations so missing hydration is measurable and repairable rather than hidden or falsely reported as executable.

## Mainframe public API

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

## High-fidelity native creative API

- `GET /api/runtime/storybook-reel/status`
- `GET /api/runtime/storybook-reel/parameters`
- `GET /api/runtime/storybook-reel/presets`
- `POST /api/runtime/storybook-reel/resolve`
- `POST /api/runtime/storybook-reel/defaults`
- `POST /api/runtime/storybook-reel/audio`
- `POST /api/runtime/storybook-reel/generate`
- `GET /api/runtime/storybook-reel/artifacts/{artifact_id}`
- `GET /api/runtime/storybook-reel/artifacts/{artifact_id}/video.mp4`
- `GET /api/runtime/storybook-reel/artifacts/{artifact_id}/download.zip`

## Interpreter and compiler authority

The exact interpreter remains restricted to the registered exact integer/rational expression grammar. Host-language imports, evaluation, file access, and side effects are rejected with witnessed results.

The compiler may create proof-carrying artifacts, IR, and provenance. Compilation does not automatically authorize execution, active admission, or permanent constraint promotion. Those transitions remain governed by the inherited admission passes.

## Native ABI authority

All discovered `hhs_*` C symbols are publicly indexed with their header, return type, and parameter declaration. A native symbol becomes remotely callable only when it is bound to a governed operation or explicit adapter. The API does not expose arbitrary dynamic-library symbol calls.

The storybook/game projection ABI preserves the inherited VM81 game state byte-for-byte while allowing the caller to select the five governed texture layers and five sprite-overlay layers. Native source discovery accepts the canonical sibling layout, a project-vendored game tree, or direct vendored source files without manual Makefile surgery.

## High-fidelity rendering authority

The authoritative VM81 frame remains an exact `160×144` RGBA source projection. That logical resolution is not the output quality ceiling. Pass 203 adds a high-resolution compositor that preserves the native frame, Hash72/Hash216 frame chains, program replay, opcode coverage, and receipts while delivering configurable portrait masters.

Public production profiles include:

- `production_vertical_1080` — 1080×1920;
- `production_vertical_1440` — 1440×2560;
- `production_vertical_2160` — 2160×3840;
- `native_integer_1080` — intentional crisp integer scaling;
- `native_lossless_rgba` — exact raw RGBA source stream.

The parameter catalog publishes:

- every mutable Storybook Style V2 typography and motion field;
- every reciprocal x/y/z/w palette component;
- all five texture-layer bits;
- all five sprite-overlay bits;
- output dimensions and foreground dimensions;
- fit mode and scaling filter;
- background derivation, blur, and color;
- contrast, saturation, brightness, gamma, sharpening, and vignette;
- codec, encoder preset, CRF, pixel format, audio bitrate, and MP4 flags;
- authority-locked timing and identity fields;
- compiled native constants as public read-only records with source locations.

Compiled constants are disclosed but are not falsely described as runtime mutable. A later contract may hydrate selected constants into a new native parameter ABI while preserving exact validation.

## Agentic plan authority

An assistant or agent may submit a typed dependency graph. The runtime validates function identities, dependency closure, cycles, schemas, capabilities, and execution modes before execution. Generation of a plan does not grant mutation authority. Each admitted step executes through its native operation or adapter and emits its own receipt; the final plan result includes the terminal VM81 receipt.

A complete creative workflow may therefore use one plan to interpret constraints, compile source, select a ranked visual direction, resolve every render parameter, submit a serialized creative job, store artifacts, and replay the final receipt lineage.

## Safety and honesty

The mainframe prohibits:

- raw Python `eval` or `exec`;
- arbitrary module import requested by a client;
- unrestricted shell or subprocess commands;
- arbitrary native symbol invocation;
- frontend-manufactured VM81 receipts;
- bypass of capability, workspace, compiler, canary, active, or rollback authority;
- fabricated success for unhydrated functions;
- fabricated media success when required transport tools are unavailable;
- treating demo defaults or the 160×144 logical frame as the only available visual quality.

Rejections include a stable schema, retryability, and remediation instruction.

## Acceptance requirements

Pass 203 closes only when validation proves:

1. Pass 190 operations, Python functions, native ABI symbols, and explicit adapters are indexed;
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
12. the storybook Makefile resolves supported source layouts without manual path editing;
13. the native projection bridge preserves state and produces distinct full/reduced layer identities;
14. every mutable renderer field and every native layer bit is publicly enumerated;
15. compiled shader constants are publicly inventoried as read-only records;
16. 1080p, 1440p, and 2160p production parameter resolution passes;
17. cinematic compositor graphs use configurable high-quality filters rather than the former fixed nearest-neighbor black-pad path;
18. the public studio exposes quality, composition, grade, codec, and native-layer controls;
19. Pass 201 federation and Pass 202 deployment invariants remain intact;
20. no floating-point value becomes canonical identity, equality, admission, proof, or receipt authority.
