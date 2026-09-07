# Pass 219 I180 — Pass170 Legacy Route Migration Restart

## Repository authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ 8b02d3a26eee0a9161939f78b19804b6fb2b7065`
- Branch: `agent/pass219-i180-pass170-legacy-route-migration`
- Merge target: `main`
- PR: `#409`
- Contract: `HHS-P170-PAPAE-HLFDCR`
- Iteration: `PASS219-I180`

## Frozen parent evidence

Pass219 I179 is exact-main closed at `8b02d3a26eee0a9161939f78b19804b6fb2b7065`.

- Dedicated exact-main run: `34077531408`
- Artifact: `10002586241`
- Artifact digest: `sha256:daecc1c3a6bbeaa431f03f2cd900460853fe643662b56ff5131952d79f460b7f`
- Native audio ABI, harmonic-time/audio ECC security binding, and non-reexecuting receipt replay are frozen inherited evidence.

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

No legacy constructor source file is modified in I180. Constructor retirement is intentionally deferred until migrated-route evidence is green.

## Validated branch evidence

First run `34078521139` failed during test collection because the preserved legacy runtime transitively imports the inherited Pass213 PQC enclosure and the bounded workflow had not installed its `cryptography` dependency. No I180 route assertion executed in that failed run.

The workflow dependency was repaired without changing route/capability/authority semantics.

Green executable head: `eb440f9d27693c70c702a3b1ea106b48f324f64b`

Dedicated I180 run: `34078617971` — **success**

Successful stages:

- bounded dependency install including inherited `cryptography` dependency
- JSON parsing and Python compilation
- seven dependency-scoped I180 tests
- independent repository migration verifier
- exact nonterminal-boundary enforcement
- evidence upload

Artifact: `10002933695`

Artifact digest: `sha256:c349f1ba854ffe62733d34d074410fb745fdbb5cb08fdcc0784a38144f92a310`

Validated state:

- 11 exact migrated HTTP signatures
- 4 canonical websocket replacements
- 0 websocket routes added by the I180 adapter
- 48 frozen parent operation records + 11 I180 records = 59 aggregate public operation records
- FastAPI constructor census remains 8
- Pass201 federation remains sorted and missing-signatures-only
- `pass170.runtime.execute`, `pass170.runtime.event.inject`, and `pass170.runtime.certification` reuse Pass190 signed-token authority
- no new VM81 authority
- no new Hash72 mint authority
- no Hash216 persistence authority
- no floating-point canonical authority

## Expected nonterminal blockers

- `PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS`
- `PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN`
- `PASS170_REMAINING_PUBLIC_OPERATION_TRANSPORT_PARITY_PENDING`
- `PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF_PENDING`

## Exact restart action

1. Require the checkpoint-only I180 workflow on the current branch head to remain green.
2. Merge PR `#409` with exact-head protection.
3. Verify signed `main` contains I180.
4. Require the push-triggered exact-main I180 workflow and artifact to be green.
5. Begin `PASS170_LEGACY_CONSTRUCTOR_RETIREMENT_AND_REMAINING_TRANSPORT_PARITY` from that verified main commit.

## Safety / authority boundary

The migrated legacy HTTP operations remain compatibility surfaces. Local/legacy Hash72-like receipt strings are projections unless an inherited canonical authority explicitly proves otherwise. I180 does not grant those paths independent VM81 commit, Hash72 mint, Hash216 persistence, capability-token issuance, or public cryptographic authority.
