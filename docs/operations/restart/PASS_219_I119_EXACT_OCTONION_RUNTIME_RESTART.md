# Pass 219 I119 — Exact Ordered Octonion Runtime Restart Record

## Authority and lineage

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base at start: `f5d8fdc014d888f93c0d85d40d2a2c0c198eefdf`
- Frozen Pass 219 I118 ancestor: `e87bc42b17c03ff98f691838b8d573a5bdf46ff2`
- Branch: `agent/pass219-exact-xyzw-octonion-abi-repair`
- Merge target: `main`
- Draft PR: `#314`

The branch was created directly from current `main`; compare state at implementation checkpoint was ahead-only with merge base exactly the authoritative base and zero commits behind.

## Implemented scope

The implementation preserves the existing formal algebra and raises the exact runtime/ABI to it.

- Public named phase channels: `x`, `y`, `z`, `w`, `xy`, `yx`, `zw`, `wz`.
- Dynamic ordered derivation preserves `xy != yx` and `zw != wz` by applying the already-frozen u72 orientation normalization rather than scalar integer multiplication.
- Full `8 x 8 = 64` ordered product surface is materialized from the eight channel phases.
- The fixed anchor surface is required to match the inherited exact 64-product table.
- Exact VM81 projection folds four selected 64-bit VM words into four phase inputs and expands the complete ordered surface without VM mutation.
- Arithmetic is integer/mod-72 only. The module exposes zero floating-point, VM81 mutation, persistence, or Hash72 commit authority.

## Files changed

- `hhs_runtime/include/hhs_pass219_octonion_runtime_1_19.h`
- `hhs_runtime/c/hhs_pass219_octonion_runtime_1_19.inc`
- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `tests/pass219/test_pass219_octonion_runtime_1_19.c`
- `tests/pass219/test_pass219_octonion_runtime_1_19.cpp`
- `.github/workflows/pass219-exact-octonion-runtime-i119.yml`
- `docs/operations/restart/PASS_219_I119_EXACT_OCTONION_RUNTIME_RESTART.md`

## Validation gates

Implemented tests cover:

1. exact ABI self-validation;
2. all eight named channel exposures;
3. anchor-state equality against `hhs_exact_phase_product` for all 64 ordered pairs;
4. dynamic noncommutative orientation for `xy/yx` and `zw/wz`;
5. exact VM81-to-eight-channel projection;
6. range rejection and corruption fail-closed behavior;
7. C and C++ ABI compatibility;
8. inherited I118 and Pass 219B exact ABI regressions;
9. exact-head and synthetic-merge CI variants.

## Current state

Implementation is committed on the branch and draft PR #314 is open. CI completion remains the next freeze gate; no merge or canonical freeze is claimed before terminal validation.
