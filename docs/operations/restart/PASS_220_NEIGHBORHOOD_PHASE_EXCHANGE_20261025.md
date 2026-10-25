# Pass 220 — nine-by-eight reciprocal phase exchange restart

Base main: `9f471be9645bec3038b9cb18531d39614523fc0c`
Branch: `checkpoint/pass220-neighborhood-72-packet-20261025`; merge target: main.
Files: `hhs_runtime/pass220/lane5_neighborhood_phase_exchange.py`, `tests/pass220/test_lane5_neighborhood_phase_exchange.py`, `.github/workflows/pass220-neighborhood-phase-exchange.yml`, this restart record.
Expected validation: `python -m pytest -q tests/pass220/test_lane5_nucleus_group_selection.py tests/pass220/test_lane5_neighborhood_phase_exchange.py`.
Change: exact integer nine-slot by eight-phase ordered candidate descriptor plus reciprocal phase opposition, 144 directed occurrences / 72 canonical paired offsets. Predecessor tick fixed and next-tick receipt required after all edits.
Authority: no new Hash72 mint, no new VM81 commitment, no Hash216 record. Existing Pass219 Appendix A normative Hash72 and Hash216 contract inherited.
Environment: GitHub connector only; local repository not checked out. Remaining: CI, merge, verify main. Next: source-bind native phase geometry, actual edit reconciliation, canonical VM81 Hash72 receipt, Hash216 triple and replay. Blocker: no confirmed native 10,368-identity phase coordinate API accessible to this projection; caller phase data is not independently verified.
