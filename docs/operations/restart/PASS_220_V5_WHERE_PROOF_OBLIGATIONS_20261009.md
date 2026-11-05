# Pass220 V5 exact A/B/P/p/q typed WHERE relation obligations

Date 2026-10-09. Restartable additive stage.

Repository `danonbrez/Holofractal_Harmonicode`, draft PR #754, branch `agent/pass220-ordered-tensor-quotient-20261009`. Parent SHA: `48ff4ca66c66341e77b5ccba562e0dc051cca5d7`. Preserve prior V4 evidence, source and native receipt lineage. No canonical VM81 mutation.

Verified preceding V5 run: https://github.com/danonbrez/Holofractal_Harmonicode/actions/runs/37951427141; job `113890902381` complete success; 12 source tests passed, real complete-source Unicode Lane 5 candidate ingress, outer-component-only native Pass159 VALIDATE_ONLY status 0, order-change native source Hash216 distinct; artifact `11625803729`.

**Normative original V5 source:** `contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_20261009.harmonicode`. It is not replaced by the ASCII-only `contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_OUTER_COMPONENT_20261009.harmonicode` subcomponent. Exact WHERE clause:

```text
where P⁴=AB=c⁴ and A/B≠B/A but P²=pq+(c²/(a²+b²)) and (p+q)/P(q-p)=(xy+zw)/b²
```

This stage adds `hhs_runtime/hhs_pass220_v5_where_proof_obligations_v1.py`, `tests/pass220/test_pass220_v5_where_proof_obligations_v1.py`, `.github/workflows/pass220-v5-where-proof-obligations-v1.yml`. It uses **actual source UTF8 byte offsets** to construct 5 independently identified unproved relations: `P⁴=AB`, `AB=c⁴`, `A/B≠B/A`, `P²=pq+(c²/(a²+b²))`, `(p+q)/P(q-p)=(xy+zw)/b²`. The chain direction is fixed, the fraction grouping is not rewritten, and xA/-yB remain two typed ordered carrier *obligations*.

This requires exactly 40 existing outer-component `==` occurrences, 18 homologous copy gates at 252 distinct source positions, outer top-level offsets 253/257, half-phase gate offset 511. No unequal reciprocal gate may be substituted with scalar symmetry, and no conventional equality or host arithmetic may grant native semantic truth.

Native WHERE interpretation is still unresolved: **five source-bound relations are NOT five true proofs**. `source_sha256` fingerprints serve provenance only, not VM81 state transitions or Hash216 authority. The only authorized closure path remains registered typed native source-general proof under one shared Lo Shu symbol environment, final cross-layer revalidation, signed VM81/PQC admission, Hash72/Hash216 transitions, deterministic replay/reverse. Keep PR draft.

Scoped commands:
```bash
python -m pytest -q tests/pass220/test_pass220_v5_where_proof_obligations_v1.py -k 'not test_replay_written_obligation_evidence'
python -m hhs_runtime.hhs_pass220_v5_where_proof_obligations_v1 --full contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_20261009.harmonicode --outer contracts/pass220/PASS_220_ORDERED_TENSOR_AB_PHASE_V5_OUTER_COMPONENT_20261009.harmonicode --out artifacts/pass220/v5-where/obligations.json
python -m pytest -q tests/pass220/test_pass220_v5_where_proof_obligations_v1.py
```
