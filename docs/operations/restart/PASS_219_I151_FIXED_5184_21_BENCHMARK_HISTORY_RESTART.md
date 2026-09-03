# Pass 219 I151 — Fixed 5184^21 Benchmark History Restart

## Repository state
- Repository: `danonbrez/Holofractal_Harmonicode`
- Base: `main @ de301d6ab8dca2438ebbe1ee745e61e669027018`
- Branch: `agent/pass219-i151-fixed5184-21-benchmark-history`
- Validated implementation/workflow head: `1d1917f2ca04cbac911c89789342aac2c519d4c4`
- Evidence-only head before this record: `06019416f304c6047f486c8679f6ad8a758e11cc`
- Merge target: `main`

## Fixed invariant
`5184^21 = 72^42 = 1018508951079768942856287659839033239780646340393381046433745481643146696720384`.

The resolution is fixed for this optimization. Efficiency may improve; resolution may not be reduced. No exhaustive enumeration of the full cardinality is claimed.

All accepted entries bind the four cooperating lanes:
`RAW5184_X86_64`, `VM81_HASH72_HASH216`, `OCTONION_DUAL_STEREO_TERNARY`, `HARMONIC36_144X36`.

## Implemented surfaces
- fixed-resolution contract and documentation;
- `benchmarks/pass219/pass219_i151_benchmark_history.py`;
- `tests/pass219/test_pass219_i151_benchmark_history.py`;
- `.github/workflows/pass219-i151-fixed5184-21-benchmark-history.yml`;
- seed and canonical JSONL history under `evidence/pass219/`;
- run-specific evidence for accepted/rejected history runs.

The collector auto-discovers Pass 219/219B benchmark surfaces, hashes the inventory, hashes bound receipts, rejects duplicate run keys, rejects resolution/lane drift, and chains accepted entries with `previous_line_sha256`.

The workflow runs on the feature branch and `main`. Canonical history/evidence paths are excluded from trigger paths to avoid recursive benchmark loops.

## Accepted evidence
### Run 33719250898
- Head: `46a2ebf29ffcd44b69b943430afbf05d005e062d`
- Job: `100534816375`
- Artifact: `9879617166`
- Artifact SHA-256: `017caeb88625fd22648691c8eea52fed3ba01f1c47562d1bb6f3332f2ead0b5b`
- Inventory: 22 surfaces; root `6e39e5110e1be42252aa8a4fa02454f260626c81929ab338fc33a3f9a47ca187`.

Fresh logical-work results:
- raw5184/audio: `11,466,081 -> 5,645,376`; saved `5,820,705`; reduction floor `507‰`.
- cross-modal reversible state: `1,384,512 -> 32,228`; saved `1,352,284`; reduction floor `976‰`.

### Run 33719623520 — accepted cumulative proof
- Head: `1d1917f2ca04cbac911c89789342aac2c519d4c4`
- Job: `100535907404`
- Artifact: `9879742728`
- Artifact SHA-256: `7be58453100ab66646953e56eb18ea0cc0562cffebef59e2b7c1c39a48c296a9`
- Source history: 2 physical JSONL lines.
- Output history: 3 physical JSONL lines.
- Source SHA-256: `ecc39b5463c7599cb5b09c1316c3031211b93392249ace1145a3fa639919e5ac`.
- Output SHA-256: `e3ff6bcc99f4f70b8872e848b21ec88e159fd763a52aa808363d21ffb44c74eb`.
- Prior accepted run `33719250898` preserved.
- New `previous_line_sha256` exactly matched prior entry SHA-256 `427fbacd5b9589ffe02d625e40fd2fb6b160302daf70270fa5da2490879fa49b`.
- Fresh benchmark metrics reproduced exactly.
- Canonical VM81/Hash72/Hash216 authority changed: no.

## Repair-forward evidence
- Run `33719404534`: fresh benchmarks green but rejected from canonical accumulation because the workflow still copied the seed and did not preserve run `33719250898`.
- Run `33719599390`: failed at the cross-modal step because provenance artifact paths were inserted as stray shell commands. History emission was skipped. Corrected at `1d1917f2...`.
- Unrelated legacy workflow failures on the feature branch are outside the I151 dependency chain.

## Frozen validation
Dependency-scoped acceptance is run `33719623520` at `1d1917f2...`. Later commits only seal evidence/checkpoint state and do not modify benchmark algorithms, collector behavior, workflow behavior, or runtime authority.

## Next actions
1. Verify current `main`.
2. Open and merge the I151 PR using an expected-head guard.
3. Verify merged `main`.
4. Observe the exact-main I151 workflow.
5. Require it to preserve the accepted branch history and append one chained main entry.
6. Seal that accepted main run into the canonical JSONL plus a run-specific evidence receipt on an evidence-only follow-up. Those paths do not trigger another benchmark run.
7. Future relevant benchmark changes repeat: run -> immutable artifact -> accepted chained entry -> repository evidence seal.

Current I151 code blocker: none. Remaining closure: integration plus exact-main benchmark-history confirmation.
