# Pass 220 V4 — Outer ordered phase chain over reciprocal tensor

## Restartable repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base commit: `056429ad4df73cee7f6d4d68ea81e2b2d5d412bc`
- Branch: `agent/pass220-ordered-tensor-quotient-20261009`; merge target: `main`
- PR: https://github.com/danonbrez/Holofractal_Harmonicode/pull/754 (draft)
- Additive changes only: V4 source fixture, focused tests, dedicated CI workflow, this checkpoint.
- V1–V3 source and green validation evidence remain immutable and inherited.

## Exact updated source

`contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode`

The user-supplied text is stored as one 526-character ASCII line plus LF. There are 40 explicit `==` occurrences. Exactly two top-level occurrences are at zero-based offsets 253 and 256. Relative to V3, the sole source transformation at the outer boundary is:

`L==R` → `L==x==-y*(R)`.

No inner tensor elements are rewritten. `L=List((u^72==x*y)/U,-S)` and `R=List(U,-S)/(u^36==(y*x*w*z)/a^2)`, where `U` and `S` are inherited unchanged from V3. This is a schematic notation only; the literal file is the authority.

The new ordered edges bind `L==x`, then `x==-y*(R)` in the exact source chain. The outer negative is part of the ordered multiplication by the complete parenthesized right quotient, not a scalar sign that can freely migrate. Existing `x==-y` inner edges are retained as distinct source occurrences. No transitivity promotion, quotient cancellation, Boolean division, commutation of `y*x*w*z`, or local shadowing of shared HARMONICODE symbols is authorized without the relevant native proof.

## Validation protocol

- Exact source byte identity, V3 derived strict lineage, 40 gate positions, 2 top-level occurrences.
- Negative tests: reversing outer chain, phase rotation, quotient/grouping, ordered product, negative gating.
- Real existing Lane 5 ingress candidate-only path.
- Real existing Pass159 full source→tokens/CST/AST/types/constraint graph/HIR/VMIR `HHS159_MODE_VALIDATE_ONLY` path.
- Validate native source Hash216 changes on an outer-edge mutation; never use historical 632-byte Pass169 proof for V4.
- No committed VM81 transition/Hash72/Hash216 canonical execution receipt is claimed by validate-only.

## Run commands

```bash
python -m pytest -q tests/pass220/test_pass220_ordered_phase_chain_v4.py
make c-abi
cc -O2 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Inative_projects/hhs_pass159_harmonicode_toolchain/include \
  -Ihhs_runtime/include tools/pass220/pass220_ordered_tensor_quotient_native_frontend_probe_v1.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" -o /tmp/pass220-tensor-v4
/tmp/pass220-tensor-v4 contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode
```

## Stage gates

- A: exact bytes and source-order/quotient-preserving tests.
- B: actual Lane 5 source candidate mediation, zero canonical mutation authority.
- C: native source-to-VMIR identities and ValidateOnly status.
- D: native whole-equation 40 Boolean witness gates true in one shared environment, source-specific VM81 signed admission, Hash72/Hash216 canonical transition, replay/reverse, and orthogonality witness if claimed.

No A–C green result certifies D. Next action: inspect dedicated CI and record genuine source-specific evidence, and apply dependency-scoped repair only for a new failure. Keep PR draft until D is satisfied. Do not rerun frozen V1–V3 history.
