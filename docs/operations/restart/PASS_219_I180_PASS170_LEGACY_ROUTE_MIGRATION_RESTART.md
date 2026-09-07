# Pass 219 I180 — Pass170 Legacy Route Migration Restart

## Repository authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ 8b02d3a26eee0a9161939f78b19804b6fb2b7065`
- Branch: `agent/pass219-i180-pass170-legacy-route-migration`
- Merge target: `main`
- Contract: `HHS-P170-PAPAE-HLFDCR`
- Iteration: `PASS219-I180`

## Frozen parent evidence

Pass219 I179 is exact-main closed at `8b02d3a26eee0a9161939f78b19804b6fb2b7065`.

- Dedicated exact-main run: `34077531408`
- Artifact: `10002586241`
- Artifact digest: `sha256:daecc1c3a6bbeaa431f03f2cd900460853fe643662b56ff5131952d79f460b7f`
- Native audio ABI, harmonic-time/audio ECC security binding, and non-reexecuting receipt replay are frozen inherited evidence and must not be replayed merely to validate I180.

## I180 bounded scope

I180 migrates the two normal legacy route-bearing public application surfaces into canonical Pass170 federation before constructor retirement:

- `hhs_backend/runtime/runtime_server.py`
- `hhs_runtime_api_server_v1.py`

The migration registers eleven HTTP routes through `hhs_backend.pass170_legacy_runtime_routes` and the sorted Pass201 `hhs_backend.api` federation. Four legacy v1 websocket paths are not duplicated because exact canonical replacements already exist in `hhs_backend.runtime.runtime_ws` through the production base.

Sensitive migrated HTTP routes are fail-closed behind new Pass170-owned scopes while reusing the inherited Pass190 `HHS-Capability` token verifier and secret. No new token issuer or signature algorithm is introduced.

## Current changed files

1. `hhs_backend/pass170_legacy_runtime_routes.py`
2. `hhs_backend/api/pass170_legacy_runtime_routes.py`
3. `HHS_PUBLIC_CAPABILITY_SCOPE_REGISTRY_I180.json`
4. `HHS_PUBLIC_LEGACY_ROUTE_MIGRATION_I180.json`
5. `contracts/pass219/pass170_operation_records_i180/HHS_PUBLIC_OPERATION_RECORDS_LEGACY_RUNTIME_MIGRATION_V1.json`
6. `HHS_PUBLIC_OPERATION_RECORD_INDEX_I180.json`
7. `hhs_runtime/pass219/pass170_legacy_route_migration_i180.py`
8. `tests/pass219/test_pass219_i180_pass170_legacy_route_migration.py`
9. `contracts/pass219/PASS_219_I180_PASS170_LEGACY_ROUTE_MIGRATION_1_0.json`
10. `.github/workflows/pass219-i180-pass170-legacy-route-migration.yml`
11. this restart record

No legacy constructor source file is modified in I180. Constructor retirement is intentionally deferred until the migrated route evidence is green.

## Target evidence

- 11 exact migrated HTTP signatures
- 4 canonical websocket replacements
- 0 websocket routes added by the I180 adapter
- 48 frozen parent operation records + 11 I180 records = 59 aggregate public operation records
- FastAPI constructor census remains 8
- Pass201 federation retains sorted, missing-signatures-only attachment
- `pass170.runtime.execute`, `pass170.runtime.event.inject`, and `pass170.runtime.certification` reuse Pass190 signed-token authority
- no new VM81 authority
- no new Hash72 mint authority
- no Hash216 persistence authority
- no floating-point canonical authority

## Validation commands

Dedicated workflow performs:

```text
python -m py_compile hhs_backend/pass170_legacy_runtime_routes.py hhs_backend/api/pass170_legacy_runtime_routes.py hhs_runtime/pass219/pass170_legacy_route_migration_i180.py tests/pass219/test_pass219_i180_pass170_legacy_route_migration.py
python -m pytest -q tests/pass219/test_pass219_i180_pass170_legacy_route_migration.py
python -c 'from hhs_runtime.pass219.pass170_legacy_route_migration_i180 import verify_i180_legacy_route_migration; verify_i180_legacy_route_migration(".")'
```

Remote dedicated I180 CI has not yet been executed for the current checkpoint. Do not claim I180 green until that workflow succeeds.

## Expected nonterminal blockers after I180 success

- `PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS`
- `PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN`
- `PASS170_REMAINING_PUBLIC_OPERATION_TRANSPORT_PARITY_PENDING`
- `PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF_PENDING`

## Exact restart action

1. Open/locate the I180 PR for this branch.
2. Run/observe `Pass 219 I180 Pass170 Legacy Route Migration` on the exact branch head.
3. If it fails, repair only the concrete I180 defect and preserve parent evidence.
4. Once green, record the exact run/artifact/digest, merge with exact-head protection, verify signed `main`, and verify the push-triggered exact-main I180 workflow/artifact.
5. Begin `PASS170_LEGACY_CONSTRUCTOR_RETIREMENT_AND_REMAINING_TRANSPORT_PARITY` from the verified I180 main commit.

## Safety / authority boundary

The migrated legacy HTTP operations remain compatibility surfaces. Local/legacy Hash72-like receipt strings are projections unless an inherited canonical authority explicitly proves otherwise. I180 does not grant those paths independent VM81 commit, Hash72 mint, Hash216 persistence, capability-token issuance, or public cryptographic authority.
