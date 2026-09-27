# Pass 220 Legacy Service Validation Closure — Restart Record

Base commit: `f9aaa2d20a8f2269a5141828852b7953b787fafc`

Branch: `pass220/legacy-service-closure-repair-20260926`

Merge target: `main`

Checkpoint commits:
- `7a17dd5368b38405805b2ec3f0b1afe11988762c` — repair workflow admission, malformed heredocs, path scoping, and supersession cancellation.
- `2a2d0fece1685430c322f37104a274bed36fa623` — repair remaining Pass 165/166/174/205 and immutable-index admission gates.
- `f1c8cdb8c9db0f10cbd4b93e5644f32ec9777f27` — add closure contract, validator, closure workflow, and restart record.

## Changed surfaces

- Repaired workflow-admission failures caused by job-level `runner.temp` references before runner assignment.
- Repaired malformed YAML heredocs in the HHS consensus gate and Lane 5 exact-boundary 1.35 workflow.
- Added dependency-scoped main replay where historical workflows previously validated only pull requests or old agent branches.
- Added same-ref supersession cancellation so obsolete queued validations do not consume runner capacity.
- Added the legacy service closure contract, static validator, and closure workflow.

## Executed operations

- GitHub API: created branch from exact base commit.
- GitHub Git Data API: created blobs/trees/commits and advanced the branch by fast-forward only.
- GitHub repository inspection: verified the source failure runs created zero jobs, scanned expression placement, and inspected workflow trigger/dependency surfaces.
- No local or hidden generated artifact is required to resume this task.

## Validation completed before PR

- Verified the failure head produced zero jobs for the affected malformed/admission workflows.
- Located the two unindented heredoc defects.
- Located the job-level runner-context defects across Pass 165/166/174/205, AGI runtime, immutable index, I119, and related workflows.
- Preserved the Lane 5 1.35 canonical boundary byte-length and SHA-256 assertions by changing only Python source representation, not the boundary payload.

## Validation remaining

The pull request must execute each touched dependency-scoped service workflow. Any substantive failure is a repair-forward obligation. Do not disable or weaken the historical contract to obtain green CI.

After merge, exact-main runs triggered by the touched workflow files establish the final closure receipts. Later unrelated commits inherit closure and do not rerun these services.

## Environment

GitHub-hosted Ubuntu runners. No physical-GPU claim is introduced. Existing GPU authority boundaries remain unchanged.

## Blockers

No repository blocker is known before opening the PR. External GitHub Actions validation remains to be executed.

## Next action

Open the pull request, inspect all dependency-scoped service results, repair forward any real regression, then merge only after the closure set is green or a restartable checkpoint explicitly records a still-running external CI obligation.

## Repair-forward findings from PR #593

The repaired workflows reached runners and exposed four substantive compatibility obligations:

1. Pass 166 inherited the Pass 165 real-MP4 tests but did not install ffmpeg.
2. Pass 205 repair validation referenced repair-era files absent from the current tree; it is redirected to the current continuation ABI and warm-boot state binding.
3. I119 strict C11 compilation exposed pre-C2X array-qualifier conversion in inherited HNAN 1.63 matrix multiplication; the helper is flattened to pointer indexing without changing matrix arithmetic.
4. The consensus gate invoked package modules by filesystem path, which removed the repository root from Python import resolution; it now uses module execution.

The Runtime OS Pass 205 gate is redirected to the same current continuation/warm-boot surface instead of conditionally skipping when obsolete repair-era modules are absent.

During PR validation, the existing immutable-index workflow materialized its staged implementation and advanced the branch with commit `c3692693a8d03dad51fd9b3810fe72a1c4c41bee`. That workflow-produced commit is retained as inherited branch state. Repair-forward runtime compatibility was then committed as `505554288474fd19dcabbc0df2c0b273bdcdb123`.

## I119 inherited exact-link repair

PR validation progressed beyond the strict-C11 source compile and then failed because the I119 workflow hand-linked the current aggregate exact ABI without its inherited support objects. This is the same link-composition defect previously repaired for I182.

I119 and the Pass 205 production workflow now use the repository-canonical helper:

`tools/pass219/build_exact_abi_link_support.sh`

and link the Hash216/PQC support objects plus OpenSSL in the established order. No Pass 205, HNAN, PQC, VM81, Hash72, or Hash216 algorithm was changed by this link repair.

## Pass 078 temporal freeze repair

The consensus gate exposed a stale whole-current-tree interpretation of the Pass 078 freeze manifest.

Repair-forward preserves the original manifest unchanged and validates its four byte identities at historical anchor:

`66c614ae1de0c1b1651451e2c406307a8dee83ed`

Current deviations are accepted only through explicit successor evidence:

- `hhs_runtime/c/hhs_runtime_abi.c` must equal the Pass 206 approved additive ABI successor blob `6a3ed4a10c5d83fa77bb4d118819fc230d32248a`.
- `hhs_runtime/HARMONICODE_VM_RUNTIME.c` must equal the I028 validated successor blob `92afd8d0e26119b6db6420740c05db25a37d389a`.
- I028 PR #547 merged at `86a66d32ba3c17430887cb4ff9fa0da7dbb4bf6f`; final head `8a750bb56d14fc9847166736bbbf2ca0660bff7f` passed dedicated run `35723417642`.
- VM81 opcodes 0..23 remain frozen and I028 24..34 remain append-only.
- The two unchanged Pass 078 header surfaces must remain byte-identical to the historical manifest.

A later change to any of these files reopens the consensus dependency cone and must provide a new explicit successor proof; the Pass 078 historical manifest itself is not rewritten.
