# Pass 219 I129 / Pass 197 repair membrane — restart record

Status: `LINEAGE ASSERTION REPAIRED — EXACT/SYNTHETIC RESEAL PENDING`

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass219-iteration129-pass197-repair-membrane`
- Pull request: `#326`
- Intended target: `main`
- Current authoritative main used for reconciliation: `634db40aaf57ec087b7353d6d9205d896622adb4`
- I129 source head before reconciliation: `fa10950aab9603ac4d78f65aaaae4304e99d8a15`
- Current-main reconciliation commit: `aff24226b2e59e9b416ab89147054d26537e3d15`
- Frozen predecessor I128: `c85b2b29cdf26d21912eb06b7d50323526944cc2`
- Accepted Pass 197 squash merge: `2321a1f05a6da410034a31ca141e3919091bb09a`
- Merge authorization: NOT GRANTED

## Reconciliation method

I129 was reconciled using a true two-parent commit: existing I129 history as the first parent and current authoritative `main` as the second parent. The tree was built from current main, overlaid with the exact live I129 Pass 197 blobs, and the cumulative exact ABI registries were composed additively by inserting inherited Pass 197 immediately after inherited Pass 198. No squash, force-push, or removed historical path recreation was used.

The live PR file census is authoritative. The earlier stale census that mentioned a V4 runtime path was rejected; that path is not part of exact I129 source head `fa10950a...`.

## Preserved repaired blobs

- `.github/workflows/pass197-i129-repair-validation.yml`: `76786543a6bac5f0884c19e8226369ae8f47ff0c`
- `applications/holofractal_harmonizer/src/pass197-calibration.mjs`: `f68cac28e29a29da99c4cb415778fb1c196a19f2`
- `hhs_backend/api/pass197_calibration_routes.py`: `0325974ff78c097b010b297971c2243d4132af43`
- `hhs_backend/runtime/hhs_pass197_ab_hydration_calibration_v1.py`: `6d86629bdf25bdb03890197475a12dbf9190c618`
- `hhs_backend/runtime/pass197_exact_v1.py`: `96be2009ca46cbcab7633f6fae97a0bea7621abb`
- `hhs_backend/runtime/pass197_state_v1.py`: `10c986063d5fa2503d732e6725bb3b8665372666`
- `hhs_runtime/c/hhs_pass219_inherited_pass197_1_29.inc`: `f9d8ff88571da6e873667a38e8e613b8451b082a`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i129_pass197.py`: `18077a0d68991f682e330843766f97d628caff54`
- `hhs_runtime/include/hhs_pass219_inherited_pass197_1_29.h`: `f9799b5d60e9fe6e731e85d57e15aa461ddb6cac`
- `hhs_runtime/include/hhs_pass219_inherited_pass197_1_29.hpp`: `e42031cdf8a0ed973b0557d40469eed487e4db97`
- `tests/pass219/test_pass219_cumulative_pass197_membrane_i129.py`: `61e0e3bc63ba7667783b816ee6012aeb114d2820`
- `tests/pass219/test_pass219_inherited_pass197_1_29.c`: `0a43fab28d0b7d8d55179c5d1c014c21ad0f5b4f`
- `tests/pass219/test_pass219_inherited_pass197_1_29.cpp`: `1c6dfab1f2727dfb2d9d741673d306b1d26f1c9c`
- `tests/test_hhs_pass197_i129_repair_v1.py`: `1924e7c9eb3642087b6b2792ce75fded38dbee00`

The Pass197 implementation blobs above remain unchanged by the lineage repair. The aggregate exact ABI header/C files remain the current-main compositions created during reconciliation.

## Implemented repair boundary

I129 repair-forwards ten substantive historical Pass 197 issues at the inherited V1 surface: kernel audit ordering, fail-closed Hash72 authority, mandatory full replay for closure, exact rational components, run serialization, report-integrity quarantine, 405-state synchronous bound, strict exponent ingress, duplicate-coordinate rejection, and CLOSED-only frontend projection.

No new candidate, canonical mutation, persistence, Hash72 clock, C++ mutation, or VM81 mutation authority is granted. Singleton VM81 authority remains inherited.

## Hosted validation evidence

### Standalone repaired Pass 197 validation — GREEN

- Run: `32866368839`
- Job: `97862527227`
- Conclusion: SUCCESS
- Passed: repaired surface compilation; historical lifecycle + twelve I129 repair regressions; complete 405-state envelope; fail-closed authority/exact ingress source gates; CLOSED-only visual projection syntax.

The repository's ordinary `Pass 197 A/B Hydration Calibration` workflow also passed on the reconciled head in run `32866368285`.

### First dedicated I129 seal — FAILED ONLY AT STALE LINEAGE METADATA

- Run: `32866370778`
- Synthetic job: `97862535691` — FAILURE
- Exact job: `97862536114` — FAILURE
- Both jobs passed checkout, Python setup, and dependency installation.
- Both failed at `Prove frozen I128 and accepted Pass 197 squash lineage` before provenance, ABI, membrane, lifecycle, or successor assertions executed.
- No implementation assertion failed in this run.

Executed stale assertion:

`test "$(git merge-base aeadabcce0ea178ad5b6a27001e109f349808dde HEAD)" = "e3d6694e06edbe8f04c02d6b665301b34f6ec074"`

GitHub compare evidence establishes the actual merge base as:

`77bf7ddfcfb09246a805a6e8f0919cfa18d0f3c0`

This value is identical when comparing `aeadabcce0ea178ad5b6a27001e109f349808dde` against the preserved pre-reconciliation I129 source head `fa10950aab9603ac4d78f65aaaae4304e99d8a15`, proving the old expected `e3d6694e...` was already stale and was not caused by current-main reconciliation.

### Repair-forward

Only `.github/workflows/pass219-cumulative-pass197-repair-membrane-i129.yml` is changed for the failed assertion: its expected merge-base value is corrected from `e3d6694e...` to observed historical value `77bf7ddf...`. All Pass197 runtime, membrane, test, and authority blobs remain untouched.

## Required reseal

The next exact/synthetic I129 workflow run must:

1. pass frozen I128 and accepted Pass197 lineage using the corrected historical merge base;
2. prove accepted historical provenance and unchanged repaired blob identities;
3. compile repaired Python and membrane surfaces;
4. reject approximate canonical arithmetic and accidental authority exports;
5. compile the cumulative exact ABI with strict C11 warnings-as-errors;
6. execute C and C++ membrane conformance;
7. execute the Pass043-derived membrane preflight;
8. rerun historical lifecycle + I129 repair regressions;
9. execute the complete 405-state repaired envelope;
10. preserve the inherited Pass198 successor membrane.

## Environment state

No local/private worktree is required for recovery. Repository-visible Git objects and GitHub Actions are the authoritative execution environment for this checkpoint.

## Next action

1. Commit the workflow lineage correction and this restart record atomically on top of `aff24226...`.
2. Fast-forward the I129 branch ref without force.
3. Observe the resulting dedicated exact/synthetic run.
4. If a new lane fails, repair only the executed failing assertion.
5. If both lanes succeed, freeze I129 by recording final evidence in PR metadata only; do not mutate the sealed tree and do not merge.

## Blockers

Final freeze is blocked only on a new documentation-inclusive exact/synthetic seal after the corrected lineage assertion executes.
