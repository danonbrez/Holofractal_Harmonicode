# DigitalOcean exact-main production deployment

Production is required to converge to the exact accepted `main` commit, not merely a nearby branch state.

## GitHub push authority

`.github/workflows/digitalocean-production-main.yml` runs for every push to `main` and for manual dispatch. It requires the repository secret `HHS_DIGITALOCEAN_SSH_PRIVATE_KEY`. Optional repository variables are `HHS_DIGITALOCEAN_HOST` and `HHS_DIGITALOCEAN_SSH_USER`; they default to the existing production IP and `root`.

The workflow:

1. connects to the production droplet;
2. verifies `/opt/hhs/app` is a clean `main` checkout of `danonbrez/Holofractal_Harmonicode`;
3. fetches `origin/main` and requires its SHA to equal `github.sha`;
4. creates a detached worktree at that exact SHA;
5. installs/refreshes the guarded updater from that detached candidate even when the live checkout is too old to contain the installer;
6. explicitly enables promotion for the GitHub-authorized production run;
7. lets the existing guarded updater perform its isolated candidate validation, fast-forward-only promotion, service restart, health verification, and rollback policy;
8. requires `/var/lib/hhs-guarded-update/last-success.json` to name the same target SHA with outcome `PROMOTED`;
9. requires `hhs.service`, `hhs-guarded-update.timer`, loopback health, and public HTTPS health to be reachable.

A dirty production checkout is never erased automatically. The workflow prints the dirty paths and fails so host-local work can be reviewed rather than silently destroyed.

## Required invariant

```text
GitHub main SHA
  == origin/main on production host
  == /opt/hhs/app HEAD after promotion
  == guarded updater candidate_sha in last-success.json
```

If any equality is false, deployment is failed rather than reported as current.
