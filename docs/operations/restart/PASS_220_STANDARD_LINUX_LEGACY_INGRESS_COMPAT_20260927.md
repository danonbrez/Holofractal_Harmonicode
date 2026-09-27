# Pass 220 standard Linux / legacy ingress compatibility — 2026-09-27

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch base: `a7c0f2363c00b389ae39bd7aeaab504e20729de9`
- Repair branch: `agent/linux-legacy-ingress-compat-20260927`
- Merge target: `main`
- Current main observed during implementation: `fed05231ed773c533c2202641949931216e88b26`
- Scope: make external ingress translate/redirect legacy and ordinary Linux/web data shapes into existing canonical workspace ingress instead of rejecting them merely because their external type label is not an HHS-native modality.

## Governing compatibility rule

External compatibility is additive.

A normal frontend, tool, Linux process, guest, file source, Unix-socket peer, or HTTP client may use its ordinary transport/data type. The compatibility membrane translates the external representation into an already-authorized canonical modality and then submits the existing `ingress.register` workspace operation.

The compatibility layer does not become a second VM81, Hash72, Hash216, receipt, persistence, or runtime authority.

Unknown external data types are not rejected solely for being unknown. They are preserved as reversible binary source data and admitted through the canonical `BINARY` adapter.

The low-level canonical packet validator remains fail-closed if code attempts to construct an undeclared canonical adapter directly. Thus:

```text
external unknown type
    -> explicit compatibility translation
    -> reversible BINARY source
    -> canonical adapter validation

direct undeclared canonical adapter
    -> reject
```

## Implemented compatibility translation

`hhs_backend/runtime/multimodal_workspace_ingress_v1.py` now supplies:

- legacy modality aliases;
- MIME-to-canonical-modality translation;
- filename/profile inference;
- code/source/media/binary/executable mappings;
- explicit `JSON_EXECUTION_GRAPH -> GRAPH_OBJECT` compatibility;
- unknown vendor types -> `BINARY`;
- bytes/bytearray/memoryview -> reversible Base64 source envelope;
- retained original declared type, MIME type, transport encoding, translation reason, and compatibility metadata;
- retained source commitment and adapter validation.

Known Linux/web profiles include ordinary text/code, JSON, YAML, CSV, PDF, image/audio/video, octet-stream, ELF/object/shared-library/executable/WASM-style content, directories, and arbitrary vendor media types.

## Standard HTTP ingress membrane

New module:

`hhs_backend/api/standard_ingress_compat_routes.py`

Canonical compatibility path:

`POST /api/runtime/ingress`

Accepted compatibility aliases:

- `POST /api/runtime/ingress/legacy`
- `POST /api/runtime/ingress/upload`
- `POST /api/ingress`

Status surface:

`GET /api/runtime/ingress/compatibility`

All POST aliases call the same adapter and internally redirect to the already-authorized:

`workspace:ingress.register`

Transport handling:

- valid JSON -> JSON object;
- malformed JSON -> reversible binary fallback rather than 422 solely for parser mismatch;
- text and source code -> text/code adapter;
- URL-encoded form -> JSON object;
- form parse overflow/error -> reversible binary fallback;
- multipart single file -> source file with its filename and MIME type;
- multipart bundles -> bounded directory/bundle representation;
- arbitrary raw/vendor body -> reversible binary source.

The request body remains bounded. Default maximum: 64 MiB. Configurable ceiling: 256 MiB. Oversize data remains a resource-bound rejection, not a type-compatibility rejection.

## Linux backend compatibility binding

The compatibility status is bound to the existing executable Pass 187 Ubuntu/Linux adapters:

- filesystem: `hhs_runtime.pass187.adapters.read_file`
- stdin/stdout process: `hhs_runtime.pass187.adapters.run_process`
- Unix domain socket: `hhs_runtime.pass187.adapters.unix_socket_roundtrip`
- HTTP client: `hhs_runtime.pass187.adapters.http_get`

This preserves the intended normal Linux-distro/VM behavior at the compatibility membrane instead of requiring every external program to understand HHS-native type labels.

## Authority path

```text
standard/legacy frontend or Linux source
    -> HTTP/file/process/socket compatibility boundary
    -> external type translation
    -> WorkspaceAuthorityLoop
    -> ingress.register
    -> canonical multimodal adapter
    -> source commitment / workspace object / receipt
```

No browser or compatibility adapter may directly commit runtime truth.

## Pass 170 / kernel surface closure

Compatibility aliases are explicitly mapped to one canonical operation in:

`contracts/pass220/PASS_220_STANDARD_LEGACY_INGRESS_COMPAT_1_0.json`

The new status and POST alias surfaces are declared in:

`hhs_runtime/hhs_kernel_conformance_surface_map_v1.py`

The aliases declare `workspace.command` and `ingress.register` as their canonical operation path rather than creating private mutation semantics.

## Production configuration

`deploy/digitalocean/hhs-pass196.env.example` now documents:

`HHS_STANDARD_INGRESS_MAX_BYTES`

The previous exact CORS origin compatibility contract remains unchanged.

## Validation

Dependency-scoped workflow:

`.github/workflows/standard-frontend-ingress.yml`

It now compiles the ingress policy, compatibility router, workspace ingress translator, workspace authority loop, kernel surface map, and canonical server and runs:

- `tests/test_hhs_standard_frontend_ingress_v1.py`
- `tests/test_hhs_linux_legacy_ingress_compat_v1.py`

Coverage includes:

1. `JSON_EXECUTION_GRAPH` legacy translation;
2. unknown vendor type reversible binary preservation;
3. Linux/web MIME translation;
4. raw octet/vendor body redirect;
5. malformed JSON fallback;
6. URL-encoded forms;
7. standard browser multipart single-file upload;
8. body-size bounds;
9. Pass 187 Linux adapter bindings;
10. Pass 220 compatibility alias contract;
11. kernel conformance surface registration;
12. preservation of the existing low-level unsupported canonical-adapter rejection witness.

## Current branch commits

- `24eee232985c3a54d99a28e929be631e0d2b5063` — legacy type translation
- `515beefaec3867471e76fb0595fc92b3c3feb01b` — workspace translator routing
- `6607304dbc004fc8dca47456807044daf4002ac7` — HTTP/Linux compatibility router
- `b2f0f61bed8f56783207952f5bdf440cc39c137f` — explicit multipart Base64 decode
- `ace83633b57c7757a0df3feac7128c2e1a673a0c` — canonical FastAPI registration
- `3bd889d9d6f1903e07cac07c310e31a1efafbc8b` — compatibility tests
- `c972b4ed22f37b5a96360c5e0c4fad3a07d5043e` — source provenance retention
- `752b705efb3f84eb4083d519aa4806a062b95554` — dependency-scoped CI
- `9dd307fe7d1fc7deca9407db056bf776e42840b5` — preserve low-level fail-closed witness
- `a9d1302d5c548214966f4cf17b3d87e1bd32aafc` — production ingress size documentation
- `ba3673118c570b7bf3f81e95ae6315aea46f7927` — executable Linux adapter binding
- `60b425f9b7f9b76006f94a4542c8d7ad38d46481` — Linux binding tests
- `18a478610f538ca3967ad49cced746ef137766a0` — kernel conformance alias surfaces
- `031300662fba5939563c9001d28d3934f57451b7` — Pass 220 compatibility contract
- `00ac5cc3426607cc2294a14569b81b02600a897a` — canonical alias mapping tests
- `66ebbeaecc94498142cdffae38257c680ee5ccff` — conformance CI scope
- `2b682296786246eba1a79ac662172aeadd38d741` — compatibility metadata provenance
- `27d878f280964ec4a568c6410885a5f78df21986` — authority-loop transport evidence
- `2ab03fd218d25258a4c2c304182ebcb742662d07` — parser fallback evidence test
- `58ae25dec080e06c25055fcef47620a89d948280` — bounded form parsing fallback

## Remaining closure

1. Open PR against current main and allow GitHub to integrate unrelated main drift.
2. Run the dependency-scoped ingress gate.
3. Repair forward any concrete compile/test/conformance failure.
4. Merge without waiting on unrelated queued CI once the branch is restartable and mergeable.
5. Verify exact main.
6. Verify production after exact-main deployment:
   - Runtime OS still receives canonical live projections;
   - Visual Program graph witness no longer rejects `JSON_EXECUTION_GRAPH`;
   - raw/text/JSON/form/multipart compatibility ingress succeeds;
   - unknown vendor media is preserved as reversible binary;
   - standard Linux adapters remain callable;
   - frontend remains request/projection only.
