# Pass 220 — V5 typed A/B phase-coupled twin tensor and global WHERE conditions

Date 2026-10-09. Append-only exact source; V4 immutable.

## Restart coordinates

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass220-ordered-tensor-quotient-20261009`, draft PR #754 → `main`
- Parent SHA at initial V5 change: `8e6a8899a5324964278f50a4f80cdfa99e84433d`
- Full authoritative V5 user Unicode source: `contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_20261009.harmonicode`
- Separately extractable ASCII outer expression candidate: `contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_OUTER_COMPONENT_20261009.harmonicode`
- Focused tests: `tests/pass220/test_pass220_ordered_tensor_ab_phase_v5.py`; workflow: `.github/workflows/pass220-ordered-tensor-ab-phase-v5.yml`
- Prior frozen green workflows: V4 obligation graph `37949088541`, V4 native/HNAN/obligation integration `37949236741`. Do not reuse their exact source Hash216 witness for V5.

## Canonical source terms — do not rewrite

Outer expression is precisely V4 with the **only** ordered lexical change `==x==-y*(` → `==xA==-yB*(`. The replacement adds two source characters and preserves 40 `==` occurrences. Top-level equality gates: byte offsets 253 and 257 (previously 253 and 256), with phase-`u^36` occurrence at offset 511. Two inner tensor copies have 18 matching ordered gates each, separated by 252 source positions, not V4's 250.

Full user-supplied WHERE clause, preserved exactly in Unicode:

```text
where P⁴=AB=c⁴ and A/B≠B/A but P²=pq+(c²/(a²+b²)) and (p+q)/P(q-p)=(xy+zw)/b²
```

- `P⁴=AB=c⁴`: declared ordered chain; do not reverse to `AB=P⁴` without a native proof.
- `A/B≠B/A`: typed directed reciprocal inequivalence. No commutation or scalar quotient cancellation is licensed.
- `P²=pq+(c²/(a²+b²))`: exact nested fraction and additive group; do not replace the fraction with scalar 1 from inner coordinate equations.
- `(p+q)/P(q-p)=(xy+zw)/b²`: preserve lexical grouping and potential implicit application ambiguity. Do not choose a conventional denominator regrouping silently.
- `xA` and `-yB` require registered native binding of x/A and y/B as ordered tensor carriers (or a proven compound-symbol interpretation); token adjacency alone does not determine exact operator authority.

The word connectors `where`, `and`, `but`, the Unicode superscripts and `≠` are part of the canonical literal contract, not comments to delete.

## Actual implementation boundaries

The full two-line **UTF-8 source** is admitted through existing Lane5 arbitrary-byte candidate-only ingress, preserving complete source bytes, encoding and provenance. The native Pass159 lexical/AST/type/constraint/HIR/VMIR and VALIDATE_ONLY probe receives **only the ASCII outer expression** as a narrowly scoped subcomponent. The native path does not yet prove the Unicode WHERE contract; its success must not be promoted to full V5 closure.

The V5 native source root is new, not a borrowed V4 source/Hash216 root. No synthetic all-true gates, scalar quotient rewrites, secret-key bypass, canonical VM81 commit or Hash72/Hash216 canonical transition may be asserted.

## Dependency-scoped tests

```bash
python -m pytest -q tests/pass220/test_pass220_ordered_tensor_ab_phase_v5.py
make c-abi
cc -O2 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Inative_projects/hhs_pass159_harmonicode_toolchain/include \
  -Ihhs_runtime/include tools/pass220/pass220_ordered_tensor_quotient_native_frontend_probe_v1.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" -o /tmp/pass220-v5-outer-probe
/tmp/pass220-v5-outer-probe contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_OUTER_COMPONENT_20261009.harmonicode
```

## Proof stage status

V5 authored; focused native integration results pending as of this checkpoint.

**Current admission block:** whole-clause Unicode algebra has no verified source-specific native typed evaluator/witness provider, and all 40 ordered equality gates plus `A/B≠B/A` and the 3 declared WHERE chains need proof in one shared environment. Existing source-bound HNAN/VM81 authority must not be bypassed. Keep PR #754 draft.

Next: inspect dedicated V5 CI; repair scoped errors; freeze full-source hash and candidate-only receipt; extend native typed parsing and registered exact algebraic constraint resolution for WHERE and outer carrier binding, then source-specific 40-gate proof, signed VM81 admission, Hash72/Hash216 transition, reverse/replay only after truth.
