# HHS Pass 202 — Guarded Continuous Integration and DigitalOcean Deployment Closure

## Contract

**Identifier:** `HHS-P202-GCI-DOD-FFP-RB-HC-RCP`

Pass 202 makes repository evolution continuously consumable by the production DigitalOcean host without permitting untested commits to replace a healthy runtime.

## Required transition

```text
candidate pull request
  -> trusted label and author gate
  -> repository-native integration validation
  -> GitHub merge into main
  -> server fetch
  -> isolated candidate worktree
  -> native + Python + Node + boot/API validation
  -> fast-forward-only local promotion
  -> systemd restart
  -> health confirmation
  -> durable promotion receipt
```

Any failed gate maps to `-1` cancellation of the candidate transition while retaining the last healthy production state. A no-change fetch maps to `0`. A validated and health-confirmed promotion maps to `+1`.

## Invariants

1. `main` is the only production source branch.
2. The configured Git remote must normalize exactly to `danonbrez/Holofractal_Harmonicode`.
3. The live checkout must be clean and attached to `main`.
4. Candidate history must be a fast-forward descendant of the deployed commit.
5. Validation runs in a detached worktree before service interruption.
6. The native runtime authority, production Python composition, application-studio JavaScript, and cold-boot API surface are deployment gates.
7. Promotion uses `git merge --ff-only`; no automated conflict resolution or force reset is authorized.
8. Post-promotion service and HTTP health are mandatory.
9. A failed restart or health check triggers rollback to the exact previous commit.
10. Every no-op, rejection, validation, promotion, and rollback emits a JSONL receipt.
11. Host-local modifications block automation and are never erased automatically.
12. The timer is bounded, singleton, and restartable from repository-visible and host-visible state.

## Repository surfaces

- `.github/workflows/guarded-continuous-integration.yml`
- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh`
- `deployment/digitalocean/guarded_auto_update/validate-candidate.sh`
- `deployment/digitalocean/guarded_auto_update/install.sh`
- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.service`
- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.timer`
- `deployment/digitalocean/guarded_auto_update/hhs-guarded-update.env.example`
- `deployment/digitalocean/guarded_auto_update/README.md`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`

## Operational boundary

GitHub performs the authoritative remote merge. The production host does not merge arbitrary feature branches and does not carry a repository write token. It consumes only `origin/main`, independently revalidates the exact commit, and promotes by fast-forward only. This separates source-control authority from runtime authority while closing the full repository-to-production loop.

## Closure

Pass 202 is complete when:

- the repository assets pass syntax and contract tests;
- the workflow is present on `main`;
- the DigitalOcean installer is run against `/opt/hhs/app`;
- the first dry-run receipt records a validated candidate or no-change state;
- live promotion is enabled only after the dry run;
- rollback has been exercised in a controlled failure test.
