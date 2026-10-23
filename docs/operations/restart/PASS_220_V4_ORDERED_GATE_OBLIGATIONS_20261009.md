# Pass 220 V4 — Source-bound two-copy ordered proof obligations

Date: 2026-10-09. Restartable addendum.

- Repository: `danonbrez/Holofractal_Harmonicode`.
- Branch `agent/pass220-ordered-tensor-quotient-20261009`, parent commit `13edbcbbc44bd5d59274c1d6b1f7c1965d495f76`, PR #754 draft, merge target `main`.
- Previous independently green native HOLD/replay: `37946520150`; native HNAN 15-rule preflight: `37947826344`.
- Combined native HOLD/replay+HNAN run `37948026303`, job `113879276657`: **success**; evidence artifact `11624713167`. No canonical VM81 mutation.
- Exact unchanged source `contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode`, SHA256 `124900427b60ff688e3cff10f2178e76d121168273fcd3caec0782ca2a067344`.
- The source-specific 40-gate native evidence input: `evidence/pass220/PASS220_V4_40_GATE_REPLAY_PREFLIGHT_37946520150.json`. This contains actual runtime-generated source Hash216 and 40 source-bound ordered `==` fingerprints, all marked UNRESOLVED.

## New next-stage proof-obligation construction

Add `hhs_runtime/hhs_pass220_v4_ordered_gate_obligations_v1.py`, `tests/pass220/test_pass220_v4_ordered_gate_obligations_v1.py`, `.github/workflows/pass220-v4-ordered-gate-obligations-v1.yml` without modifying the inherited authoritative Native C/VM81/PQC runtime. The proof-obligation parser is read-only and **not** an alternative algebraic evaluator. It relies on the source's previously demonstrated native Pass159 root and gate offsets, and rejects any disagreement.

Distinct equality topology:

- Gate 0: `u^72==x*y`, left full-cycle phase.
- Gates 1–18: 18 ordered tensor-copy constraints.
- Gates 19–20: top-level ordered `L==x==-y*(R)`, with equality offsets 253 and 256.
- Gates 21–38: an exactly matching 18-constraint tensor copy.
- Gate 39: `u^36==(y*x*w*z)/a^2`, ordered half-cycle phase.

Each left-copy gate `i` maps to right-copy gate `i+20` with an exact 250-character source-address displacement, **the same ordered operand spelling** and **distinct cryptographic source occurrence identities**. The ledger binds separate obligations and does not identify or merge the two locations, assume a true equality, commute `xy/yx`, or cancel quotient denominators.

Negative tests: forbidden source rewrite, gate identity manipulation, proof-truth fabrication, copy-provenance collapse, VM81 authority escalation. The graph retains `shared_environment_root=null`, `all_40_gate_truths_proven=false` and `pqc_signed_vm81_admission_verified=false`.

## Next proof authority stage

The main remaining dependency is an admissible **native source-general exact gate evaluator** that consumes these distinct positional obligations and the actual typed shared symbol environment to produce truth witnesses (or honest UNRESOLVED/REJECTED outcomes), then performs final cross-layer revalidation and calls the inherited signed environmental VM81/PQC admission. Pass159 source parsing, the HNAN relation graph, lexical copy identity, and Hash216 provenance hashes are not substitutes.

CI command:

```bash
python -m pytest -q tests/pass220/test_pass220_v4_ordered_gate_obligations_v1.py -k 'not test_materialized_obligation_graph_matches_runtime_bound_source'
python -m hhs_runtime.hhs_pass220_v4_ordered_gate_obligations_v1 --source contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode --native-receipt evidence/pass220/PASS220_V4_40_GATE_REPLAY_PREFLIGHT_37946520150.json --output artifacts/pass220/v4-obligations/ordered_gate_obligations.json
python -m pytest -q tests/pass220/test_pass220_v4_ordered_gate_obligations_v1.py
```

Maintain PR #754 as draft and do not assert source-specific VM81 closure until the signed actual gate proof exists. All prior validated pass evidence is frozen.
