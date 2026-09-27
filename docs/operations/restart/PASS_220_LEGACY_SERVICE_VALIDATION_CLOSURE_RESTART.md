# Pass 220 Legacy Service Validation Closure — Restart Record

Base commit: `f9aaa2d20a8f2269a5141828852b7953b787fafc`

Branch: `pass220/legacy-service-closure-repair-20260926`

Merge target: `main`

## Changed surfaces

- Repaired workflow-admission failures caused by job-level `runner.temp` references before runner assignment.
- Repaired malformed YAML heredocs in the HHS consensus gate and Lane 5 exact-boundary 1.35 workflow.
- Added dependency-scoped main replay where historical workflows previously validated only pull requests or old agent branches.
- Added same-ref supersession cancellation so obsolete queued validations do not consume runner capacity.
- Added the legacy service closure contract, static validator, and closure workflow.

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

## Next action

Open the pull request, inspect all dependency-scoped service results, repair forward any real regression, then merge only after the closure set is green or a restartable checkpoint explicitly records a still-running external CI obligation.
