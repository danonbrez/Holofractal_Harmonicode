# Production outage recovery checkpoint — 2026-10-05

## Incident identity

- authoritative main: `5660cb38e556422f284b394d0ef72b26ca351c1a`
- source subject: `docs: refresh Hash216 repository dependency index`
- production droplet: `hhs-production-04`
- droplet ID: `603583798`
- production public IP: `159.65.178.254`
- incident class: live production/runtime availability regression after previously closed exact-main browser acceptance
- source delta during incident: none

## Observed outage

The user reported production unavailable after terminal exact-main/browser closure.

DigitalOcean control-plane state still reported the production droplet as:

- status: `active`
- locked: `false`
- region: `nyc3`
- expected production tags present.

A direct external probe from the agent execution environment could not connect to production TCP/443 and also observed no listeners on 22/80/443/8080/8715/8720. The same probe environment could not connect to corresponding ports on sibling recovery droplets, so those direct probes are evidence of observed unavailability from that path but are not sufficient to classify DigitalOcean firewall/network root cause.

No new authoritative-main commit or production workflow mutation preceded the incident.

A DigitalOcean backup action for the production droplet completed at `2026-10-05T16:26:49Z`. This is temporally near the reported outage but is not established as causal.

## Recovery actions

1. Issued controlled DigitalOcean reboot:
   - action ID: `3451136325`
   - type: `reboot`
   - status: `completed`
   - started/completed: `2026-10-05T16:48:39Z`.

2. Re-ran only the canonical proven Exact-Main deployment job for the unchanged authoritative main:
   - workflow run: `37334420124`
   - run attempt: `2`
   - deploy job: `111877207837`
   - deployment contract: SUCCESS
   - exact Runtime OS build/seal: SUCCESS
   - pinned SSH target/credential verification: SUCCESS
   - exact bundle transfer: SUCCESS
   - guarded updater/bootstrap: SUCCESS
   - public HTTPS verification: SUCCESS
   - live Chromium capability projection: SUCCESS
   - browser evidence upload: SUCCESS
   - terminal Hash216 successor logic: SUCCESS.

The GitHub deployment plane successfully reached the production host over SSH and transferred the exact-main bundle, proving the canonical deployment path remained available.

## Recovered production evidence

Runtime bootstrap/ingress:

- `HHS_LANE5_HOST_INGRESS_READY=1`
- `HHS_LANE5_HOST_INGRESS_SOCKET_ACTIVATED=1`
- `HHS_LANE5_HOST_INGRESS_NGINX_ZERO_BYPASS=1`
- `HHS_DIGITALOCEAN_LANE5_HOST_INGRESS_VERIFIED=1`
- exact-main marker bound to `5660cb38e556422f284b394d0ef72b26ca351c1a`.

Public Runtime OS:

- `HHS_DIGITALOCEAN_PUBLIC_RUNTIME_OS_VERIFIED`
- `HHS_DIGITALOCEAN_PUBLIC_SERVICE_REGISTRY_VERIFIED=380`.

Live Chromium:

- `HHS_DIGITALOCEAN_PUBLIC_FRONTEND_CAPABILITY_SURFACE_VERIFIED=380`
- selectable service: `agent_economy.agent_algorithm_identity_v1_self_test`
- `console_errors: []`
- `page_errors: []`
- `request_failures: []`
- `http_5xx: []`
- `missing_services: []`.

Hash216 convergence:

- `HHS_EXACT_MAIN_HASH216_INDEX_TERMINAL_GENERATED_SUCCESSOR=5660cb38e556422f284b394d0ef72b26ca351c1a`
- no additional index cycle required.

## Classification

Production is recovered at the unchanged authoritative source SHA `5660cb38...`.

No source repair is justified by this incident evidence. The recovery was runtime/infrastructure-facing and succeeded through the existing exact-main bootstrap/deployment machinery.

The precise initiating cause is not proven. Do not attribute the outage to the DigitalOcean backup solely from temporal proximity.

## Restart rule

For any recurrence:

1. resolve authoritative main;
2. verify DigitalOcean droplet control-plane state;
3. use canonical Exact-Main deployment plane as the authoritative reachability/runtime recovery path;
4. require public HTTPS, service-registry, and live Chromium gates before declaring recovery;
5. if recovery fails at SSH, promotion, HTTPS, or Chromium, repair-forward only the concrete failing layer;
6. preserve exact source SHA and avoid source edits unless evidence identifies a source defect.
