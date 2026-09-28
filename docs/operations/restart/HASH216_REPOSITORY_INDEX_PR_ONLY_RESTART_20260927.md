# Hash216 Repository Index PR-Only Publication Restart Checkpoint

Date: 2026-09-27

## Base

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base main SHA: `ba331f994a29f96ea1881bbfef798c29feb1e75a`
- Branch: `repair/hash216-index-pr-only-20260927`
- Merge target: `main`

## Scope

Convert the Hash216 repository dependency-index refresher from a direct write to `main` into a PR-only publication path before strict PR protection becomes absolute.

## Changed files

- `.github/workflows/repository-hash216-dependency-index.yml`
- `tests/pass219/test_repository_hash216_dependency_index_pr_only.py`
- this restart record

## Implemented

- removed `git push origin HEAD:main`;
- removed PR-triggered redispatch of the main workflow;
- added a stable non-authoritative automation branch: `automation/hash216-repository-index`;
- generation still runs from the current authoritative main SHA;
- stale-main detection remains fail-safe;
- generated artifacts are committed only on the automation branch;
- the automation branch is updated with `--force-with-lease`, never by bypassing `main`;
- the workflow opens or updates one PR targeting `main`;
- generated-index PRs must merge through normal branch protection and required checks;
- added workflow concurrency to suppress duplicate same-ref refreshes;
- replaced unnecessary `actions: write` with `pull-requests: write`;
- added dependency-scoped static regression tests proving there is no direct-main publication command.

## Authentication note

GitHub suppresses some workflow events when a PR is created using the default `GITHUB_TOKEN`. The workflow therefore prefers `secrets.HHS_AUTOMATION_PR_TOKEN` and falls back to `github.token` only so publication remains usable before that credential is configured.

Before `merged-green-dataflow-lineage-guard` becomes a mandatory check, configure `HHS_AUTOMATION_PR_TOKEN` as a fine-grained PAT or GitHub App token that can update the automation branch and create/update PRs but has **no branch-protection bypass**. If the fallback token does not trigger downstream PR workflows, protection must fail closed rather than grant a bypass.

## Validation target

```bash
PYTHONPATH=. pytest -q tests/pass219/test_repository_hash216_dependency_index_pr_only.py
```

The existing Hash216 workflow continues to build the cumulative exact ABI, run Lane 5 hydration validation, deep-scan the repository, self-verify the generated graph, and upload evidence before publication.

## Next action

Run the PR workflow from this branch. Merge only after the dependency-index workflow and existing required checks are green. After merge, verify the next main-triggered index refresh creates/updates `automation/hash216-repository-index` and an ordinary PR rather than writing `main`.

## Repair-forward validation note

The first PR run (`HHS Hash216 Repository Dependency Index`, job `deep-index`) failed before executing any repository scan because the newly added pytest gate was ordered before the existing dependency-install step:

```text
pytest: command not found
exit code 127
```

Repair: move `Enforce PR-only publication contract` immediately after `Install exact runtime build dependencies`. No assertion, authority rule, publication restriction, or PR-only requirement was weakened.
