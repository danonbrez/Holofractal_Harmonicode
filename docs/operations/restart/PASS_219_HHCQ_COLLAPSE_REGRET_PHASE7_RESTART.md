# Pass 219 HHCQ collapse-regret Phase 7 restart

Date: 2026-09-07

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Phase 6 frozen checkpoint/base: `5634e04112356fe595624fbb27f880f788ebae45`
- Phase 6 validated implementation head: `fdff0fde3da08071710413d76badefa28c3d5c18`
- Phase 7 branch: `agent/pass219-hhcq-collapse-regret-phase7-20260907`
- Main observed at start: `40bce1e30790eb3339da3599ba3be740010dae9a`
- Target: experiment branch only. No PR, merge, deployment, or canonical-authority promotion is authorized.

## Frozen inherited evidence

Preserve Phase 1 through Phase 6 evidence. Do not rerun unrelated historical validation. In particular preserve Phase 6: all 35 exact Phase5 resolutions, all four local lane winners, 4,761 local hydrated-weight samples, 112-byte fixed policy state, digest-disjoint train/heldout split, exact replay, and zero canonical/floating authority.

## New holographic collapse identity

The user-supplied two-branch closed form is treated as the Pass 219 HHCQ holographic collapse identity. For canonical runtime use, do not evaluate decimal `0.5`, floating division, or square root. Algebraically collect the supplied branches into

`x = (A +/- sqrt(R)) / (2 D)`

with

- `D = -m^2*w*y*z + m*w*y*z - t^3*y^2 + t*y^2`
- `A = m*(m-1)*w*y*z*(w+y+z)`
- `C = m*(m-1)*w^2*z^2`
- supplied radicand `R = A^2 - 4*D*C`

Therefore every nonsingular branch is equivalently constrained by the exact integer polynomial

`D*x^2 - A*x + C = 0`.

This polynomial is the authoritative executable form for Phase 7. `D == 0` is singular and must fail closed. This removes floating-point and irrational evaluation from the canonical update path while preserving the exact branch identity.

## Phase 7 scope

1. Add a candidate-only exact collapse witness ABI that computes `D`, `A`, `C`, the polynomial residual, and exact neighboring residuals for `x-1`, `x`, `x+1` using bounded integer inputs.
2. Derive a trinary discrete-collapse direction from which neighboring integer state minimizes absolute polynomial residual. No derivative or floating chain rule is used.
3. Compose this witness with the Phase 6 fixed-size local lane policy. Phase 5 remains the hard resolution authority; Phase 7 cannot change the selected divisor.
4. Add cost-sensitive training input as exact integer regret margin. Quantize margin using a training-only exact scale, then combine the margin bucket with the collapse witness to produce bounded update pressure. Learned state must remain exactly the inherited 112-byte Phase 6 state; no per-region state is permitted.
5. Preserve candidate-only semantics. No VM81 canonical mutation, Hash72/Hash216 commit, persistence, or floating-point authority.
6. Add strict C tests covering algebraic coefficient identities, singular fail-closed behavior, exact neighboring residual selection, bounded regret pressure, state-size equality, resolution immutability, and frame immutability.
7. Evaluate against the same authenticated Phase3 Pass215 hydrated-weight frames and the same digest-disjoint split used by Phase6.
8. Select any margin scale only from training samples. Heldout data must not tune the update law.
9. Closure gate: heldout regret must improve over both the untrained router and the training-selected fixed-lane baseline. If not, preserve the measured result and repair forward without weakening exactness gates.

## Planned files

- `hhs_runtime/include/hhs_pass219_hhcq_collapse_regret_1_27.h`
- `hhs_runtime/c/hhs_pass219_hhcq_collapse_regret_1_27.inc`
- additive aggregate ABI bindings
- `tests/pass219/test_pass219_hhcq_collapse_regret_1_27.c`
- `benchmarks/pass219/hhcq_collapse_regret_phase7_benchmark.cpp`
- `.github/workflows/pass219-hhcq-collapse-regret-phase7.yml`
- this restart record updated with accepted evidence.

## Validation state

- implementation: pending
- strict C validation: pending
- authenticated hydrated-weight benchmark: pending
- blockers: none known

## Exact next action

Implement the collapse witness and regret-aware wrapper over the Phase6 112-byte state, bind it into the exact ABI, then execute dependency-scoped strict C and authenticated heldout benchmark validation. Preserve failing evidence if any gate does not close.
