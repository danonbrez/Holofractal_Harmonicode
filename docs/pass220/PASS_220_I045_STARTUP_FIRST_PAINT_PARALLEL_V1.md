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

### 1. Lane-5-mediated public first paint

`deployment/digitalocean/configure_runtime_os_static_first.py` retains the
root/asset cache-policy locations in the existing TLS server:

```text
location = /
location ^~ /assets/
```

Those locations no longer serve files directly from the nginx filesystem.
Root HTML, hashed assets, APIs, and WebSockets all proxy first to the
systemd-owned Lane 5 host ingress socket on `127.0.0.1:8715`. The gateway
binds exact request bytes and provenance through the inherited arbitrary-byte
Lane 5 1.48 membrane before forwarding accepted traffic to the private runtime
on `:8080` or the application-VM service on `:8720`.

This repair-forward removes the prior presentation bypass. First-paint caching
is still allowed; bypassing Lane 5 admission is not.

The configurator is installed during guarded production promotion only after
the candidate Runtime OS bundle and the local Lane 5 native self-test are
health-verified.

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

The guarded updater remains a follower to push-triggered exact-main delivery and
is deliberately delayed so it cannot contend with host recovery:

```text
OnBootSec=15min
OnUnitActiveSec=30min
RandomizedDelaySec=2min
AccuracySec=30s
```

This repair-forward refinement preserves the same validation/promotion authority
while removing the former five-minute recurring contender from startup.

## Authority boundary

I045 creates no new canonical state path.

```text
public 80/443 -> nginx -> systemd socket :8715
             -> exact-byte Lane 5 candidate mediation
             -> private :8080 / :8720
             -> inherited signed environmental VM81 admission where mutating
status fan-out -> read-only projection only
guarded updater -> same existing authority and validation
SSH/22 -> independent recovery/management plane
```

Lane 5 remains candidate-only at this host boundary. The gateway cannot mint
VM81, Hash72, Hash216, persistence, PQC-key, or receipt-clock authority. If the
private backend is unavailable, the socket remains owned and the public request
degrades to a mediated 503 rather than treating backend disappearance as a valid
bypass.

## Acceptance

I045 is accepted when:

- nginx patching is idempotent;
- root/index, hashed assets, APIs, and WebSockets all traverse Lane 5 ingress;
- no public nginx route proxies directly to `:8080` or `:8720`;
- the Lane 5 socket remains independently owned when the private backend fails;
- status paths overlap with concurrency >1;
- emitted status records retain input order;
- probe ledger projection remains non-mutating;
- production probe concurrency is bounded to 2;
- the first probe is delayed 90 seconds;
- guarded updater cannot begin at the former three-minute boot boundary;
- watchdog boot eligibility is at least 15 minutes;
- recurring watchdog cadence is 30 minutes rather than the former five-minute contender;
- dependency-scoped regression tests pass.

## Current live-host distinction

During implementation the DigitalOcean control plane reported the Droplet
`active`, but direct TCP probes still found ports 22, 80, 443, 8080, and 8720
closed. That is a lower host/OS boot condition; I045 does not claim application
optimization can repair an Ubuntu instance that has not brought up networking or
system services.

I045 instead removes avoidable application/deployment latency once the host
reaches normal service startup.
