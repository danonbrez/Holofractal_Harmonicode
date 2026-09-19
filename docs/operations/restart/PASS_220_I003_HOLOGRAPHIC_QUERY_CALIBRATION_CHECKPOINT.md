# Pass 220 I003 restart checkpoint — four-phase A:B:C max-hardware query calibration

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — CI PENDING**

## Lineage

- repository: danonbrez/Holofractal_Harmonicode
- merge target: main
- working branch: pass220-lo-shu-normalization-checkpoint-1
- frozen I002 predecessor head: f6be3098697b00c0a2ce056dca8fbd11388ef5a2
- I003 pre-task checkpoint: 66d0c0f1ac4319c28f90caf559da1c631b67ef83
- draft PR: #491

## Implemented files

- hhs_backend/runtime/hhs_pass220_holographic_hash216_lane5_bridge_v1.py
- benchmarks/pass220/hhs_pass220_i003_four_phase_abc_max_hardware_v1.py
- tools/pass220/hhs_pass220_i003_four_phase_abc_analyze_v1.py
- tests/pass220/test_hhs_pass220_i003_four_phase_abc_max_hardware_v1.py
- .github/workflows/pass220-i003-four-phase-abc-max-hardware.yml
- docs/pass220/PASS_220_I003_FOUR_PHASE_ABC_MAX_HARDWARE_QUERY_CALIBRATION.md
- docs/operations/restart/PASS_220_I003_PREIMPLEMENTATION_CHECKPOINT.md
- docs/operations/restart/PASS_220_I003_HOLOGRAPHIC_QUERY_CALIBRATION_CHECKPOINT.md

## Functional delta

1. I002 holographic ranker is now composable with the inherited Pass 219 1.37 Lane 5 Hash216 search surface through a candidate-only bridge.
2. Four reciprocal phase gates are frozen at xy 0->36, yx 36->0, zw 18->54, wz 54->18.
3. A:B:C same-dataset query benchmark is implemented:
   - A = holographic compositional ranking
   - B = inherited three-Hash72 Lane 5 ranking
   - C = raw exact cyclic Hash216-symbol control
4. Timed arm order rotates ABC/BCA/CAB.
5. Candidate counts begin with inherited 8..2048 ladder and may double further to an environment-configured ceiling.
6. Per-phase and all-phase max closed N are computed under one common per-arm deadline.
7. Exact analyzer retains throughput and A:B/A:C/B:C ratios as rational numerator/denominator pairs.
8. Dedicated workflow runs the inherited Pass 219 raw-runner A:B:C benchmark first in the same job before executing I003.
9. Runner hardware profile and both preflight/I003 result artifacts are uploaded together.
10. Search remains candidate-only; probability is search allocation, not admission authority.

## Validation state at checkpoint

Repository-side implementation and workflow wiring are complete.

No I003 performance result is claimed at this checkpoint. The dedicated workflow must execute on the repository runner before max-hardware N or A:B:C performance ratios are treated as measured evidence.

The workflow contains:

- strict inherited raw-runner A:B:C preflight;
- cumulative exact ABI build;
- Pass 207 CPU-reference driver build and symbol audit;
- Python syntax compilation;
- dependency-scoped I001/I002/I003 pytest run;
- small real Lane 5 integration test;
- time-bounded four-phase A:B:C max-hardware benchmark;
- exact analyzer;
- evidence artifact upload.

## Default workflow benchmark parameters

- HHS_PASS220_I003_LEG_BUDGET_NS = 120000000
- HHS_PASS220_I003_GLOBAL_BUDGET_NS = 12000000000
- HHS_PASS220_I003_MAX_CANDIDATES = 16384
- HHS_PASS220_I003_REPEATS = 3
- HHS_PASS207_GPU_BACKEND = CPU_REFERENCE

These are observational calibration settings and are not canonical constants.

## Authority state

- candidate_only = true
- canonical VM81 mutation authority = false
- canonical Hash72 authority = false
- canonical Hash216 authority = false
- timing is observational only
- exact CPU/VM81 replay remains required for inherited candidate execution

## Validation remaining

1. Dedicated I003 workflow result.
2. Repair-forward only if that workflow exposes an impacted integration defect.
3. If green, record measured per-phase max N, global max N, exact A:B/A:C/B:C ratios, and runner identity in a sealed evidence document.
4. Then compare the compositional hierarchy's retrieval quality/path closure against the inherited segment-distance ordering on a real hydrated multimodal corpus.

## Next action

Wait only for the scheduled/queued repository workflow evidence; do not reopen I001/I002 arithmetic. On workflow completion, repair forward if required, otherwise seal the measured I003 evidence and proceed to I004 real hydrated multimodal query workload calibration.
