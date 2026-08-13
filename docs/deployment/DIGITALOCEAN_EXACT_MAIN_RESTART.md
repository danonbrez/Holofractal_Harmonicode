# DigitalOcean exact-main deployment restart record

- Base main: `482bc7f2c8b11161989687338ba18d4f4b94d6f6`
- Branch: `agent/digitalocean-exact-main-deployment`
- Merge target: `main`
- Scope: restore repository-visible exact-main DigitalOcean deployment bootstrap; no Pass 217 backend semantic changes.

## Changed files

- `.github/workflows/digitalocean-production-main.yml`
- `deployment/digitalocean/guarded_auto_update/install.sh`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
- `docs/deployment/DIGITALOCEAN_EXACT_MAIN.md`
- `docs/deployment/DIGITALOCEAN_EXACT_MAIN_RESTART.md`

## Validation completed before remote commit

- `bash -n deployment/digitalocean/guarded_auto_update/install.sh`
- YAML parse of `digitalocean-production-main.yml`
- source assertions for exact `github.sha`, promotion receipt equality, timer/service health, and required SSH authority
- verified current main is one clean successor of the prior interface merge, touching only Pass 159 closure evidence

## Production observations

- Existing `hhs-runtime-os-deploy.yml` validates/uploads artifacts but does not deploy to the droplet.
- The existing guarded updater is designed to fetch and fast-forward all of `origin/main` once installed.
- Historical host evidence showed `hhs-guarded-update.timer` absent.
- Direct connection attempts to production IP `137.184.223.84` on ports 80, 443, and 8080 were refused from the current execution environment.
- GitHub integration cannot list repository Action secret names; exact host bootstrap therefore requires `HHS_DIGITALOCEAN_SSH_PRIVATE_KEY` to be configured.

## Next action

Commit the branch, open a PR, validate the deployment contract, reconcile any main movement, merge exact-head, and inspect the push-triggered `DigitalOcean Production Exact Main` run. If it fails, use the workflow logs as the authoritative deployment blocker and repair forward without erasing host-local changes.
