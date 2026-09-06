# Pass 219 I176 / Pass170 Canonical Base Launcher + Capability Reconciliation — Restart Checkpoint

## Repository authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base authoritative main: `8d9ab8a0ec453b2e3f527c8420542929e29cb9d0`
- Branch: `agent/pass219-i176-pass170-canonical-base-capability-parity`
- Merge target: `main`
- Implementation head before checkpoint: `fe01f8d34afda861c33e4f3fb7aa082fba540536`
- Parent: Pass219 I175 / Pass170 audio route migration + ECC/PQ security role
- Parent exact-main workflow: `34062282668`
- Parent exact-main artifact: `9997852836`
- Parent artifact digest: `sha256:6af6f3cf900f2502f8e531ed2b5cd35fad866dc349c65814b0287195db890476`

## Implemented I176 changes

### 1. Last normal public self-launch bypass removed

`hhs_backend/server.py` preserves its canonical base FastAPI constructor, lifespan, routes, and self-test, but its `__main__` uvicorn target now points to:

`hhs_backend.public_api_server:app`

The source delta is exactly one removed launcher target line and one added target line.

Because the connected GitHub contents API only exposes whole-file replacement for writes and `server.py` is large, the exact one-line edit was applied by a bounded repository-native migration tool through a one-shot GitHub Actions bootstrap. The bootstrap workflow was removed immediately after the source commit and is not present in the final I176 tree.

Retained audit tool:

- `tools/pass219_i176_redirect_canonical_base_launcher.py`

Bootstrap evidence:

- workflow run: `34062501010`
- bootstrap source-edit commit: `99a4d2e2fc6aefc159158564f0d0219fce43dd59`
- result: success

### 2. Successor launcher census

`HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I176.json` freezes the parent I175 exact-main evidence and requires:

- observed launchers: `6`
- canonical gateway launchers: `6`
- pending launchers: `0`
- canonical gateway: `hhs_backend.public_api_server:app`

I176 therefore clears the normal self-launch bypass boundary without deleting legacy compatibility app constructors.

### 3. Capability-model reconciliation

Repository inspection of `Pass190CompletionContext.verify_capability` establishes:

- `public` and `none` scopes require no token;
- all other scopes require a configured capability secret and signed token satisfying the required scope;
- operation capability identity comes from the operation record.

No authoritative inherited audio-specific scope was found for `public.audio_language.feedback.run`. I176 therefore does **not** invent a scope or mutate the frozen Pass190 registry.

`HHS_PUBLIC_CAPABILITY_MODEL_RECONCILIATION_I176.json` records the state as:

`UNRESOLVED_NO_AUTHORITATIVE_INHERITED_AUDIO_SCOPE`

### 4. Public audio admission is now actually fail closed

The I175 operation record remains frozen with pending capability/admission fields.

I176 adds `HHS_PUBLIC_OPERATION_ADMISSION_OVERLAY_I176.json` and modifies `hhs_backend/pass170_audio_language_routes.py` so the public canonical and deprecated alias routes call `enforce_audio_public_admission()` before the internal adapter.

Until a future Pass170 boundary authoritatively binds a capability scope, public transport returns:

- HTTP `503`
- detail `HHS_PASS170_AUDIO_CAPABILITY_MODEL_UNRESOLVED`

This refusal occurs before auxiliary persistence, linguistic training, or audio-language orchestration. The internal/governed adapter remains callable for non-public composition.

### 5. Audio ECC and internal PQ-oriented security role preserved

I176 does not weaken I175's cross-cutting audio role:

- local audio-language application;
- harmonic-time/audio phase ECC witness source;
- redundant internal post-quantum-oriented security enforcement signal.

It creates no public crypto primitive, KEM/key authority, standardized PQ proof, VM81 authority, Hash72 mint authority, or Hash216 persistence authority.

## Final intended I176 tree delta

- `.github/workflows/pass219-i176-pass170-canonical-base-capability.yml`
- `HHS_PUBLIC_CAPABILITY_MODEL_RECONCILIATION_I176.json`
- `HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I176.json`
- `HHS_PUBLIC_OPERATION_ADMISSION_OVERLAY_I176.json`
- `contracts/pass219/PASS_219_I176_PASS170_CANONICAL_BASE_CAPABILITY_1_0.json`
- `hhs_backend/pass170_audio_language_routes.py`
- `hhs_backend/server.py`
- `hhs_runtime/pass219/pass170_canonical_base_capability_i176.py`
- `tests/pass219/test_pass219_i176_pass170_canonical_base_capability.py`
- `tools/pass219_i176_redirect_canonical_base_launcher.py`
- this restart record

## Expected successful verified state

- launchers observed: `6`
- canonical redirects: `6`
- pending launchers: `0`
- all normal public launchers canonical: `true`
- FastAPI constructor census preserved: `10`
- audio capability scope resolved: `false`
- audio public admission fail closed: `true`
- new capability scope created: `false`
- Pass170 terminal: `false`

## Expected target blockers

- `PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS`
- `PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN`
- `PASS170_PUBLIC_AUDIO_CAPABILITY_BINDING_PENDING`
- `PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING`
- `PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING`

Cleared by I176:

- `PASS170_CANONICAL_BASE_SELF_LAUNCH_PENDING_REDIRECT`
- `PASS170_LEGACY_SELF_LAUNCH_BYPASSES_REMAIN`

## Validation

Dedicated workflow:

`Pass 219 I176 Pass170 Canonical Base Capability`

Equivalent bounded commands:

```bash
python -m json.tool HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I176.json >/dev/null
python -m json.tool HHS_PUBLIC_CAPABILITY_MODEL_RECONCILIATION_I176.json >/dev/null
python -m json.tool HHS_PUBLIC_OPERATION_ADMISSION_OVERLAY_I176.json >/dev/null
python -m json.tool contracts/pass219/PASS_219_I176_PASS170_CANONICAL_BASE_CAPABILITY_1_0.json >/dev/null
python -m py_compile hhs_backend/server.py
python -m py_compile hhs_backend/pass170_audio_language_routes.py
python -m py_compile hhs_runtime/pass219/pass170_canonical_base_capability_i176.py
python tools/pass219_i176_redirect_canonical_base_launcher.py
PYTHONPATH=. python -m pytest -q --tb=short tests/pass219/test_pass219_i176_pass170_canonical_base_capability.py
```

## Validation state at checkpoint creation

- exact launcher migration bootstrap: green
- final I176 dependency-scoped workflow: not yet claimed green at checkpoint creation

## Remaining closure sequence

1. Open I176 PR against exact `main @ 8d9ab8a0ec453b2e3f527c8420542929e29cb9d0`.
2. Run the dedicated I176 workflow on exact PR head.
3. Repair only concrete I176 evidence defects; do not invent an audio capability scope or allow pending-policy fallthrough.
4. Seal green run/artifact evidence in this checkpoint if another checkpoint update is needed.
5. Merge only exact green head.
6. Verify signed exact main and dedicated I176 push workflow.
7. Continue with `PASS170_PUBLIC_CAPABILITY_MODEL_EXTENSION_AND_CONSTRUCTOR_RETIREMENT`.

## Restart rule

Resume from repository-visible state. Preserve frozen I169-I175 evidence. Treat I176 as a launcher-closure and capability-reconciliation boundary, not as authorization to create a new capability model without an explicit cumulative Pass170 contract extension.
