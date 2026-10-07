# Production Backend Compile Closure Restart Checkpoint — 2026-10-07

## Restart identity

- Canonical base `main`: `c65b205736ba66f477da839103df0186eaf67099`
- Repair branch: `repair/production-backend-compile-closure-20261007`
- Pull request: #733 — `Require production backend compile and assistant closure before deployment`
- Pre-checkpoint repair head: `1ddc0873bf2e0c60cbc4797b03094515321eb8fe`
- Merge target: `main`
- State: **NOT MERGED; production acceptance NOT CLOSED**

This record is the restart authority for the deployment/backend-closure repair. Resume from the branch head produced by this checkpoint commit, not from an older working SHA.

## Triggering production failure

Current canonical main `c65b205736ba66f477da839103df0186eaf67099` was promoted successfully by Exact-Main run `37563908027` before final browser acceptance failed.

Promotion evidence from that run:

- guarded updater receipt: `PROMOTED`
- candidate SHA = Runtime OS bundle SHA = `c65b205736ba66f477da839103df0186eaf67099`
- local Runtime OS service registry: 380 services
- public Runtime OS service registry: 380 services
- production backend service was active
- Lane 5 ingress was active
- public HTTPS Runtime OS was reachable

Final failure remained the live Chromium assistant path:

- `page.waitForResponse: Timeout 180000ms exceeded`
- first POST to `/api/assistant/chat` did not complete in time

This motivated explicit backend compilation and two-turn assistant closure gates before browser acceptance.

## Repairs implemented on PR #733

### Native LiteRT C/C++ compile repair

1. `native_projects/hhs_pass220_litert_native_model_runtime/include/hhs_pass220_litert_native_model_runtime_v1.hpp`
   - restored backing members:
     - `HHSLiteRTNativeStatusV1 status_`
     - `HHSLiteRTNativeModelRegistrationV1 record_`

2. `native_projects/hhs_pass220_litert_native_model_runtime/tests/hhs_pass220_litert_native_model_runtime_v1_cpp_test.cpp`
   - added `<cstdint>` for `std::uint32_t` / `std::uint8_t`

### Production backend closure gates

3. `scripts/production-backend-closure-verify.py`
   - exercises the real production assistant FastAPI router
   - uses `ProductionAssistantService`
   - forces repository-native provider mode
   - verifies two-turn exact-token memory
   - verifies one thread across both turns
   - rejects optional Pass153 fallback use on the native-first path
   - bounded by workflow timeout
   - current head `1ddc087...` bootstraps repository root into `sys.path` so direct script execution can import `hhs_backend`

4. `scripts/production-assistant-http-verify.py`
   - bounded deployed HTTP two-turn assistant probe
   - verifies exact token recall and thread continuity

5. `.github/workflows/digitalocean-production-main.yml`
   - adds `validate-production-backend-closure` before `deploy-exact-main`
   - requires:
     - Python `compileall` across `hhs_backend` and `hhs_runtime`
     - native LiteRT C/C++ registry build and execution
     - production assistant route/service imports
     - two-turn backend closure
     - dependency-scoped assistant/native regressions
   - production deployment now also probes after promotion:
     - backend directly at `127.0.0.1:8080`
     - Lane 5 at `127.0.0.1:8715`
   - both probes execute before Chromium
   - failures emit bounded service/journal diagnostics

### Native test-harness alignment

6. `tests/pass220/test_hhs_pass220_litert_native_model_runtime_v1.py`
   - no longer compiles cumulative `hhs_runtime_exact_abi.c` incorrectly as a one-file shared library
   - uses canonical production `make c-abi`, which supplies inherited Hash216/Pass159/Pass169/link dependencies
   - requirements assertion now checks active dependency lines, not comments

7. `tests/test_hhs_litert_lm_repo_bootstrap_v1.py`
   - requirements assertion now ignores comment-only install examples

## Commit chain before checkpoint

- `3eff3cffcee63c6d5d0a2149691a435a8a27978f` — restore C++ native registration storage
- `853efee3e89a6be192c942beebbb2632fca71a09` — include fixed-width C++ integer types
- `5c0cd485446573807f3f4e833f2e4eb42550b761` — add backend assistant closure verifier
- `fe5f7bf76a97954b0e7c62ee8369be12e6727911` — add deployed assistant HTTP verifier
- `27895de0897eb711aee284a14ecec436a18e78cf` — require backend compile/chat closure in Exact-Main
- `b28ddd8691b44b0864aa56ccddadd1a283f33b2d` — use canonical production c-abi build path in LiteRT tests
- `6c840b6df165aa5bf94bb97e48a059324b8d24c2` — ignore commented compatibility-install example in dependency tests
- `1ddc0873bf2e0c60cbc4797b03094515321eb8fe` — bootstrap repository root in backend closure verifier

## Validation completed

### Native LiteRT workflow

PR workflow run `37613044642` / job `112764676719`:

- dependency install: PASS
- native LiteRT C registry compile/run: PASS
- native LiteRT C++ registry compile/run: PASS
- native/RNA dependency inversion tests: PASS
- launcher syntax validation: PASS
- workflow conclusion: **SUCCESS**

This confirms the original native C/C++ compile defect is repaired at `6c840b6...` and inherited by `1ddc087...`.

### Exact-Main PR validation

PR Exact-Main run `37613044595`:

- `validate-deployment-contract` job `112764677240`: **SUCCESS**
- `validate-production-backend-closure` job `112764677677`: **FAILURE**
- `deploy-exact-main`: correctly skipped because closure validation failed

Within the failed backend-closure job:

- production dependency install: PASS
- full Python `compileall`: PASS
  - emitted `HHS_PRODUCTION_BACKEND_PYTHON_COMPILE_CLOSURE=1`
- native LiteRT C/C++ compile/run: PASS
  - emitted `HHS_PRODUCTION_BACKEND_NATIVE_COMPILE_CLOSURE=1`
- production assistant import/route closure: PASS
  - emitted `HHS_PRODUCTION_ASSISTANT_IMPORT_CLOSURE=1`
- failure occurred only when executing `scripts/production-backend-closure-verify.py` directly:
  - `ModuleNotFoundError: No module named 'hhs_backend'`

That failure is a script-execution import-path defect, not a backend compile failure.

The current pre-checkpoint head `1ddc087...` repairs exactly that defect by inserting repository root into `sys.path` before importing `hhs_backend`.

At checkpoint creation time, no new PR workflow run for `1ddc087...` had yet appeared in the queried Actions results.

## Known production/backend conclusions

Confirmed:

- complete Python backend source compilation passes in the new closure job
- the production assistant route and service import successfully
- the native LiteRT C and C++ registry compile and execute
- the dedicated LiteRT native workflow is green after test-harness correction
- canonical `make c-abi` is now the test/build authority for the cumulative exact ABI
- the deployment workflow now fails closed before production mutation when backend closure fails

Not yet confirmed:

- `scripts/production-backend-closure-verify.py` passes after the `1ddc087...` import-path fix
- direct two-turn HTTP assistant probe on deployed `:8080`
- Lane 5 two-turn HTTP assistant probe on deployed `:8715`
- Chromium two-turn assistant acceptance
- final Exact-Main success on the eventual merged current-main SHA
- any generated Hash216 successor convergence after successful promotion

## Changed files before this checkpoint

- `.github/workflows/digitalocean-production-main.yml`
- `native_projects/hhs_pass220_litert_native_model_runtime/include/hhs_pass220_litert_native_model_runtime_v1.hpp`
- `native_projects/hhs_pass220_litert_native_model_runtime/tests/hhs_pass220_litert_native_model_runtime_v1_cpp_test.cpp`
- `scripts/production-assistant-http-verify.py`
- `scripts/production-backend-closure-verify.py`
- `tests/pass220/test_hhs_pass220_litert_native_model_runtime_v1.py`
- `tests/test_hhs_litert_lm_repo_bootstrap_v1.py`
- this restart record

## Commands / validations represented by CI

Equivalent critical commands now encoded in CI:

```bash
python -m compileall -q hhs_backend hhs_runtime \
  scripts/production-backend-closure-verify.py \
  scripts/production-assistant-http-verify.py

make -C native_projects/hhs_pass220_litert_native_model_runtime clean all test

python scripts/production-backend-closure-verify.py

make c-abi

python -m pytest -q \
  tests/pass220/test_hhs_pass220_litert_native_model_runtime_v1.py \
  tests/test_hhs_litert_lm_repo_bootstrap_v1.py
```

Post-promotion remote probes encoded in Exact-Main:

```bash
python3 /opt/hhs/app/scripts/production-assistant-http-verify.py \
  --base-url http://127.0.0.1:8080 --timeout-seconds 30 --label backend

python3 /opt/hhs/app/scripts/production-assistant-http-verify.py \
  --base-url http://127.0.0.1:8715 --timeout-seconds 30 --label lane5
```

## Exact next action

1. Re-read PR #733 head and canonical `main`.
2. Inspect the newest PR workflows for the checkpoint successor head.
3. Require `validate-production-backend-closure` to reach the actual two-turn assistant assertions after the `1ddc087...` import-path repair.
4. If that gate fails, repair only the observed backend-closure defect.
5. If it passes, require the dedicated LiteRT workflow and Exact-Main contract gate to remain green.
6. Merge PR #733 only after dependency-scoped gates are green.
7. Verify merged `main` exactly.
8. Follow the post-merge Exact-Main deployment through:
   - guarded promotion
   - direct `:8080` assistant two-turn probe
   - Lane 5 `:8715` assistant two-turn probe
   - public HTTPS Runtime OS
   - 380-service registry
   - Chromium full workspace + two-turn assistant memory acceptance
9. If a Hash216 repository-index successor advances `main`, follow the serialized successor Exact-Main run to terminal convergence.

Do not weaken the browser gate, bypass Lane 5, disable native authority, or merely increase assistant timeouts.

## Blockers at checkpoint

Only one current repair-local blocker is known:

- post-`1ddc087...` backend closure CI has not yet been observed to terminal completion.

Production remains unaccepted until merged-current-main Exact-Main passes the complete backend → Lane 5 → public/browser path.
