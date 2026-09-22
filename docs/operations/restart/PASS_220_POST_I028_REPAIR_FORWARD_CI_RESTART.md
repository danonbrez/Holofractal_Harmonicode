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
