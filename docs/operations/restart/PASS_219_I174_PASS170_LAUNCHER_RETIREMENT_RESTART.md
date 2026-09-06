# Pass 219 I174 / Pass170 Launcher Retirement Tranche A — Restart Checkpoint

## Repository authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base authoritative main: `cb39509ec5e16dc884d9556ed65cfc1a40d8c5d8`
- Branch: `agent/pass219-i174-pass170-launcher-retirement`
- Merge target: `main`
- I174 implementation head before this checkpoint: `48b654d9fce1606c7998eb88a4e27fd4a072253e`
- Parent: Pass219 I173 / Pass170 full operation records
- Parent exact-main workflow: `34030977410`
- Parent exact-main artifact: `9988603949`
- Parent artifact digest: `sha256:a96c116ae5c32679f4b2372bf589618417c972a2eb7f58f3cee53e79d39721cb`

## Frozen parent evidence

I173 remains frozen rather than live-replayed across the changed launcher census.

The I174 verifier pins:

- exact I173 main commit;
- exact I173 workflow run;
- exact I173 artifact identity and digest;
- the repository-visible I173 operation-record index;
- aggregate operation-record count `47`.

No I173 operation-record file was modified by I174.

## Implemented I174 source changes

Three legacy `uvicorn.run` self-launch targets now point to the canonical Pass170 public gateway `hhs_backend.public_api_server:app`:

1. `hhs_backend/runtime/runtime_server.py`
2. `hhs_runtime/main.py`
3. `hhs_runtime_api_server_v1.py`

Their legacy FastAPI objects, route functions, and callable exports remain intact for compatibility. I174 changes their network self-launch authority only.

The inherited `hhs_runtime/runtime_ws_server.py` redirect remains canonical.

## Explicitly pending launchers

Two launchers remain nonterminal:

1. `hhs_backend/server.py`
   - remains the canonical production base constructor;
   - its `__main__` self-launch still targets `hhs_backend.server:app`;
   - next repair is a bounded whole-file-safe redirect to the Pass170 gateway.

2. `hhs_runtime_api_server_plus_v1.py`
   - imports the v1 legacy app and adds `/api/audio-language/run`;
   - SHALL NOT be redirected until that route is migrated into canonical composition and receives a governed Pass170 operation identity/record.

## New repository-visible evidence

- `HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I174.json`
- `hhs_runtime/pass219/pass170_launcher_retirement_i174.py`
- `tests/pass219/test_pass219_i174_pass170_launcher_retirement.py`
- `contracts/pass219/PASS_219_I174_PASS170_LAUNCHER_RETIREMENT_1_0.json`
- `.github/workflows/pass219-i174-pass170-launcher-retirement.yml`
- this restart record

## Expected verified census

- observed uvicorn launchers: `6`
- canonical gateway redirects: `4`
- pending launchers: `2`
- FastAPI constructors preserved: `10`
- I173 operation records preserved: `47`

## Expected successful target blockers

- `PASS170_AUDIO_LANGUAGE_ROUTE_MIGRATION_PENDING`
- `PASS170_CANONICAL_BASE_SELF_LAUNCH_PENDING_REDIRECT`
- `PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS`
- `PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN`
- `PASS170_LEGACY_SELF_LAUNCH_BYPASSES_REMAIN`
- `PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING`
- `PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING`

Pass170 remains nonterminal.

## Dependency-scoped validation

Canonical local-equivalent CI commands:

```bash
python -m json.tool HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I174.json >/dev/null
python -m json.tool HHS_PUBLIC_OPERATION_RECORD_INDEX.json >/dev/null
python -m json.tool contracts/pass219/PASS_219_I174_PASS170_LAUNCHER_RETIREMENT_1_0.json >/dev/null
python -m py_compile hhs_backend/runtime/runtime_server.py
python -m py_compile hhs_runtime/main.py
python -m py_compile hhs_runtime_api_server_v1.py
python -m py_compile hhs_runtime/pass219/pass170_launcher_retirement_i174.py
python -m py_compile tests/pass219/test_pass219_i174_pass170_launcher_retirement.py
PYTHONPATH=. python -m pytest -q --tb=short tests/pass219/test_pass219_i174_pass170_launcher_retirement.py
```

Dedicated workflow:

`Pass 219 I174 Pass170 Launcher Retirement`

## Validation state at checkpoint creation

Implementation and repository-visible evidence are complete. Dedicated I174 CI has not yet been claimed green at checkpoint creation.

## Remaining closure sequence

1. Open the I174 PR against exact `main @ cb39509ec5e16dc884d9556ed65cfc1a40d8c5d8`.
2. Run/observe the dedicated I174 workflow on the exact PR head.
3. If it fails, repair only the concrete launcher/verifier mismatch; do not weaken the two pending launcher blockers.
4. Record green workflow run/artifact evidence in this restart record if another checkpoint update is needed.
5. Merge only the exact green I174 head.
6. Verify the dedicated I174 push workflow on merged exact main.
7. Continue with `PASS170_CANONICAL_BASE_LAUNCHER_AND_AUDIO_ROUTE_MIGRATION`.

## Non-authoritative auxiliary refs

Two inert auxiliary refs were accidentally created during branch-existence checks and SHALL NOT be used as restart authority:

- `agent/pass219-i174-pass170-launcher-retirement-proof`
- `agent/pass219-i174-pass170-launcher-retirement-successor`

Both point to the pre-evidence source-edit head and contain no unique work beyond the authoritative I174 branch.

## Restart rule

Resume from repository state, not reconstructed conversation context. Treat the branch above as the sole I174 authority. Preserve all green I169-I173 evidence. Rerun only I174-impacted launcher surfaces and subsequent canonical-base/audio-route migration work.
