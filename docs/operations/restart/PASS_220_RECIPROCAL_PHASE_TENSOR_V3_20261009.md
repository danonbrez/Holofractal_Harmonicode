# Pass 220 — Exact reciprocal full/half-phase tensor V3

## Restart coordinates

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass220-ordered-tensor-quotient-20261009`
- Base commit: `2d91cca6ff8d0f4be5de30e82e8e1a9d6646e58b`
- Target: PR #754 → `main`, **draft until actual source-specific VM81 proof**
- Additive files: `contracts/pass220/PASS_220_RECIPROCAL_PHASE_TENSOR_V3_20261009.harmonicode`, `tests/pass220/test_pass220_reciprocal_phase_tensor_v3.py`, `.github/workflows/pass220-reciprocal-phase-tensor-v3.yml`, this record
- All inherited V1 and V2 fixtures remain frozen.

## Verbatim source and structural equation

V3 is a 518-byte ASCII source expression plus a single trailing LF, with 39 syntactic `==` occurrences, one top-level `==` at zero-based byte offset 253, and **no reordering**. The original source itself is authoritative: `contracts/pass220/PASS_220_RECIPROCAL_PHASE_TENSOR_V3_20261009.harmonicode`.

For readability **only**, set:
- `X=List(x==-y,x+y==0,x*y,y==a^2/x)`
- `Z=List(z==-w,z+w==0,z*w,w==a^2/w)`
- `C=List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==x*y+z*w,c^2==a^2+b^2)`
- `Q=((x*y+z*w)/b^2==a^2+x+y-z-w)`
- `U=List(X,Z,C/Q)`
- `S=List(1==z*w,1==x*y,6==b^2*c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8)))`
- `T=List(U,-S)`
- `G72=(u^72==x*y)`, `G36=(u^36==(y*x*w*z)/a^2)`.

Then the literal top-level structure is:
`List(G72/U,-S)==T/G36`.

**Critical asymmetry:** LHS phase quotient targets `U`, not `T`; RHS phase quotient targets `T`. Do not rewrite to `G72/T == T/G36`, distribute quotient into List without proof, or cross-multiply `G72*G36==T*T`. Both tensor occurrences carry the same symbol spelling but distinct source addresses/provenance; follow one native global symbol environment unless licensed by exact copy-instance semantics.

The reverse ordered product `y*x*w*z` is not generally interchangeable with `x*y*z*w`. The nested `==` operation produces its own Boolean value in the inherited I121.9 membrane but its source node and gate evidence remain distinct, and the enclosing tensor object cannot be replaced by a host Boolean quotient.

## Validation and correctness

- Pass219 I121.9 global-membrane rules apply as inherited for type/graph constraints, but its *fixed 632-byte five-gate witness verifier* cannot be reused as a 39-gate native proof. Explicit source-specific proof binding is mandatory.
- Candidate-only Lane 5 mediation and Pass159 frontend + `VALIDATE_ONLY` are exercised in real CI using the existing Runtime ABI; neither has VM81 mutation authority.
- Non-authoritative exact coordinate projection: `a²=1, b²=2, c²=3, d²=5, e²=8` yields zero squared-geometry/magnitude residuals, signed numeric anchors `(-1,-1,-6,+8)` yield zero sum.
- No scalar-complex branch is imported as canonical native phase authority.
- Admission stage requires native proof of 39 ordered Boolean gate witnesses, global environment revalidation, phase quotient type eligibility, VM81 signed admission, Hash72/Hash216 execution evidence, replay and reverse.

## Scoped commands

```bash
python -m pytest -q tests/pass220/test_pass220_reciprocal_phase_tensor_v3.py
make c-abi
cc -O2 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Inative_projects/hhs_pass159_harmonicode_toolchain/include -Ihhs_runtime/include \
  tools/pass220/pass220_ordered_tensor_quotient_native_frontend_probe_v1.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" -o /tmp/pass220-tensor-v3
/tmp/pass220-tensor-v3 contracts/pass220/PASS_220_RECIPROCAL_PHASE_TENSOR_V3_20261009.harmonicode
```

## Status and next

- Authored on source branch; no host-side source mutation or canonical VM81 commit.
- Pending scoped CI results for V3.
- Reuse inherited validations for V1/V2, do not rerun unrelated work.
- On V3 green, record immutable source and validation identities, then apply existing signed global-proof/VM81 admission surfaces **only** if a source-specific all-gates-true proof exists.
- Full phase-entanglement/orthogonality and canonical closure remain assertions requiring native evidence beyond source ingestion.
