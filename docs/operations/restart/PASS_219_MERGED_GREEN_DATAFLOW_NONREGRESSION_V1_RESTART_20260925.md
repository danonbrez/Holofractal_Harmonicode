# Pass 219 — Merged-Green Dataflow Nonregression v1 Restart

Date: 2026-09-25

Status: **IMPLEMENTED / PR OPEN / EXACT-HEAD CI QUEUED / NOT MERGED**

## Repository state

```text
repository: danonbrez/Holofractal_Harmonicode
base main at branch creation: ea3948afecb40a35b61eb7473f094eee6fd63cb0
branch: policy/pass219-merged-green-dataflow-nonregression-v1-20260925
merge target: main
pull request: #584
pull request URL: https://github.com/danonbrez/Holofractal_Harmonicode/pull/584
last protected implementation/proof head before this checkpoint record:
  7c9129f52f03d2b24dd37cd13aebcda3266bbc86
```

Prerequisite open Lane 5 proof-binding PR:

```text
PR: #583
policy: Pass 219 Lane 5 Mediation Proof Binding 1.49
state at checkpoint: open / mergeable / dedicated exact-head job queued
```

## Governing rule

```text
MergedGreenDataflow(p)
AND ChangedOrRemovedOrBypassed(p)
=>
ValidatedSuccessorProof(CurrentPullRequest, p)
```

Scope is Pass 219 and every upstream pass represented inside the cumulative
Pass 219 runtime image.

## Written main-branch rules

The repository now contains both the declarative machine ruleset and the
normative human-readable merge rules derived from current history/contracts:

```text
.github/rulesets/HHS_MAIN_MERGED_GREEN_DATAFLOW_RULESET_V1.json
contracts/pass219/PASS_219_MAIN_BRANCH_MERGE_RULES_V1.md
```

These rules encode, without adding unsupported review requirements:

```text
pull request required
direct push forbidden
force push forbidden
main deletion forbidden
branch must be current with main
conversation resolution required
required status check:
  merged-green-dataflow-lineage-guard
queued/pending/cancelled/failed required check => DO NOT MERGE
protected change => exact successor proof
backward-compatible iteration => no predecessor identifier removal
repair-forward refinement => explicit replacement + compatibility adapter
fixed inherited validation profiles => mandatory
policy/ruleset weakening => forbidden
```

No mandatory human approval count was invented because the current HHS
contracts define executable proof/validation rather than a review quorum.
No signed-commit rule was invented because the current repository contracts do
not establish that as an inherited acceptance condition.

Both rule files are now included in `always_protected_paths` and the policy
self-integrity set. Future modification/deletion therefore requires
`REPAIR_FORWARD_REFINEMENT` under the predecessor guard.

## Implemented repository surfaces

```text
contracts/pass219/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.json
contracts/pass219/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.md
tools/pass219/pass219_merged_green_dataflow_guard_v1.py
tests/pass219/test_pass219_merged_green_dataflow_guard_v1.py
.github/workflows/pass219-merged-green-dataflow-nonregression-v1.yml
artifacts/pass219/merged_green_successor_proofs/BOOTSTRAP_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.json
AGENTS.md
docs/architecture/HHS_CUMULATIVE_PASS_GLOBAL_DEFAULTS.md
docs/operations/restart/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1_RESTART_20260925.md
```

## Enforced change classes

Protected data-flow changes are admitted only as:

```text
BACKWARD_COMPATIBLE_ITERATION
REPAIR_FORWARD_REFINEMENT
```

Backward-compatible iteration:

- exact predecessor/successor Git blobs are bound;
- no predecessor HHS callable/type identity may disappear;
- inherited authority/receipt/exactness invariants remain true;
- fixed inherited validation profiles must execute.

Repair-forward refinement:

- exact predecessor/successor Git blobs are bound;
- deletion or rename requires replacement paths;
- every removed HHS identifier requires a replacement identity and repository-
  visible compatibility adapter;
- defect, migration/continuity, rollback, negative tests and validation profiles
  are explicit.

## Protected surface discovery

The machine manifest protects:

1. Pass 206 frozen core and approved successor lineage;
2. cumulative exact ABI/build/authority architecture files;
3. pass-numbered runtime/backend/Python/native-project/contracts/tests/
   benchmarks/tools/workflows/artifacts/evidence at Pass <= 219;
4. root HHS_PASS_<n> identities at Pass <= 219;
5. new source files that increase sensitive-authority symbol occurrences;
6. this nonregression policy itself.

New proof JSON files under
`artifacts/pass219/merged_green_successor_proofs/` may be introduced by the
PR that needs them. Once merged, those evidence files become protected from
later mutation/deletion.

## Self-monotonic policy

The policy cannot weaken itself in place.

Once present on main, any change to the policy manifest, contract, guard,
tests, or workflow requires `REPAIR_FORWARD_REFINEMENT` under the predecessor
guard.

The predecessor guard rejects a successor that:

```text
decreases protected_pass_ceiling
removes protected roots
removes always-protected paths
removes mandatory invariants
removes mandatory validation profiles
removes sensitive symbols
removes protected source extensions
turns true fail-closed flags false
changes the proof directory
changes the proof schema in place
renames the required status check
removes base-guard/direct-push/fixed-validation anchors
```

Equal-or-stronger additions are permitted.

## Base-authoritative evaluation

Future PRs execute the guard and manifest from the authoritative base commit in
a detached worktree.

Therefore changing the guard in the same PR does not change the rules used to
judge that PR.

The installation PR uses the explicit bootstrap path because its base does not
yet contain the guard.

## Bootstrap proof

Exact bootstrap successor proof:

```text
artifacts/pass219/merged_green_successor_proofs/BOOTSTRAP_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.json
```

It binds the actual base merge point and Git blobs for:

```text
workflow
machine manifest
normative contract
guard implementation
guard negative tests
AGENTS.md
cumulative global-default architecture
```

The proof is `BACKWARD_COMPATIBLE_ITERATION` because the installation adds an
enforcement membrane without removing or replacing inherited runtime behavior.

## Fixed validation profiles

A protected change requires all of:

```text
PASS206_CORE_FREEZE
PASS219_CUMULATIVE_MEMBRANE
EXACT_ABI_BUILD
VM81_SINGLE_AUTHORITY
HASH72_HASH216_LINEAGE
RNA_VM5184_CELL_WALL
```

Workflow implementations run:

```text
tests/pass206/test_pass206_cumulative_enforcement_v1.py
tests/pass219/test_pass219_cumulative_pass_membrane_i116.py
make clean && make c-abi
dynamic singleton VM81 export audit
tests/pass219/test_pass219_rna_vm5184_abi_1_33.c
tests/pass219/test_pass219_vm81_pqc_firewall_1_30.cpp
tests/pass219/test_pass219_vm81_environmental_recovery_1_32.cpp
```

These commands are fixed by repository policy rather than accepted as arbitrary
proof-authored shell commands.

## Main direct-push audit

For a protected push to `main`, structural proof is not enough.

The workflow queries the GitHub commit-to-pull-request relation and requires
the head commit to be associated with an actually merged PR targeting `main`.

A protected direct push therefore fails with:

```text
PROTECTED_MAIN_PUSH_WITHOUT_ASSOCIATED_MERGED_PULL_REQUEST
```

This is an after-push audit. Hard prevention before the ref update requires the
GitHub hosting ruleset described below.

## GitHub hosting-layer state

Repository rulesets query during implementation returned:

```text
[]
```

The connected GitHub integration does not expose administration write
permission for branch-protection/ruleset mutation.

Required hosting configuration for `main` is machine-recorded as:

```text
require pull requests
disable direct pushes
required status check = merged-green-dataflow-lineage-guard
require branch to be up to date before merge
ordinary development may not bypass the required check
```

Repository contract + CI enforcement are implemented. GitHub-side physical
merge prevention requires an administrator to enable those settings.

## Validation state

PR #584 exact-head workflow:

```text
workflow: Pass 219 Merged-Green Dataflow Nonregression v1
job: merged-green-dataflow-lineage-guard
latest observed run before checkpoint: 36158089968
latest observed job: 108130192135
state: queued
```

No semantic or implementation failure has been observed from that exact-head
job because it has not yet executed.

Prerequisite PR #583 latest observed dedicated state before checkpoint:

```text
workflow: Pass 219 Lane 5 Mediation Proof Binding 1.49
run: 36151853795
job: 108126798630
state: queued
```

## Required merge order

1. Let PR #583's dedicated 1.49 proof execute.
2. If #583 is green, merge #583 and verify authoritative main.
3. Reconcile PR #584 onto that verified main.
4. Recompute the #584 bootstrap merge-base/blob proof only where the main
   reconciliation changes protected identities.
5. Rerun #584 guard plus only impacted inherited profiles.
6. Merge #584 only when the guard is green.
7. Verify main and confirm the newly merged 1.49 Pass 219 files are protected by
   the <=219 path and sensitive-symbol rules.

This ordering prevents the new policy from retroactively blocking the already
open prerequisite 1.49 repair before it reaches main, while ensuring 1.49 is
inside the protected baseline immediately afterward.

## Next action

Inspect PR #583's exact-head dedicated job first.

Do not merge either PR while its required dependency-scoped proof remains
queued or red. Do not weaken the contracts to satisfy CI. Repair only concrete
implementation, test, build, or workflow divergence.
