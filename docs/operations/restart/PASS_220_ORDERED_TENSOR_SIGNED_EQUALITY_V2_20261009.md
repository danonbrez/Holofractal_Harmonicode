# Pass 220 — Revised signed equality tensor, source-v2 native validation

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Parent branch: `agent/pass220-ordered-tensor-quotient-20261009`; merge target `main`; parent commit `0294845c391f1ad94e20a91efb9b59a6ba57ba41`
- Supersedes as latest source **without deleting or rewriting** the inherited V1 fixture.
- Exact user source: `contracts/pass220/PASS_220_ORDERED_TENSOR_SIGNED_EQUALITY_V2_20261009.harmonicode`, one line plus LF; 18 syntactic `==` occurrences.
- Explicit equality-chain amendment: `b^2==c^2-a^2==x*y+z*w`.
- Signed witness identities: `1==z*w`, `1==x*y`, `6==b^2*c^2==b^2+c^2+a^2`, and nested `(-(e^2==c^2+d^2==b^6==8))`.
- Signed numeric anchors are `(-1,-1,-6,+8)`; these are *licensed projections of anchors*, not replacement of equality-node source identities.

## Current exact projection results

Constants: `a²=1,b²=2,c²=3,d²=5,e²=8`. Coordinate/magnitude residuals are all zero. Product sum `1+1=b²` closes if the two ordered unit-product gate witnesses are admitted. Original phase relations with a conventional commutative complex projection force `z*w=-1`, conflicting with the new gate `1==z*w`. That projection is an explicit diagnostic, not a native HARMONICODE counterproof. No Boolean gate or double unary negative is numerically replaced in the source.

## Native path and authority

- Existing `Lane5IngressMediator.mediate` handles exact source bytes as a candidate only.
- Existing `hhs159_source_open_bytes → lex → CST → AST → types → graph → HIR → VMIR → HHS159_MODE_VALIDATE_ONLY` uses the real built ABI.
- A separately sourced `hhs159_get_hash216` receipt records native source and validation identities, **not** a VM81 execution-and-commit receipt.
- Existing historical Pass169 `hhs_exact_pass219_i168_bind_canonical` is fixed to an unrelated 632-byte source, so it must not be passed this candidate or cited as its proof.
- Full acceptance requires the existing native ordered-phase rules to admit all 18 source equality occurrences with one global environment, and to produce a source-specific signed VM81 admission, Hash72/Hash216 transition and deterministic replay/reverse. No alternative scalar or floating-point authority is permitted.

## Dependency-scoped commands

```bash
python -m pytest -q tests/pass220/test_pass220_ordered_tensor_signed_equality_v2.py
make c-abi
cc -O2 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Inative_projects/hhs_pass159_harmonicode_toolchain/include -Ihhs_runtime/include \
  tools/pass220/pass220_ordered_tensor_quotient_native_frontend_probe_v1.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" -o /tmp/pass220-tensor-v2
/tmp/pass220-tensor-v2 contracts/pass220/PASS_220_ORDERED_TENSOR_SIGNED_EQUALITY_V2_20261009.harmonicode
```

## Validation state and next action

- Files: V2 fixture, V2 exact regression tests, dedicated CI workflow, restart record.
- Environment: branch / PR #754; no production, VM81, or canonical state mutation.
- Required B/C evidence: GitHub Actions Pass 220 Ordered Tensor Signed Equality V2.
- D (VM81 commit and runtime-generated Hash72/Hash216 transition/replay): not established by candidate-only/validate-only checks.
- Next: inspect V2 CI, repair source-path-dependent failures without weakening constraints, preserve V1 frozen evidence, and only promote a native closure after actual source-specific VM81 proof and replay.
