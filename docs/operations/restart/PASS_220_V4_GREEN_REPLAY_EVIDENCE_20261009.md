# Pass 220 — V4 source-bound native replay: immutable green evidence

Date: 2026-10-09

## Restartability

- Repository `danonbrez/Holofractal_Harmonicode`
- Branch `agent/pass220-ordered-tensor-quotient-20261009`, draft PR #754, merge target `main`
- Base commit of evidence publication: `a90b5edc1aa105e9319d22f05d02d3288a9d08a0`
- Frozen tensor source: `contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode` — 527 bytes with LF, 40 equality occurrences.
- New files: `evidence/pass220/PASS220_V4_40_GATE_REPLAY_PREFLIGHT_37946520150.json`, `tests/pass220/test_pass220_v4_40_gate_replay_evidence.py`, `.github/workflows/pass220-v4-40-gate-replay-evidence.yml`, this checkpoint.
- No historical V1–V4 files, canonical Pass159/169, VM81, or PQC mutation surfaces altered.

## Actual validated workflow run

- [Pass 220 V4 Source-General Replay Preflight](https://github.com/danonbrez/Holofractal_Harmonicode/actions/runs/37946520150)
- Run `37946520150`, job `113874078401`, completed **success**.
- Green scope: source exactness, `make c-abi`, C native preflight compile, real Pass159 HOLD (3 diagnostic VM81 steps, no commit), interpreter replay, compiler equality, 40 separately bound gate digests, fail-closed outer phase-chain mutation.
- Python: 2 passed (pre-evidence; 1 deselected); then 3 passed (with produced native artifact). Existing pytest unknown-`asyncio_mode` warning was non-fatal.
- Artifact ID `11623606771` (`pass220-v4-source-general-replay-preflight-6c2dcd30239cce4933383130a97d991462a83598`).
- Source hash: `124900427b60ff688e3cff10f2178e76d121168273fcd3caec0782ca2a067344`.
- Green run head: `a90b5edc1aa105e9319d22f05d02d3288a9d08a0`.

## Witness provenance and admission semantics

`evidence/pass220/PASS220_V4_40_GATE_REPLAY_PREFLIGHT_37946520150.json` is derived from the **actual native job logs**, not a fabricated runtime receipt. It freezes all 40 source positions and diagnostic occurrence identities, including:

`SHA256("GATE" || SHA256(exact 527 source bytes) || BE32(gate index) || BE32(offset))`

All `truth` values remain `UNRESOLVED`. The provenance hashes are not Boolean proof and are not canonical Hash216 transition indices.

This evidence is `NONCANONICAL_SOURCE_GENERAL_REPLAY_PREFLIGHT_VERIFIED`. It does **not** certify each `==` gate as true, grant the source-general Pass159 replay receipt a canonical VM81 interpretation, mint signed Hash72/Hash216 authority, prove native orthogonality, or permit production commit.

## Next stage / blockers

- Dependency-scoped green replay/ingress evidence frozen. No need to rerun `make c-abi` or earlier pass histories for this evidence-file addition.
- CI for the evidence integrity record is standalone, exact-source-bound, with negative tests for source mutation, gate identity permutation, fabricated gate truth, and authority escalation.
- Unresolved: native source-general ordered gate truth proof for all 40 edges in one shared typed environment; cross-layer revalidation; signed VM81 admission and replay/reverse. Historical I121.9/I162 sources are bound to 632 bytes and five gates and cannot certify this equation.
- No PQC signing key/authorization or source-general proof provider is claimed in this checkpoint.
- Remain draft PR #754 until genuine signed native proof and main verification. Next repair should target an actual source-specific proof-producing runtime provider, not replace `UNRESOLVED` with synthetic truth values.
