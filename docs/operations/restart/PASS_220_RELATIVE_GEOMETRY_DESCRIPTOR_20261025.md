# Pass 220 — relative geometry descriptor checkpoint

- Base main: `4ba9d8634d72cc4c49e460de336170361bebb353`
- Branch: `checkpoint/pass220-relative-geometry-descriptor-20261025`; target: main.
- Changed source: `hhs_runtime/pass220/lane5_nucleus_group_selection.py`.
- Changed tests: `tests/pass220/test_lane5_nucleus_group_selection.py`.
- CI: inherited `.github/workflows/pass220-nucleus-group-selection.yml` scoped test.
- Design: selected nucleus group is recorded as exact integer relative xyz offsets and directed relative integer phase from its source nucleus, with ordered particle identities and source tick. No absolute position or momentum copied; no particle creation/removal.
- Known boundary: source xyz and integer phase projections are caller-supplied and NOT native verified; descriptor deliberately flags native_geometry_projection_verified=false. No native phase equivalence, physical move, temporal intervention, HNAN closure or native VM81 admission occurs. These require integrating existing authoritative C++ physics pathway.
- Commands expected in CI: `python -m pytest -q tests/pass220/test_lane5_nucleus_group_selection.py`; native/production tests not run locally (GitHub connector-only environment).
- Validation remaining: GitHub PR CI, merge and exact-main verification.
- Next: bind exact native source projection and implement constraint-checked group transfer/replay in existing Pass219 C++ cell wall with no second authority.
- Blockers: absent verified public mapping from 10,368 particle identities to native 5,184 BigInt serial positions and exact phase/momentum witness.
