# Pass 219 I181 — Pass170 Legacy Constructor Retirement Restart

## Repository authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ 2e8bfa52ede8af64bd4c39cc9e6318f40f6844bf`
- Branch: `agent/pass219-i181-pass170-legacy-constructor-retirement`
- Merge target: `main`
- Contract: `HHS-P170-PAPAE-HLFDCR`
- Iteration: `PASS219-I181`

## Frozen parent evidence

Pass219 I180 is exact-main closed at `2e8bfa52ede8af64bd4c39cc9e6318f40f6844bf`.

- Dedicated exact-main run: `34078826576`
- Artifact: `10002996393`
- Artifact digest: `sha256:69d16fd63ab9b763998541e11ef28a725ed09ee4a74e8ae36108948b1a08a7e8`
- I180 migrated 11 legacy-compatible HTTP operations into governed Pass170 adapters and proved 4 websocket identities already have canonical replacements.

Do not rerun I180 as if it still owned an 8-constructor census; I181 intentionally changes that inherited topology.

## I181 bounded scope

I181 retires exactly two independent FastAPI constructors whose route migration was completed in I180:

1. `hhs_backend/runtime/runtime_server.py`
2. `hhs_runtime_api_server_v1.py`

The two modules retain their request models, execution/helper functions, HTTP handler callables, and historical router shapes through non-deployment `APIRouter` objects. They no longer construct a FastAPI application or register public middleware/listener authority.

Legacy `module:app` access is preserved through module-level lazy `__getattr__` resolution to the exact canonical target `hhs_backend.public_api_server:app`. Direct execution also targets that canonical gateway.

The explicit source-only degraded gateway is not modified in I181 and remains a separate fail-closed reconciliation boundary.

## Changed files

1. `hhs_backend/runtime/runtime_server.py`
2. `hhs_runtime_api_server_v1.py`
3. `HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I181.json`
4. `hhs_runtime/pass219/pass170_legacy_constructor_retirement_i181.py`
5. `tests/pass219/test_pass219_i181_pass170_legacy_constructor_retirement.py`
6. `contracts/pass219/PASS_219_I181_PASS170_LEGACY_CONSTRUCTOR_RETIREMENT_1_0.json`
7. `.github/workflows/pass219-i181-pass170-legacy-constructor-retirement.yml`
8. this restart record

## Target evidence

- FastAPI constructor census: `8 -> 6`
- Newly retired constructors: `2`
- Cumulative retired constructors: `4`
- I180 migrated HTTP parity preserved: `11`
- canonical websocket replacements preserved: `4`
- both legacy `app` attributes resolve to exact `hhs_backend.public_api_server:app`
- no new capability-token authority
- no new VM81 authority
- no new Hash72 mint authority
- no Hash216 persistence authority
- no floating-point canonical authority

## Validation

Dedicated workflow:

`Pass 219 I181 Pass170 Legacy Constructor Retirement`

It performs JSON parse, Python compile, dependency-scoped tests, repository census/verifier execution, exact bounded blocker enforcement, and artifact upload.

Remote I181 CI has not yet been executed for this checkpoint. Do not claim I181 green, merged, or exact-main closed until that dedicated workflow succeeds and merge/main verification is complete.

## Expected nonterminal blockers after I181 success

- `PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS`
- `PASS170_REMAINING_PUBLIC_OPERATION_TRANSPORT_PARITY_PENDING`
- `PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF_PENDING`

`PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN` must be cleared by I181.

## Exact restart action

1. Open/locate the I181 PR for this branch.
2. Observe the dedicated I181 workflow on the exact branch head.
3. Repair only concrete I181 defects; do not reconstruct or rerun frozen I180 topology assertions.
4. Once green, record exact run/artifact/digest in this restart record if another checkpoint commit is needed.
5. Merge with exact-head protection, verify signed `main`, and verify the push-triggered exact-main I181 workflow/artifact.
6. Begin `PASS170_REMAINING_PUBLIC_OPERATION_TRANSPORT_PARITY_AND_DEGRADED_GATEWAY_RECONCILIATION` from verified I181 main.
