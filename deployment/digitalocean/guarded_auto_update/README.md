# Guarded Continuous Integration and DigitalOcean Deployment

This directory implements the repository-to-server closure loop for the integrated HHS production service.

## Authority flow

```text
trusted feature branch
  -> pull request labeled hhs-automerge
  -> repository integration gate
  -> merge into main only after the gate passes
  -> DigitalOcean timer fetches origin/main
  -> detached candidate worktree
  -> native, Python, Node, API, and optional browser validation
  -> fast-forward promotion of the live checkout
  -> systemd restart and health verification
  -> automatic rollback on any post-promotion failure
```

The production host never runs `git pull` directly into a live process. It fetches first, validates the exact remote commit in an isolated worktree, then performs a fast-forward-only merge while the service is stopped. Non-fast-forward history, dirty host changes, failed tests, failed boot, failed service restart, or failed health checks are all deployment blockers.

## Install on the current production host

The current integrated host checkout is expected at `/opt/hhs/app` and the service at `hhs.service`.

```bash
cd /opt/hhs/app
sudo REPO_ROOT=/opt/hhs/app \
  bash deployment/digitalocean/guarded_auto_update/install.sh
```

The installer creates:

- `/usr/local/lib/hhs-guarded-update/`
- `/etc/hhs/guarded-update.env`
- `/var/lib/hhs-guarded-update/`
- `hhs-guarded-update.service`
- `hhs-guarded-update.timer`

The timer checks `origin/main` every five minutes with a randomized delay.

## First-run safety check

Before enabling live promotion, set:

```text
HHS_UPDATE_DRY_RUN=1
```

Then run:

```bash
sudo systemctl start hhs-guarded-update.service
sudo journalctl -u hhs-guarded-update.service -n 200 --no-pager
sudo tail -n 20 /var/lib/hhs-guarded-update/receipts.jsonl
```

After a candidate validates successfully, set `HHS_UPDATE_DRY_RUN=0` and run the service again.

## Candidate gate

`validate-candidate.sh` performs the bounded deployment gate:

1. `git diff --check`;
2. shell syntax validation;
3. compilation of the integrated Python entrypoints;
4. inherited native build through `bin/post_compile`;
5. production integration pytest targets;
6. JavaScript syntax and application-studio tests;
7. cold boot on an isolated candidate port;
8. structured API response checks;
9. optional Playwright browser acceptance.

After the live fast-forward, the default post-merge command rebuilds the native runtime in the live checkout. Rollback rebuilds the restored commit before service restart. The updater also synchronizes its installed scripts and systemd units from the promoted repository revision.

Browser acceptance is disabled by default on the host because Chromium installation is environment-specific. Enable it after Playwright Chromium is installed:

```text
HHS_VALIDATE_BROWSER=1
```

## Merge gate

The GitHub workflow `.github/workflows/guarded-continuous-integration.yml` runs only for same-repository, trusted-author pull requests carrying the `hhs-automerge` label. It validates the merge candidate and requests a normal GitHub merge. Branch protection remains authoritative: GitHub refuses the merge when required checks or review rules are not satisfied.

Do not use the label on forked or untrusted pull requests.

## Receipts and rollback

Every run appends a JSON receipt to:

```text
/var/lib/hhs-guarded-update/receipts.jsonl
```

The most recent successful promotion is also stored at:

```text
/var/lib/hhs-guarded-update/last-success.json
```

If restart or health verification fails after promotion, the updater resets the checkout to the previous commit, restarts the services, rechecks health, and records the rollback result.

## Operations

```bash
systemctl list-timers hhs-guarded-update.timer
sudo systemctl start hhs-guarded-update.service
sudo systemctl stop hhs-guarded-update.timer
sudo systemctl enable --now hhs-guarded-update.timer
sudo journalctl -fu hhs-guarded-update.service
```

To block automation without altering the repository:

```bash
sudo systemctl disable --now hhs-guarded-update.timer
```

A dirty live checkout intentionally blocks deployment. Commit or remove the host-local change after review; never configure the updater to erase unexplained work.
