# DigitalOcean Production Recovery — 2026-08-09

## Purpose

Freeze the evidence and repair authority for the production interface outage observed on the DigitalOcean HHS deployment at `137.184.223.84`.

This recovery record is intentionally dependency-scoped. It does not redefine HHS runtime authority, alter frozen pass evidence, or promote unrelated draft branches.

## Incident evidence

### Deployment state

At diagnosis the production checkout reported:

- branch: `main`
- deployed commit: `36d110ba2f808f83bace25d6df84d45e44ab024b`
- current remote `main` at repair-branch creation: `66c614ae1de0c1b1651451e2c406307a8dee83ed`
- the deployed commit was an ancestor of current `main` and substantially behind the repository head.

Runtime-generated state was present in the checkout, including a modified filesystem ledger and untracked runtime/state directories. Those are production-state artifacts and must not be treated as authority for source promotion.

### TLS failure

Certbot 5.7.0 attempted HTTP-01 renewal using the webroot authenticator and failed with:

`137.184.223.84: Fetching http://137.184.223.84/.well-known/acme-challenge/...: Connection refused`

The repository renewal policy combined webroot validation with a pre-hook that stopped Nginx. The port-80 Nginx configuration also redirected every request to HTTPS instead of reserving the ACME challenge path.

The production certificate was successfully reissued using an online webroot flow:

- certificate name: `hhs-production-ip`
- subject alternative name: `IP Address:137.184.223.84`
- issuer: Let's Encrypt `YE1`
- notBefore: `Aug 9 02:34:25 2026 GMT`
- notAfter: `Aug 15 18:34:24 2026 GMT`

### Interface and runtime failure

Before the problematic restart, the existing HHS process served the interface assets successfully, including all tested CSS files with HTTP 200 responses.

After restart, startup required almost ten minutes before Uvicorn reported `Application startup complete`. During that interval Nginx correctly returned 502 because the upstream application was not yet ready.

After startup:

- local `/` returned HTTP 200;
- local `/src/styles.css` returned HTTP 200 with `text/css`;
- public critical CSS returned HTTP 200;
- public `production-startup-coordinator.mjs` returned HTTP 200;
- the public root could still time out under runtime load.

The live runtime status then proved the idle-load regression:

- `running: true`
- `authority_ready: true`
- `background_task_active: true`
- cognition `enabled: true`
- runtime tick count continued advancing without an explicit user workload
- the HHS Uvicorn process consumed approximately `99.7%` CPU during the observed sample.

The previous long-running process had accumulated more than three days of CPU time and reached approximately 1.9 GB peak resident memory before restart.

## Root causes

### 1. Certificate renewal lifecycle

The renewal policy stopped Nginx immediately before a webroot HTTP-01 challenge. This removed the exact HTTP service needed by the certificate authority and deterministically produced connection refusal.

### 2. Idle runtime lifecycle

`LiveFastAPIRuntimeWorkflow` accepted `auto_start=True` from server composition and unconditionally created a continuous background tick task. The cognition coordinator also historically defaulted its own automatic processing to enabled. The result was continuous kernel, semantic-memory, vector-cache, replay, prediction, and cognition work while the production UI was otherwise idle.

## Canonical repair branch

Branch:

`agent/canonicalize-production-recovery`

Base:

`main` at `66c614ae1de0c1b1651451e2c406307a8dee83ed`

The branch is deliberately independent of the broader draft repair PRs.

## Repair authority

### Runtime quiescence

Production behavior is now:

1. perform one real startup transition sufficient to establish receipt/runtime authority;
2. do not create a continuous background tick task unless `HHS_RUNTIME_AUTO_TICK=1` is explicitly configured;
3. do not enable cognition auto-processing unless `HHS_COGNITION_AUTO_TICK=1` is explicitly configured;
4. move synchronous packet export and graph ingestion off the FastAPI serving event loop;
5. expose bounded authority status proving whether continuous ticking and cognition are enabled.

The canonical DigitalOcean service definition explicitly sets both automatic clocks to zero, and the production gateway applies the same defaults defensively when a service environment is incomplete.

### TLS renewal

Production renewal now:

1. keeps Nginx online throughout HTTP-01 validation;
2. reserves `/.well-known/acme-challenge/` on port 80 for a dedicated webroot;
3. locally self-tests the Nginx ACME path before renewal is considered configured;
4. removes obsolete Nginx stop/start renewal hooks;
5. uses a deploy hook to reload Nginx only after a successful certificate deployment;
6. preserves ordinary port-80 traffic as an HTTPS redirect;
7. verifies the HTTPS root, critical stylesheets, and startup JavaScript as production acceptance surfaces.

## Required validation

Repository CI must prove:

- shell syntax for the production HTTPS closure;
- ACME webroot configuration is present;
- a successful-renewal deploy hook is present;
- no production renewal path contains `systemctl stop nginx`;
- no webroot renewal path contains `--pre-hook`;
- runtime automatic clocks default disabled;
- explicit opt-in still enables continuous runtime execution;
- production service definition freezes both automatic clocks to zero;
- production gateway remains importable and status-cache tests pass.

## Deployment closure procedure

After this focused repair is merged to `main`, production should be reconciled from repository authority rather than from either draft repair branch.

Before source synchronization, preserve the production runtime-state directories and current systemd/Nginx configuration as rollback evidence. Runtime-generated state must not be accidentally committed as source.

After source synchronization:

1. install `deploy/digitalocean/hhs-pass196-integrated-environment.service` as the active `hhs.service`;
2. reload systemd and restart the HHS service once;
3. require `running=true` and `authority_ready=true`;
4. require `background_task_active=false`;
5. require continuous runtime ticking disabled;
6. require cognition auto-ticking disabled;
7. require local and public root/CSS/critical-JS responses to succeed within bounded time;
8. require idle CPU to fall materially below the previously observed saturated-core state;
9. apply the canonical HTTPS closure with the online ACME webroot policy;
10. only after those checks pass, perform the pending operating-system reboot and rerun the same acceptance checks.

## Non-authority statements

- The broad draft PRs that originally explored interface repairs are not deployment authority.
- A local DigitalOcean hotfix is not repository authority.
- Runtime-generated ledgers, caches, hydration artifacts, and state directories are not source commits.
- Successful static-asset responses do not by themselves prove application responsiveness; the root/API path and idle runtime state are required acceptance evidence.
