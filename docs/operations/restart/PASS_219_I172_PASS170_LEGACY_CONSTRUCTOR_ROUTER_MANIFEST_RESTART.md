# Pass 219 I172 — Pass170 Legacy Constructor / Router Manifest Restart Checkpoint

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `main @ 08bd2db30706a88d3e6ffee2e8c3ff8ca592788c`
- inherited I171 PR: `#400`
- inherited I171 merge: `08bd2db30706a88d3e6ffee2e8c3ff8ca592788c`
- inherited exact-main I171 workflow: `34028582671` — success
- inherited exact-main I171 artifact: `9987853310`
- inherited artifact digest: `sha256:19b4e100055031a1e66b87b92518d099fdcb7ff0ade4c9bdc34379320c4e0b67`
- branch: `agent/pass219-i172-pass170-legacy-constructor-router-manifest`
- merge target: `main`
- implementation head before checkpoint: `568423b14516fd4aeff2bb6e99411ae64e0fd0bf`
- Pass170 contract: `HHS-P170-PAPAE-HLFDCR`

The two commits that advanced main between I170 and the I171 merge changed only `README.md`; no executable Pass170 surface drifted before I171 was merged and exact-main validated.

## I172 purpose

I172 resolves the previous opaque `PASS170_FULL_ROUTER_MANIFEST_PENDING` boundary and turns the raw constructor count into an explicit authority census. It does not hide or waive legacy constructors. Instead it classifies every current FastAPI constructor and every current `uvicorn.run` launcher, repairs one already-delegating websocket compatibility launcher to the canonical Pass170 gateway, and establishes a deterministic ordered public router manifest over the existing cumulative composition.

I172 remains intentionally nonterminal. Full Pass170 operation records, five legacy self-launch targets, several legacy constructors, and the explicit source-only degraded gateway remain repair-forward work.

## Changed files

- `HHS_FASTAPI_CONSTRUCTOR_REGISTRY.json`
- `HHS_PUBLIC_ROUTER_MANIFEST.json`
- `hhs_runtime/runtime_ws_server.py`
- `hhs_runtime/pass219/pass170_legacy_constructor_router_manifest_i172.py`
- `hhs_runtime/pass219/pass170_legacy_constructor_router_manifest_i172_gate.py`
- `tests/pass219/test_pass219_i172_pass170_legacy_constructor_router_manifest.py`
- `contracts/pass219/PASS_219_I172_PASS170_LEGACY_CONSTRUCTOR_ROUTER_MANIFEST_1_0.json`
- `.github/workflows/pass219-i172-pass170-legacy-constructor-router-manifest.yml`
- `docs/operations/restart/PASS_219_I172_PASS170_LEGACY_CONSTRUCTOR_ROUTER_MANIFEST_RESTART.md`

## Frozen inherited evidence

I171 proved on exact merged main:

- one normal production application identity shared by Pass170 and the cumulative RuntimeOS stack;
- 12 direct Pass170 routes;
- 18 Pass168 delegate routes;
- 17 Pass169 delegate routes;
- 35 delegated route identities;
- 47 direct + delegated registered route signatures;
- inherited I170 registry verification green;
- no canonical state mutation from this evidence layer;
- no new VM81, Hash72 mint, Hash216 persistence, or floating-point canonical authority.

The I169 raw scanner still observes 10 FastAPI constructor sites. I172 preserves that evidence exactly rather than changing the scanner or reclassifying its raw blocker.

## Implemented I172 boundary

### Constructor and launcher registry

`HHS_FASTAPI_CONSTRUCTOR_REGISTRY.json` classifies all 10 observed constructor sites and all 6 observed `uvicorn.run` launchers.

Constructor classes distinguish:

- the inherited production-base constructor (`hhs_backend.server.py`);
- the Pass170 isolated test-ephemeral fallback constructor;
- the explicit source-only degraded gateway;
- private development/test/native-program factories;
- legacy servers that still require adapter retirement.

The registry requires exact census equality: any newly added, removed, duplicated, or unclassified constructor/launcher fails I172 evidence.

### WebSocket compatibility repair

`hhs_runtime/runtime_ws_server.py` now imports and launches `hhs_backend.public_api_server:app`, not the pre-Pass170 `hhs_backend.server:app`. It remains a compatibility launcher with no independent public-port authority.

### Full router manifest

`HHS_PUBLIC_ROUTER_MANIFEST.json` freezes nine ordered composition stages:

1. `hhs_backend.server`
2. `hhs_backend.public_api_server`
3. `hhs_backend.production_server`
4. `hhs_backend.production_ide_server`
5. `hhs_backend.pass174_server`
6. `hhs_backend.application_ide_server`
7. Pass201 sorted `hhs_backend.api` package closure
8. `hhs_backend.runtime_os_application_server_full`
9. `hhs_backend.runtime_os_application_server`

The Pass201 stage is accepted only if its source preserves sorted package discovery, missing-signature-only attachment, import-failure closure, and unexposed-route closure. Thus the manifest accounts for the large cumulative router surface without copying hundreds of dynamic route records into a second semantic registry.

## Expected validated classification

`PASS170_CONSTRUCTOR_AUTHORITY_AND_FULL_ROUTER_MANIFEST_VERIFIED_NONTERMINAL`

Expected exact target blockers after successful I172 validation:

```text
PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS
PASS170_FULL_OPERATION_RECORDS_PENDING
PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN
PASS170_LEGACY_SELF_LAUNCH_BYPASSES_REMAIN
```

The prior target blocker `PASS170_FULL_ROUTER_MANIFEST_PENDING` must be absent after successful I172 validation.

Expected next boundary:

`PASS170_LEGACY_LAUNCHER_RETIREMENT_AND_FULL_OPERATION_RECORD_COMPLETION`

## Validation encoded in dedicated CI

```text
python -m json.tool HHS_FASTAPI_CONSTRUCTOR_REGISTRY.json
python -m json.tool HHS_PUBLIC_ROUTER_MANIFEST.json
python -m json.tool contracts/pass219/PASS_219_I172_PASS170_LEGACY_CONSTRUCTOR_ROUTER_MANIFEST_1_0.json
python -m py_compile hhs_runtime/runtime_ws_server.py
python -m py_compile hhs_runtime/pass219/pass170_legacy_constructor_router_manifest_i172.py
python -m py_compile hhs_runtime/pass219/pass170_legacy_constructor_router_manifest_i172_gate.py
python -m py_compile tests/pass219/test_pass219_i172_pass170_legacy_constructor_router_manifest.py
python -m pytest -q --tb=short tests/pass219/test_pass219_i172_pass170_legacy_constructor_router_manifest.py
python -m hhs_runtime.pass219.pass170_public_authority_inventory_i169 . --output artifacts/pass219/i172/i169_authority_inventory.json
```

The dedicated workflow additionally executes the canonical I172 gate and enforces exact constructor, launcher, router-stage, target-blocker, inherited-authority, and next-boundary values.

## Validation state at checkpoint creation

Implementation is repository-visible and restartable. Dedicated I172 CI has not yet been accepted as green in this checkpoint. Do not merge based only on this implementation record.

## Restart instructions

1. Resume from this branch and checkpoint, not reconstructed conversation state.
2. Open or resolve the I172 PR against current `main`.
3. Run/inspect `Pass 219 I172 Pass170 Legacy Constructor Router Manifest`.
4. If it fails, repair only the reported I172 evidence mismatch; do not rerun or rewrite frozen I171 surfaces unless the failure proves them impacted.
5. When the dedicated I172 gate is green, record workflow/artifact evidence in this checkpoint or an immediate successor checkpoint.
6. Merge the exact validated I172 head, then verify the dedicated workflow on exact merged `main`.
7. Do not block on unrelated broad workflow fan-out once the dedicated I172 boundary is green.
8. Continue with `PASS170_LEGACY_LAUNCHER_RETIREMENT_AND_FULL_OPERATION_RECORD_COMPLETION`.
