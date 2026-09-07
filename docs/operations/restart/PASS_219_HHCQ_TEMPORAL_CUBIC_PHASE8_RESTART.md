# Pass 219 HHCQ temporal cubic Phase 8 restart

Date: 2026-09-07

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen Phase 7 checkpoint/base: `12273cab9cfbe294a0dbaa1d1fe8db17358b1497`
- Phase 7 validated implementation head: `1d3e1a3943998c7f0c644fc15916418ce0694209`
- Phase 8 branch: `agent/pass219-hhcq-temporal-cubic-phase8-20260907`
- Main observed through Phase 7: `40bce1e30790eb3339da3599ba3be740010dae9a`
- Target: experiment branch only. No PR, merge, deployment, or canonical-authority promotion is authorized.

## Frozen inherited evidence

Preserve Phase 1 through Phase 7 evidence. In particular preserve Phase 7: exact collapse polynomial update, 35/35 Phase5 resolutions, 4/4 natural lane winners, 4,761 local authenticated samples, fixed 112-byte policy state, digest-disjoint heldout evaluation, no canonical sqrt/division, and heldout mean regret 5,491 beating the fixed-lane 8,457 baseline.

## New temporal Cardano identity

The user-supplied three-branch exact radical solution for `t` is treated as a symbolic Cardano presentation of one temporal cubic. Define

`G = x*y*(x+y+z+w) - w*z`

and

`B = 27*m*(m-1)*w*x^4*y^4*z*G`.

The full supplied square-root radicand factors exactly as

`R = B^2 - 108*x^12*y^12`.

The real Cardano branch has the form `t = -(u+v)` with `u*v = 1/3`, so the full three-branch radical system is equivalently constrained by the exact integer cubic

`x^2*y^2*(t^3 - t) + m*(m-1)*w*z*G = 0`.

The other two displayed roots are the two cube-root-of-unity Cardano branches of the same cubic. They may be carried by exact phase-branch identity; Phase 8 must not assume their numerical values are literally `0,1,2` unless the polynomial proves that for a specific state.

## Phase 8 scope

1. Add an exact temporal cubic witness ABI over bounded integer inputs `(m,w,x,y,z,t)`.
2. Compute the compact cubic residual directly, plus neighboring residuals at `t-1,t,t+1`, with no radical evaluation, floating division, Newton iteration, or chain-rule approximation.
3. Expose the factored Cardano invariants `G`, `B`, and `R = B^2 - 108*x^12*y^12` using checked integer arithmetic where representable; overflow must fail closed.
4. Add an exact `Z_72` root scan over `t in [0,71]`, returning a 72-bit root mask, root count, and deterministic preferred phase branch. The scan is evidence/routing only and has no canonical mutation authority.
5. Map the temporal cubic local residual direction into the existing HHCQ trinary phase vocabulary without changing Phase5 quantization resolution authority.
6. Preserve the inherited Phase7 fixed 112-byte learned policy state. No per-root or per-region learned allocation is permitted.
7. Add strict C tests for the compact polynomial identity, radicand factorization, root-mask determinism, singular/overflow fail-closed behavior, neighboring residual direction, state-size preservation, and zero canonical/floating authority.
8. Evaluate against the same authenticated Phase3 Pass215 hydrated SUMMARY frames. Measure cubic closure/root coverage and compare a Phase8 temporal-direction composition against the frozen Phase7 learner on the same digest-disjoint heldout identities.
9. Performance result must be reported honestly. Do not weaken exactness gates if the temporal composition does not improve Phase7 regret.

## Planned files

- `hhs_runtime/include/hhs_pass219_hhcq_temporal_cubic_1_28.h`
- `hhs_runtime/c/hhs_pass219_hhcq_temporal_cubic_1_28.inc`
- additive aggregate exact ABI bindings
- `tests/pass219/test_pass219_hhcq_temporal_cubic_1_28.c`
- `benchmarks/pass219/hhcq_temporal_cubic_phase8_benchmark.cpp`
- `.github/workflows/pass219-hhcq-temporal-cubic-phase8.yml`
- this restart record updated with accepted evidence.

## Validation state

- implementation: pending
- dependency-scoped strict C validation: pending
- authenticated hydrated-weight benchmark: pending
- blockers: none known

## Exact next action

Implement the compact temporal cubic witness and Z72 root scanner, bind it into the exact ABI, then run strict dependency-scoped C validation and the authenticated Phase8 benchmark. Preserve all Phase7 evidence and do not merge, deploy, or promote authority.
