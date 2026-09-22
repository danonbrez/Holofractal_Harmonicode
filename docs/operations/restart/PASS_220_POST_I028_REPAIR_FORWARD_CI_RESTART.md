# Pass 220 post-I028 repair-forward checkpoint

Base main commit:
`86a66d32ba3c17430887cb4ff9fa0da7dbb4bf6f`

Branch:
`pass220/post-i028-repair-forward-ci-v1`

## Frozen green evidence

- PR #547 / I028 merged at the base commit.
- I028 exact-head run 35723417642 succeeded on feature head 8a750bb56d14fc9847166736bbbf2ca0660bff7f.
- Post-merge I028 run 35723644399 succeeded on main.

## Errors observed on base main

GitHub-invalid workflow definitions:
- hhs-acceptance-gate: malformed heredoc YAML.
- hhs-agi-runtime-wiring: runner.temp used in job env.
- hhs-immutable-agent-sql-index: runner.temp used in job env.
- pass165-mmvs: runner.temp used in job env.
- pass166-validation-relay: runner.temp used in job env.
- pass166-word2vec: runner.temp used in job env.
- pass174-heroku-boot-resilience: runner.temp used in job env.
- pass205-multimodal-continuation-contract: runner.temp used in job env.
- pass205-production-runtime: runner.temp used in job env.
- pass205-repair-validation-base: runner.temp used in job env.
- pass219-cumulative-pass205-membrane-i119: runner.temp used in job env.
- pass219-lane5-exact-boundary-quantum-thermo-1-35: one unindented Python triple-string continuation broke YAML.

Additional actionlint security findings repaired:
- hhs-agi-runtime-wiring no longer interpolates github.head_ref directly in shell.
- vm81-game-level10 checks out immutable PR head SHA or github.sha.

Production deployment failure:
- run 35723644365 reached the production host but systemd failed with status 200/CHDIR because user hhs could not traverse the release path under /var/lib/hhs.
- installer now establishes /var/lib/hhs as root:hhs 0750, verifies service-user traversal/read access before restart, and resets stale systemd failure state.

## Validation plan

1. Branch-local actionlint syntax/expression audit with shellcheck advisory checks disabled.
2. Dependency-scoped Pass 220 application VM tests and shell syntax.
3. Open a repair PR and allow affected workflows to construct real jobs.
4. Repair-forward any newly exposed executable failure by dependency frontier.
5. Merge only after repair-specific gates are green.
6. Verify main and production deployment.
7. Remove the temporary actionlint helper before final merge.


## Repair-forward cycle — 2026-09-22 post-I028 exact-head failures

Implementation head before this restart-record update:
`e6234a0df28d279cbae70966ae3a8e23115a8ce9`

Merge target:
`main`

Branch state at implementation head:
- base/merge-base: `86a66d32ba3c17430887cb4ff9fa0da7dbb4bf6f`
- ahead: 22 commits
- behind: 0 commits
- PR: #548

### Exact-head failures reproduced from e5965ace

The prior PR head constructed real jobs and exposed nine failing workflow families:

1. Pass 166 Word2Vec: real MP4 fixture required `ffmpeg`.
2. Pass 205 Repair Validation Base: retired `deployment/digitalocean/pass205_state/install.sh` path.
3. HHS Consensus Gate: direct script invocation broke package imports.
4. Lane 5 Exact Boundary Quantum Thermo: registry tests lacked FastAPI test dependencies.
5. Pass 205 Production Runtime: inherited exact ABI test hand-linked `exact.o` without Hash72/C++ cell-wall dependencies.
6. Pass 219 cumulative Pass 205 membrane: stale Pass 214 VM81 rebind identity test.
7. Pass 205 Multimodal Continuation: direct validation script lacked repository import root.
8. Pass 219 cumulative Pass 202 membrane: two legitimate successor deployment blobs had changed but the successor identity seal was stale.
9. VM81 Exact ABI Repair: six inherited membrane tests repeated the obsolete standalone `exact.o` link composition.

### Repair commits in this cycle

- `6e4b8be57696aafa7c5e2068b19c3562fbd1ff83` — install ffmpeg for Pass 166 real-format validation.
- `2dbfb267708e1482b221405485440d96ea79d689` — remove retired Pass 205 deployment path/test references.
- `6ca923041a5bf7c78142aed78843dbaa73d72dba` — invoke consensus verification as package modules and checkout repository in the consensus job.
- `a11fedf61ff78b3f66e283429898bb4e31794b86` — install exact quantum/symbolic Python dependencies.
- `a818be9da4b022b2a3f3dbb3fafe79a43261bbef` — bind Pass 205 hosted validation to `PYTHONPATH="$PWD"`.
- `67176a2f13e933131076fb8c16543246963d450b` — use canonical `libhhs_runtime.so` link composition for Pass 205 I119 validation.
- `d6303d804bda432cd68e2868e0716e67054ab189` — make inherited exact-ABI pytest regressions use the canonical shared runtime rather than standalone `exact.o`.
- `81dabf30abbd9b344335beb7ca2d242fd43ee476` — reseal current Pass 202 successor deployment blobs while retaining frozen historical identities.
- `e6234a0df28d279cbae70966ae3a8e23115a8ce9` — repair Pass 214 VM81 successor identity membrane by verifying actual current Git blob identities and preserving historical blob identities separately.

### Changed surfaces added by this cycle

- `.github/workflows/pass166-word2vec.yml`
- `.github/workflows/pass205-repair-validation-base.yml`
- `.github/workflows/hhs-acceptance-gate.yml`
- `.github/workflows/pass219-lane5-exact-boundary-quantum-thermo-1-35.yml`
- `.github/workflows/pass205-multimodal-continuation-contract.yml`
- `.github/workflows/pass205-production-runtime.yml`
- `.github/workflows/pass219-cumulative-pass202-membrane-i122.yml`
- `tests/test_hhs_exact_runtime_abi_v1.py`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i116_pass214.py`

### Validation completed

- Failure logs for all nine red workflow families were inspected at exact head `e5965ace86d49bbaf77d84e6d71161d54988b523`.
- Each repair was traced to its failing command/step rather than suppressing the gate.
- Canonical exact ABI composition follows the already-validated I028 pattern:
  `make c-abi -> libhhs_runtime.so -> -lcrypto -lstdc++ -pthread -lm`.
- Pass 202 current successor file identities were recomputed from repository blobs before resealing.
- Pass 214 now computes Git blob SHA-1 from file bytes and compares against explicit current successor identities; it no longer requires a SHA literal to be embedded in unrelated validator source.
- Repair Forward Workflow Syntax Audit completed successfully on commits `6e4b8be5...` and `2dbfb267...`; later workflow-edit audit runs were queued at checkpoint time.
- Static inspection confirmed the repaired Pass 205 production workflow and inherited exact ABI tests use canonical shared-runtime linkage.

### Validation remaining / external queue state

At implementation head `e6234a0d...`, GitHub had 42 PR workflow runs queued and one pending. No completed run on that head had produced a new failure yet. This is an external CI queue condition, not a local repair blocker.

The latest workflow-only syntax-audit run covering all workflow edits is run `35733423965` at head `81dabf30abbd9b344335beb7ca2d242fd43ee476`; it was queued at checkpoint time.

Key exact-head runs to inspect first when the queue advances:
- Pass 166 Word2Vec: `35733636067`
- HHS Consensus Gate: `35733636023`
- Pass 205 Repair Validation Base: `35733635984`
- Pass 205 Production Continuation Runtime: `35733635694`
- Pass 205 Multimodal Continuation Contract: `35733635939`
- Pass 219 Lane 5 Exact Boundary Quantum Thermo 1.35: `35733635894`
- Pass 219 Cumulative Pass 205 Membrane I119: `35733636100`
- Pass 219 Cumulative Pass 202 Membrane I122: `35733635930`
- VM81 Exact ABI Repair: `35733635960`

### Environment and authority state

- GitHub Actions runners: Ubuntu latest / Ubuntu 24.04 according to each workflow.
- Python: 3.11 or 3.12 according to workflow.
- Canonical native ABI build: repository `make c-abi`.
- No authority widening, warning suppression, or bypass was introduced.
- Historical Pass 214/Pass 202 identities remain recorded separately from repair-forward successor identities.
- Main was unchanged during this repair cycle and remained at `86a66d32ba3c17430887cb4ff9fa0da7dbb4bf6f`.

### Next action

Read the exact-head run conclusions listed above. For every new failure, repair only the impacted dependency surface and preserve already-green evidence. If those repaired workflow families are green, verify PR #548 remains zero commits behind main, then merge/verify main. Do not rerun unaffected historical workloads solely for reassurance.

### Blockers

No repository-code blocker is known at this checkpoint. The only unresolved item is queued GitHub Actions execution.
