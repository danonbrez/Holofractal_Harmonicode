# Pass 219 I177 / Pass170 Capability Extension + Constructor Retirement — Restart Checkpoint

## Repository authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base authoritative main: `0707cedbbe41cae8478b498f60db56117da5c462`
- Branch: `agent/pass219-i177-pass170-capability-extension-constructor-retirement`
- Merge target: `main`
- Implementation head before this checkpoint: `9a74ebfbe642da866b80557a703bcc7f3e287ba1`
- Parent: Pass219 I176 / Pass170 canonical-base launcher + fail-closed capability reconciliation

## Frozen parent evidence

I176 is exact-main closed and is not replayed against I177 successor state:

- exact main: `0707cedbbe41cae8478b498f60db56117da5c462`
- workflow: `Pass 219 I176 Pass170 Canonical Base Capability`
- exact-main run: `34065089119`
- artifact: `9998685624`
- digest: `sha256:01ac05b0614a2ac68f0d8506bc1439a7f6aaf5a54f61ad007e30a1b3ecd78e1e`
- all I176 dedicated stages: success

## Implemented I177 changes

1. Explicit Pass170 audio capability extension
   - scope: `pass170.audio_language.feedback`
   - operation: `public.audio_language.feedback.run`
   - authorization scheme: `HHS-Capability`
   - token schema: inherited `HHS_PASS_190_CAPABILITY_V1`
   - verifier: inherited `hhs_runtime.pass190.completion.verify_capability_token`
   - secret: inherited `HHS_PASS190_CAPABILITY_SECRET`
   - no new token issuer, signature algorithm, or Pass190 registry mutation.

2. Public audio admission
   - anonymous requests reject before the auxiliary orchestrator executes;
   - malformed/invalid capability rejects;
   - valid token without the Pass170 audio scope rejects;
   - valid inherited signed token carrying the exact scope admits;
   - deprecated `/api/audio-language/run` alias requires the same scope;
   - internal/governed adapter remains callable independently of public HTTP admission.

3. Audio ECC / post-quantum-oriented security boundary
   - harmonic-time/audio ECC remains an inherited internal constraint;
   - the post-quantum-oriented audio security role remains an internal redundant enforcement signal;
   - neither role is exposed by the new public application capability;
   - no public crypto primitive, standardized PQ cryptography claim, key/KEM authority, VM81 authority, Hash72 mint authority, or Hash216 canonical persistence authority is created.

4. Constructor retirement tranche A
   - `hhs_backend/heroku_server.py` no longer constructs `FastAPI`;
   - residual `hhs_backend.heroku_server:app` imports resolve to `hhs_backend.public_api_server:app`;
   - expected constructor census moves from `10` to `9`;
   - all six I176 uvicorn launchers remain canonical.

5. Successor operation evidence
   - frozen I175 aggregate operation identity count remains `48`;
   - I177 replaces only the authority metadata for `public.audio_language.feedback.run`;
   - successor aggregate remains `48` with no new operation ID.

## Changed files

- `hhs_backend/pass170_audio_language_routes.py`
- `hhs_backend/heroku_server.py`
- `HHS_PUBLIC_CAPABILITY_SCOPE_REGISTRY_I177.json`
- `HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I177.json`
- `HHS_PUBLIC_OPERATION_RECORD_INDEX_I177.json`
- `contracts/pass219/pass170_operation_records_i177/HHS_PUBLIC_OPERATION_RECORDS_AUDIO_LANGUAGE_CAPABILITY_V1.json`
- `contracts/pass219/PASS_219_I177_PASS170_CAPABILITY_EXTENSION_CONSTRUCTOR_1_0.json`
- `hhs_runtime/pass219/pass170_capability_extension_constructor_i177.py`
- `tests/pass219/test_pass219_i177_pass170_capability_extension_constructor.py`
- `.github/workflows/pass219-i177-pass170-capability-extension-constructor.yml`
- this restart record

## Dependency-scoped validation

Dedicated workflow:

`Pass 219 I177 Pass170 Capability Extension Constructor Retirement`

Equivalent bounded validation:

```bash
python -m pip install pytest fastapi httpx
python -m json.tool HHS_PUBLIC_CAPABILITY_SCOPE_REGISTRY_I177.json >/dev/null
python -m json.tool HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I177.json >/dev/null
python -m json.tool HHS_PUBLIC_OPERATION_RECORD_INDEX_I177.json >/dev/null
python -m json.tool contracts/pass219/pass170_operation_records_i177/HHS_PUBLIC_OPERATION_RECORDS_AUDIO_LANGUAGE_CAPABILITY_V1.json >/dev/null
python -m json.tool contracts/pass219/PASS_219_I177_PASS170_CAPABILITY_EXTENSION_CONSTRUCTOR_1_0.json >/dev/null
python -m py_compile hhs_backend/pass170_audio_language_routes.py
python -m py_compile hhs_backend/heroku_server.py
python -m py_compile hhs_runtime/pass219/pass170_capability_extension_constructor_i177.py
PYTHONPATH=. python -m pytest -q --tb=short tests/pass219/test_pass219_i177_pass170_capability_extension_constructor.py
```

## Expected successor evidence

- I176 exact-main inherited: true
- operation count: `48`
- audio capability scope: `pass170.audio_language.feedback`
- signed public admission: verified
- inherited Pass190 token verifier reused: true
- new token authority: false
- parent FastAPI constructor count: `10`
- successor FastAPI constructor count: `9`
- retired constructor: `hhs_backend/heroku_server.py`
- uvicorn launchers: `6`
- canonical launcher targets: `6`
- public audio capability binding pending blocker: removed
- Pass170 terminal: false

## Remaining target blockers

- `PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS`
- `PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN`
- `PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING`
- `PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING`

## Validation state at checkpoint creation

Implementation, contract, tests, verifier, dedicated workflow, and restartable evidence are committed. Dedicated I177 PR validation has not yet been claimed green at checkpoint creation.

## Remaining closure sequence

1. Open I177 PR against exact `main @ 0707cedbbe41cae8478b498f60db56117da5c462`.
2. Run the dedicated I177 workflow on the exact PR head.
3. Repair only concrete I177 defects; do not weaken signed capability admission, internal audio ECC/PQ separation, constructor-count reduction, or remaining Pass170 blockers.
4. Merge only a dedicated green exact head.
5. Verify dedicated I177 push workflow on merged exact main and seal its artifact identity.
6. Continue `PASS170_CONSTRUCTOR_RETIREMENT_TRANCHE_B_AND_PUBLIC_TRANSPORT_PARITY`.

## Restart rule

Resume from repository-visible state, not conversational reconstruction. Preserve exact-main I176 evidence and historical I169-I175 receipts. The new Pass170 audio scope authorizes only the local audio-language application operation; it does not authorize, expose, or supersede the internal harmonic-time/audio error-correction or post-quantum-oriented security enforcement roles.
