# Pass 219 Lane 5 1.49 — T5184 Phase-Support Optimization Restart Checkpoint

**Date:** 2026-09-19  
**Base main:** `ce0898979ceaa6d0a33fe00a257e8a71344f8de5`  
**Branch:** `pass219/lane5-t5184-phase-support-1-49`  
**Merge target:** `main`  
**PR:** `#509`  
**Reviewed defect head:** `1aa8ab9acb8a828bd71fdd077eea16c1ca33b40c`  
**Repair head before this checkpoint record:** `7661fa86c8a3cd8c99299f13a24222b228d06070`

## Objective

Lower the repaired Pass 220 ordered operation64 phase geometry into the next executable Lane 5 optimization cycle, with independent Wolfram evidence and without relaxing full-state identity, CPU replay, or canonical authority boundaries.

## Implemented exact optimization

The operation64 support set is:

```text
{4,5,6,7,16,17,18,19,44,45,46,47,56,57,58,59}
```

and the exact mask is:

```text
0x0f00f000000f00f0
```

Per VM81 cell:

```text
phase support = 16
phase-specific bypass = 48
```

Across 81 cells:

```text
support = 1296 = 36^2 = 18*72
bypass = 3888
xy = yx = zw = wz = 324 occurrences each = 18^2
```

The optimization directly enumerates the 16 support positions for phase-specific work. The other 48 positions bypass only the phase-specific inspection loop. Full 5,184-position state identity and exact replay remain mandatory.

## Wolfram validation already executed

Independent Wolfram Language kernel evaluation:

```text
18/18 exact checks PASS
support mask: 0f00f000000f00f0
support positions: 16/64
VM81 support: 1296
VM81 bypass: 3888
ordered pair counts: 324 each
x^2=I, y^2=-I, xy+yx=0, zw=xy, wz=yx
```

Repository-visible evidence:

```text
evidence/pass219/lane5_t5184_phase_support_1_49.wl
evidence/pass219/lane5_t5184_phase_support_1_49.output.json
evidence/pass219/lane5_t5184_phase_support_1_49.receipt.json
```

## PR #509 review repair

Two post-review blockers on `1aa8ab9acb8a828bd71fdd077eea16c1ca33b40c` were repaired forward on the existing PR branch.

### Exact local64 classification proof

Commit:

```text
ee2b8a52b7817449ea66022dace10f3f62d9961d
```

The native 1.49 test now derives the expected tuple independently for every local64 address and asserts, for all 81 VM81 cells:

```text
phase_bearing
requires_phase_specific_check
phase_code
phase_sign
representative_phase_code
support_ordinal
```

The exact ordered classification is:

```text
4..7   -> xy, +1, representative xy, ordinals 0..3
16..19 -> yx, -1, representative yx, ordinals 4..7
44..47 -> zw, +1, representative xy, ordinals 8..11
56..59 -> wz, -1, representative yx, ordinals 12..15
other   -> none, 0, representative none, ordinal UINT32_MAX
```

This closes the aggregate-count weakness that could previously allow swapped codes or incorrect individual signs to pass.

### Mandatory baseline coverage before evidence seal

Commit:

```text
7661fa86c8a3cd8c99299f13a24222b228d06070
```

The 1.49 workflow now runs, before sealing evidence:

```bash
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
make -C native_projects/hhs_pass190_operation_fabric validate
```

Each baseline writes an artifact log, and the evidence-seal step requires all four logs to exist and be non-empty. The sealed summary also records:

```text
exact_local64_classification = true
repository_baselines_passed = true
repository_baseline_count = 4
```

These fields are emitted only after the preceding commands return successfully.

## Changed files

Original 1.49 implementation surface:

```text
hhs_runtime/include/hhs_pass219_lane5_t5184_phase_support_1_49.h
hhs_runtime/c/hhs_pass219_lane5_t5184_phase_support_1_49.inc
hhs_runtime/include/hhs_runtime_exact_abi.h
hhs_runtime/c/hhs_runtime_exact_abi.c
tests/pass219/test_pass219_lane5_t5184_phase_support_1_49.c
contracts/pass219/PASS_219_LANE5_T5184_PHASE_SUPPORT_OPTIMIZER_1_49.md
docs/whitepapers/HHS_LANE5_T5184_PHASE_SUPPORT_OPTIMIZATION_1_49_V1.md
docs/whitepapers/HHS_LANE5_WHITEPAPER_INDEX_V1.md
evidence/pass219/lane5_t5184_phase_support_1_49.wl
evidence/pass219/lane5_t5184_phase_support_1_49.output.json
evidence/pass219/lane5_t5184_phase_support_1_49.receipt.json
.github/workflows/pass219-lane5-t5184-phase-support-1-49.yml
docs/operations/restart/PASS_219_LANE5_T5184_PHASE_SUPPORT_1_49_RESTART_20260919.md
```

Review-repair files:

```text
tests/pass219/test_pass219_lane5_t5184_phase_support_1_49.c
.github/workflows/pass219-lane5-t5184-phase-support-1-49.yml
docs/operations/restart/PASS_219_LANE5_T5184_PHASE_SUPPORT_1_49_RESTART_20260919.md
```

## Validation completed before this checkpoint

Repository-visible review verification confirmed:

1. PR #509 remains open and mergeable.
2. The two reported findings are present on reviewed head `1aa8ab9acb...`.
3. The runtime classifier implementation already encodes the intended exact ordered ranges; the second finding is a proof-coverage defect rather than a production-classifier defect.
4. `AGENTS.md` requires the smoke, regression, bundle-runner, and Pass 190 validation baselines.
5. The repair commits above are present on the same PR branch.

No claim is made here that the new final head is green until CI executes the repaired workflow.

## Validation remaining

On the final checkpoint head, repository CI must still:

1. build the cumulative exact C ABI;
2. verify all four 1.49 exported symbols;
3. run the exhaustive native 5,184-position classifier;
4. prove the exact code, sign, representative, and support ordinal for every local64 address across all 81 cells;
5. reproduce 1,296 support / 3,888 bypass / 324-per-pair counts;
6. rerun Lane 5 1.48 full-manifold streaming;
7. rerun Pass 220 I019 native and Python ordered-phase binding;
8. run the required runtime smoke, regression, legacy bundle-runner, and Pass 190 validation suites;
9. verify sealed Wolfram evidence SHA-256 values;
10. seal and upload the 1.49 artifact only after all preceding stages pass;
11. merge only on latest-head green, then verify the main-push 1.49 gate and current-main integration.

## Environment state

No canonical runtime state was mutated by the repair. The Lane 5 surface remains:

```text
candidate_only = true
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
canonical_persistence_authority = false
floating_point_canonical_authority = false
requires_exact_cpu_vm81_replay = true
full_state_identity_still_required = true
```

The separate Runtime OS deployment composition fault is outside this optimization cycle and remains untouched.

## Next action

Use the final checkpoint commit as the PR #509 review-repair head. Inspect the dependency-scoped CI result. Repair forward only an impacted failure. Merge only after the repaired 1.49 gate and required repository baselines are green, then verify exact main before continuing the Pass 219 sequence.


## Latest-head gate binding

The repair also closes a path-filter edge case discovered after the first checkpoint commit. A documentation-only checkpoint advanced the PR head without scheduling the path-filtered 1.49 workflow, while an older Open Stack run could be cancelled by the newer head.

Commit:

```text
1d259c7b78989676bb33496f0d5f38f4c9da470e
```

adds this restart checkpoint file itself to both the push and pull-request path filters for the 1.49 workflow. Therefore this checkpoint update schedules the repaired 1.49 gate on the actual latest PR head rather than relying on a green or queued run from an ancestor commit.

The final acceptance rule remains unchanged: do not merge until the latest-head 1.49 gate and required integration gates are green.

## Geometric I / O / K constants update

**Parent branch head:** `b13d795f58aa8fca4e7bb0f3ed6f808f22f561ea`
**Branch:** `pass219/lane5-t5184-phase-support-1-49`
**Merge target:** `main`

Added the locked typed constants, machine-readable contract, 11/11 Wolfram certificate, CI verifier, and white-paper/compendium updates. No VM81/Hash72/Hash216 authority changed.

Completed validation: connected Wolfram Language exact geometric audit `11/11 PASS`, including independent 4/4 orders, specialization, HMod covariance, built-in Mod exclusion, no machine-real constructor terms, `I_H^2=-Identity(2)`, `O->Pi`, `K->E`, and exponential closure.

Remaining: latest-head 1.49, Open Stack, and Pass 217 integration CI, then exact-main verification after merge. Queued CI is not an implementation blocker; repair forward only substantive failures.
