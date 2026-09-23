# Pass 220 I045 — Startup First-Paint Parallel Restart Checkpoint

## Repository identity

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `398e286ee0c9d36e421ee8960315848b9284b41c`
- branch: `pass220/i045-startup-first-paint-parallel-v1`
- merge target: `main`

## Trigger

After powering on `hhs-production-01`, the DigitalOcean control plane reported
the Droplet active but the public page did not recover. Direct TCP probes from
the task environment found ports 22, 80, 443, 8080, and 8720 closed.

Repository audit also confirmed avoidable production serialization:

- public root proxied through the cumulative Python backend;
- full Runtime OS composition happens before Uvicorn port bind;
- runtime status probe explicitly executed status paths sequentially;
- guarded updater became boot-eligible after 3 minutes.

## Implemented files

```text
deployment/digitalocean/configure_runtime_os_static_first.py
deployment/digitalocean/guarded_auto_update/install.sh
deployment/digitalocean/guarded_auto_update/hhs-guarded-update.timer
deploy/digitalocean/hhs-pass196-integrated-environment.service
hhs_backend/runtime_status_probe.py
tests/pass220/test_pass220_i045_startup_first_paint_parallel.py
.github/workflows/pass220-i045-startup-first-paint-parallel.yml
docs/pass220/PASS_220_I045_STARTUP_FIRST_PAINT_PARALLEL_V1.md
docs/operations/restart/PASS_220_I045_STARTUP_FIRST_PAINT_PARALLEL_20260923.md
```

## Implemented behavior

1. nginx serves exact Runtime OS `/` and `/assets/` directly from the
   versioned current Runtime OS release.
2. all other inherited backend proxy behavior remains.
3. read-only status projection hydrates with bounded concurrency=2 and
   deterministic ordered emission.
4. production delays status probe eligibility from 30s to 90s.
5. guarded updater boot eligibility moves from 3min to 10min.
6. guarded production promotion installs/reloads the static-first nginx
   projection after successful runtime promotion.

## Authority state

No new VM81, Hash72, Hash216, Lane 5, Pass 190, or canonical mutation authority
is introduced.

## Validation next action

1. Open I045 PR.
2. Run `Pass 220 I045 Startup First Paint Parallel`.
3. Repair only impacted I045 surfaces on failure.
4. Merge exact green head if still mergeable.
5. Verify main contains I045.
6. The main push may attempt production deployment. If SSH is still unavailable,
   treat that as host recovery state rather than I045 regression.
7. Once SSH returns, rerun failed exact-main deployment and verify:
   - nginx is active;
   - `/` and `/assets/` render without backend 8080;
   - backend 8080 warms independently;
   - no boot-time updater contention before 10 minutes.
