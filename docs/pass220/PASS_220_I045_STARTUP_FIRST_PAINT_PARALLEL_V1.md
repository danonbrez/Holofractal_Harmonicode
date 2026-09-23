# Pass 220 I045 — Startup First-Paint + Bounded Parallel Hydration v1

## Problem

The production recovery path still coupled browser first paint to cumulative Python
application composition and allowed heavy auxiliary work to contend shortly after
boot.

The observed structure was:

1. nginx proxied the public root to `127.0.0.1:8080`;
2. Uvicorn could not bind 8080 until `hhs_backend.production_visual_server`
   imported the cumulative Runtime OS composition;
3. that composition imports and installs many inherited Pass 218 control planes
   in one Python cold-import path;
4. runtime status hydration invoked independent read-only status routes
   sequentially;
5. the guarded updater timer was eligible three minutes after boot.

On the production 2-vCPU host this creates avoidable startup coupling and
post-boot contention.

## I045 changes

### 1. Static-first public first paint

`deployment/digitalocean/configure_runtime_os_static_first.py` installs two
presentation-only nginx locations into the existing TLS server:

```text
location = /
location ^~ /assets/
```

They serve only:

```text
/var/lib/hhs/runtime-os/current/index.html
/var/lib/hhs/runtime-os/current/assets/*
```

The inherited generic `location /` backend proxy remains present and owns
non-static requests. API/WebSocket/runtime authority remains downstream of the
existing HHS backend.

The configurator is installed during the guarded production promotion only
after the candidate Runtime OS bundle has been activated and health-verified.

### 2. Bounded parallel read-only status hydration

`hhs_backend.runtime_status_probe` now fans out independent status GETs with a
bounded semaphore.

Production default:

```text
HHS_RUNTIME_STATUS_PROBE_CONCURRENCY=2
```

The unified Hash72 ledger remains fail-closed read-only in the synthetic probe
process. `asyncio.gather` preserves the original requested path order for
emitted records, so overlap does not change deterministic external ordering.

### 3. Reduced post-start contention

The production service now uses:

```text
HHS_RUNTIME_STATUS_PROBE_START_DELAY_SECONDS=90
HHS_RUNTIME_STATUS_PROBE_CONCURRENCY=2
```

The guarded updater timer changes only its boot eligibility:

```text
OnBootSec=10min
```

Its normal recurring update cadence and all validation/promotion gates remain
unchanged.

## Authority boundary

I045 creates no new canonical state path.

```text
nginx static bytes -> presentation only
status fan-out -> read-only projection only
guarded updater -> same existing authority and validation
Lane 5 / Pass 190 / VM81 -> unchanged canonical admission
```

The static shell may render while backend hydration is unavailable, but it does
not fabricate backend health or canonical state.

## Acceptance

I045 is accepted when:

- nginx patching is idempotent;
- only root/index and hashed assets bypass backend readiness;
- the generic backend proxy remains present;
- status paths overlap with concurrency >1;
- emitted status records retain input order;
- probe ledger projection remains non-mutating;
- production probe concurrency is bounded to 2;
- the first probe is delayed 90 seconds;
- guarded updater cannot begin at the former three-minute boot boundary;
- dependency-scoped regression tests pass.

## Current live-host distinction

During implementation the DigitalOcean control plane reported the Droplet
`active`, but direct TCP probes still found ports 22, 80, 443, 8080, and 8720
closed. That is a lower host/OS boot condition; I045 does not claim application
optimization can repair an Ubuntu instance that has not brought up networking or
system services.

I045 instead removes avoidable application/deployment latency once the host
reaches normal service startup.
