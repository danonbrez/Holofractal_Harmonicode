# Pass 220 nucleus-centered group selection checkpoint (2026-10-24)

- Base main commit: `f69121388f6f5c1598a8ca7cb457dd47ca7fd1bd`.
- Branch / merge target: `checkpoint/pass220-nucleus-neighbor-selection-20261024` -> `main`.
- Changed source: `hhs_runtime/pass220/lane5_nucleus_group_selection.py`.
- Changed tests: `tests/pass220/test_lane5_nucleus_group_selection.py`.
- CI: `.github/workflows/pass220-nucleus-group-selection.yml`.
- Implementation: complete 10,368-identity immutable graph snapshot; exact integer xyz squared distances; optional 3-axis toroidal wrap; stable particle-ID ties; nucleus plus 0..10,367 closest others; computational tick is never a spatial axis.
- Existing native authority remains unchanged. Projection has NO intrinsic HNAN native coordinate verification, no physical edit, no momentum transfer, no VM81/Hash72/Hash216 mint or persistence authority. Consumer must bind native verified tick and exact replay before commit.
- Intended validation: `python -m pytest -q tests/pass220/test_lane5_nucleus_group_selection.py`.
- Environment: GitHub connector-only, no checked-out local HHS repository; Python native suite not run locally.
- Validations remaining: PR CI and main verification.
- Next: connect this read-only nucleus selector to the authoritative native geometry projection and then separately implement group motion/relative-geometry transplant with replay witnesses.
- Blocker: no repository-native verified per-particle xyz projection currently bound to this selection API; untrusted input is explicitly flagged.

## Validation repair cycle (2026-10-25)
- Initial focused run `40155033172`: 10 passed, 1 failed. Toroidal fixture had another particle at x=9, exactly coincident with x=0 under period 9; algorithm tie behavior was consistent.
- Changed `tests/pass220/test_lane5_nucleus_group_selection.py` to put unrelated graph particles at nonzero y so the intended wrapped neighbor is uniquely closest.
- Test repair commit: `452a841dfc26c37e4b226c5985b683882f63f043`.
- Focused rerun `40182088011`: queued at inspection; do not assert green without checking result and job logs.
- Changed files in this cycle: test fixture and this restart record. No source behavior changes.
- Next: inspect rerun; on success mark PR ready, merge if gates permit, verify exact main. Then source-bind native xyz geometry and preserve all typed provenance.
