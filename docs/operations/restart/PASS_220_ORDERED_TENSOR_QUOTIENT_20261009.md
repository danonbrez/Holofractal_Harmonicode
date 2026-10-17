# Pass 220 — User ordered tensor quotient source ingress

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base commit: `7fefacde360e6a5bb537cb01e94415c96430915b`
- Branch: `agent/pass220-ordered-tensor-quotient-20261009`
- Merge target: `main`
- Change type: additive source, negative/source regression, native probe and workflow.
- Authority: existing Lane 5 candidate mediation + Pass159 source-to-VMIR; final VM81/Hash72/Hash216 admission remains exclusively with established runtime.

## User-supplied equation

The first line of `contracts/pass220/PASS_220_ORDERED_TENSOR_QUOTIENT_USER_SOURCE_20261009.harmonicode` is the exact, unmodified submitted List expression. The second line is the separately supplied exact relation `xy+zw=b²`.

The equation is one global source envelope with a separately identified new relation. The lexical symbols `xy` and `zw` shall not be commuted or automatically collapsed to scalar values. The quotiented `==` remains a typed source node.

## Existing execution surfaces

1. `Lane5IngressMediator.mediate`: candidate-only mediation of the exact UTF-8 bytes; cannot authorize VM81 mutation.
2. `hhs159_source_open_bytes` through `hhs159_lower_vmir`: source-preserving native frontend, type and graph identity.
3. `hhs159_interpret` with `HHS159_MODE_VALIDATE_ONLY`: bounded native evaluation attempt; no direct commit bypass.
4. The historical `hhs_exact_pass219_i168_bind_canonical` is **not** called: it is fixed to a different 632-byte source and cannot produce evidence for this candidate.

## Exact non-authoritative projections

`(a²,b²,c²,e²)=(1,2,3,8)` yields four zero squared-coordinate residuals and signed vector `(-1,-1,-6,8)` with sum zero. Given the new source relation `xy+zw=b²`, and `x+y=z+w=0`, the denominator equality has a unit projection. This does not assert that the conventional complex-scalar branches also satisfy the supplemental relation.

## Local / CI commands

```bash
python -m pytest -q tests/pass220/test_pass220_ordered_tensor_quotient_ingress_v1.py
make c-abi
cc -O2 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Inative_projects/hhs_pass159_harmonicode_toolchain/include \
  -Ihhs_runtime/include tools/pass220/pass220_ordered_tensor_quotient_native_frontend_probe_v1.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" -o /tmp/pass220-tensor-probe
/tmp/pass220-tensor-probe contracts/pass220/PASS_220_ORDERED_TENSOR_QUOTIENT_USER_SOURCE_20261009.harmonicode
```

## Stage gates and blockers

- Gate A: exact source identity, ten ordered equality occurrences, separate new relation, coordinate and signed-vector regression.
- Gate B: real Lane 5 candidate mediation, with candidate-only/no mutation authority.
- Gate C: native source/token/CST/AST/type/constraint/HIR/VMIR chain and `VALIDATE_ONLY` status captured.
- Gate D (not claimed by A-C): source-specific full gate witnesses, VM81 admission, runtime-generated Hash72/Hash216 transition evidence, deterministic replay and reverse, no type/provenance bypass.

If B or C fails, trace the existing membrane and parser interfaces; do not scalarize or modify the source to manufacture passage. If A-C succeeds but D remains unproved, report `SOURCE_INGRESS_VERIFIED_VM81_PROOF_PENDING`, never `FULL_CLOSURE`.

## Restart state

- Files authored: source fixture, Python regression, native probe, CI workflow, this checkpoint.
- Environment: remote GitHub source branch; no local runtime or production host mutation.
- Pending: CI artifact inspection; any impact-scoped repair; an exact source-specific native proof/VM81 receipt from the existing admission path; merge and verified-main replay.
- Next action: inspect the pull-request CI run and use its native status to determine whether the existing gate admits the candidate without replacement semantics.
